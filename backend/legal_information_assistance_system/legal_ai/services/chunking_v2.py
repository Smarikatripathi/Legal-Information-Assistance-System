"""
Advanced Legal Chunker for Nepal Legal Documents

Features:
- OCR correction for Nepali text
- Legal hierarchy tracking (Part/Chapter/Article/Clause)
- Parent-child chunk relationships
- Unique deterministic chunk IDs
- Citation label generation
- Source page tracking
- OCR status tracking
- Content hashing for deduplication
- Schedule/Annex handling
"""

import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from legal_information_assistance_system.legal_ai.services.language import language_service


# OCR Correction Map for Nepali Legal Documents
OCR_CORRECTIONS = {
    # Common OCR errors in Nepali legal documents
    "रािः": "राज्यः",
    "राि": "राज्य",
    "बिुजािीय": "बौद्धिक",
    "बिुभावर्क": "बौद्धिक",
    "बिुधाममवक": "बौद्धिक",
    "स्ििन्त्र": "सम्पत्ति",
    "स्ििन्त्रिा": "सम्पत्तिको",
    "अखण्डिा": "अखण्डता",
    "सािवभौम": "सार्वभौम",
    "सािवभौमसत्ता": "सार्वभौमसत्ता",
    "रावियिा": "राष्ट्रियता",
    "स्िाधीनिा": "स्वाधीनता",
    "स्िामभमान": "स्वाभिमान",
    "नागररक": "नागरिक",
    "नेपालराज्यः": "नेपालको राज्य",
    "स‍ चारकोिकः": "सञ्चारको अधिकार",
    "समानिाकोिकः": "समानताको अधिकार",
    "न्यायसम्बन्धीिकः": "न्यायसम्बन्धी अधिकार",
    "मनिारकनजरबन्द": "मृत्युदण्ड वा जन्मकारागार",
    "छुिाछूििथाभेदभाि": "छुवा-छूत वा भेदभाव",
    "सम्पजत्तकोिकः": "सम्पत्तिको अधिकार",
    "विचारर": "विचार",
    "अमभव्यजक्तको": "अभिव्यक्तिको",
    "विनािाििमियार": "विना अनुमोदन या अनुमति",
    "राजनीमिक": "राजनीतिक",
    "सम्प्रदायबीचको": "सम्प्रदाय बीचको",
    "सु–सम्बन्धमाखललपन": "सु–सम्बन्ध माथि लिने",
    "रािको": "राज्यको",
    "राविय": "राष्ट्र",
    "रावियगोपनीयिा": "राष्ट्रिय गोपनीयता",
    "सुरक्ष": "सुरक्षा",
    "अधीनमािासंघीय": "अधीनमा संघीय",
    "इकाइिाविमभन्न": "इकाई विभिन्न",
    "जाि": "जाने",
    "जामि": "जाने",
    "धमव": "धर्म",
    "समािेशी": "समाजशील",
    "स्ििन्त्रिािुनेछ": "सम्पत्तिको हुनेछ",
    "द ेिायको": "देहायको",
    "स्ििन्त्रिािुनेछः": "सम्पत्तिको हुनेछः",
    "विद्युिीय": "विद्युतीय",
    "प्रकाशन": "प्रकाशन",
    "प्रसारणिथाछापालग": "प्रसारण वा छापाखाना",
    "न्यायसम्बन्धीिकः": "न्यायसम्बन्धी अधिकार",
    "मनिारकनजरबन्द": "मृत्युदण्ड वा जन्मकारागार",
    "सािवभौमसत्ता": "सार्वभौमसत्ता",
    "भौगोमलकअखण्डिा": "भौगोलिक अखण्डता",
    "विरुद्धजासूसी": "विरुद्ध जासूसी",
    "रावियगोपनीयिाभंग": "राष्ट्रिय गोपनीयता भंग",
    "सुरक्ष": "सुरक्षा",
    "गैरआिासीय": "गैर-आवासीय",
    "प्रदानगनवसवकनेः": "प्रदान गर्ने सम्बन्धी कानून",
    "विदेशीमुलुकक": "विदेशी मुलुकको",
    "कानूनबमोजजम": "कानून बमोजिम",
    "बािेककुनैपमनव्यजक": "बाहेक कुनै पनि व्यक्ति",
    "सबैनागररककानूनकोदृविमा": "सबै नागरिक कानूनको दृष्टिमा",
    "समानिाको": "समानताको",
    "समानिुनेछ": "समान हुनेछ",
    "पक्राउभएकोका": "पक्राउ गरिएको का",
    "सािवभौमसत्ता": "सार्वभौमसत्ता",
    "भौगोमलकअखण्डिा": "भौगोलिक अखण्डता",
    "रावियिा": "राष्ट्रियता",
    "स्िाधीनिा": "स्वाधीनता",
    "माखललपन": "माथि लिने",
    "रािको": "राज्यको",
    "विरुद्धजासूसी": "विरुद्ध जासूसी",
    "रावियगोपनीयिाभंग": "राष्ट्रिय गोपनीयता भंग",
    "सुरक्ष": "सुरक्षा",
    "प्रत्येकनागररकलाई": "प्रत्येक नागरिकलाई",
    "कानूनकोअधीनमा": "कानूनको अधीनमा",
    "सम्पजत्तको": "सम्पत्तिको",
    # Additional patterns from test output
    "बिुसांस्कृमिक": "सांस्कृतिक",
    "विविधिामार": "विविधतामा",
    "िेकासमान": "विकासमान",
    "सम्पत्तििा": "सम्पत्तिको",
    "राष्ट्र विििथास": "राष्ट्र विकासको",
    "सृवद्धप्रमिआस्थािान": "समृद्धि प्रमुख अवस्थान",
    "किाकोसूत्रमाआबद्ध": "को सूत्रमा आबद्ध",
    "राष्ट्र विििथास": "राष्ट्र विकासको",
    "सृवद्ध": "समृद्ध",
    "प्रमिआस्थािान": "प्रमुख अवस्थान",
    "िेकास": "विकास",
    "विविधिा": "विविधता",
}


# Nepali digit normalization
NEPALI_DIGIT_MAP = str.maketrans("०१२३४५६७८९", "0123456789")

# Legal hierarchy patterns
PART_PATTERN = re.compile(
    r"^(?:Part|भाग)\s*[-–]?\s*([\d०-९]+|[A-Za-z]+)(?:\s+(.*))?$",
    re.I | re.M,
)
CHAPTER_PATTERN = re.compile(
    r"^(?:Chapter|परिच्छेद)\s*[-–]?\s*([\d०-९]+|[A-Za-z\s]+)(?:\s+(.*))?$",
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
SCHEDULE_PATTERN = re.compile(
    r"^(?:Schedule|अनुसूची)\s*[-–]?\s*([\d०-९]+)(?:\s+(.*))?$",
    re.I | re.M,
)
ANNEX_PATTERN = re.compile(
    r"^(?:Annex|अनुसंधान)\s*[-–]?\s*([\d०-९]+)(?:\s+(.*))?$",
    re.I | re.M,
)
CLAUSE_PATTERN = re.compile(
    r"^(?:Clause|\(\d+\)|\([ivxIVX]+\)|\d+\))\s*[-–]?\s*([\d०-९]+)?",
    re.I | re.M,
)
NUMBERED_ARTICLE_PATTERN = re.compile(
    r"^(\d{1,3})\.\s+([A-Z\u0900-\u097F][^\n]{5,120})$",
    re.M,
)

HEADER_PATTERN = re.compile(
    r'(?:^|\n)\s*(?:'
    r'Part\s*[-–]?\s*[^\n]+'
    r'|Chapter\s*[-–]?\s*[^\n]+'
    r'|Section\s*[-–]?\s*[^\n]+'
    r'|Article\s*[-–]?\s*[^\n]+'
    r'|Schedule\s*[-–]?\s*[^\n]+'
    r'|Annex\s*[-–]?\s*[^\n]+'
    r'|धारा\s*[^\n]+'
    r'|भाग\s*[^\n]+'
    r'|परिच्छेद\s*[^\n]+'
    r'|दफा\s*[^\n]+'
    r'|अनुच्छेद\s*[-–]?\s*[^\n]+'
    r'|अनुसूची\s*[-–]?\s*[^\n]+'
    r'|अनुसंधान\s*[-–]?\s*[^\n]+'
    r'|\(\d+\)\s+[^\n]+'
    r'|\([ivxIVX]+\)\s+[^\n]+'
    r'|\d{1,3}\.\s+[A-Z\u0900-\u097F][^\n]{5,80}'
    r')',
    re.I | re.M,
)


from dataclasses import dataclass, field
from typing import Tuple


def _map_char_to_page(
    char_position: int,
    page_mapping: Dict[int, Tuple[int, int]]
) -> Optional[int]:
    """Map character position to page number.
    
    Args:
        char_position: Character position in the text
        page_mapping: Dictionary mapping page numbers to (start_char, end_char) tuples
    
    Returns:
        Page number if found, None otherwise
    """
    for page_num, (start, end) in page_mapping.items():
        if start <= char_position <= end:
            return page_num
    return None


def _determine_page_range(
    text: str,
    start_pos: int,
    end_pos: int,
    page_mapping: Dict[int, Tuple[int, int]]
) -> Tuple[Optional[int], Optional[int]]:
    """Determine page range for a text segment.
    
    Args:
        text: Full text of the document
        start_pos: Start character position of the segment
        end_pos: End character position of the segment
        page_mapping: Dictionary mapping page numbers to (start_char, end_char) tuples
    
    Returns:
        Tuple of (page_start, page_end) or (None, None) if not found
    """
    page_start = _map_char_to_page(start_pos, page_mapping)
    page_end = _map_char_to_page(end_pos, page_mapping)
    return page_start, page_end


@dataclass
class OCRCorrection:
    """Represents a single OCR correction with tracking."""
    original: str
    corrected: str
    confidence: float
    rule_id: str


class SafeOCRCorrector:
    """Safe OCR correction with tracking and audit trail."""
    
    def __init__(self):
        self.corrections = self._load_safe_corrections()
    
    def _load_safe_corrections(self) -> Dict[str, OCRCorrection]:
        """Load only high-confidence, validated OCR corrections."""
        # Only include corrections that have been validated
        # This is a subset of the original OCR_CORRECTIONS
        return {
            "राि": OCRCorrection("राि", "राज्य", 0.95, "NEP-001"),
            "रािः": OCRCorrection("रािः", "राज्यः", 0.95, "NEP-002"),
            # Add only validated corrections here
            # Each correction should be tested before inclusion
        }
    
    def correct(self, text: str) -> Tuple[str, List[OCRCorrection]]:
        """Apply corrections with tracking.
        
        Args:
            text: Source text to correct
            
        Returns:
            Tuple of (corrected_text, list_of_applied_corrections)
        """
        corrected = text
        applied_corrections = []
        
        for original, correction in self.corrections.items():
            if original in corrected:
                corrected = corrected.replace(original, correction.corrected)
                applied_corrections.append(correction)
        
        return corrected, applied_corrections


@dataclass
class ChunkMetadata:
    """Metadata for a legal chunk."""
    chunk_id: str
    document_id: int
    document_name: str
    document_type: str
    jurisdiction: str
    language: str
    
    part_number: Optional[str] = None
    part_title: Optional[str] = None
    chapter_number: Optional[str] = None
    chapter_title: Optional[str] = None
    section_number: Optional[str] = None
    section_title: Optional[str] = None
    article_number: Optional[str] = None
    article_title: Optional[str] = None
    clause_number: Optional[str] = None
    subclause_number: Optional[str] = None
    paragraph_number: Optional[str] = None
    schedule_number: Optional[str] = None
    schedule_title: Optional[str] = None
    annex_number: Optional[str] = None
    annex_title: Optional[str] = None
    
    chunk_type: str = "provision"
    parent_chunk_id: Optional[str] = None
    hierarchy_path: List[str] = field(default_factory=list)
    ocr_corrections: List[OCRCorrection] = field(default_factory=list)
    
    source_page_start: Optional[int] = None
    source_page_end: Optional[int] = None
    pdf_page_number: Optional[int] = None
    
    source_text: str = ""
    corrected_text: str = ""
    contextualized_text: str = ""
    
    ocr_status: str = "uncertain"
    content_hash: str = ""
    citation_label: str = ""


def normalize_nepali_digits(text: str) -> str:
    """Convert Nepali digits to Arabic digits."""
    return text.translate(NEPALI_DIGIT_MAP)


def apply_ocr_correction(text: str) -> Tuple[str, bool]:
    """
    Apply OCR corrections to Nepali text.
    Returns (corrected_text, was_corrected)
    """
    corrected = text
    was_corrected = False
    
    for wrong, correct in OCR_CORRECTIONS.items():
        if wrong in corrected:
            corrected = corrected.replace(wrong, correct)
            was_corrected = True
    
    return corrected, was_corrected


def generate_chunk_id(
    document_name: str,
    part: Optional[str],
    chapter: Optional[str],
    article: Optional[str],
    clause: Optional[str],
    schedule: Optional[str],
    annex: Optional[str],
    chunk_sequence: int,
    content_hash: Optional[str] = None,
) -> str:
    """Generate deterministic unique chunk ID from hierarchy.
    
    Args:
        document_name: Name of the document
        part: Part number
        chapter: Chapter number
        article: Article number
        clause: Clause number
        schedule: Schedule number
        annex: Annex number
        chunk_sequence: Sequence number for uniqueness within same hierarchy
        content_hash: Optional content hash for additional uniqueness
    
    Returns:
        Unique chunk ID string
    """
    # Normalize document name
    doc_slug = document_name.lower().replace(" ", "-").replace("।", "").replace(",", "")
    
    parts = [doc_slug]
    
    if part:
        parts.append(f"part-{part}")
    if chapter:
        parts.append(f"chapter-{chapter}")
    if schedule:
        parts.append(f"schedule-{schedule}")
    elif annex:
        parts.append(f"annex-{annex}")
    elif article:
        parts.append(f"article-{article}")
        if clause:
            parts.append(f"clause-{clause}")
    
    # Add sequence number for uniqueness within same hierarchy
    parts.append(f"seq-{chunk_sequence}")
    
    # Optional: Add content hash for additional uniqueness
    if content_hash:
        parts.append(f"hash-{content_hash[:8]}")
    
    return "-".join(parts)


def generate_citation_label(
    document_name: str,
    article: Optional[str],
    clause: Optional[str],
    section: Optional[str],
    schedule: Optional[str],
    annex: Optional[str],
) -> str:
    """Generate citation label from metadata."""
    if schedule:
        return f"{document_name}, अनुसूची {schedule}"
    if annex:
        return f"{document_name}, अनुसंधान {annex}"
    
    if article:
        if clause:
            return f"{document_name}, धारा {article}({clause})"
        return f"{document_name}, धारा {article}"
    
    if section:
        return f"{document_name}, दफा {section}"
    
    return document_name


def compute_content_hash(text: str) -> str:
    """Compute SHA-256 hash of content for deduplication."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


class AdvancedLegalChunker:
    """
    Advanced legal chunker with:
    - OCR correction
    - Legal hierarchy tracking
    - Parent-child relationships
    - Unique IDs
    - Citation labels
    - Source page tracking
    """
    
    def __init__(self, document_id: int, document_name: str, document_type: str):
        self.document_id = document_id
        self.document_name = document_name
        self.document_type = document_type
        self.jurisdiction = "Nepal"
        
        # Current hierarchy context
        self.context: Dict[str, Optional[str]] = {
            "part": None,
            "part_title": None,
            "chapter": None,
            "chapter_title": None,
            "section": None,
            "section_title": None,
            "article": None,
            "article_title": None,
            "clause": None,
            "schedule": None,
            "schedule_title": None,
            "annex": None,
            "annex_title": None,
        }
        
        # Track parent chunks for relationships
        self.parent_chunks: Dict[str, ChunkMetadata] = {}
        
    def _parse_header(self, header: str) -> Dict[str, Optional[str]]:
        """Parse header and update context."""
        header = header.strip()
        
        if m := PART_PATTERN.match(header):
            self.context["part"] = normalize_nepali_digits(m.group(1))
            self.context["part_title"] = m.group(2).strip() if m.group(2) else None
            # Reset lower levels
            self.context["chapter"] = None
            self.context["section"] = None
            self.context["article"] = None
            self.context["clause"] = None
            self.context["schedule"] = None
            self.context["annex"] = None
            
        elif m := CHAPTER_PATTERN.match(header):
            self.context["chapter"] = normalize_nepali_digits(m.group(1).strip())
            self.context["chapter_title"] = m.group(2).strip() if m.group(2) else None
            # Reset lower levels
            self.context["section"] = None
            self.context["article"] = None
            self.context["clause"] = None
            self.context["schedule"] = None
            self.context["annex"] = None
            
        elif m := SECTION_PATTERN.match(header):
            self.context["section"] = normalize_nepali_digits(m.group(1))
            self.context["section_title"] = m.group(2).strip() if m.group(2) else None
            self.context["clause"] = None
            
        elif m := ARTICLE_PATTERN.match(header):
            self.context["article"] = normalize_nepali_digits(m.group(1))
            self.context["article_title"] = m.group(2).strip() if m.group(2) else None
            self.context["clause"] = None
            self.context["schedule"] = None
            self.context["annex"] = None
            
        elif m := SCHEDULE_PATTERN.match(header):
            self.context["schedule"] = normalize_nepali_digits(m.group(1))
            self.context["schedule_title"] = m.group(2).strip() if m.group(2) else None
            self.context["article"] = None
            self.context["clause"] = None
            self.context["annex"] = None
            
        elif m := ANNEX_PATTERN.match(header):
            self.context["annex"] = normalize_nepali_digits(m.group(1))
            self.context["annex_title"] = m.group(2).strip() if m.group(2) else None
            self.context["article"] = None
            self.context["clause"] = None
            self.context["schedule"] = None
            
        elif m := NUMBERED_ARTICLE_PATTERN.match(header):
            self.context["article"] = normalize_nepali_digits(m.group(1))
            self.context["article_title"] = m.group(2).strip()
            self.context["clause"] = None
            
        elif m := CLAUSE_PATTERN.match(header):
            self.context["clause"] = m.group(1) or header
            
        return dict(self.context)
    
    def _split_at_headers(self, text: str) -> List[Dict[str, str]]:
        """Split text at legal headers."""
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
    
    def _create_chunk_metadata(
        self,
        text: str,
        context: Dict[str, Optional[str]],
        chunk_sequence: int,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None,
    ) -> ChunkMetadata:
        """Create metadata for a chunk."""
        # Detect language
        language = language_service.detect_language(text)
        
        # Apply safe OCR correction with tracking
        ocr_corrector = SafeOCRCorrector()
        corrected_text, ocr_corrections = ocr_corrector.correct(text)
        ocr_status = "corrected" if ocr_corrections else "verified"
        
        # Compute content hash
        content_hash = compute_content_hash(corrected_text)
        
        # Generate chunk ID with sequence number for uniqueness
        chunk_id = generate_chunk_id(
            self.document_name,
            context.get("part"),
            context.get("chapter"),
            context.get("article"),
            context.get("clause"),
            context.get("schedule"),
            context.get("annex"),
            chunk_sequence,
            content_hash,
        )
        
        # Generate citation label
        citation_label = generate_citation_label(
            self.document_name,
            context.get("article"),
            context.get("clause"),
            context.get("section"),
            context.get("schedule"),
            context.get("annex"),
        )
        
        # Build hierarchy path
        hierarchy_path = []
        if context.get("part"):
            hierarchy_path.append(f"part-{context['part']}")
        if context.get("chapter"):
            hierarchy_path.append(f"chapter-{context['chapter']}")
        if context.get("schedule"):
            hierarchy_path.append(f"schedule-{context['schedule']}")
        elif context.get("annex"):
            hierarchy_path.append(f"annex-{context['annex']}")
        elif context.get("article"):
            hierarchy_path.append(f"article-{context['article']}")
            if context.get("clause"):
                hierarchy_path.append(f"clause-{context['clause']}")
        
        # Determine chunk type
        if context.get("schedule"):
            chunk_type = "schedule"
        elif context.get("annex"):
            chunk_type = "annex"
        elif context.get("article"):
            chunk_type = "article" if not context.get("clause") else "clause"
        else:
            chunk_type = "provision"
        
        # Build contextualized text for embeddings
        contextualized_parts = [self.document_name]
        if context.get("part_title"):
            contextualized_parts.append(context["part_title"])
        if context.get("chapter_title"):
            contextualized_parts.append(context["chapter_title"])
        if context.get("article_title"):
            contextualized_parts.append(context["article_title"])
        contextualized_parts.append(corrected_text)
        contextualized_text = " ".join(contextualized_parts)
        
        # Compute content hash
        content_hash = compute_content_hash(corrected_text)
        
        return ChunkMetadata(
            chunk_id=chunk_id,
            document_id=self.document_id,
            document_name=self.document_name,
            document_type=self.document_type,
            jurisdiction=self.jurisdiction,
            language=language,
            part_number=context.get("part"),
            part_title=context.get("part_title"),
            chapter_number=context.get("chapter"),
            chapter_title=context.get("chapter_title"),
            section_number=context.get("section"),
            section_title=context.get("section_title"),
            article_number=context.get("article"),
            article_title=context.get("article_title"),
            clause_number=context.get("clause"),
            chunk_type=chunk_type,
            hierarchy_path=hierarchy_path,
            ocr_corrections=ocr_corrections,
            source_page_start=page_start,
            source_page_end=page_end,
            source_text=text,
            corrected_text=corrected_text,
            contextualized_text=contextualized_text,
            ocr_status=ocr_status,
            content_hash=content_hash,
            citation_label=citation_label,
        )
    
    def chunk(
        self,
        text: str,
        page_mapping: Optional[Dict[int, Tuple[int, int]]] = None,
    ) -> List[ChunkMetadata]:
        """
        Chunk legal text with advanced features.
        
        Args:
            text: Full text of the document
            page_mapping: Optional mapping of character positions to page numbers
                         {page_num: (start_char, end_char)}
        """
        if not text or not text.strip():
            return []
        
        sections = self._split_at_headers(text)
        all_chunks: List[ChunkMetadata] = []
        chunk_sequence = 0
        
        # Track character positions for page mapping
        current_char_pos = 0
        
        for section in sections:
            header = section["header"]
            content = section["content"]
            
            # Update context from header
            if header:
                self._parse_header(header)
            
            # Determine page range if mapping provided
            page_start = None
            page_end = None
            if page_mapping:
                # Calculate character positions for this section
                section_start = current_char_pos
                section_end = current_char_pos + len(content)
                page_start, page_end = _determine_page_range(
                    text, section_start, section_end, page_mapping
                )
            
            # Create chunk for this section
            if len(content.split()) >= 10:  # Minimum chunk size
                metadata = self._create_chunk_metadata(
                    content,
                    dict(self.context),
                    chunk_sequence,
                    page_start,
                    page_end,
                )
                all_chunks.append(metadata)
                chunk_sequence += 1
            
            # Update character position for next section
            current_char_pos += len(content)
        
        return all_chunks
