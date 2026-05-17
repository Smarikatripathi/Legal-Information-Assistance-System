import re


LEGAL_PATTERNS = [
    r"भाग\s*[०-९0-9]+",
    r"परिच्छेद\s*[०-९0-9]+",
    r"दफा\s*[०-९0-9]+",
    r"धारा\s*[०-९0-9]+",
    r"Section\s*\d+",
    r"Article\s*\d+",
    r"Part\s*-?\s*\d+",
    r"Chapter\s*-?\s*\d+",
]


def split_legal_sections(text):

    # normalize text (VERY IMPORTANT for PDFs)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("Part -", "Part-")
    text = text.replace("Chapter -", "Chapter-")

    combined = "|".join(LEGAL_PATTERNS)

    splits = re.split(f"({combined})", text)

    chunks = []
    current = ""

    for part in splits:

        if not part:
            continue

        if re.fullmatch(combined, part.strip()):

            if current.strip():
                chunks.append(current.strip())

            current = part.strip()

        else:
            current += " " + part

    if current.strip():
        chunks.append(current.strip())

    return chunks


def smart_chunk(text, chunk_size=800):

    legal_sections = split_legal_sections(text)

    final_chunks = []

    for section in legal_sections:

        words = section.split()
        temp = []
        count = 0

        for w in words:
            temp.append(w)
            count += len(w)

            if count > chunk_size:
                final_chunks.append(" ".join(temp))
                temp = []
                count = 0

        if temp:
            final_chunks.append(" ".join(temp))

    return final_chunks