"""Text preprocessing pipeline for resume and job description analysis."""
import re
import string
from typing import List


class TextPreprocessor:
    """Preprocesses text for NLP tasks: normalization, tokenization, cleaning."""

    # Common stop words for resume context
    STOP_WORDS = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'dare', 'ought', 'used', 'i', 'me', 'my', 'myself', 'we', 'our',
        'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
        'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
        'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
        'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
        'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'would',
        'could', 'ought', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours',
        # Domain-specific noise words to ignore for scoring and highlighting
        'experience', 'experienced', 'skill', 'skills', 'year', 'years', 'knowledge',
        'ability', 'proficient', 'proficiency', 'familiar', 'familiarity', 'working',
        'using', 'required', 'requirements', 'responsibilities', 'responsibility'
    }

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
            tokens = [t for t in tokens if t not in self.STOP_WORDS]
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
