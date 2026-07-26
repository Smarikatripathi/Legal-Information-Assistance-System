from typing import Any, Dict, List, Optional
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class RetrievalError(Exception):
    """Base exception for retrieval errors."""
    pass


class VectorStoreError(RetrievalError):
    """Exception raised when vector store operations fail."""
    pass


class EmbeddingError(RetrievalError):
    """Exception raised when embedding generation fails."""
    pass

from legal_information_assistance_system.legal_ai.models import EmbeddingConfig, LegalChunk
from legal_information_assistance_system.legal_ai.services.embedding import create_query_embedding, get_embedding_model
from legal_information_assistance_system.legal_ai.services.hybrid_retrieval import MIN_SCORE, filter_by_threshold, hybrid_score
from legal_information_assistance_system.legal_ai.services.reranker import rerank_results
from legal_information_assistance_system.legal_ai.services.legal_concepts import expand_query, is_arrest_related
from legal_information_assistance_system.legal_ai.services.language import language_service
from legal_information_assistance_system.legal_ai.storage.vector_db import FAISSService

RETRIEVAL_CANDIDATES = getattr(settings, "RAG_RETRIEVAL_CANDIDATES", 15)
FINAL_TOP_K = getattr(settings, "RAG_FINAL_TOP_K", 5)

_vector_store: FAISSService | None = None

# Cache the vector store to avoid repeated loading
_vector_store_loaded = False


def get_vector_store() -> FAISSService:
    global _vector_store, _vector_store_loaded
    if _vector_store is None:
        _vector_store = FAISSService()
        _vector_store_loaded = True
    return _vector_store


def _build_faiss_metadata(chunk: LegalChunk, embedding_id: int) -> Dict[str, Any]:
    meta = chunk.to_metadata()
    meta["embedding_id"] = embedding_id
    return meta


def rebuild_faiss_index() -> bool:
    """Rebuild FAISS index once from all LegalChunk rows."""
    try:
        chunks = list(LegalChunk.objects.select_related("doc").order_by("id"))
        store = get_vector_store()

        if not chunks:
            store.clear()
            logger.info("No chunks found, cleared vector store")
            return False

        model = get_embedding_model()
        texts = [c.text for c in chunks]
        
        # Build metadata for title augmentation in embeddings
        metadata_list = [_build_faiss_metadata(chunk, idx) for idx, chunk in enumerate(chunks)]
        embeddings = model.embed_passages(texts, metadata=metadata_list)

        store.build_index(embeddings, metadata_list, model_name=model.model_name)

        for idx, chunk in enumerate(chunks):
            chunk.embedding_id = idx
        LegalChunk.objects.bulk_update(chunks, ["embedding_id"])

        EmbeddingConfig.objects.filter(is_active=True).update(is_active=False)
        EmbeddingConfig.objects.create(
            model_name=model.model_name,
            dimension=model.dimension,
            is_active=True,
        )
        logger.info(f"Successfully rebuilt FAISS index with {len(chunks)} chunks")
        return True
    except Exception as e:
        logger.error(f"Failed to rebuild FAISS index: {e}")
        raise VectorStoreError(f"FAISS index rebuild failed: {e}")


def sync_vector_store() -> None:
    """Ensure FAISS matches the database."""
    db_count = LegalChunk.objects.count()
    store = get_vector_store()
    store.load()
    faiss_count = store.count()

    if db_count == 0 and faiss_count > 0:
        store.clear()
        return

    if db_count > 0 and (faiss_count == 0 or faiss_count != db_count):
        rebuild_faiss_index()


def search(
    query: str,
    top_k: int = FINAL_TOP_K,
    *,
    min_score: float | None = None,
) -> List[Dict[str, Any]]:
    """Hybrid FAISS search with similarity threshold and query expansion."""
    if not query or not query.strip():
        return []

    try:
        sync_vector_store()
        store = get_vector_store()
        store.load()

        if not store.has_embeddings():
            logger.warning("Vector store has no embeddings")
            return []

        # For arrest-related queries, prioritize direct database search
        # BUT still apply threshold filtering to prevent hallucinations
        if is_arrest_related(query):
            arrest_keywords = ["arrest", "apprehension", "warrant", "detention", "custody", "पक्राउ", "वारेन्ट", "गिरफ्तार", "हिरासत"]
            db_chunks = LegalChunk.objects.select_related("doc").filter(
                text__icontains=arrest_keywords[0]
            ) | LegalChunk.objects.select_related("doc").filter(
                text__icontains=arrest_keywords[1]
            ) | LegalChunk.objects.select_related("doc").filter(
                text__icontains=arrest_keywords[2]
            )
            
            db_results = []
            for chunk in db_chunks[:20]:
                entry = chunk.to_metadata()
                entry["score"] = 1.5  # Highest priority for database results
                entry["dense_score"] = 1.5
                entry["search_query"] = "database_primary"
                entry["from_db"] = True
                entry["db_boost"] = True
                db_results.append(entry)
            
            # If we have database results, rerank them but still apply threshold
            if db_results:
                db_results.sort(key=lambda x: x["score"], reverse=True)
                reranked_db = rerank_results(query, db_results, top_k=len(db_results))
                
                # Apply threshold filtering to database results too
                threshold = min_score if min_score is not None else MIN_SCORE
                filtered_db = [r for r in reranked_db if r.get("score", 0) >= threshold]
                
                if filtered_db:
                    return filtered_db[:top_k]
                # If no DB results pass threshold, continue to vector search

        # Detect language and expand query for other queries
        language = language_service.detect_language(query)
        queries_to_search = [query]
        
        # Use query expansion for arrest-related queries (if DB search didn't return results)
        if is_arrest_related(query):
            expanded = expand_query(query, language)
            queries_to_search = expanded[:3]  # Limit to 3 expanded queries

        all_candidates: List[Dict[str, Any]] = []
        
        for search_query in queries_to_search:
            try:
                query_vector = create_query_embedding(search_query).reshape(1, -1)
                distances, indices = store.search(query_vector, RETRIEVAL_CANDIDATES)

                for dense_score, idx in zip(distances[0].tolist(), indices[0].tolist()):
                    if idx < 0 or idx >= len(store.metadata):
                        continue
                    faiss_meta = dict(store.metadata[idx])
                    text = faiss_meta.get("text", "")
                    combined = hybrid_score(float(dense_score), query, text, faiss_meta)
                    
                    # Build entry with metadata nested properly
                    entry = {
                        "text": text,
                        "score": combined,
                        "dense_score": float(dense_score),
                        "search_query": search_query,
                        "metadata": faiss_meta,  # Keep all FAISS metadata nested
                    }
                    all_candidates.append(entry)
            except Exception as e:
                logger.error(f"Error during vector search for query '{search_query}': {e}")
                continue

        # Remove duplicates by chunk ID
        seen_ids = set()
        unique_candidates = []
        for candidate in all_candidates:
            chunk_id = candidate.get("id")
            if chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                unique_candidates.append(candidate)

        unique_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Re-enable reranker - it's critical for filtering irrelevant content
        reranked = rerank_results(query, unique_candidates, top_k=RETRIEVAL_CANDIDATES)
        
        threshold = min_score if min_score is not None else MIN_SCORE
        filtered = filter_by_threshold(reranked, min_score=threshold)
        
        # CRITICAL: Do NOT return low-confidence results to prevent hallucinations
        # If no results pass the confidence threshold, return empty list
        # The system should respond "not found" rather than fabricating answers
        if not filtered:
            return []
        
        return filtered[:top_k]
    except Exception as e:
        logger.error(f"Error during search for query '{query}': {e}")
        raise RetrievalError(f"Search failed: {e}")


# Backward-compatible aliases
rebuild_index_from_chunks = rebuild_faiss_index
