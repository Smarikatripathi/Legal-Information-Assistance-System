"""Question-answering entry point: retrieval → LangChain prompt → LLM."""

import time
from typing import Any, Dict

from legal_information_assistance_system.legal_ai.models import LegalChunk, LegalDocument
from legal_information_assistance_system.legal_ai.services.language import language_service
from legal_information_assistance_system.legal_ai.services.langchain_rag import run_grounded_rag
from legal_information_assistance_system.legal_ai.services.retrieval import FINAL_TOP_K


def answer_query(
    query: str,
    top_k: int = FINAL_TOP_K,
    *,
    min_score: float | None = None,
) -> Dict[str, Any]:
    start = time.perf_counter()

    if not LegalDocument.objects.exists():
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            "query": query,
            "answer": (
                "No legal documents are available. "
                "Run the scraper and `python manage.py ingest_pdfs` to load documents."
            ),
            "sources": [],
            "confidence_score": 0.0,
            "response_time_ms": elapsed_ms,
            "query_language": language_service.detect_language(query),
            "retrieval_time_ms": 0,
            "skipped_llm": True,
        }

    if not LegalChunk.objects.exists():
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            "query": query,
            "answer": "Documents exist but are not indexed yet. Run `python manage.py ingest_pdfs`.",
            "sources": [],
            "confidence_score": 0.0,
            "response_time_ms": elapsed_ms,
            "query_language": language_service.detect_language(query),
            "retrieval_time_ms": 0,
            "skipped_llm": True,
        }

    retrieval_start = time.perf_counter()
    result = run_grounded_rag(query, top_k=top_k, min_score=min_score)
    retrieval_time = int((time.perf_counter() - retrieval_start) * 1000)

    generation_time = 0 if result.get("skipped_llm") else int((time.perf_counter() - retrieval_start) * 1000)

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    result["response_time_ms"] = elapsed_ms
    result["retrieval_time_ms"] = retrieval_time
    result["generation_time_ms"] = generation_time
    return result
