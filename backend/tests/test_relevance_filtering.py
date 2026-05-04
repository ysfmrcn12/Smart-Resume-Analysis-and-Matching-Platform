"""Tests for relevance-aware scoring (skill overlap penalization)."""
from app.nlp.matching_engine import MatchingEngine


def test_accountant_vs_java_low_score():
    engine = MatchingEngine()
    job = "Java developer, backend services, Spring, Java 11"
    accountant_resume = (
        "Experienced accountant with expertise in financial reporting, budgeting, and "
        "tax compliance. Proficient in Excel, QuickBooks, payroll reconciliation, and "
        "audit preparation. Managed accounts receivable and payable for mid-size firms."
    )
    score = engine.compute_similarity(job, accountant_resume)
    assert score < 0.2


def test_java_resume_high_score():
    engine = MatchingEngine()
    job = "Java developer, backend services, Spring, Java 11"
    java_resume = (
        "Senior Java developer with 6 years experience building backend services using "
        "Spring Framework, REST APIs, and Java 11. Familiar with Hibernate, Maven, and Docker."
    )
    score = engine.compute_similarity(job, java_resume)
    assert score > 0.4


def test_negated_required_skill_reduces_score_and_is_reported():
    engine = MatchingEngine()
    job = "Frontend developer with React, TypeScript, and JavaScript"
    resume = (
        "I am a frontend engineer with JavaScript and TypeScript experience, "
        "but I do not know React and have no React project experience."
    )
    report = engine.explain_score(job, resume)
    score = report["final_score"]

    assert "react" in report["skills"]["negated_required_skills"]
    # Negation should significantly lower skill multiplier.
    assert report["skills"]["skill_multiplier"] < 0.7
    # Final score should be moderated instead of being treated as a strong match.
    assert score < 0.6


def test_non_negation_words_do_not_trigger_negation():
    engine = MatchingEngine()
    job = "Frontend developer with React and TypeScript"
    resume = (
        "I know React and TypeScript very well. "
        "I know modern frontend engineering patterns."
    )
    report = engine.explain_score(job, resume)

    # "know" contains "no" as a substring, but should not be treated as negation.
    assert "react" not in report["skills"]["negated_required_skills"]
    assert report["skills"]["skill_multiplier"] >= 0.6
