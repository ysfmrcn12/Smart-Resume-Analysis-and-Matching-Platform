"""Resume parsing engine supporting PDF, DOCX, and TXT formats."""
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil

from app.nlp.preprocessing import TextPreprocessor


class ResumeParser:
    """Parse resumes from PDF, DOCX, and TXT formats."""

    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}
    EMAIL_PATTERN = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    )
    PHONE_PATTERN = re.compile(
        r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4}'
    )

    def __init__(self):
        self.preprocessor = TextPreprocessor(lowercase=False, remove_stop_words=False)

    def _find_tesseract_cmd(self) -> Optional[str]:
        """Find Tesseract executable."""
        cmd = os.getenv('TESSERACT_CMD') or shutil.which('tesseract')
        if cmd:
            return cmd
        # Common Windows install locations
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None

    def _find_poppler_path(self) -> Optional[str]:
        """Find Poppler's bin directory."""
        path = os.getenv('POPPLER_PATH')
        if path and os.path.isdir(path):
            return path
        # Check if pdftoppm is in PATH
        pdftoppm_path = shutil.which('pdftoppm')
        if pdftoppm_path:
            return str(Path(pdftoppm_path).parent)
        # Common Windows locations
        common_paths = [
            r"C:\Program Files\poppler-23.11.0\Library\bin", # Example version
            r"C:\Program Files\poppler-0.68.0\bin",
            r"C:\tools\poppler\bin",
        ]
        for p in common_paths:
            if os.path.isdir(p):
                return p
        return None

    def _read_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        MIN_EXTRACTED_TEXT_CHARS = 50
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            text = '\n'.join(text_parts) if text_parts else ''
            if len(text.strip()) >= MIN_EXTRACTED_TEXT_CHARS:
                return text
            # If pdfplumber extracted nothing, try OCR fallback below
        except Exception as e:
            # Fallback to PyPDF2
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(file_path)
                text_parts = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                text = '\n'.join(text_parts) if text_parts else ''
                if len(text.strip()) >= MIN_EXTRACTED_TEXT_CHARS:
                    return text
                # If PyPDF2 also extracted nothing, fall through to optional OCR
            except Exception:
                # preserve original exception message for diagnostics
                orig_exc = e

        # If text extraction failed or yielded too little text, attempt OCR.
        try:
            from pdf2image import convert_from_path
            import pytesseract
        except Exception:
            raise ValueError("Python OCR libraries missing. Please run: pip install pytesseract pdf2image")

        tesseract_cmd = self._find_tesseract_cmd()
        poppler_path = self._find_poppler_path()

        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            raise ValueError("Tesseract OCR not found. If you just installed it via Chocolatey, completely close and restart your terminal/IDE to update the PATH.")

        try:
            images = convert_from_path(file_path, poppler_path=poppler_path)
        except Exception as e:
            if not poppler_path:
                raise ValueError("Poppler not found. If you just installed it, completely close and restart your terminal/IDE to update the PATH.")
            raise ValueError(f"OCR failed to convert PDF to images. Error: {str(e)}")

        if not images:
            return ''

        ocr_text_parts = []
        ocr_errors = []

        for idx, img in enumerate(images):
            try:
                ocr_text = pytesseract.image_to_string(img, lang='eng')
                if ocr_text and ocr_text.strip():
                    ocr_text_parts.append(ocr_text)
            except Exception as e:
                ocr_errors.append(f"Page {idx}: {str(e)}")

        if ocr_errors:
            print(f"OCR warnings: {', '.join(ocr_errors)}")

        ocr_text = '\n'.join(ocr_text_parts) if ocr_text_parts else ''
        return ocr_text

    def _read_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            from docx import Document
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return '\n'.join(paragraphs)
        except Exception as e:
            raise ValueError(f"Could not parse DOCX: {e}")

    def _read_txt(self, file_path: str) -> str:
        """Read text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Could not read TXT: {e}")

    def extract_text(self, file_path: str) -> str:
        """
        Extract text from resume file based on extension.

        Args:
            file_path: Path to resume file (PDF, DOCX, or TXT)

        Returns:
            Extracted text content

        Raises:
            ValueError: If format not supported or parsing fails
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported format: {ext}. "
                f"Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

        if ext == '.pdf':
            return self._read_pdf(str(path))
        elif ext in ('.docx', '.doc'):
            return self._read_docx(str(path))
        elif ext == '.txt':
            return self._read_txt(str(path))
        else:
            raise ValueError(f"Unsupported format: {ext}")

    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        match = self.EMAIL_PATTERN.search(text)
        return match.group(0) if match else None

    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text."""
        match = self.PHONE_PATTERN.search(text)
        return match.group(0).strip() if match else None

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information from resume text."""
        return {
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
        }

    def parse(self, file_path: str) -> Dict:
        """
        Parse resume file and return structured data.

        Args:
            file_path: Path to resume file

        Returns:
            Dict with keys: text, contact_info, filename
        """
        text = self.extract_text(file_path)

        contact = self.extract_contact_info(text)
        filename = os.path.basename(file_path)

        return {
            'text': text,
            'contact_info': contact,
            'filename': filename,
        }

    @classmethod
    def is_supported(cls, filename: str) -> bool:
        """Check if file format is supported."""
        ext = Path(filename).suffix.lower()
        return ext in cls.SUPPORTED_EXTENSIONS
