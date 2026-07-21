import re
from typing import Any, Dict, List, Optional

from legal_information_assistance_system.legal_ai.services.language import language_service

PART_PATTERN = re.compile(
    r"^(?:Part|भाग)\s*[-–]?\s*([\d०-९]+|[A-Za-z]+)(?:\s+(.*))?$",
    re.I | re.M,
)
CHAPTER_PATTERN = re.compile(
    r"^(?:Chapter|परिच्छेद)\s*[-–]?\s*([\d०-९]+|[A-Za-z\s]+)(?:\s+(.*))?$",
    re.I | re.M,
)
RULE_PATTERN = re.compile(
    r"^(?:Rule|नियम|उपनियम|अनुच्छेद|अनुसूची)\s*[-–]?\s*([\d०-९A-Za-z]+)(?:\s+(.*))?$",
    re.I | re.M,
)
SECTION_PATTERN = re.compile(
    r"^(?:Section|धारा|दफा)\s*[-–]?\s*([\d०-९]+)(?:\s+(.*))?$",
    re.I | re.M,
)
ARTICLE_PATTERN = re.compile(
    r"^(?:Article|अनुच्छेद)\s*[-–]?\s*([\d०-९]+)(?:\s+(.*))?$",
    re.I | re.M,
)
NUMBERED_ARTICLE_PATTERN = re.compile(
    r"^(\d{1,3})\.\s+([A-Z\u0900-\u097F][^\n]{5,120})$",
    re.M,
)
CLAUSE_PATTERN = re.compile(
    r"^(?:Clause|\(\d+\)|\([ivxIVX]+\)|\d+\))\s*[-–]?\s*([\d०-९]+)?",
    re.I | re.M,
)
SUBRULE_PATTERN = re.compile(r"^(\(?[ivxIVX]+\)|\(?\d+\))\s+", re.I | re.M)

HEADER_PATTERN = re.compile(
    r'(?:^|\n)\s*(?:'
    r'Part\s*[-–]?\s*[^\n]+'
    r'|Chapter\s*[-–]?\s*[^\n]+'
    r'|Section\s*[-–]?\s*[^\n]+'
    r'|Article\s*[-–]?\s*[^\n]+'
    r'|Rule\s*[-–]?\s*[^\n]+'
    r'|धारा\s*[^\n]+'
    r'|भाग\s*[^\n]+'
    r'|परिच्छेद\s*[^\n]+'
    r'|दफा\s*[^\n]+'
    r'|नियम\s*[-–]?\s*[^\n]+'
    r'|उपनियम\s*[-–]?\s*[^\n]+'
    r'|अनुच्छेद\s*[-–]?\s*[^\n]+'
    r'|अनुसूची\s*[-–]?\s*[^\n]+'
    r'|Clause\s*[-–]?\s*[^\n]+'
    r'|\(\d+\)\s+[^\n]+'
    r'|\([ivxIVX]+\)\s+[^\n]+'
    r'|\d{1,3}\.\s+[A-Z\u0900-\u097F][^\n]{5,80}'
    r')',
    re.I | re.M,
)


def _extract_title(content: str) -> str:
    first_line = content.strip().split("\n", 1)[0].strip()
    if len(first_line) <= 200:
        return first_line
    return first_line[:200]


def extract_legal_keywords(text: str) -> List[str]:
    """Extract key legal terms from chunk for better retrieval."""
    legal_terms_en = [
        "right", "duty", "liability", "penalty", "offense", "jurisdiction",
        "contract", "property", "marriage", "divorce", "inheritance",
        "fundamental", "constitutional", "provision", "section", "article"
    ]
    legal_terms_ne = [
        "अधिकार", "कर्तव्य", "दायित्व", "दण्ड", "अपराध", "अधिकारक्षेत्र",
        "सम्झौता", "सम्पत्ति", "विवाह", "विवाह विच्छेद", "सम्पत्ति विभाजन",
        "मौलिक", "संवैधानिक", "व्यवस्था", "धारा", "अनुच्छेद"
    ]
    
    text_lower = text.lower()
    found = []
    
    for term in legal_terms_en:
        if term in text_lower:
            found.append(term)
    
    for term in legal_terms_ne:
        if term in text_lower:
            found.append(term)
    
    return found


def _parse_header(header: str, context: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    ctx = dict(context)
    header = header.strip()

    if m := PART_PATTERN.match(header):
        ctx["part"] = f"Part-{m.group(1)}"
        ctx["chapter"] = None
        ctx["section"] = None
        ctx["article"] = None
        ctx["rule"] = None
        ctx["subrule"] = None
        ctx["clause"] = None
        if m.group(2):
            ctx["title"] = m.group(2).strip()
        return ctx

    if m := CHAPTER_PATTERN.match(header):
        ctx["chapter"] = f"Chapter-{m.group(1).strip()}"
        ctx["section"] = None
        ctx["article"] = None
        ctx["rule"] = None
        ctx["subrule"] = None
        ctx["clause"] = None
        if m.group(2):
            ctx["title"] = m.group(2).strip()
        return ctx

    if m := RULE_PATTERN.match(header):
        ctx["rule"] = f"Rule-{m.group(1)}"
        ctx["subrule"] = None
        ctx["clause"] = None
        if m.group(2):
            ctx["title"] = m.group(2).strip()
        return ctx

    if m := SECTION_PATTERN.match(header):
        num = m.group(1)
        ctx["section"] = num
        ctx["dhara"] = num
        ctx["clause"] = None
        if m.group(2):
            ctx["title"] = m.group(2).strip()
        return ctx

    if m := ARTICLE_PATTERN.match(header):
        ctx["article"] = m.group(1)
        ctx["clause"] = None
        if m.group(2):
            ctx["title"] = m.group(2).strip()
        return ctx

    if m := NUMBERED_ARTICLE_PATTERN.match(header):
        ctx["article"] = m.group(1)
        ctx["title"] = m.group(2).strip()
        ctx["clause"] = None
        return ctx

    if m := CLAUSE_PATTERN.match(header):
        ctx["clause"] = m.group(1) or header
        return ctx

    if m := SUBRULE_PATTERN.match(header):
        ctx["subrule"] = m.group(1)
        return ctx

    return ctx


class LegalChunker:
    """Structure-aware chunker for Nepal legal documents (Part / Chapter / Rule / Section / Article / Clause)."""

    def __init__(self, max_words: int = 300, overlap: int = 50):
        self.max_words = max_words
        self.overlap = overlap

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
        words = content.split()
        if len(words) <= self.max_words:
            return [content]

        # Try clause/subrule splitting first (preserves legal structure)
        clause_splits = re.split(r"(?<=\))\s+(?=\(\d+\))|(?<=\n)(?=उपनियम|अनुच्छेद|अनुसूची)", content)
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

        # Split by sentence boundaries (both English and Nepali)
        # Nepali uses । (danda) as sentence terminator
        sentences = re.split(r"(?<=[.!?।])\s+", content)
        
        # Implement sliding window with overlap
        chunks = []
        current_words = []
        
        for sentence in sentences:
            sentence_words = sentence.split()
            
            # Check if adding this sentence would exceed max_words
            if len(current_words) + len(sentence_words) > self.max_words and current_words:
                # Save current chunk
                chunks.append(" ".join(current_words))
                
                # Keep overlap words from end of current chunk
                if self.overlap > 0:
                    current_words = current_words[-self.overlap:] if len(current_words) >= self.overlap else current_words
                else:
                    current_words = []
            
            current_words.extend(sentence_words)
        
        # Add final chunk if there's remaining content
        if current_words:
            chunks.append(" ".join(current_words))
        
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
            "rule": None,
            "subrule": None,
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

            for sub in self._split_large_section(content):
                if len(sub.split()) < 15:
                    continue

                # Detect language of this chunk
                chunk_language = language_service.detect_language(sub)
                
                # Extract legal keywords for better retrieval
                keywords = extract_legal_keywords(sub)
                
                # Calculate hierarchy depth
                hierarchy_depth = sum([
                    1 for field in [context.get("part"), context.get("chapter"), 
                                   context.get("section"), context.get("article")] 
                    if field
                ])
                
                # Determine chunk type
                chunk_type = "definition" if ("define" in sub.lower() or "परिभाषा" in sub) else "provision"

                metadata = {
                    "document_name": document_name,
                    "part": context.get("part") or "",
                    "chapter": context.get("chapter") or "",
                    "section": context.get("section") or "",
                    "article": context.get("article") or "",
                    "rule": context.get("rule") or "",
                    "subrule": context.get("subrule") or "",
                    "clause": context.get("clause") or "",
                    "dhara": context.get("dhara") or context.get("section") or "",
                    "title": context.get("title") or _extract_title(sub),
                    "language": chunk_language,
                    "keywords": keywords,
                    "hierarchy_depth": hierarchy_depth,
                    "chunk_type": chunk_type,
                }

                all_chunks.append({
                    "text": sub,
                    "title": metadata["title"],
                    "part": metadata["part"],
                    "chapter": metadata["chapter"],
                    "section": metadata["section"],
                    "article": metadata["article"],
                    "rule": metadata["rule"],
                    "subrule": metadata["subrule"],
                    "clause": metadata["clause"],
                    "dhara": metadata["dhara"],
                    "metadata": metadata,
                    "chunk_index": chunk_index,
                })
                chunk_index += 1

        return all_chunks


# Backward-compatible alias
SmartLegalChunker = LegalChunker
