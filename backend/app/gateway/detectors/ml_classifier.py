from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from app.gateway.context import RequestContext
from app.gateway.detectors.base import PromptDetector
from app.gateway.detectors.result import DetectorResult, DetectorStatus


MODEL_PATH = Path(__file__).resolve().parents[3] / "models" / "security-classifier-v3"


class MLClassifierDetector(PromptDetector):
    _tokenizer = None
    _model = None
    _device = None

    @classmethod
    def _load_model(cls):
        if cls._model is not None:
            return

        cls._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        cls._tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
        cls._model = AutoModelForSequenceClassification.from_pretrained(
            str(MODEL_PATH)
        )

        cls._model.to(cls._device)
        cls._model.eval()

    def analyze(self, context: RequestContext) -> DetectorResult:
        self._load_model()

        inputs = self._tokenizer(
            context.prompt,
            return_tensors="pt",
            truncation=True,
            max_length=256,
        )

        inputs = {
            key: value.to(self._device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            outputs = self._model(**inputs)

        probabilities = torch.softmax(outputs.logits, dim=-1)[0]
        predicted_id = int(torch.argmax(probabilities).item())

        label = self._model.config.id2label[predicted_id]
        confidence = float(probabilities[predicted_id].item() * 100)

        label = label.lower().replace(" ", "_")

        dangerous_labels = {
            "pii",
            "prompt_injection",
            "jailbreak",
            "toxicity",
            "harmful_behavior",
            "obfuscation",
        }

        if label in dangerous_labels:
            status = DetectorStatus.DANGEROUS
            score = confidence
            reason = (
                f"ML classifier detected {label} "
                f"with {confidence:.2f}% confidence."
            )
        else:
            status = DetectorStatus.SAFE
            score = 0
            reason = (
                f"ML classifier classified the prompt as safe "
                f"with {confidence:.2f}% confidence."
            )

        return DetectorResult(
            detector_name=self.__class__.__name__,
            status=status,
            score=score,
            confidence=confidence,
            reason=reason,
            matched_patterns=[],
        )