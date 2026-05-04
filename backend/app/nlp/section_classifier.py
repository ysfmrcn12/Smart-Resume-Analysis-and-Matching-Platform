"""Resume section detection helpers (rule-based + trainable support)."""
from __future__ import annotations

import os
import re
from typing import Dict, List, Optional


class SectionClassifier:
    """
    Detect common resume sections.

    This starts with lightweight heuristics and exposes hooks for a future
    trainable classifier that can be loaded from disk.
    """

    SECTION_PATTERNS: Dict[str, List[str]] = {
        "skills": [
            r"^skills?$",
            r"^technical skills$",
            r"^core competencies$",
            r"^technologies$",
        ],
        "experience": [
            r"^experience$",
            r"^work experience$",
            r"^professional experience$",
            r"^employment history$",
            r"^work history$",
        ],
        "education": [
            r"^education$",
            r"^academic background$",
            r"^qualifications$",
        ],
        "summary": [
            r"^summary$",
            r"^professional summary$",
            r"^profile$",
            r"^objective$",
        ],
    }

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv("SECTION_CLASSIFIER_MODEL_PATH", "").strip()
        self._model = None
        self._model_load_error: Optional[str] = None

    @property
    def model(self):
        """Load a trained sklearn pipeline when configured."""
        if self._model is not None or self._model_load_error:
            return self._model
        if not self.model_path:
            return None
        try:
            from joblib import load

            self._model = load(self.model_path)
        except Exception as exc:  # pragma: no cover - depends on local model path
            self._model_load_error = str(exc)
            self._model = None
        return self._model

    def _match_header(self, line: str) -> Optional[str]:
        line_norm = re.sub(r"\s+", " ", line.strip().lower()).strip(":")
        for section, patterns in self.SECTION_PATTERNS.items():
            if any(re.match(pattern, line_norm) for pattern in patterns):
                return section
        return None

    def classify_lines(self, text: str) -> List[Dict[str, str]]:
        """
        Label each non-empty line with the currently active section.

        Returns list of: {"line": <text>, "section": <section_name>}
        """
        if not text:
            return []

        labeled: List[Dict[str, str]] = []
        current_section = "other"

        model = self.model
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue

            detected = self._match_header(line)
            if detected:
                current_section = detected
                continue

            if model is not None:
                try:
                    predicted = str(model.predict([line])[0]).strip().lower()
                    if predicted in self.SECTION_PATTERNS or predicted == "other":
                        current_section = predicted
                except Exception:
                    pass

            labeled.append({"line": line, "section": current_section})

        return labeled

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Group lines by predicted section label."""
        grouped: Dict[str, List[str]] = {
            "summary": [],
            "skills": [],
            "experience": [],
            "education": [],
            "other": [],
        }
        for item in self.classify_lines(text):
            sec = item["section"] if item["section"] in grouped else "other"
            grouped[sec].append(item["line"])
        return {k: "\n".join(v).strip() for k, v in grouped.items() if v}
