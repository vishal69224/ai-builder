"""Local trained classifier — predicts website type from user prompt."""

from __future__ import annotations

from app.ai_model.trainer import META_PATH, MODEL_PATH, load_model
from app.generation.analyzer.website_types import WEBSITE_TYPES, WebsiteType


class LocalWebsiteClassifier:
    def __init__(self) -> None:
        self._pipeline = load_model()
        self._by_id = {t.id: t for t in WEBSITE_TYPES}

    @property
    def is_ready(self) -> bool:
        return self._pipeline is not None

    def predict(self, prompt: str) -> tuple[WebsiteType, float] | None:
        if self._pipeline is None:
            return None
        proba = self._pipeline.predict_proba([prompt])[0]
        classes = list(self._pipeline.classes_)
        best_idx = int(proba.argmax())
        type_id = classes[best_idx]
        confidence = float(proba[best_idx])
        wt = self._by_id.get(type_id)
        if wt is None:
            return None
        return wt, confidence

    def status(self) -> dict:
        meta = {}
        if META_PATH.exists():
            import json

            meta = json.loads(META_PATH.read_text())
        return {
            "ready": self.is_ready,
            "model_path": str(MODEL_PATH),
            "provider": "local_trained_classifier",
            "requires_api_key": False,
            **meta,
        }
