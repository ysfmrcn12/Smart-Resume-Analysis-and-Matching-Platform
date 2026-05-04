# Training Pipelines

This folder provides scripts to train the three model upgrades for the project:

1. **Ranking model** (highest impact): cross-encoder relevance scorer
2. **Skill extraction model**: spaCy NER fine-tuning
3. **Section classifier**: lightweight classifier for resume section detection

## 1) Train ranking model

Expected dataset columns (`CSV`):

- `job_text`
- `resume_text`
- `label` (0..1 or graded relevance)

Run:

```bash
python training/train_ranker.py \
  --dataset data/training/ranker_pairs.csv \
  --output-dir models/ranker-cross-encoder \
  --epochs 1
```

Then set:

```bash
export SEMANTIC_RANKER_MODEL_PATH=/absolute/path/to/models/ranker-cross-encoder
export SEMANTIC_RANKER_WEIGHT=0.6
```

`SEMANTIC_RANKER_WEIGHT` controls the blend:

`base_score = (1 - weight) * tfidf_score + weight * semantic_score`

TF-IDF remains active as fallback and baseline even when semantic scoring is enabled.

## 2) Train NER model

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

## 3) Train section classifier

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
- semantic model contribution (if enabled)
- skill overlap ratio and multiplier
- final weighted score
- matching keywords and highlighted positions in resume text
