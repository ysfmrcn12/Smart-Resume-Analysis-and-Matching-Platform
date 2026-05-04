"""Train a lightweight resume section classifier from labeled lines.

Expected CSV columns:
- text
- section (skills, experience, education, summary, other)
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List, Tuple


def _load_rows(csv_path: Path) -> Tuple[List[str], List[str]]:
    texts: List[str] = []
    labels: List[str] = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"text", "section"}
        missing = required.difference(reader.fieldnames or set())
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        for row in reader:
            text = (row.get("text") or "").strip()
            section = (row.get("section") or "").strip().lower()
            if not text or not section:
                continue
            texts.append(text)
            labels.append(section)
    if not texts:
        raise ValueError("No valid section training rows found.")
    return texts, labels


def main():
    parser = argparse.ArgumentParser(description="Train resume section classifier.")
    parser.add_argument("--dataset", required=True, help="CSV path with text/section columns")
    parser.add_argument("--output", required=True, help="Output .joblib path")
    args = parser.parse_args()

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        from joblib import dump
    except Exception as exc:
        raise RuntimeError("scikit-learn + joblib are required for section training.") from exc

    dataset_path = Path(args.dataset).resolve()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    texts, labels = _load_rows(dataset_path)
    model = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=8000)),
            ("clf", LogisticRegression(max_iter=300)),
        ]
    )
    model.fit(texts, labels)
    dump(model, output_path)
    print(f"Saved section classifier to: {output_path}")


if __name__ == "__main__":
    main()
