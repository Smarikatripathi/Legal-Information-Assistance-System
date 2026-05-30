import re
from typing import Dict, List


class SmartLegalChunker:
    """
    Production-grade legal document chunker.
    Designed for Constitution / Acts / Legal PDFs.
    """

    def __init__(self, max_tokens: int = 250, overlap: int = 50):
        self.max_tokens = max_tokens
        self.overlap = overlap

        # 🔥 More flexible legal header detection
        self.header_pattern = re.compile(
            r"(Article\s*\d+[A-Za-z\-.:]*)"
            r"|(Section\s*\d+[A-Za-z\-.:]*)"
            r"|(Part\s*\d+[A-Za-z\-.:]*)"
            r"|(Chapter\s*\d+[A-Za-z\-.:]*)"
            r"|(Clause\s*\d+[A-Za-z\-.:]*)"
            r"|(धारा\s*\d+[०-९0-9\-.:]*)"
            r"|(भाग\s*\d+[०-९0-9\-.:]*)"
            r"|(परिच्छेद\s*\d+[०-९0-9\-.:]*)"
            r"|(दफा\s*\d+[०-९0-9\-.:]*)",
            re.IGNORECASE
        )

    # =========================
    # CLEAN TEXT
    # =========================
    def _clean_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)  # remove extra spaces
        text = re.sub(r"-\n", "", text)   # fix broken words
        return text.strip()

    # =========================
    # SPLIT INTO SECTIONS
    # =========================
    def _split_sections(self, text: str) -> List[Dict[str, str]]:
        matches = list(self.header_pattern.finditer(text))

        if not matches:
            return [{"header": "document", "content": text}]

        sections = []

        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

            header = match.group().strip()
            content = text[start:end].strip()

            sections.append({
                "header": header,
                "content": content
            })

        return sections

    # =========================
    # SMART TEXT CHUNKING
    # =========================
    def _chunk_text(self, text: str) -> List[str]:
        sentences = re.split(r"(?<=[.!?।])\s+", text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            words = sentence.split()
            sentence_len = len(words)

            if current_length + sentence_len > self.max_tokens:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = words
                current_length = sentence_len
            else:
                current_chunk.extend(words)
                current_length += sentence_len

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        # 🔁 add overlap for context continuity
        final_chunks = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                final_chunks.append(chunk)
            else:
                prev_words = chunks[i - 1].split()[-self.overlap:]
                final_chunks.append(" ".join(prev_words + chunk.split()))

        return final_chunks

    # =========================
    # MAIN CHUNK FUNCTION
    # =========================
    def chunk(self, text: str) -> List[Dict[str, str]]:
        text = self._clean_text(text)

        if not text:
            return []

        sections = self._split_sections(text)

        all_chunks = []

        for section_index, section in enumerate(sections):
            header = section["header"]
            content = section["content"]

            chunks = self._chunk_text(content)

            for chunk_index, chunk_text in enumerate(chunks):
                all_chunks.append({
                    "text": chunk_text,
                    "section_header": header,
                    "section_index": section_index,
                    "chunk_index": chunk_index,
                })

        return all_chunks