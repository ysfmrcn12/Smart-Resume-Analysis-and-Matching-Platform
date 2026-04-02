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

    def print_ocr_debug(self) -> None:
        """Print detected OCR tool paths for debugging."""
        import shutil
        tesseract_cmd = os.getenv('TESSERACT_CMD') or shutil.which('tesseract')
        if not tesseract_cmd:
            common_tess = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe\tesseract.exe",
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            for p in common_tess:
                if os.path.exists(p):
                    tesseract_cmd = p
                    break

        poppler_path = os.getenv('POPPLER_PATH')
        if not poppler_path:
            pdftoppm_sh = shutil.which('pdftoppm')
            if pdftoppm_sh:
                poppler_path = os.path.dirname(pdftoppm_sh)
            else:
                common_poppler = [
                    r"C:\Program Files\poppler-0.68.0\bin",
                    r"C:\Program Files\poppler-21.03.0\Library\bin",
                    r"C:\tools\poppler\bin",
                ]
                for p in common_poppler:
                    if os.path.isdir(p):
                        poppler_path = p
                        break

        print('OCR debug:')
        print('  TESSERACT_CMD =', tesseract_cmd)
        print('  POPPLER_PATH  =', poppler_path)
        if not poppler_path:
            print('  --> Poppler not found; install from https://poppler.freedesktop.org/ and set POPPLER_PATH or add to PATH')
        if not tesseract_cmd:
            print('  --> Tesseract not found; install from https://github.com/tesseract-ocr/tesseract and set TESSERACT_CMD or add to PATH')

    def _read_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        # If extracted text is "too small", treat as no-text and try OCR.
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

        # Optional OCR fallback for scanned/image PDFs (requires poppler and tesseract)
        try:
            from pdf2image import convert_from_path
        except Exception:
            raise ValueError(
                "pdf2image is not installed. Install pdf2image and pytesseract to enable OCR fallback."
            )

        try:
            import pytesseract
        except Exception:
            raise ValueError(
                "pytesseract is not installed. Install pytesseract to enable OCR fallback."
            )

        # Auto-detect tesseract cmd and poppler path
        tesseract_cmd = os.getenv('TESSERACT_CMD')
        if not tesseract_cmd:
            tesseract_sh = shutil.which('tesseract')
            if tesseract_sh:
                tesseract_cmd = tesseract_sh
            else:
                # common Windows install locations
                common_tess = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                ]
                for p in common_tess:
                    if os.path.exists(p):
                        tesseract_cmd = p
                        break

        poppler_path = os.getenv('POPPLER_PATH')
        if not poppler_path:
            pdftoppm_sh = shutil.which('pdftoppm')
            if pdftoppm_sh:
                poppler_path = os.path.dirname(pdftoppm_sh)
            else:
                # common Windows locations (user may extract poppler to these)
                common_poppler = [
                    r"C:\Program Files\poppler-0.68.0\bin",
                    r"C:\Program Files\poppler-21.03.0\Library\bin",
                    r"C:\tools\poppler\poppler-23.08.0\Library\bin",
                    r"C:\tools\poppler\poppler-23.08.0\bin",
                    r"C:\tools\poppler\bin",
                ]
                for p in common_poppler:
                    if os.path.isdir(p):
                        poppler_path = p
                        break

        # configure tesseract if we found it
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        # convert pages to images using poppler if available
        try:
            if poppler_path:
                images = convert_from_path(file_path, poppler_path=poppler_path)
            else:
                images = convert_from_path(file_path)
        except Exception as e:
            # If OCR tooling (Poppler) isn't available, don't fail the whole upload.
            # We return empty text and let the rest of the pipeline score/extract safely.
            print(
                "OCR skipped: could not convert PDF pages to images for OCR:",
                str(e),
            )
            return ''

        if not images:
            return ''

        ocr_text_parts = []
        ocr_errors = []
        
        for idx, img in enumerate(images):
            try:
                # Pass PIL Image directly to pytesseract to avoid path encoding issues
                ocr_text = pytesseract.image_to_string(img, lang='eng')
                if ocr_text and ocr_text.strip():
                    ocr_text_parts.append(ocr_text)
            except Exception as e:
                ocr_errors.append(f"Page {idx}: {str(e)}")
        
        if ocr_errors:
            print(f"OCR warnings: {', '.join(ocr_errors)}")
        
        ocr_text = '\n'.join(ocr_text_parts) if ocr_text_parts else ''
        if ocr_text.strip():
            return ocr_text
        # final fallback
        print(
            "OCR skipped: no text extracted from PDF images. " 
            "Returning empty resume text."
        )
        return ''
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
