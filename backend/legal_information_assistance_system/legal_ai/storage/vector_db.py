import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import faiss
import numpy as np
from django.conf import settings


DEFAULT_INDEX_DIR = Path(
    getattr(settings, "FAISS_INDEX_DIR", Path(settings.BASE_DIR) / "faiss_store")
).resolve()
DEFAULT_INDEX_PATH = DEFAULT_INDEX_DIR / "legal_faiss.index"
DEFAULT_META_PATH = DEFAULT_INDEX_DIR / "legal_faiss_meta.json"


class FaissVectorStore:
    def __init__(
        self,
        index_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None,
    ):
        self.index_path = Path(index_path or DEFAULT_INDEX_PATH)
        self.metadata_path = Path(metadata_path or DEFAULT_META_PATH)
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict[str, Any]] = []

    def _ensure_store_dir(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

    def _create_index(self, dimension: int) -> faiss.IndexFlatIP:
        return faiss.IndexFlatIP(dimension)

    def load(self, dimension: Optional[int] = None) -> None:
        self._ensure_store_dir()

        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        elif dimension is not None:
            self.index = self._create_index(dimension)
        else:
            self.index = None

        if self.metadata_path.exists():
            self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        else:
            self.metadata = []

    def save(self) -> None:
        if self.index is None:
            raise RuntimeError("FAISS index has not been initialized.")

        self._ensure_store_dir()
        faiss.write_index(self.index, str(self.index_path))
        self.metadata_path.write_text(json.dumps(self.metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    def reset(self, dimension: int) -> None:
        self._ensure_store_dir()
        self.index = self._create_index(dimension)
        self.metadata = []

    def add(self, embeddings: Any, metadatas: List[Dict[str, Any]]) -> None:
        if self.index is None:
            self.load(dimension=embeddings.shape[1])

        self.index.add(embeddings)
        self.metadata.extend(metadatas)
        self.save()

    def search(self, query_vector: Any, top_k: int) -> Tuple[Any, Any]:
        if self.index is None:
            self.load()

        if self.index is None or self.index.ntotal == 0 or not self.metadata:
            return np.zeros((1, 0), dtype="float32"), np.full((1, 0), -1, dtype="int64")

        distances, indices = self.index.search(query_vector, top_k)
        return distances, indices

    def has_embeddings(self) -> bool:
        return self.index is not None and self.index.ntotal > 0 and bool(self.metadata)

    def count(self) -> int:
        return len(self.metadata)
