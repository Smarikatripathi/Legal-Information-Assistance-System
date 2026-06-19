from typing import Any, Dict, List

from legal_ai.services.hybrid_retrieval import tokenize


def rerank_results(query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Rerank top-N candidates using:
    - Lexical density
    - Metadata relevance
    - Legal section specificity
    - Query-title alignment
    """
    if not candidates:
        return []

    query_tokens = set(tokenize(query))
    query_lower = query.lower()

    for hit in candidates:
        text = hit.get("text", "")
        text_tokens = set(tokenize(text))
        
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
        
        # Article/section number match is VERY relevant for legal queries
        article = hit.get("article") or hit.get("dhara") or ""
        section = hit.get("section") or ""
        article_section_str = str(article) + str(section)
        article_boost = 0.0
        if article_section_str and any(str(t).isdigit() and str(t) in article_section_str for t in query_tokens):
            article_boost = 0.1  # Legal queries with section numbers are very precise
        
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
            article_boost +
            doc_boost -
            length_penalty
        )

    ranked = sorted(candidates, key=lambda x: x.get("rerank_score", x.get("score", 0)), reverse=True)
    return ranked[:top_k]
