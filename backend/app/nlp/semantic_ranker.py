"""Optional semantic ranking model for job-resume relevance."""
from __future__ import annotations

import math
import os
from typing import Dict, Optional


class SemanticRanker:
    """
    Lazy wrapper around a fine-tuned cross-encoder model.

    The model is optional. If no model path is configured, the ranker is disabled
    and callers should rely on TF-IDF fallback scores.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv("SEMANTIC_RANKER_MODEL_PATH", "").strip()
        self._model = None
        self._load_error: Optional[str] = None

    @property
    def model(self):
        """Load and cache sentence-transformers cross-encoder on first use."""
        if self._model is not None or self._load_error:
            return self._model

        if not self.model_path:
            return None

        try:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(self.model_path)
        except Exception as exc:  # pragma: no cover - depends on local model setup
            self._load_error = str(exc)
            self._model = None

        return self._model

    @staticmethod
    def _normalize_score(value: float) -> float:
        """
        Normalize model output to [0, 1].

        Cross-encoder outputs are often logits. If output is already between 0 and
        1 we keep it; otherwise we pass it through a sigmoid.
        """
        if 0.0 <= value <= 1.0:
            return value
        return 1.0 / (1.0 + math.exp(-value))

    def score_pair(self, job_text: str, resume_text: str) -> Optional[float]:
        """Return semantic relevance score for one job/resume pair."""
        model = self.model
        if model is None:
            return None
        if not job_text or not resume_text:
            return None

        try:
            pred = model.predict([(job_text, resume_text)])
            raw = float(pred[0]) if hasattr(pred, "__len__") else float(pred)
            return max(0.0, min(1.0, self._normalize_score(raw)))
        except Exception:  # pragma: no cover - external model runtime
            return None

    @property
    def enabled(self) -> bool:
        """Whether semantic scoring is available."""
        return self.model is not None

    def info(self) -> Dict[str, Optional[str]]:
        """Expose model availability details for debugging/reporting."""
        return {
            "enabled": self.enabled,
            "model_path": self.model_path or None,
            "load_error": self._load_error,
        }
