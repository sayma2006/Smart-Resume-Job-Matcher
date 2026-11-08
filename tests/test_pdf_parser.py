from io import BytesIO

import pytest
from reportlab.pdfgen import canvas

from src.pdf_parser import extract_text_from_pdf


def make_pdf(text):
    output = BytesIO()
    pdf = canvas.Canvas(output)
    pdf.drawString(72, 760, text)
    pdf.save()
    output.seek(0)
    return output


def test_extracts_text_from_valid_pdf():
    content = "Python Java SQL Flask and software engineering project experience"
    assert content in extract_text_from_pdf(make_pdf(content))


def test_rejects_non_pdf_upload():
    with pytest.raises(ValueError, match="valid PDF"):
        extract_text_from_pdf(BytesIO(b"not a pdf"))


def test_scanned_or_empty_pdf_returns_actionable_error(monkeypatch):
    monkeypatch.setenv("OCR_ENABLED", "0")
    with pytest.raises(ValueError, match="selectable text"):
        extract_text_from_pdf(make_pdf("tiny"))
