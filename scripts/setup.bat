@echo off
echo Setting up Smart Resume Analysis...

echo.
echo [1/4] Pre‑req check - OCR tools...
REM You may install Poppler/Tesseract via Chocolatey if you plan to upload scanned PDFs.
REM choco install poppler -y
REM choco install tesseract -y

echo.
echo [1/3] Backend setup...
cd /d "%~dp0..\backend"
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
python -m spacy download en_core_web_sm

echo.
echo [2/3] Frontend setup...
cd /d "%~dp0..\frontend"
call npm install

echo.
echo Done! To run:
echo   Backend:  cd backend ^&^& venv\Scripts\activate ^&^& python run.py
echo   Frontend: cd frontend ^&^& npm run dev
pause
