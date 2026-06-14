import re
from typing import Any, Dict, List, Optional

# Legal structure markers (English + Nepali)
PART_PATTERN = re.compile(
    r"^(?:Part|भाग)\s*[-–]?\s*([\d०-९]+|[A-Za-z]+)\b",
    re.I | re.M,
)
CHAPTER_PATTERN = re.compile(
    r"^(?:Chapter|परिच्छेद)\s*[-–]?\s*([\d०-९]+|[A-Za-z\s]+)\b",
    re.I | re.M,
)
SECTION_PATTERN = re.compile(
    r"^(?:Section|धारा|दफा)\s*[-–]?\s*([\d०-९]+)\b",
    re.I | re.M,
)
ARTICLE_PATTERN = re.compile(
    r"^(?:Article|अनुच्छेद)\s*[-–]?\s*([\d०-९]+)\b",
    re.I | re.M,
)
# Constitution style: "11. To be citizens of Nepal"
NUMBERED_ARTICLE_PATTERN = re.compile(
    r"^(\d{1,3})\.\s+([A-Z\u0900-\u097F][^\n]{5,120})$",
    re.M,
)
CLAUSE_PATTERN = re.compile(
    r"^(?:Clause|\(\d+\))\s*[-–]?\s*([\d०-९]+)?",
    re.I | re.M,
)

HEADER_PATTERN = re.compile(
    r"(?:^|\n)"
    r"(?:"
    r"Part\s*[-–]?\s*[\d०-९A-Za-z]+"
    r"|Chapter\s*[-–]?\s*[\d०-९A-Za-z\s]+"
    r"|Section\s*[-–]?\s*[\d०-९]+"
    r"|Article\s*[-–]?\s*[\d०-९]+"
    r"|Clause\s*[-–]?\s*[\d०-९]+"
    r"|धारा\s*[\d०-९]+"
    r"|भाग\s*[\d०-९]+"
    r"|परिच्छेद\s*[\d०-९]+"
    r"|दफा\s*[\d०-९]+"
    r"|\d{1,3}\.\s+[A-Z\u0900-\u097F][^\n]{5,80}"
    r")",
    re.I | re.M,
)


def _extract_title(content: str) -> str:
    first_line = content.strip().split("\n", 1)[0].strip()
    if len(first_line) <= 200:
        return first_line
    return first_line[:200]


def _parse_header(header: str, context: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """Update hierarchy context from a detected legal header."""
    ctx = dict(context)
    header = header.strip()

    if m := PART_PATTERN.match(header):
        ctx["part"] = f"Part-{m.group(1)}"
        ctx["chapter"] = None
        ctx["section"] = None
        ctx["article"] = None
        ctx["clause"] = None
        return ctx

    if m := CHAPTER_PATTERN.match(header):
        ctx["chapter"] = f"Chapter-{m.group(1).strip()}"
        ctx["section"] = None
        ctx["article"] = None
        ctx["clause"] = None
        return ctx

    if m := SECTION_PATTERN.match(header):
        num = m.group(1)
        ctx["section"] = num
        ctx["dhara"] = num
        ctx["clause"] = None
        return ctx

    if m := ARTICLE_PATTERN.match(header):
        ctx["article"] = m.group(1)
        ctx["clause"] = None
        return ctx

    if m := NUMBERED_ARTICLE_PATTERN.match(header):
        ctx["article"] = m.group(1)
        ctx["title"] = m.group(2).strip()
        ctx["clause"] = None
        return ctx

    if m := CLAUSE_PATTERN.match(header):
        ctx["clause"] = m.group(1) or header
        return ctx

    return ctx


class SmartLegalChunker:
    """
    Legal-structure-aware chunker for Nepal legal documents.
    Chunks by Part / Chapter / Section / Article — not by character count.
    """

    def __init__(self, max_words: int = 400):
        self.max_words = max_words

    def _split_at_headers(self, text: str) -> List[Dict[str, str]]:
        matches = list(HEADER_PATTERN.finditer(text))
        if not matches:
            return [{"header": "", "content": text}]

        sections: List[Dict[str, str]] = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            header = match.group().strip()
            content = text[start:end].strip()
            sections.append({"header": header, "content": content})
        return sections

    def _split_large_section(self, content: str) -> List[str]:
        """Split only when a legal unit exceeds max_words — at clause/sentence boundaries."""
        words = content.split()
        if len(words) <= self.max_words:
            return [content]

        # Try splitting at numbered clauses: (1), (2), etc.
        clause_splits = re.split(r"(?<=\))\s+(?=\(\d+\))", content)
        if len(clause_splits) > 1:
            chunks: List[str] = []
            current: List[str] = []
            current_len = 0
            for part in clause_splits:
                part_len = len(part.split())
                if current_len + part_len > self.max_words and current:
                    chunks.append(" ".join(current))
                    current = [part]
                    current_len = part_len
                else:
                    current.append(part)
                    current_len += part_len
            if current:
                chunks.append(" ".join(current))
            return chunks

        # Sentence boundary fallback
        sentences = re.split(r"(?<=[.!?।])\s+", content)
        chunks = []
        current: List[str] = []
        current_len = 0
        for sentence in sentences:
            slen = len(sentence.split())
            if current_len + slen > self.max_words and current:
                chunks.append(" ".join(current))
                current = [sentence]
                current_len = slen
            else:
                current.append(sentence)
                current_len += slen
        if current:
            chunks.append(" ".join(current))
        return chunks

    def chunk(self, text: str, document_name: str = "") -> List[Dict[str, Any]]:
        if not text or not text.strip():
            return []

        sections = self._split_at_headers(text)
        context: Dict[str, Optional[str]] = {
            "part": None,
            "chapter": None,
            "section": None,
            "article": None,
            "clause": None,
            "dhara": None,
            "title": None,
        }

        all_chunks: List[Dict[str, Any]] = []
        chunk_index = 0

        for section in sections:
            header = section["header"]
            content = section["content"]

            if header:
                context = _parse_header(header, context)
                if not context.get("title"):
                    context["title"] = _extract_title(content)

            sub_chunks = self._split_large_section(content)

            for sub in sub_chunks:
                if len(sub.split()) < 15:
                    continue

                metadata = {
                    "document_name": document_name,
                    "part": context.get("part") or "",
                    "chapter": context.get("chapter") or "",
                    "section": context.get("section") or "",
                    "article": context.get("article") or "",
                    "clause": context.get("clause") or "",
                    "dhara": context.get("dhara") or context.get("section") or "",
                    "title": context.get("title") or _extract_title(sub),
                }

                all_chunks.append({
                    "text": sub,
                    "title": metadata["title"],
                    "part": metadata["part"],
                    "chapter": metadata["chapter"],
                    "section": metadata["section"],
                    "article": metadata["article"],
                    "clause": metadata["clause"],
                    "dhara": metadata["dhara"],
                    "metadata": metadata,
                    "chunk_index": chunk_index,
                })
                chunk_index += 1

        return all_chunks
