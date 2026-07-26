"""Single RAG pipeline entry point: classification → retrieval → generation."""

import time
from typing import Any, Dict, Optional

from legal_information_assistance_system.legal_ai.models import LegalChunk, LegalDocument, Conversation
from legal_information_assistance_system.legal_ai.services.language import language_service
from legal_information_assistance_system.legal_ai.services.query_classifier import query_classifier
from legal_information_assistance_system.legal_ai.services.clarification import clarification_service
from legal_information_assistance_system.legal_ai.services.domain_classifier import get_non_legal_response
from legal_information_assistance_system.legal_ai.services.retrieval import search, FINAL_TOP_K
from legal_information_assistance_system.legal_ai.services.llm import llm
from legal_information_assistance_system.legal_ai.clarification.conversation_manager import conversation_manager
from legal_information_assistance_system.legal_ai.knowledge_gaps.detector import knowledge_gap_detector


def answer_query(
    query: str,
    top_k: int = FINAL_TOP_K,
    *,
    min_score: float | None = None,
    conversation_id: Optional[int] = None,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Answer a legal query using the staged RAG pipeline.
    
    Staged Pipeline:
    1. Language Detection
    2. Query Classification (LEGAL/NON_LEGAL/UNCLEAR)
    3. Clarification (if UNCLEAR)
    4. RAG Retrieval (if LEGAL)
    5. Knowledge Gap Detection
    6. LLM Answer Generation (if high confidence)
    
    Args:
        query: The user's question
        top_k: Number of top chunks to retrieve
        min_score: Minimum relevance score (optional)
        conversation_id: Conversation ID for context (optional)
        user_id: User ID for context (optional)
    
    Returns:
        Dict with answer, sources, confidence, timing info
    """
    start = time.perf_counter()

    # Check if documents exist
    if not LegalDocument.objects.exists():
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            "query": query,
            "answer": "No legal documents are available. Run the scraper and `python manage.py ingest_pdfs` to load documents.",
            "sources": [],
            "confidence_score": 0.0,
            "response_time_ms": elapsed_ms,
            "query_language": language_service.detect_language(query),
            "retrieval_time_ms": 0,
            "generation_time_ms": 0,
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
            "generation_time_ms": 0,
            "skipped_llm": True,
        }

    # Step 1: Language Detection
    query_language = language_service.detect_language(query)

    # Step 2: Query Classification (LEGAL/NON_LEGAL/UNCLEAR)
    classification = query_classifier.classify(query)
    
    # Step 3: Handle NON_LEGAL queries
    if classification.label == "NON_LEGAL":
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            "query": query,
            "answer": get_non_legal_response(classification.language),
            "sources": [],
            "confidence_score": 0.0,
            "response_time_ms": elapsed_ms,
            "query_language": classification.language,
            "retrieval_time_ms": 0,
            "generation_time_ms": 0,
            "skipped_llm": True,
            "skipped_retrieval": True,
            "out_of_scope": True,
            "classification": classification.label,
        }
    
    # Step 4: Handle UNCLEAR queries - ask for clarification
    if classification.label == "UNCLEAR":
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        clarification_response = clarification_service.get_clarification_response(classification.language)
        return {
            "query": query,
            **clarification_response,
            "response_time_ms": elapsed_ms,
            "query_language": classification.language,
            "classification": classification.label,
        }

    # Step 5: LEGAL query - Apply conversation context (if available)
    enhanced_query = query
    conversation_history = ""
    if conversation_id and user_id:
        context = conversation_manager.get_context(conversation_id, user_id)
        if context:
            enhanced_query = conversation_manager.combine_query_with_context(query, context)
            # Get conversation summary for LLM context
            conversation_history = conversation_manager.get_conversation_summary(conversation_id, user_id)

    # Step 6: RAG Retrieval
    retrieval_start = time.perf_counter()
    retrieved_chunks = search(enhanced_query, top_k=top_k, min_score=min_score)
    retrieval_time = int((time.perf_counter() - retrieval_start) * 1000)

    if not retrieved_chunks:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        # Return the exact message specified in the prompt for low-confidence retrieval
        not_found_message = "The uploaded legal documents do not contain enough information to answer this question."
        if query_language == "ne":
            not_found_message = "अपलोड गरिएका कानुनी कागजातहरूमा यो प्रश्नको उत्तर दिन पर्याप्त जानकारी छैन।"
        return {
            "query": query,
            "answer": not_found_message,
            "sources": [],
            "confidence_score": 0.0,
            "response_time_ms": elapsed_ms,
            "query_language": query_language,
            "retrieval_time_ms": retrieval_time,
            "generation_time_ms": 0,
            "skipped_llm": True,
            "classification": classification.label,
        }

    # Step 7: Knowledge Gap Detection
    relevance_scores = [chunk.get("score", 0.0) for chunk in retrieved_chunks]
    retrieval_assessment = knowledge_gap_detector.assess_retrieval(
        enhanced_query, retrieved_chunks, relevance_scores
    )

    if retrieval_assessment.gap_detected:
        # Create knowledge gap record
        knowledge_gap_detector.create_knowledge_gap(
            user_id=user_id,
            conversation_id=conversation_id,
            query=enhanced_query,
            retrieval_assessment=retrieval_assessment,
            retrieved_chunks=retrieved_chunks,
            relevance_scores=relevance_scores,
            detected_language=query_language,
        )

        # If gap is detected, return gap response
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        not_found_message = "The uploaded legal documents do not contain enough information to answer this question."
        if query_language == "ne":
            not_found_message = "अपलोड गरिएका कानुनी कागजातहरूमा यो प्रश्नको उत्तर दिन पर्याप्त जानकारी छैन।"
        return {
            "query": query,
            "answer": not_found_message,
            "sources": [],
            "confidence_score": retrieval_assessment.confidence_score,
            "response_time_ms": elapsed_ms,
            "query_language": query_language,
            "retrieval_time_ms": retrieval_time,
            "generation_time_ms": 0,
            "skipped_llm": True,
            "knowledge_gap_detected": True,
            "knowledge_gap_reason": retrieval_assessment.gap_reason,
            "classification": classification.label,
        }

    # Step 8: LLM Answer Generation (only if high confidence)
    generation_start = time.perf_counter()
    
    # Build context from chunks with better metadata
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks[:5], 1):
        content = chunk.get("text", "")
        metadata = chunk.get("metadata", {})
        doc_name = metadata.get("document_name", "")
        section = metadata.get("section", "")
        article = metadata.get("article", "")
        chapter = metadata.get("chapter", "")
        part = metadata.get("part", "")
        
        # Build comprehensive header
        header_parts = [f"[Source {i}"]
        if doc_name:
            header_parts.append(doc_name)
        if part:
            header_parts.append(part)
        if chapter:
            header_parts.append(chapter)
        if section:
            header_parts.append(f"Section {section}")
        if article:
            header_parts.append(f"Article {article}")
        
        header = " | ".join(header_parts) + "]"
        context_parts.append(f"{header}\n{content}")
    
    context = "\n\n".join(context_parts)
    
    try:
        answer = llm.generate(query, context, conversation_history)
    except Exception as e:
        print(f"Generation error: {e}")
        answer = f"Based on the available documents, here's what I found:\n\n{context[:500]}\n\nHowever, I encountered an issue generating a complete answer. Please try again."
    
    generation_time = int((time.perf_counter() - generation_start) * 1000)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    # Format sources
    sources = []
    for chunk in retrieved_chunks[:3]:
        metadata = chunk.get("metadata", {})
        sources.append({
            "document": metadata.get("document_name", ""),
            "section": metadata.get("section", ""),
            "article": metadata.get("article", ""),
            "score": chunk.get("score", 0.0),
        })

    return {
        "query": query,
        "answer": answer,
        "sources": sources,
        "confidence_score": retrieval_assessment.confidence_score,
        "response_time_ms": elapsed_ms,
        "query_language": query_language,
        "retrieval_time_ms": retrieval_time,
        "generation_time_ms": generation_time,
        "skipped_llm": False,
        "knowledge_gap_detected": False,
        "classification": classification.label,
    }
