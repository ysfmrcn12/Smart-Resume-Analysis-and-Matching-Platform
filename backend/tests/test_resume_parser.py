"""Unit tests for ResumeParser."""
import os
import tempfile
import pytest
from app.nlp.resume_parser import ResumeParser


class TestResumeParser:
    """Tests for ResumeParser."""

    def test_is_supported(self):
        assert ResumeParser.is_supported("resume.pdf") is True
        assert ResumeParser.is_supported("resume.docx") is True
        assert ResumeParser.is_supported("resume.txt") is True
        assert ResumeParser.is_supported("resume.jpg") is False

    def test_parse_txt(self):
        parser = ResumeParser()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("John Doe\njohn@example.com\nPython developer with 5 years experience.\n")
            path = f.name
        try:
            result = parser.parse(path)
            assert 'text' in result
            assert 'john@example.com' in result['text'].lower() or result['contact_info'].get('email')
            assert result['filename'] == os.path.basename(path)
        finally:
            os.unlink(path)

    def test_extract_email(self):
        parser = ResumeParser()
        text = "Contact: john.doe@company.com"
        assert parser.extract_email(text) == "john.doe@company.com"

    def test_extract_phone(self):
        parser = ResumeParser()
        text = "Call me at 555-123-4567"
        assert parser.extract_phone(text) is not None
