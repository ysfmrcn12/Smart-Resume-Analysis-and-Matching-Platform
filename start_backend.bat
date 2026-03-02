@echo off
REM Start backend with POPPLER_PATH and TESSERACT_CMD set
setlocal enabledelayedexpansion

set POPPLER_PATH=C:\tools\poppler\poppler-23.08.0\Library\bin
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe\tesseract.exe
set SCRIPT_DIR=%~dp0

echo.
echo Checking OCR tools...
if exist "!POPPLER_PATH!\pdftoppm.exe" (
    echo [OK] pdftoppm found
) else (
    echo [ERROR] pdftoppm NOT found at !POPPLER_PATH!
    exit /b 1
)

if exist "!TESSERACT_CMD!" (
    echo [OK] tesseract found
) else (
    echo [ERROR] tesseract NOT found at !TESSERACT_CMD!
    exit /b 1
)

echo.
echo Activating virtual environment...
call "!SCRIPT_DIR!venv\Scripts\activate.bat"

echo.
echo POPPLER_PATH=!POPPLER_PATH!
echo TESSERACT_CMD=!TESSERACT_CMD!
echo.
echo Starting Flask backend...
cd /d "!SCRIPT_DIR!backend"
python run.py

pause
