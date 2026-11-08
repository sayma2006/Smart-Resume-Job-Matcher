import os
from pypdf import PdfReader


def extract_text_from_pdf(file_stream) -> str:
    """Extract text from an uploaded PDF stream without saving it to disk."""
    try:
        if hasattr(file_stream, "seek"):
            file_stream.seek(0)
        header = file_stream.read(8)
        if hasattr(file_stream, "seek"):
            file_stream.seek(0)
        if b"%PDF-" not in header:
            raise ValueError("The uploaded file does not appear to be a valid PDF.")

        reader = PdfReader(file_stream, strict=False)
        if reader.is_encrypted:
            try:
                decrypted = reader.decrypt("")
            except Exception as exc:
                raise ValueError("This PDF is password-protected. Upload an unlocked PDF.") from exc
            if not decrypted:
                raise ValueError("This PDF is password-protected. Upload an unlocked PDF.")

        if len(reader.pages) > 50:
            raise ValueError("This PDF has more than 50 pages. Upload a shorter resume PDF.")

        pages = [(page.extract_text() or "") for page in reader.pages]
        text = "\n".join(pages).strip()
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("The uploaded file could not be read as a valid PDF.") from exc

    if len(text) < 40 and os.getenv("OCR_ENABLED", "0") == "1":
        try:
            import pytesseract
            from pdf2image import convert_from_bytes

            tesseract_cmd = os.getenv("TESSERACT_CMD")
            if tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            if hasattr(file_stream, "seek"):
                file_stream.seek(0)
            pdf_bytes = file_stream.read()
            images = convert_from_bytes(pdf_bytes, dpi=220)
            text = "\n".join(pytesseract.image_to_string(image) for image in images).strip()
        except ImportError as exc:
            raise ValueError(
                "This appears to be a scanned PDF. Install requirements-ocr.txt, Tesseract OCR, "
                "and Poppler, or upload a text-based PDF."
            ) from exc
        except Exception as exc:
            raise ValueError(
                "OCR could not read this scanned PDF. Check Tesseract/Poppler installation "
                "or upload a text-based PDF."
            ) from exc

    if len(text) < 40:
        raise ValueError(
            "Very little selectable text was found. This may be a scanned PDF. "
            "To enable OCR, install requirements-ocr.txt plus Tesseract OCR and Poppler, "
            "then set OCR_ENABLED=1."
        )
    return text
