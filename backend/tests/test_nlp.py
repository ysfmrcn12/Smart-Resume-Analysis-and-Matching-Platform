"""Unit tests for NLP components."""
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

    def test_explain_score_contains_breakdown(self):
        engine = MatchingEngine()
        job = "Python backend engineer with Flask, PostgreSQL, and Docker experience"
        resume = "Backend developer with Python, Flask APIs, Docker and SQL skills"
        report = engine.explain_score(job, resume)

        assert "final_score" in report
        assert "weights" in report
        assert "skills" in report
        assert "semantic" in report
        assert "calculation_breakdown" in report
        assert 0.0 <= report["final_score"] <= 1.0
        assert report["skills"]["matched_skill_count"] >= 1

    def test_skill_matching_is_case_insensitive(self):
        engine = MatchingEngine()

        def fake_extract_skills(text):
            if "job text" in text:
                return ["Python", "React", "SQL"]
            return ["python", "REACT", "sql", "Docker"]

        engine.extractor.extract_skills = fake_extract_skills

        metrics = engine._compute_skill_metrics("job text", "resume text")
        assert metrics["job_skill_count"] == 3
        assert metrics["matched_skill_count"] == 3
        assert metrics["matched_skills"] == ["python", "react", "sql"]

    def test_explain_score_breakdown_steps(self):
        engine = MatchingEngine()
        report = engine.explain_score(
            "Senior Python engineer with Flask and Docker.",
            "Python developer with Flask and Docker experience.",
        )

        breakdown = report["calculation_breakdown"]
        assert breakdown["formula"] == "clamp(base_score * skill_multiplier * experience_multiplier)"
        assert "pre_clamp_score" in breakdown
        assert "final_score" in breakdown
        assert isinstance(breakdown["was_clamped"], bool)
        assert isinstance(breakdown["steps"], list)
        step_names = [step["name"] for step in breakdown["steps"]]
        assert step_names == ["base_score", "skill_multiplier", "experience_multiplier"]
