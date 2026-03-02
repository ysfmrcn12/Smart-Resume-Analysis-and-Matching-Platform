#!/bin/bash
set -e
echo "Setting up Smart Resume Analysis..."

echo ""
echo "[0/4] Pre‑req check - OCR tools..."
# you may need poppler-utils and tesseract-ocr installed for scanned PDF OCR
# e.g. apt install poppler-utils tesseract-ocr (Debian/Ubuntu) or brew install poppler tesseract

echo ""
echo "[1/3] Backend setup..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

echo ""
echo "[2/3] Frontend setup..."
cd ../frontend
npm install

echo ""
echo "Done! To run:"
echo "  Backend:  cd backend && source venv/bin/activate && python run.py"
echo "  Frontend: cd frontend && npm run dev"
