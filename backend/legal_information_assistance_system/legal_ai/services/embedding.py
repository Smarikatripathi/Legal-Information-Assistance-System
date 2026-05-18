import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List


class LegalEmbeddingModel:
    """
    10/10 Embedding Engine for Legal RAG System
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Lightweight + fast + good accuracy model
        """
        self.model = SentenceTransformer(model_name)

    # -----------------------------------
    # SINGLE TEXT EMBEDDING
    # -----------------------------------
    def embed(self, text: str) -> np.ndarray:
        """
        Convert single text → vector
        """
        vector = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True  # IMPORTANT for FAISS
        )
        return vector

    # -----------------------------------
    # BATCH EMBEDDING (VERY IMPORTANT)
    # -----------------------------------
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Convert multiple chunks → vectors
        """

        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return np.array(vectors, dtype="float32")

    # -----------------------------------
    # QUERY EMBEDDING (OPTIMIZED)
    # -----------------------------------
    def embed_query(self, query: str) -> np.ndarray:
        """
        Optimized for search queries
        """

        return self.embed(query).astype("float32")


# ---------------------------------------------------
# GLOBAL INSTANCE (IMPORTANT for performance)
# ---------------------------------------------------
embedding_model = LegalEmbeddingModel()


# ===================================================
# PUBLIC FUNCTIONS (USE THESE IN YOUR PIPELINE)
# ===================================================

def create_embedding(texts):
    """
    Smart wrapper:
    - if list → batch
    - if string → single
    """

    if isinstance(texts, list):
        return embedding_model.embed_batch(texts)

    return embedding_model.embed(texts)


def create_query_embedding(query: str):
    """
    Used in RAG search pipeline
    """
    return embedding_model.embed_query(query)