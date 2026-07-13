from functools import lru_cache
from typing import List

import numpy as np
from django.conf import settings
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = getattr(
    settings,
    "RAG_EMBEDDING_MODEL",
    "intfloat/multilingual-e5-base",
)


class LegalEmbeddingModel:
    """Multilingual E5 embeddings for English + Nepali legal text."""

    QUERY_PREFIX = "query: "
    PASSAGE_PREFIX = "passage: "

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or DEFAULT_MODEL
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def embed_passages(self, texts: List[str]) -> np.ndarray:
        prefixed = [f"{self.PASSAGE_PREFIX}{t}" for t in texts]
        vectors = self.model.encode(
            prefixed,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=32,
        )
        return np.asarray(vectors, dtype="float32")

    def embed_query(self, query: str) -> np.ndarray:
        prefixed = f"{self.QUERY_PREFIX}{query}"
        vector = self.model.encode(
            prefixed,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return np.asarray(vector, dtype="float32")

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        return self.embed_passages(texts)


@lru_cache(maxsize=1)
def get_embedding_model() -> LegalEmbeddingModel:
    return LegalEmbeddingModel()


# Module-level singleton (lazy-loaded)
class _EmbeddingProxy:
    def __getattr__(self, name):
        return getattr(get_embedding_model(), name)


embedding_model = _EmbeddingProxy()


def create_embedding(texts):
    model = get_embedding_model()
    if isinstance(texts, list):
        return model.embed_passages(texts)
    return model.embed_query(texts)


def create_query_embedding(query: str) -> np.ndarray:
    return get_embedding_model().embed_query(query)
