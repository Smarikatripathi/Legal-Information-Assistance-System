import math
import re
from typing import Any, Dict, List

from django.conf import settings

DENSE_WEIGHT = getattr(settings, "RAG_DENSE_WEIGHT", 0.7)
KEYWORD_WEIGHT = getattr(settings, "RAG_KEYWORD_WEIGHT", 0.3)
MIN_SCORE = getattr(settings, "RAG_MIN_SCORE", 0.55)

NEPALI_DIGIT_MAP = str.maketrans("०१२३४५६७८९", "0123456789")

SECTION_QUERY_PATTERN = re.compile(
    r"(?:section|article|clause|धारा|दफा|अनुच्छेद)\s*[-#]?\s*([\d०-९]+)",
    re.I,
)
NUMBER_PATTERN = re.compile(r"\b(\d{1,4})\b")


def normalize_nepali_digits(text: str) -> str:
    return text.translate(NEPALI_DIGIT_MAP)


def tokenize(text: str) -> List[str]:
    text = normalize_nepali_digits(text.lower())
    return [t for t in re.findall(r"[\w\u0900-\u097F]+", text) if len(t) > 1]


def extract_legal_numbers(query: str) -> set[str]:
    numbers = set()
    query_norm = normalize_nepali_digits(query)
    for match in SECTION_QUERY_PATTERN.finditer(query_norm):
        numbers.add(match.group(1))
    return numbers


def keyword_score(query: str, text: str, metadata: Dict[str, Any]) -> float:
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return 0.0

    text_tokens = set(tokenize(text))
    overlap = len(query_tokens & text_tokens) / len(query_tokens)

    # Exact section/article number match boost
    legal_numbers = extract_legal_numbers(query)
    meta_numbers = {
        normalize_nepali_digits(str(v))
        for v in (
            metadata.get("section"),
            metadata.get("article"),
            metadata.get("dhara"),
            metadata.get("clause"),
        )
        if v
    }
    if legal_numbers & meta_numbers:
        overlap = min(1.0, overlap + 0.45)

    # Title match boost
    title = (metadata.get("title") or "").lower()
    title_hits = sum(1 for t in query_tokens if t in title)
    if title_hits:
        overlap = min(1.0, overlap + 0.15 * title_hits)

    return min(1.0, overlap)


def metadata_score(query: str, metadata: Dict[str, Any]) -> float:
    """Score based on document name / type relevance."""
    score = 0.0
    query_lower = query.lower()

    doc_name = (metadata.get("document_name") or metadata.get("document_title") or "").lower()
    doc_type = (metadata.get("document_type") or "").lower()

    type_keywords = {
        "constitution": ["constitution", "sanvidhan", "संविधान"],
        "civil_code": ["civil", "muluki", "marriage", "property", "national civil"],
        "criminal_code": ["criminal", "crime", "offence"],
    }
    for dtype, keywords in type_keywords.items():
        if doc_type == dtype and any(kw in query_lower for kw in keywords):
            score += 0.2

    if doc_name and any(word in doc_name for word in tokenize(query)[:5]):
        score += 0.15

    return min(1.0, score)


def hybrid_score(
    dense_score: float,
    query: str,
    text: str,
    metadata: Dict[str, Any],
) -> float:
    kw = keyword_score(query, text, metadata)
    meta = metadata_score(query, metadata)
    combined = (
        DENSE_WEIGHT * dense_score
        + KEYWORD_WEIGHT * kw
        + 0.1 * meta
    )
    return min(1.0, combined)


def filter_by_threshold(results: List[Dict[str, Any]], min_score: float | None = None) -> List[Dict[str, Any]]:
    threshold = min_score if min_score is not None else MIN_SCORE
    return [r for r in results if r.get("score", 0) >= threshold]
