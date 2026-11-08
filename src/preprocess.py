import re

def clean_text(text: str) -> str:
    """Normalize text while preserving line breaks for section-aware parsing."""
    text = (text or "").replace("\x00", " ")
    text = re.sub(r"https?://\S+|www\.\S+", " ", text, flags=re.I)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"[•●▪■◦·]", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()
