# AI Agent Context: Smart Resume Analysis and Matching Platform

## 🎯 Project Overview
This project is an AI-powered platform designed to analyze job postings and candidate resumes. It extracts candidate skills and experience using Natural Language Processing (NLP), evaluates matches via TF-IDF and Cosine Similarity, and ranks applicants by a calculated compatibility score. 

## 🏗️ Architecture & Tech Stack
- **Backend:** Python (Flask), PostgreSQL, SQLAlchemy.
- **Frontend:** Next.js (App Router, React).
- **Core NLP Stack:** `spaCy` (NER), `scikit-learn` (TF-IDF, section classification), `pdfplumber`/`PyPDF2` (PDF parsing), `pytesseract`/`pdf2image` (OCR fallback).

## 📂 Key Directory Structure
- `backend/app/nlp/`: The core NLP engine containing text preprocessing, resume parsing, NER extraction, section classification, and the matching/scoring engine.
- `backend/app/routes/`: Flask API endpoints. Includes logic for file uploads, ranking, and explainable score highlights (`applications.py`).
- `backend/training/`: Scripts and documentation for fine-tuning the spaCy NER model and section classifier.
- `frontend/`: The Next.js frontend application.
- `docs/`: Literature research and dataset sources.

## ⚙️ Core Workflows
1. **Document Parsing (`resume_parser.py`):** Handles PDF, DOCX, and TXT files. Implements a multi-tier fallback system for PDFs: `pdfplumber` -> `PyPDF2` -> `pytesseract` (OCR).
2. **Information Extraction (`ner_extractor.py` & `section_classifier.py`):** Identifies typical resume sections, extracts entities (like skills, organizations, and dates), and uses a mix of regex, NLP noun chunks, and trained models to map skills.
3. **Scoring Engine (`matching_engine.py`):** Calculates a compatibility score by taking a raw TF-IDF cosine similarity, calibrating it with a saturating exponential function, and applying a penalty/bonus multiplier based on the exact ratio of matching skills.
4. **Insights Generation:** Provides transparent ranking and candidate highlight reports detailing raw TF-IDF scores, matched skill overlaps, and keyword positions within the text.

## ⚠️ Important Notes for AI Agents
- When generating or modifying Next.js frontend code, remember it uses the **App Router** paradigm (refer to `frontend/AGENTS.md` for Next.js specific instructions).
- The matching engine does not blindly penalize candidates if job skills cannot be successfully extracted (defaults multiplier to `1.0`).
- Testing environments must have Poppler (`pdftoppm`) and Tesseract OCR installed and added to the system `PATH` for the PDF OCR fallback to function correctly.
- Always preserve the human-readable explanation endpoints (like `/api/applications/<app_id>/highlights`), as explainability is a core feature of the platform.