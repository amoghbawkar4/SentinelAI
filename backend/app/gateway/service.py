import json
import logging
import time
from sqlalchemy.orm import Session

from app.core.config import settings
from app.gateway.context import RequestContext
from app.gateway.policy.decision import PolicyDecisionType
from app.gateway.authorization.decision import AuthorizationStatus
from app.gateway.response_security.engine import ResponseSecurityEngine
from app.gateway.stages import AuditLogger, AuthorizationEngine, PolicyEngine, PromptPipeline, ResponsePipeline, RiskEngine
from app.services.openai_service import OpenAIService, OpenAIServiceError

logger = logging.getLogger("sentinelai.gateway")
BLOCKED_RESPONSE = "This request has been blocked by SentinelAI Security Policy."
UNAUTHORIZED_RESPONSE = "This request is not authorized under your current access permissions."
REVIEW_RESPONSE = "This request requires additional authorization."


def _configure_development_logger() -> None:
    if settings.env != "development":
        return
    logger.setLevel(logging.INFO)
    if not any(getattr(handler, "_sentinelai_gateway_console", False) for handler in logger.handlers):
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        handler._sentinelai_gateway_console = True  # type: ignore[attr-defined]
        logger.addHandler(handler)
    logger.propagate = False


_configure_development_logger()


class GatewayError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        self.status_code = status_code
        super().__init__(message)


class SentinelAIGateway:
    """The single interception point between Workspace API and LLM providers."""

    def __init__(self, openai_service: OpenAIService | None = None, db: Session | None = None) -> None:
        self.prompt_pipeline = PromptPipeline()
        self.authorization_engine = AuthorizationEngine()
        self.risk_engine = RiskEngine()
        self.policy_engine = PolicyEngine()
        self.response_security_engine = ResponseSecurityEngine()
        self.response_pipeline = ResponsePipeline()
        self.audit_logger = AuditLogger(db)
        self.openai_service = openai_service or OpenAIService()

    def process_request(self, context: RequestContext, messages: list[dict[str, str]]) -> str:
        started = time.perf_counter()
        outcome = "error"
        provider_called = False
        provider_status_code = None
        response_outcome = None
        error = None
        try:
            self._record(context, "request_received", started)
            context = self.authorization_engine.authorize(context)
            self._record(context, "authorization", started)
            if context.authorization_decision and context.authorization_decision.status is AuthorizationStatus.DENY:
                outcome = "denied"
                self._record(context, "gateway_authorization_denied", started)
                return UNAUTHORIZED_RESPONSE
            if context.authorization_decision and context.authorization_decision.status is AuthorizationStatus.REVIEW:
                outcome = "review"
                self._record(context, "gateway_authorization_review_required", started)
                return REVIEW_RESPONSE

            context = self.prompt_pipeline.process(context)
            self._record(context, "prompt_pipeline", started)
            context = self.risk_engine.evaluate(context)
            self._record(context, "risk_engine", started)
            context = self.policy_engine.evaluate(context)
            self._record(context, "policy_engine", started)

            if context.policy_decision and context.policy_decision.decision is PolicyDecisionType.BLOCK:
                outcome = "blocked"
                response = self.response_pipeline.process(context, BLOCKED_RESPONSE)
                response_outcome = "blocked_response"
                self._record(context, "gateway_request_blocked", started)
                self._record(context, "response_pipeline", started)
                self._record(context, "gateway_completed", started)
                return response

            self._record(context, "openai_request_started", started)
            provider_called = True
            try:
                response = self.openai_service.chat(messages)
            except OpenAIServiceError as exc:
                provider_status_code = exc.status_code
                outcome = "provider_error"
                error = exc
                self._log(context, "gateway_provider_failure", started, logging.WARNING, provider_status_code=exc.status_code)
                raise GatewayError(str(exc), exc.status_code) from exc

            self._record(context, "openai_response_received", started)
            response = self.response_security_engine.analyze(context, response)
            self._record(context, "response_security", started)
            response = self.response_pipeline.process(context, response)
            response_outcome = "returned"
            outcome = "allowed"
            self._record(context, "response_pipeline", started)
            self._record(context, "gateway_completed", started)
            return response
        except Exception as exc:
            if error is None:
                error = exc
            raise
        finally:
            self.audit_logger.persist(
                context,
                outcome=outcome,
                provider_called=provider_called,
                latency_ms=round((time.perf_counter() - started) * 1000, 2),
                provider_status_code=provider_status_code,
                response_outcome=response_outcome,
                error=error,
            )

    def _record(self, context: RequestContext, event: str, started: float) -> None:
        self.audit_logger.record(context, event)

        self._log(context, event, started, logging.INFO)

    @staticmethod
    def _log(
        context: RequestContext,
        event: str,
        started: float,
        level: int,
        **additional_fields: object,
    ) -> None:
        payload = {
            "event": event,
            "request_id": context.request_id,
            "conversation_id": context.conversation_id,
            "user_id": context.user_id,
            "provider": context.provider,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
            **additional_fields,
        }
        logger.log(level, json.dumps(payload))
