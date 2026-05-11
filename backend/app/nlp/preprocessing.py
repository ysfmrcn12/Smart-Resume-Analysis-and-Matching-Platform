"""Text preprocessing pipeline for resume and job description analysis."""
import re
import string
from typing import List

from app.nlp.nlp_terms import STOP_WORDS


class TextPreprocessor:
    """Preprocesses text for NLP tasks: normalization, tokenization, cleaning."""

    def __init__(self, lowercase: bool = True, remove_stop_words: bool = False):
        """
        Initialize preprocessor.

        Args:
            lowercase: Convert text to lowercase
            remove_stop_words: Remove common stop words
        """
        self.lowercase = lowercase
        self.remove_stop_words = remove_stop_words

    def normalize(self, text: str) -> str:
        """Normalize text: lowercase, unicode, whitespace."""
        if not text or not isinstance(text, str):
            return ''
        text = text.strip()
        if self.lowercase:
            text = text.lower()
        # Normalize unicode
        text = text.encode('utf-8', 'ignore').decode('utf-8')
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text

    def remove_special_chars(self, text: str, keep_hyphens: bool = True) -> str:
        """Remove or replace special characters."""
        if keep_hyphens:
            # Keep alphanumeric, spaces, hyphens
            text = re.sub(r'[^\w\s\-]', ' ', text)
        else:
            text = re.sub(r'[^\w\s]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        text = self.normalize(text)
        text = self.remove_special_chars(text)
        tokens = text.split()
        if self.remove_stop_words:
            tokens = [t for t in tokens if t not in STOP_WORDS]
        return tokens

    def preprocess_for_tfidf(self, text: str) -> str:
        """Preprocess text for TF-IDF vectorization (returns string)."""
        tokens = self.tokenize(text)
        return ' '.join(tokens)

    def preprocess_for_ner(self, text: str) -> str:
        """Preprocess text for NER (preserves structure, minimal cleaning)."""
        if not text or not isinstance(text, str):
            return ''
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def process(self, text: str, for_ner: bool = False) -> str:
        """
        Main preprocessing method.

        Args:
            text: Input text
            for_ner: If True, use NER-friendly preprocessing (less aggressive)

        Returns:
            Preprocessed text
        """
        if for_ner:
            return self.preprocess_for_ner(text)
        return self.preprocess_for_tfidf(text)
