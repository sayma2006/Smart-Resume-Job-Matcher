import re


def clean_text(text):
    # Convert text to lowercase
    text = text.lower()

    # Keep letters, numbers, +, # and spaces
    text = re.sub(r"[^a-z0-9+#\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()