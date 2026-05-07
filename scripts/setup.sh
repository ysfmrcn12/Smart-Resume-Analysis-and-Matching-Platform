#!/bin/bash
set -e
echo "Setting up Smart Resume Analysis..."

echo ""
echo "[1/4] Pre‑req check - OCR tools..."
echo "Checking for OCR dependencies (optional, for scanned PDFs)..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect package manager and install if missing
if command_exists apt-get; then
    if ! command_exists tesseract || ! command_exists pdftoppm; then
        echo "Attempting to install tesseract-ocr and poppler-utils for Debian/Ubuntu..."
        echo "This may require sudo privileges."
        sudo apt-get update && sudo apt-get install -y tesseract-ocr poppler-utils
    fi
elif command_exists brew; then
    if ! command_exists tesseract || ! command_exists pdftoppm; then
        echo "Attempting to install tesseract and poppler for macOS..."
        brew install tesseract poppler
    fi
else
    echo "Could not detect a supported package manager (apt or brew)."
    echo "If you need to process scanned PDFs, please install 'tesseract-ocr' and 'poppler' manually."
fi

echo ""
echo "[2/4] Backend setup..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m pip install --upgrade spacy typer click
python -m spacy download en_core_web_sm

echo ""
echo "[3/4] Frontend setup..."
cd ../frontend
npm install

echo ""
echo "[4/4] Done! To run:"
echo "  Backend:  cd backend && source venv/bin/activate && python run.py"
echo "  Frontend: cd frontend && npm run dev"
