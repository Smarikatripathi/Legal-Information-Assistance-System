"""LangChain RAG orchestration: retrieval, prompt construction, grounded generation."""

import re
from typing import Any, Dict, List

from django.conf import settings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from legal_information_assistance_system.legal_ai.services.domain_classifier import (
    classify_query,
    get_non_legal_response,
)
from legal_information_assistance_system.legal_ai.services.langchain_retriever import LegalHybridRetriever
from legal_information_assistance_system.legal_ai.services.language import language_service
from legal_information_assistance_system.legal_ai.services.llm import llm

MIN_SCORE = getattr(settings, "RAG_MIN_SCORE", 0.35)
FINAL_TOP_K = getattr(settings, "RAG_FINAL_TOP_K", 5)

GROUNDED_SYSTEM_PROMPT = """You are a Legal Information Assistant for Nepal law.

GUIDELINES:
1. Use the provided legal context and retrieved sources as your primary source.
2. You MAY infer logical conclusions from the provided context.
3. You MAY draw logical inferences when the context provides a clear legal framework.
4. NEVER say you cannot find information if relevant context exists — use what is available.
5. If the context is genuinely insufficient for a specific question, provide the best answer possible based on what IS available, and note any limitations.
6. Do not rely on general legal knowledge outside the provided context.
7. Combine multiple relevant sources into one coherent answer.
8. Respond ONLY in {response_language} (same language as the user's question).
9. Keep answers factual, neutral, and easy to understand.
10. Never provide personal legal advice — only legal information.
11. Format the answer in Markdown:
    - Use ## headings for main sections
    - Use bullet or numbered lists where appropriate
    - Use markdown tables when comparing provisions
    - End with a ## Sources section listing citations as markdown links when URLs exist

CITATION FORMAT:
- Inline: [Source N] after each claim
- In Sources section: document name, act, chapter/section/article, and link if available

IMPORTANT:
- Never mix information from different legal documents unless explicitly required by the question.
- If the question asks about a specific document (e.g., Constitution, Civil Code), prioritize that document.
- If section/article numbers are mentioned in the question, cite those specific provisions.
- Do not hallucinate section numbers or legal provisions that are not in the provided context.
- If the context contains conflicting information, acknowledge the conflict and cite all relevant sources.

ANSWER STRUCTURE:
- Start with a direct answer: "हो।" (Yes) or "होइन।" (No) for Nepali, "Yes" or "No" for English, followed by the main point
- Provide comprehensive explanation of the legal provision
- Include specific section/article numbers when available in the context
- Explain the requirements, procedures, or conditions mentioned in the law
- Conclude with a summary of the key points
"""

USER_PROMPT = """--- LEGAL CONTEXT ---
{context}

--- USER QUESTION ---
{question}

--- ANSWER (Markdown, in {response_language} only) ---"""


def _format_context_from_docs(docs: List[Document]) -> str:
    """Format retrieved documents with clear source attribution and document separation."""
    # Deduplicate documents by chunk_id to avoid duplicate sources
    seen_chunks = set()
    unique_docs = []
    for doc in docs:
        chunk_id = doc.metadata.get("chunk_id")
        if chunk_id and chunk_id not in seen_chunks:
            seen_chunks.add(chunk_id)
            unique_docs.append(doc)
        elif not chunk_id:
            # If no chunk_id, include it anyway (fallback)
            unique_docs.append(doc)
    
    blocks = []
    for i, doc in enumerate(unique_docs, 1):
        meta = doc.metadata
        
        # Clean document name - remove artifacts like IDs
        doc_name = meta.get("document_name") or meta.get("document_title", "")
        doc_name = re.sub(r'\s+[a-z0-9]{6,}$', '', doc_name)  # Remove trailing IDs like "zpq6wk7"
        
        header_parts = [
            doc_name,
            meta.get("act_name"),
            meta.get("part"),
            meta.get("chapter"),
            meta.get("section") and f"Section {meta['section']}",
            meta.get("article") and f"Article {meta['article']}",
            meta.get("title"),
        ]
        header = " | ".join(str(p) for p in header_parts if p)
        url = meta.get("source_url") or meta.get("url")
        url_line = f"\nURL: {url}" if url else ""
        
        # Add document type and language info for better context
        doc_type = meta.get("document_type", "")
        doc_lang = meta.get("language", "")
        type_lang_info = ""
        if doc_type:
            type_lang_info += f" [{doc_type}]"
        if doc_lang:
            type_lang_info += f" [{doc_lang.upper()}]"
        
        blocks.append(f"[Source {i}] {header}{type_lang_info}{url_line}\n{doc.page_content}")
    return "\n\n".join(blocks)


def _format_sources(docs: List[Document]) -> List[Dict[str, Any]]:
    sources = []
    for doc in docs:
        meta = doc.metadata
        sources.append({
            "document": meta.get("document_name") or meta.get("document_title", ""),
            "act_name": meta.get("act_name", ""),
            "part": meta.get("part", ""),
            "chapter": meta.get("chapter", ""),
            "section": meta.get("section", "") or meta.get("dhara", ""),
            "article": meta.get("article", ""),
            "title": meta.get("title", ""),
            "url": meta.get("source_url") or meta.get("url", ""),
            "source_type": meta.get("source_type", ""),
            "score": round(float(meta.get("similarity_score", 0)), 4),
        })
    return sources


def _insufficient_retrieval_message(language: str) -> str:
    if language == "ne":
        return "म यो प्रश्नको लागि पर्याप्त कानूनी जानकारी फेला पार्न सकिन।"
    return "I couldn't find sufficient legal information to answer this question."


def run_grounded_rag(
    query: str,
    top_k: int = FINAL_TOP_K,
    *,
    min_score: float | None = None,
) -> Dict[str, Any]:
    """LangChain-orchestrated RAG: classify → retrieve → prompt → generate."""
    classification = classify_query(query)
    query_language = classification.language or language_service.detect_language(query)

    if not classification.is_legal:
        return {
            "query": query,
            "answer": get_non_legal_response(query_language),
            "sources": [],
            "confidence_score": 0.0,
            "query_language": query_language,
            "skipped_retrieval": True,
            "skipped_llm": True,
            "classification": classification.reason,
        }

    threshold = min_score if min_score is not None else MIN_SCORE
    retriever = LegalHybridRetriever(top_k=top_k, min_score=threshold)
    scored_docs = retriever.retrieve_with_scores(query)

    # Fallback: if no docs with current threshold, try with weaker threshold
    if not scored_docs:
        fallback_threshold = 0.15  # Very weak threshold for fallback
        retriever_fallback = LegalHybridRetriever(top_k=top_k, min_score=fallback_threshold)
        scored_docs = retriever_fallback.retrieve_with_scores(query)

    if not scored_docs:
        return {
            "query": query,
            "answer": _insufficient_retrieval_message(query_language),
            "sources": [],
            "confidence_score": 0.0,
            "query_language": query_language,
            "skipped_llm": True,
        }

    best_score = max(score for _, score in scored_docs)
    # Only skip LLM if even the fallback threshold wasn't met
    if best_score < 0.15:
        return {
            "query": query,
            "answer": _insufficient_retrieval_message(query_language),
            "sources": [],
            "confidence_score": round(best_score, 4),
            "query_language": query_language,
            "skipped_llm": True,
        }

    docs = [doc for doc, _ in scored_docs]
    confidence = round(sum(s for _, s in scored_docs) / len(scored_docs), 4)
    context = _format_context_from_docs(docs)

    response_lang = "Nepali" if query_language == "ne" else "English"
    prompt = ChatPromptTemplate.from_messages([
        ("system", GROUNDED_SYSTEM_PROMPT),
        ("human", USER_PROMPT),
    ])
    messages = prompt.format_messages(
        response_language=response_lang,
        context=context,
        question=query,
    )

    system_text = messages[0].content
    user_text = messages[1].content
    full_prompt = f"{system_text}\n\n{user_text}"
    try:
        answer = llm.generate_from_prompt(full_prompt, query_language=query_language)
    except Exception as exc:
        answer = (
            "Unable to generate an answer because the LLM service is unavailable. "
            f"Error: {exc}"
        )
        return {
            "query": query,
            "answer": answer,
            "sources": _format_sources(docs),
            "confidence_score": confidence,
            "query_language": query_language,
            "skipped_llm": False,
            "llm_error": str(exc),
        }

    return {
        "query": query,
        "answer": answer,
        "sources": _format_sources(docs),
        "confidence_score": confidence,
        "query_language": query_language,
        "skipped_llm": False,
    }
