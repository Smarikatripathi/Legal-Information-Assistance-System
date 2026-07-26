"""Legal concept mapping for improved retrieval."""

from typing import Dict, List, Optional
import re


# Legal concept mappings for query expansion
LEGAL_CONCEPTS = {
    "arrest_without_warrant": {
        "english": [
            "arrest without warrant",
            "warrantless arrest",
            "police arrest without warrant",
            "arrest procedure",
            "apprehension",
            "detention",
            "custody",
            "police powers",
            "arrest authority",
            "rights relating to justice",
            "rights after arrest",
            "arrested person",
        ],
        "nepali": [
            "पक्राउ",
            "वारेन्ट बिना पक्राउ",
            "प्रहरी पक्राउ",
            "गिरफ्तार",
            "हिरासत",
            "पक्राउ प्रक्रिया",
            "अभियुक्त पक्राउ",
            "न्याय सम्बन्धी अधिकार",
            "पक्राउ पछि अधिकार",
        ],
        "related_terms": [
            "apprehension",
            "custody",
            "detention",
            "habeas corpus",
            "fundamental rights",
            "police",
            "arrest warrant",
            "justice",
            "legal practitioner",
        ],
    },
    "arrest_warrant": {
        "english": [
            "arrest warrant",
            "warrant",
            "court warrant",
            "judicial warrant",
            "warrant procedure",
        ],
        "nepali": [
            "वारेन्ट",
            "गिरफ्तारी वारेन्ट",
            "अदालत वारेन्ट",
            "न्यायिक वारेन्ट",
        ],
        "related_terms": [
            "summons",
            "court order",
            "judicial process",
        ],
    },
    "rights_after_arrest": {
        "english": [
            "rights after arrest",
            "rights of arrested person",
            "arrested person rights",
            "detainee rights",
            "custody rights",
        ],
        "nepali": [
            "पक्राउ पछि अधिकार",
            "पक्राउ परेको व्यक्तिको अधिकार",
            "हिरासतमा रहेको व्यक्तिको अधिकार",
        ],
        "related_terms": [
            "fundamental rights",
            "justice",
            "torture prohibition",
            "legal representation",
        ],
    },
}


def detect_legal_concept(query: str, language: str = "en") -> Optional[str]:
    """Detect the legal concept from a query."""
    query_lower = query.lower()
    
    for concept, data in LEGAL_CONCEPTS.items():
        terms = data.get("english", []) if language == "en" else data.get("nepali", [])
        for term in terms:
            if term.lower() in query_lower:
                return concept
    
    return None


def expand_query(query: str, language: str = "en") -> List[str]:
    """Expand query with related legal terms for better retrieval."""
    concept = detect_legal_concept(query, language)
    if not concept:
        return [query]
    
    concept_data = LEGAL_CONCEPTS.get(concept, {})
    related_terms = concept_data.get("related_terms", [])
    
    # Add related terms to query
    expanded_queries = [query]
    for term in related_terms:
        expanded_queries.append(f"{query} {term}")
    
    return expanded_queries


def get_legal_keywords(concept: str, language: str = "en") -> List[str]:
    """Get keywords for a legal concept."""
    concept_data = LEGAL_CONCEPTS.get(concept, {})
    return concept_data.get("english" if language == "en" else "nepali", [])


def is_arrest_related(query: str) -> bool:
    """Check if query is related to arrest."""
    arrest_keywords = [
        "arrest", "warrant", "apprehension", "detention", "custody",
        "पक्राउ", "वारेन्ट", "गिरफ्तार", "हिरासत",
    ]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in arrest_keywords)
