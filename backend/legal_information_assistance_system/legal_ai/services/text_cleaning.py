import re


def clean_text(text: str) -> str:
    """
    Clean legal documents WITHOUT breaking structure.
    """

    # normalize line breaks
    text = re.sub(r"\r", "\n", text)

    # remove excessive whitespace
    text = re.sub(r"[ \t]+", " ", text)

    # normalize multiple new lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # fix spacing around punctuation (light touch only)
    text = re.sub(r"\s+([,.;:])", r"\1", text)

    return text.strip()