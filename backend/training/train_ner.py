"""Fine-tune a spaCy NER model for resume domain entities.

Expected JSONL format:
{"text": "...", "entities": [[start, end, "SKILL"], [start, end, "YEARS_EXP"]]}
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import List, Tuple


def _load_examples(path: Path) -> List[Tuple[str, dict]]:
    examples = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            text = obj.get("text", "")
            entities = obj.get("entities", [])
            if not text:
                continue
            examples.append((text, {"entities": entities}))
    if not examples:
        raise ValueError("No valid examples found in NER dataset.")
    return examples


def main():
    parser = argparse.ArgumentParser(description="Train resume-specific spaCy NER model.")
    parser.add_argument("--dataset", required=True, help="JSONL NER annotations path")
    parser.add_argument("--output-dir", required=True, help="Directory for saved model")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--base-model", default="en_core_web_sm")
    args = parser.parse_args()

    try:
        import spacy
        from spacy.training import Example
    except Exception as exc:
        raise RuntimeError("spaCy is required. Install backend requirements first.") from exc

    dataset_path = Path(args.dataset).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    train_data = _load_examples(dataset_path)
    nlp = spacy.load(args.base_model)
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")

    for _, annotations in train_data:
        for start, end, label in annotations.get("entities", []):
            if isinstance(label, str):
                ner.add_label(label)

    unaffected_pipes = [p for p in nlp.pipe_names if p != "ner"]
    with nlp.disable_pipes(*unaffected_pipes):
        optimizer = nlp.resume_training()
        for epoch in range(args.epochs):
            random.shuffle(train_data)
            losses = {}
            for text, annotations in train_data:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                nlp.update([example], drop=0.2, losses=losses, sgd=optimizer)
            print(f"Epoch {epoch + 1}/{args.epochs} losses={losses}")

    nlp.to_disk(str(output_dir))
    print(f"Saved NER model to: {output_dir}")


if __name__ == "__main__":
    main()
