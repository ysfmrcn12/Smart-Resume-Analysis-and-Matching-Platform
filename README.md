# Smart Resume Analysis and Matching Platform

An AI-powered platform that analyzes job postings and candidate resumes using NLP. The system matches candidate skills and experience with job requirements, scores applicants via TF-IDF cosine similarity, and ranks them by compatibility.

## Features

- **Resume Parsing**: PDF, DOCX, and TXT support
- **NLP Pipeline**: TF-IDF, spaCy NER for skills/experience extraction
- **Matching Engine**: Cosine similarity-based compatibility scoring
- **REST API**: Flask backend with job and application management

## Project Structure

```
smart resume analysis/
├── backend/           # Flask API
│   ├── app/
│   │   ├── nlp/       # Preprocessing, parser, NER, matching
│   │   ├── routes/    # API endpoints
│   │   └── models.py
│   ├── config.py
│   └── run.py
├── docs/              # Literature research, API docs, datasets
├── data/              # Sample resumes
└── README.md
```

## Prerequisites

- Python 3.9+
- PostgreSQL (create a database, then set `DATABASE_URL` in `backend/.env`)

## Setup

### 0. OCR Dependencies (scanned PDFs)

Some resumes may be scanned images which require OCR to extract text. This project uses [`pdf2image`](https://pypi.org/project/pdf2image/)
and [`pytesseract`](https://pypi.org/project/pytesseract/) for the fallback. Two binary tools must be installed on your
machine:

- **Poppler** – provides `pdftoppm` used by `pdf2image`.
- **Tesseract OCR** – performs the actual text recognition.

On **Windows** you can install both using [Chocolatey](https://chocolatey.org/):

```powershell
choco install poppler -y        # adds pdftoppm to PATH
choco install tesseract -y      # installs tesseract.exe
```

Alternatively download Poppler from <https://poppler.freedesktop.org/> and Tesseract from
<https://github.com/tesseract-ocr/tesseract>, then add the respective `bin` folders to your `PATH`
or set the environment variables `POPPLER_PATH` and `TESSERACT_CMD` to point at the executables.

If the parser cannot locate these tools it will raise a warning such as:

```
Could not convert PDF pages to images for OCR. Ensure Poppler is installed and pdftoppm is available.
```

Installing the binaries and/or setting the environment variables will prevent this message.

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Optional (Transformer-based experiments):

```bash
pip install -r requirements-transformers.txt
```

Create `.env` (or use existing):

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smart_resume
SECRET_KEY=change-me-in-production
```

Run the backend:

```bash
python run.py
```

API runs at http://localhost:5000

### 3. Database

Ensure PostgreSQL is running and your `DATABASE_URL` points to an existing database. Tables are created automatically on first run via `db.create_all()`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/jobs | List jobs |
| POST | /api/jobs | Create job |
| GET | /api/jobs/:id | Get job |
| PUT | /api/jobs/:id | Update job |
| DELETE | /api/jobs/:id | Delete job |
| GET | /api/applications/job/:id | List applications |
| POST | /api/applications/job/:id/upload | Upload resume |
| GET | /api/applications/job/:id/rank | Rank applicants |

## Testing

**Backend (pytest):**
```bash
cd backend
pytest tests/ -v
```

## Datasets

See `docs/DATASETS.md` for Kaggle and GitHub resume dataset sources.

## Documentation

- `docs/LITERATURE_RESEARCH.md` - NLP techniques and resume parsing
- `docs/API_DOCUMENTATION.md` - Full API reference
