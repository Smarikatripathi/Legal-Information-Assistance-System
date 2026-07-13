"""
Purpose:
- Reject only obviously non-legal questions.
- Allow everything else to reach the retriever.
- The retriever decides whether relevant legal documents exist.
"""

import re
from dataclasses import dataclass

from django.conf import settings

from legal_information_assistance_system.legal_ai.services.language import language_service


NON_LEGAL_PATTERNS = [
    r"\b(joke|jokes|funny|laugh|meme)\b",
    r"\b(weather|temperature|forecast|rain)\b",
    r"\b(movie|movies|film|music|song|actor|actress)\b",
    r"\b(recipe|cook|cooking|food|restaurant|pizza|burger)\b",
    r"\b(cricket|football|basketball|sport|match|score)\b",
    r"\b(hello|hi|hey|good morning|good evening|how are you)\b",

    r"(जोक|हासो)",
    r"(खाना|रेसिपी|पकाउने)",
    r"(मौसम|तापक्रम)",
    r"(चलचित्र|फिल्म|गीत|संगीत)",
    r"(क्रिकेट|फुटबल|खेल)",
]


@dataclass
class ClassificationResult:
    is_legal: bool
    confidence: float
    reason: str
    language: str


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def classify_query(query: str) -> ClassificationResult:
    """
    Reject only obvious non-legal queries.
    Everything else is sent to the retriever.
    """

    if not query or not query.strip():
        return ClassificationResult(
            False,
            0.0,
            "empty_query",
            "en",
        )

    language = language_service.detect_language(query)
    normalized = _normalize(query)

    for pattern in NON_LEGAL_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return ClassificationResult(
                False,
                0.98,
                "non_legal_pattern",
                language,
            )

    # Allow retrieval to determine legality.
    return ClassificationResult(
        True,
        0.70,
        "retrieval_required",
        language,
    )


def get_non_legal_response(language: str) -> str:
    if language == "ne":
        return (
            "म नेपालका कानुनी विषयहरूमा मात्र सहयोग गर्न सक्छु। "
            "कृपया नेपालको कानून, अधिकार, अदालत, नागरिकता, जग्गा, विवाह, सम्पत्ति वा अन्य कानुनी विषय सम्बन्धी प्रश्न सोध्नुहोस्।"
        )

    return (
        "I can only answer questions related to Nepal law. "
        "Please ask about Nepalese laws, legal rights, courts, citizenship, property, marriage, employment, taxation, or other legal matters."
    )


def is_legal_query(query: str) -> bool:
    if not getattr(settings, "RAG_DOMAIN_CLASSIFIER_ENABLED", True):
        return True

    return classify_query(query).is_legal