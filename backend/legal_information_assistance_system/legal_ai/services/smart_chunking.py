import re
from typing import List


class SmartLegalChunker:
    """
    10/10 Legal-aware Smart Chunker for RAG systems
    """

    LEGAL_PATTERNS = [
        r"(भाग\s*[०-९0-9]+)",
        r"(परिच्छेद\s*[०-९0-9]+)",
        r"(दफा\s*[०-९0-9]+)",
        r"(धारा\s*[०-९0-9]+)",
        r"(Section\s*\d+)",
        r"(Article\s*\d+)",
        r"(Part\s*-?\s*\d+)",
        r"(Chapter\s*-?\s*\d+)",
    ]

    def __init__(self, max_tokens: int = 180, overlap: int = 40):
        self.max_tokens = max_tokens
        self.overlap = overlap
        self.pattern = re.compile("|".join(self.LEGAL_PATTERNS))

    # -----------------------------
    # STEP 1: Normalize text
    # -----------------------------
    def normalize(self, text: str) -> str:
        text = re.sub(r"\r", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # -----------------------------
    # STEP 2: Split by legal headers
    # -----------------------------
    def split_by_legal_sections(self, text: str) -> List[str]:
        parts = self.pattern.split(text)

        sections = []
        buffer = ""

        for part in parts:
            if not part:
                continue

            # if it's a legal header
            if self.pattern.fullmatch(part.strip()):
                if buffer:
                    sections.append(buffer.strip())
                buffer = part
            else:
                buffer += " " + part

        if buffer:
            sections.append(buffer.strip())

        return sections

    # -----------------------------
    # STEP 3: Smart chunking
    # -----------------------------
    def chunk_section(self, section: str) -> List[str]:
        words = section.split()

        chunks = []
        temp = []
        length = 0

        for word in words:
            temp.append(word)
            length += 1

            if length >= self.max_tokens:
                chunks.append(" ".join(temp))

                # overlap handling (VERY IMPORTANT)
                temp = temp[-self.overlap:]
                length = len(temp)

        if temp:
            chunks.append(" ".join(temp))

        return chunks

    # -----------------------------
    # MAIN FUNCTION
    # -----------------------------
    def chunk(self, text: str) -> List[str]:

        text = self.normalize(text)
        sections = self.split_by_legal_sections(text)

        final_chunks = []

        for section in sections:
            section_chunks = self.chunk_section(section)
            final_chunks.extend(section_chunks)

        return final_chunks