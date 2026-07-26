"""Legal AI service helpers - Core services exports."""

# RAG pipeline
from legal_information_assistance_system.legal_ai.services.rag import answer_query

# Understanding
from legal_information_assistance_system.legal_ai.services.domain_classifier import classify_query, get_non_legal_response
from legal_information_assistance_system.legal_ai.services.language import language_service

# LLM
from legal_information_assistance_system.legal_ai.services.llm import LegalLLM, correct_typos, llm

# Retrieval
from legal_information_assistance_system.legal_ai.services.retrieval import (
    search,
    FINAL_TOP_K,
    rebuild_faiss_index,
    rebuild_index_from_chunks,
    sync_vector_store,
)

# Ingestion
from legal_information_assistance_system.legal_ai.services.ingestion import (
    ingest_pdfs_from_directory,
    process_document,
    process_pdf,
)

# Chunking
from legal_information_assistance_system.legal_ai.services.chunking_v2 import AdvancedLegalChunker

# Embedding
from legal_information_assistance_system.legal_ai.services.embedding import get_embedding_model, create_query_embedding

__all__ = [
    # RAG
    "answer_query",
    # Understanding
    "classify_query",
    "get_non_legal_response",
    "language_service",
    # LLM
    "LegalLLM",
    "correct_typos",
    "llm",
    # Retrieval
    "search",
    "FINAL_TOP_K",
    "rebuild_faiss_index",
    "rebuild_index_from_chunks",
    "sync_vector_store",
    # Ingestion
    "ingest_pdfs_from_directory",
    "process_document",
    "process_pdf",
    # Chunking
    "AdvancedLegalChunker",
    # Embedding
    "get_embedding_model",
    "create_query_embedding",
]
