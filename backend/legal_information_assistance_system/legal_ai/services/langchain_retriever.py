"""LangChain retriever backed by the existing FAISS + hybrid search pipeline."""

from typing import Any, List

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field


class LegalHybridRetriever(BaseRetriever):
    """Wrap hybrid FAISS retrieval and expose similarity scores in metadata."""

    top_k: int = Field(default=5)
    min_score: float | None = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun | None = None,
    ) -> List[Document]:
        from legal_information_assistance_system.legal_ai.services.retrieval import search

        hits = search(query, top_k=self.top_k, min_score=self.min_score)
        documents: List[Document] = []
        for hit in hits:
            page_content = hit.get("text", "")
            metadata = {k: v for k, v in hit.items() if k != "text"}
            metadata["similarity_score"] = hit.get("score", 0.0)
            documents.append(Document(page_content=page_content, metadata=metadata))
        return documents

    def retrieve_with_scores(self, query: str) -> List[tuple[Document, float]]:
        from legal_information_assistance_system.legal_ai.services.retrieval import search

        hits = search(query, top_k=self.top_k, min_score=self.min_score)
        results: List[tuple[Document, float]] = []
        for hit in hits:
            metadata = {k: v for k, v in hit.items() if k != "text"}
            score = float(hit.get("score", 0.0))
            metadata["similarity_score"] = score
            doc = Document(page_content=hit.get("text", ""), metadata=metadata)
            results.append((doc, score))
        return results
