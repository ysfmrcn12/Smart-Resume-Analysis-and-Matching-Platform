"""Fine-tune a cross-encoder ranking model on job/resume relevance labels.

Expected CSV columns:
- job_text
- resume_text
- label (float in [0, 1] or integer relevance grade)
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List, Tuple


def _load_rows(csv_path: Path) -> List[Tuple[str, str, float]]:
    rows: List[Tuple[str, str, float]] = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"job_text", "resume_text", "label"}
        missing = required.difference(reader.fieldnames or set())
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        for item in reader:
            job = (item.get("job_text") or "").strip()
            resume = (item.get("resume_text") or "").strip()
            if not job or not resume:
                continue
            try:
                label = float(item.get("label", 0))
            except ValueError:
                continue
            rows.append((job, resume, label))
    if not rows:
        raise ValueError("No usable training rows found in dataset.")
    return rows


def main():
    parser = argparse.ArgumentParser(description="Train relevance cross-encoder for ranking.")
    parser.add_argument("--dataset", required=True, help="CSV path with job/resume/label columns")
    parser.add_argument(
        "--base-model",
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        help="Cross-encoder checkpoint to fine-tune",
    )
    parser.add_argument("--output-dir", required=True, help="Directory to save trained model")
    parser.add_argument("--epochs", type=int, default=1, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    args = parser.parse_args()

    try:
        from sentence_transformers import InputExample
        from torch.utils.data import DataLoader
        from sentence_transformers.cross_encoder import CrossEncoder
    except Exception as exc:
        raise RuntimeError(
            "Missing dependencies. Install with: pip install -r requirements-transformers.txt sentence-transformers"
        ) from exc

    dataset_path = Path(args.dataset).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = _load_rows(dataset_path)
    train_examples = [
        InputExample(texts=[job, resume], label=float(label))
        for job, resume, label in rows
    ]
    train_loader = DataLoader(train_examples, shuffle=True, batch_size=args.batch_size)

    model = CrossEncoder(args.base_model, num_labels=1)
    warmup_steps = max(1, int(len(train_loader) * args.epochs * 0.1))
    model.fit(
        train_dataloader=train_loader,
        epochs=args.epochs,
        warmup_steps=warmup_steps,
        output_path=str(output_dir),
    )
    print(f"Saved ranking model to: {output_dir}")


if __name__ == "__main__":
    main()
