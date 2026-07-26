from typing import Any, Dict, List

from legal_information_assistance_system.legal_ai.services.hybrid_retrieval import tokenize
from legal_information_assistance_system.legal_ai.services.language import language_service
from legal_information_assistance_system.legal_ai.services.legal_concepts import is_arrest_related


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
    - Lexical density (token overlap)
    - Title boost (metadata title matching)
    - Section/article match (exact number matching)
    - Language match (bilingual support)
    - Legal concept matching
    - Length optimization
    - Relevance filtering for arrest queries
    """
    if not candidates:
        return []

    query_tokens = set(tokenize(query))
    query_lower = query.lower()
    query_lang = language_service.detect_language(query)
    
    # Extract legal concepts from query for concept matching
    query_concepts = extract_legal_concepts(query)
    
    # Check if this is an arrest-related query
    is_arrest_query = is_arrest_related(query)

    for hit in candidates:
        text = hit.get("text", "")
        text_tokens = set(tokenize(text))
        text_lang = hit.get("language", "en")
        metadata = hit.get("metadata", {})
        text_lower = text.lower()
        
        # Lexical density: how many query tokens appear in text
        density = len(query_tokens & text_tokens) / max(len(query_tokens), 1)

        # Prefer focused chunks (not too long, not too short)
        word_count = len(text.split())
        length_penalty = 0.0
        if word_count > 700:
            length_penalty = 0.05
        elif word_count < 30:
            length_penalty = 0.08
        elif 60 <= word_count <= 450:
            length_penalty = 0.0  # Optimal length range

        # Boost if title contains query terms
        title = (hit.get("title") or "").lower()
        title_boost = 0.0
        if title and any(t in title for t in query_tokens):
            title_boost = 0.20
        
        # Language match boost (stronger for bilingual system)
        language_boost = 0.0
        if query_lang == text_lang:
            language_boost = 0.20
        
        # Section/article number match (strong signal for legal queries)
        article_boost = 0.0
        if has_section_number_match(query, hit):
            article_boost = 0.30
        
        # Legal concept matching boost
        concept_boost = 0.0
        for concept in query_concepts:
            if concept in text_lower:
                concept_boost += 0.10
        concept_boost = min(concept_boost, 0.25)  # Cap at 0.25

        # Relevance filtering for arrest queries
        relevance_penalty = 0.0
        if is_arrest_query:
            # Extra boost for database fallback results
            if hit.get("db_boost", False):
                concept_boost += 0.50
            
            # Penalize chunks that mention detention/imprisonment but not arrest
            detention_keywords = ["detention", "detain", "imprisonment", "imprison", "custody"]
            arrest_keywords = ["arrest", "apprehension", "warrant", "पक्राउ", "गिरफ्तार"]
            rights_keywords = ["rights", "justice", "अधिकार", "न्याय"]
            
            has_detention = any(kw in text_lower for kw in detention_keywords)
            has_arrest = any(kw in text_lower for kw in arrest_keywords)
            has_rights = any(kw in text_lower for kw in rights_keywords)
            
            # If chunk mentions detention but not arrest, penalize heavily
            if has_detention and not has_arrest:
                relevance_penalty = 0.60  # Increased penalty
            
            # Penalize chunks about parliamentary privileges
            if "privilege" in text_lower or "parliament" in text_lower or "assembly" in text_lower:
                if has_arrest:
                    relevance_penalty += 0.70  # Heavy penalty for parliamentary arrest immunity
            
            # Penalize chunks about court jurisdiction
            if "jurisdiction" in text_lower or "supreme court" in text_lower or "high court" in text_lower:
                if not has_rights:
                    relevance_penalty += 0.60
            
            # Boost chunks that specifically mention arrest/warrant
            if has_arrest:
                concept_boost += 0.25  # Increased boost
            
            # Extra boost for chunks with both arrest and rights/justice
            if has_arrest and has_rights:
                concept_boost += 0.30  # Increased boost for rights + arrest
            
            # Penalize chunks about arms/weapons for arrest queries
            if "arms" in text_lower or "weapon" in text_lower or "license" in text_lower:
                if not has_arrest:
                    relevance_penalty += 0.50
            
            # Penalize chunks about goods/commercial law
            if "goods" in text_lower or "bailor" in text_lower or "bailee" in text_lower or "contract" in text_lower:
                if not has_arrest:
                    relevance_penalty += 0.70
            
            # Penalize "warrant" when used in commercial context (warranty)
            if "warrant" in text_lower:
                commercial_context = ["goods", "bailor", "bailee", "quality", "separate provision", "fault"]
                if any(ctx in text_lower for ctx in commercial_context):
                    relevance_penalty += 0.80

        # Combined rerank score
        hit["rerank_score"] = (
            hit.get("score", 0) + 
            density * 0.20 +  # Increased weight for lexical density
            title_boost + 
            language_boost +
            article_boost +
            concept_boost -
            length_penalty -
            relevance_penalty
        )

    ranked = sorted(candidates, key=lambda x: x.get("rerank_score", x.get("score", 0)), reverse=True)
    return ranked[:top_k]
