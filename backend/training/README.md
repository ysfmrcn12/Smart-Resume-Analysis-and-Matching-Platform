# Training Pipelines

This folder provides scripts to train the two model upgrades currently used by the project:

1. **Skill extraction model**: spaCy NER fine-tuning
2. **Section classifier**: lightweight classifier for resume section detection

The ranking pipeline in the app uses TF-IDF + skill overlap/negation logic.

## 1) Train NER model

Expected dataset format (`JSONL`):

```json
{"text":"...", "entities":[[start,end,"SKILL"], [start,end,"YEARS_EXP"]]}
```

Run:

```bash
python training/train_ner.py \
  --dataset data/training/ner_annotations.jsonl \
  --output-dir models/ner-resume \
  --epochs 10
```

Then set:

```bash
export NER_MODEL_PATH=/absolute/path/to/models/ner-resume
```

## 2) Train section classifier

Expected dataset columns (`CSV`):

- `text`
- `section` (`skills`, `experience`, `education`, `summary`, `other`)

Run:

```bash
python training/train_section_classifier.py \
  --dataset data/training/section_lines.csv \
  --output models/section/section_classifier.joblib
```

## Explainability report endpoint

Scoring reports are available at:

- `GET /api/applications/<app_id>/highlights`
- `POST /api/nlp/similarity/report`

Reports include:

- TF-IDF raw/calibrated components
- skill overlap ratio and multiplier
- final weighted score
- matching keywords and highlighted positions in resume text
