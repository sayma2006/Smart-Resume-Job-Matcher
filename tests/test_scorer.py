from src import scorer
from src.scorer import analyze


def test_analysis_returns_expected_sections(monkeypatch):
    monkeypatch.setattr(
        scorer, "semantic_similarity",
        lambda a, b: {"score": 50.0, "method": "tfidf"}
    )
    result = analyze(
        "Skills\nPython, Java, SQL\nEducation\nBachelor of Engineering\nProjects\nBuilt REST API",
        "Requirements\nPython and Java. Required skills\nSQL\nPreferred\nDocker"
    )
    assert 0 <= result["overall"] <= 100
    assert "breakdown" in result
    assert "matched" in result
    assert "missing" in result
    assert any(item["skill"] == "docker" for item in result["missing"])


def test_experience_and_education_are_omitted_when_not_required(monkeypatch):
    monkeypatch.setattr(
        scorer, "semantic_similarity",
        lambda a, b: {"score": 40.0, "method": "tfidf"}
    )
    result = analyze("Python developer", "Python programming experience preferred.")
    assert result["breakdown"]["experience"] is None
    assert result["breakdown"]["education"] is None


def test_scores_stay_within_bounds_for_empty_resume(monkeypatch):
    monkeypatch.setattr(
        scorer, "semantic_similarity",
        lambda a, b: {"score": 0.0, "method": "tfidf"}
    )
    result = analyze("", "Required skills\nPython\nJava")
    assert 0 <= result["overall"] <= 100
    assert result["breakdown"]["skills"] == 0


def test_missing_experience_is_not_a_crash(monkeypatch):
    monkeypatch.setattr(
        scorer, "semantic_similarity",
        lambda a, b: {"score": 50.0, "method": "tfidf"}
    )
    result = analyze("Python and Java", "Required: 3 years experience with Python.")
    assert result["years"]["required"] == 3
    assert result["years"]["found"] is None
    assert any("years of experience" in warning for warning in result["warnings"])


def test_foundational_skill_receives_partial_credit(monkeypatch):
    monkeypatch.setattr(
        scorer, "semantic_similarity",
        lambda a, b: {"score": 50.0, "method": "tfidf"}
    )
    result = analyze(
        "Basic React knowledge.",
        "Required Skills\nReact"
    )
    react = next(item for item in result["matched"] if item["skill"] == "react")
    assert react["proficiency"] == "foundational"
    assert react["credit"] == 0.5
    assert result["breakdown"]["skills"] == 50.0


def test_currently_learning_skill_is_not_counted_as_matched(monkeypatch):
    monkeypatch.setattr(
        scorer, "semantic_similarity",
        lambda a, b: {"score": 50.0, "method": "tfidf"}
    )
    result = analyze(
        "Skills\nPython\nCurrently Learning\nDocker, pytest",
        "Required Skills\nPython\nDocker\npytest"
    )
    matched_names = {item["skill"] for item in result["matched"]}
    developing_names = {item["skill"] for item in result["developing"]}
    assert "python" in matched_names
    assert "docker" not in matched_names
    assert "testing" not in matched_names
    assert {"docker", "testing"}.issubset(developing_names)
    assert all(item["status"] == "In progress" for item in result["missing"] if item["skill"] in developing_names)


def test_fresher_eligibility_does_not_create_experience_penalty(monkeypatch):
    monkeypatch.setattr(
        scorer, "semantic_similarity",
        lambda a, b: {"score": 50.0, "method": "tfidf"}
    )
    result = analyze(
        "Skills\nPython\nEducation\nBachelor of Engineering",
        "Junior Developer\nExperience: 0-1 years\nFreshers and candidates with up to one year of experience can apply.\nRequired Skills\nPython"
    )
    assert result["years"]["required"] is None
    assert result["breakdown"]["experience"] is None


def test_minimum_experience_requirement_is_still_detected(monkeypatch):
    monkeypatch.setattr(
        scorer, "semantic_similarity",
        lambda a, b: {"score": 50.0, "method": "tfidf"}
    )
    result = analyze("Skills\nPython", "Required: 3 years of experience with Python.")
    assert result["years"]["required"] == 3
    assert result["breakdown"]["experience"] == 0.0


def test_flask_or_django_does_not_penalize_candidate_with_flask(monkeypatch):
    monkeypatch.setattr(
        scorer, "semantic_similarity",
        lambda a, b: {"score": 50.0, "method": "tfidf"}
    )
    result = analyze(
        "Skills\nPython, Flask\nProjects\nBuilt a Flask REST API.",
        "Required Skills\nPython\nKnowledge of Flask or Django framework."
    )
    matched_names = {item["skill"] for item in result["matched"]}
    missing_names = {item["skill"] for item in result["missing"]}
    assert "flask" in matched_names
    assert "django" not in missing_names


def test_fresher_eligibility_is_exposed_in_result(monkeypatch):
    monkeypatch.setattr(
        scorer, "semantic_similarity",
        lambda a, b: {"score": 50.0, "method": "tfidf"}
    )
    result = analyze(
        "Skills\nPython",
        "Freshers and candidates with up to one year of experience can apply.\nRequired Skills\nPython"
    )
    assert result["years"]["required"] is None
    assert result["years"]["fresher_eligible"] is True
