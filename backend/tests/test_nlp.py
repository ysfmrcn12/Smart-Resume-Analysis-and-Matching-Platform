"""Unit tests for NLP components."""
import pytest
from app.nlp.preprocessing import TextPreprocessor
from app.nlp.matching_engine import MatchingEngine


class TestTextPreprocessor:
    """Tests for TextPreprocessor."""

    def test_normalize_lowercase(self):
        preprocessor = TextPreprocessor(lowercase=True)
        assert preprocessor.normalize("Hello World") == "hello world"

    def test_normalize_whitespace(self):
        preprocessor = TextPreprocessor()
        assert preprocessor.normalize("  multiple   spaces  ") == "multiple spaces"

    def test_tokenize(self):
        preprocessor = TextPreprocessor(remove_stop_words=False)
        tokens = preprocessor.tokenize("Python developer with 5 years experience")
        assert "python" in tokens
        assert "developer" in tokens
        assert "years" in tokens

    def test_preprocess_for_tfidf(self):
        preprocessor = TextPreprocessor()
        result = preprocessor.preprocess_for_tfidf("Hello! World? 123")
        assert "hello" in result
        assert "world" in result


class TestMatchingEngine:
    """Tests for MatchingEngine."""

    def test_compute_similarity_identical(self):
        engine = MatchingEngine()
        text = "Python developer with React experience"
        score = engine.compute_similarity(text, text)
        assert 0.99 <= score <= 1.0

    def test_compute_similarity_similar(self):
        engine = MatchingEngine()
        job = "Python developer, React, SQL"
        resume = "I have 5 years Python experience and know React and SQL"
        score = engine.compute_similarity(job, resume)
        assert score > 0.3

    def test_compute_similarity_different(self):
        engine = MatchingEngine()
        job = "Java developer"
        resume = "Marketing manager with Excel skills"
        score = engine.compute_similarity(job, resume)
        assert score < 0.5

    def test_compute_similarity_empty(self):
        engine = MatchingEngine()
        assert engine.compute_similarity("", "something") == 0.0
        assert engine.compute_similarity("something", "") == 0.0
