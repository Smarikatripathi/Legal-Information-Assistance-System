"""Backward-compatible re-exports for existing imports."""

from legal_information_assistance_system.legal_ai.services.ingestion import (
    ingest_pdfs_from_directory,
    process_document,
    process_pdf,
)
from legal_information_assistance_system.legal_ai.services.rag import answer_query
from legal_information_assistance_system.legal_ai.services.retrieval import (
    FINAL_TOP_K,
    rebuild_faiss_index,
    rebuild_index_from_chunks,
    search,
    sync_vector_store,
)

__all__ = [
    "FINAL_TOP_K",
    "answer_query",
    "ingest_pdfs_from_directory",
    "process_document",
    "process_pdf",
    "rebuild_faiss_index",
    "rebuild_index_from_chunks",
    "search",
    "sync_vector_store",
]
