from typing import Any, Dict, List

from legal_ai.services.hybrid_retrieval import tokenize


def rerank_results(query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Rerank top-N candidates using lexical density and metadata relevance.
    """
    if not candidates:
        return []

    query_tokens = set(tokenize(query))

    for hit in candidates:
        text = hit.get("text", "")
        text_tokens = set(tokenize(text))
        density = len(query_tokens & text_tokens) / max(len(query_tokens), 1)

        # Prefer focused chunks (not too long)
        word_count = len(text.split())
        length_penalty = 0.0
        if word_count > 500:
            length_penalty = 0.05
        elif word_count < 30:
            length_penalty = 0.1

        # Boost if title contains query terms
        title = (hit.get("title") or "").lower()
        title_boost = 0.1 if any(t in title for t in query_tokens) else 0.0

        hit["rerank_score"] = hit.get("score", 0) + density * 0.15 + title_boost - length_penalty

    ranked = sorted(candidates, key=lambda x: x.get("rerank_score", x.get("score", 0)), reverse=True)
    return ranked[:top_k]
