import logging
import time
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger("sentinelai.openai")


class OpenAIServiceError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        self.status_code = status_code
        super().__init__(message)


class OpenAIService:
    def chat(self, messages: list[dict[str, str]]) -> str:
        if not settings.openai_api_key:
            raise OpenAIServiceError("OpenAI is not configured", 503)

        started = time.perf_counter()
        for attempt in range(settings.openai_retry_count + 1):
            try:
                with httpx.Client(timeout=settings.openai_timeout_seconds) as client:
                    response = client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"},
                        json={"model": settings.openai_model, "messages": messages},
                    )
                if response.status_code >= 500 and attempt < settings.openai_retry_count:
                    self._log_provider_error(response, attempt)
                    continue
                if response.is_error:
                    self._raise_provider_error(response, attempt)
                content = response.json()["choices"][0]["message"]["content"]
                logger.info("openai_chat_completed model=%s latency_ms=%s", settings.openai_model, round((time.perf_counter() - started) * 1000, 2))
                return content
            except httpx.TimeoutException as exc:
                if attempt < settings.openai_retry_count:
                    logger.warning("openai_request_timeout attempt=%s exception=%r", attempt + 1, exc)
                    continue
                logger.exception("openai_request_timeout attempt=%s exception=%r", attempt + 1, exc)
                raise OpenAIServiceError("OpenAI request timed out", 504) from exc
            except httpx.HTTPError as exc:
                if attempt < settings.openai_retry_count:
                    logger.warning("openai_transport_error attempt=%s exception=%r", attempt + 1, exc)
                    continue
                logger.exception("openai_transport_error attempt=%s exception=%r", attempt + 1, exc)
                raise OpenAIServiceError("OpenAI is unavailable", 502) from exc
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                logger.exception("openai_invalid_response exception=%r", exc)
                raise OpenAIServiceError("OpenAI returned an invalid response", 502) from exc
        raise OpenAIServiceError("OpenAI is unavailable", 502)

    @staticmethod
    def _provider_error_message(response: httpx.Response) -> str:
        try:
            payload: Any = response.json()
            error = payload.get("error", payload) if isinstance(payload, dict) else payload
            if isinstance(error, dict):
                return str(error.get("message") or error)
            return str(error)
        except ValueError:
            return response.text

    def _log_provider_error(self, response: httpx.Response, attempt: int) -> str:
        message = self._provider_error_message(response)
        logger.error(
            "openai_provider_error status_code=%s attempt=%s error_message=%r",
            response.status_code,
            attempt + 1,
            message,
        )
        return message

    def _raise_provider_error(self, response: httpx.Response, attempt: int) -> None:
        self._log_provider_error(response, attempt)
        if response.status_code in {401, 403}:
            raise OpenAIServiceError("OpenAI authentication failed", 502)
        if response.status_code == 429:
            raise OpenAIServiceError("OpenAI is rate limited", 429)
        raise OpenAIServiceError("OpenAI request failed", 502)
