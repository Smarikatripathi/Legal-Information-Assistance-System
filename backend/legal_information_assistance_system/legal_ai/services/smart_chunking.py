import re

def detect_dhara(text):
    """
    Detect Nepali / English legal articles
    """
    pattern = r"(धारा\s*\d+|Article\s*\d+|\d+\.)"
    return re.split(pattern, text)


def smart_chunk(text, doc_title):
    parts = detect_dhara(text)

    chunks = []
    current = ""

    for p in parts:
        if re.match(r"(धारा\s*\d+|Article\s*\d+|\d+\.)", p or ""):
            if current:
                chunks.append(current)
            current = p
        else:
            current += p

    if current:
        chunks.append(current)

    final_chunks = []

    for c in chunks:
        if len(c.strip()) > 50:
            final_chunks.append({
                "doc": doc_title,
                "text": c.strip()
            })

    return final_chunks