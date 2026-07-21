from typing import Any, Dict, List

from legal_information_assistance_system.legal_ai.services.hybrid_retrieval import tokenize
from legal_information_assistance_system.legal_ai.services.language import language_service


def extract_legal_concepts(text: str) -> List[str]:
    """Extract legal concepts using keyword matching."""
    concepts_en = [
        "fundamental right", "due process", "liability", "jurisdiction",
        "contract", "property", "marriage", "divorce", "inheritance",
        "offense", "penalty", "duty", "constitutional", "provision"
    ]
    concepts_ne = [
        "मौलिक अधिकार", "न्यायिक प्रक्रिया", "दायित्व", "अधिकारक्षेत्र",
        "सम्झौता", "सम्पत्ति", "विवाह", "विवाह विच्छेद", "सम्पत्ति विभाजन",
        "अपराध", "दण्ड", "कर्तव्य", "संवैधानिक", "व्यवस्था"
    ]
    
    text_lower = text.lower()
    found = []
    
    for concept in concepts_en:
        if concept in text_lower:
            found.append(concept)
    
    for concept in concepts_ne:
        if concept in text_lower:
            found.append(concept)
    
    return found


def has_section_number_match(query: str, hit: Dict[str, Any]) -> bool:
    """Check if query has a section/article number that matches the chunk."""
    query_tokens = set(tokenize(query))
    article = hit.get("article") or hit.get("dhara") or ""
    section = hit.get("section") or ""
    article_section_str = str(article) + str(section)
    
    if article_section_str and any(str(t).isdigit() and str(t) in article_section_str for t in query_tokens):
        return True
    return False


def rerank_results(query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Enhanced reranking with:
    - Lexical density
    - Metadata relevance
    - Legal section specificity
    - Query-title alignment
    - Language match boost
    - Legal concept matching
    """
    if not candidates:
        return []

    query_tokens = set(tokenize(query))
    query_lower = query.lower()
    query_lang = language_service.detect_language(query)
    
    # Extract legal concepts from query
    query_concepts = set(extract_legal_concepts(query))

    for hit in candidates:
        text = hit.get("text", "")
        text_tokens = set(tokenize(text))
        text_lang = hit.get("language", "en")
        
        # Lexical density: how many query tokens appear in text
        density = len(query_tokens & text_tokens) / max(len(query_tokens), 1)

        # Prefer focused chunks (not too long, not too short)
        word_count = len(text.split())
        length_penalty = 0.0
        if word_count > 700:  # Very long chunks get slight penalty
            length_penalty = 0.03
        elif word_count < 20:  # Very short chunks less useful
            length_penalty = 0.05
        elif 50 <= word_count <= 400:  # Ideal range
            length_penalty = 0.0

        # Boost if title/section contains query terms
        title = (hit.get("title") or "").lower()
        title_boost = 0.0
        if title and any(t in title for t in query_tokens):
            title_boost = 0.15
        
        # Language match boost - significant for bilingual retrieval
        language_boost = 0.0
        if query_lang == text_lang:
            language_boost = 0.15
        
        # Article/section number match is VERY relevant for legal queries
        article_boost = 0.0
        if has_section_number_match(query, hit):
            article_boost = 0.25  # Increased boost for precise section matches
        
        # Legal concept matching
        chunk_concepts = set(extract_legal_concepts(text))
        concept_overlap = len(query_concepts & chunk_concepts)
        concept_boost = concept_overlap * 0.05
        
        # Document type alignment (constitution for constitutional questions, etc)
        doc_type = (hit.get("document_type") or "").lower()
        doc_name = (hit.get("document_name") or hit.get("document_title") or "").lower()
        doc_boost = 0.0
        if ("constitution" in query_lower or "sanvidhan" in query_lower) and ("constitution" in doc_name or "sanvidhan" in doc_name):
            doc_boost = 0.1
        elif ("civil" in query_lower or "marriage" in query_lower or "property" in query_lower) and ("civil" in doc_name):
            doc_boost = 0.08
        elif ("criminal" in query_lower or "crime" in query_lower or "offence" in query_lower) and ("criminal" in doc_name):
            doc_boost = 0.08

        # Combined rerank score
        hit["rerank_score"] = (
            hit.get("score", 0) + 
            density * 0.15 + 
            title_boost + 
            language_boost +
            article_boost +
            concept_boost +
            doc_boost -
            length_penalty
        )

    ranked = sorted(candidates, key=lambda x: x.get("rerank_score", x.get("score", 0)), reverse=True)
    return ranked[:top_k]
