from io import BytesIO

import app as app_module


def _client(monkeypatch):
    app_module.app.config.update(TESTING=True)
    monkeypatch.setattr(
        app_module, "extract_text_from_pdf",
        lambda stream: "Skills\nPython Java SQL\nExperience\n2 years\nEducation\nBachelor of Engineering\nProjects"
    )
    monkeypatch.setattr(
        app_module, "analyze",
        lambda resume, jd: {
            "overall": 72.0,
            "breakdown": {"skills": 80.0, "semantic": 60.0, "experience": None, "education": None},
            "matched": [{"skill": "python", "priority": "Required"}],
            "missing": [],
            "resume_quality": [],
            "warnings": [],
            "disclaimer": "Informational estimate only."
        }
    )
    return app_module.app.test_client()


def test_health_endpoint():
    client = app_module.app.test_client()
    assert client.get("/health").json == {"status": "ok"}


def test_api_analyze_accepts_pdf_upload(monkeypatch):
    client = _client(monkeypatch)
    response = client.post(
        "/api/analyze",
        data={
            "resume": (BytesIO(b"%PDF-1.4 test"), "resume.pdf"),
            "job_description": "A sufficiently long job description for this test."
        },
        content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert response.json["overall"] == 72.0


def test_api_rejects_missing_resume(monkeypatch):
    client = _client(monkeypatch)
    response = client.post(
        "/analyze",
        data={"job_description": "A sufficiently long job description for this test."}
    )
    assert response.status_code == 400


def test_report_endpoint_returns_pdf(monkeypatch):
    client = _client(monkeypatch)
    response = client.post(
        "/download-report",
        data={
            "resume": (BytesIO(b"%PDF-1.4 test"), "resume.pdf"),
            "job_description": "A sufficiently long job description for this test."
        },
        content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
