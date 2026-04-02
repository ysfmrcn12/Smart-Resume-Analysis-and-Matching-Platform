"""Integration-ish tests using the repo's small sample resumes."""

from pathlib import Path

from app.nlp.matching_engine import MatchingEngine


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def test_sample_resumes_tf_idf_matching():
    repo_root = Path(__file__).resolve().parents[2]
    sample_dir = repo_root / "data" / "sample_resumes"

    python_resume = _read_text(sample_dir / "python_react_engineer.txt")
    marketing_resume = _read_text(sample_dir / "marketing_manager.txt")

    job_text = (
        "Software Engineer required: Python, React, Flask, REST API, PostgreSQL experience."
    )

    engine = MatchingEngine()
    py_score = engine.compute_similarity(job_text, python_resume)
    mkt_score = engine.compute_similarity(job_text, marketing_resume)

    assert py_score > mkt_score
    assert py_score > 0.15

