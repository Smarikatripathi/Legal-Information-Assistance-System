import json
from datetime import datetime, timezone
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
DEFAULT_INFO_PATH = DEFAULT_INDEX_DIR / "legal_faiss_info.json"


class FAISSService:
    """Production FAISS vector store with persistence and inspection."""

    def __init__(
        self,
        index_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None,
        info_path: Optional[Path] = None,
    ):
        self.index_path = Path(index_path or DEFAULT_INDEX_PATH)
        self.metadata_path = Path(metadata_path or DEFAULT_META_PATH)
        self.info_path = Path(info_path or DEFAULT_INFO_PATH)
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict[str, Any]] = []
        self._loaded = False

    def _ensure_store_dir(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

    def _create_index(self, dimension: int) -> faiss.IndexFlatIP:
        return faiss.IndexFlatIP(dimension)

    def load(self, dimension: Optional[int] = None) -> None:
        if self._loaded and self.index is not None:
            return

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

        self._loaded = True

    def save(self, *, model_name: str = "", dimension: int = 0) -> None:
        if self.index is None:
            raise RuntimeError("FAISS index has not been initialized.")

        self._ensure_store_dir()
        faiss.write_index(self.index, str(self.index_path))
        self.metadata_path.write_text(
            json.dumps(self.metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        info = {
            "model_name": model_name,
            "dimension": dimension or (self.index.d if self.index else 0),
            "total_vectors": self.count(),
            "last_rebuild": datetime.now(timezone.utc).isoformat(),
            "index_file_size_bytes": self.index_path.stat().st_size if self.index_path.exists() else 0,
        }
        self.info_path.write_text(json.dumps(info, indent=2), encoding="utf-8")

    def build_index(
        self,
        embeddings: np.ndarray,
        metadatas: List[Dict[str, Any]],
        *,
        model_name: str = "",
    ) -> None:
        """Build a fresh index from scratch."""
        dimension = embeddings.shape[1]
        self.index = self._create_index(dimension)
        self.metadata = []
        self.index.add(embeddings)
        self.metadata.extend(metadatas)
        self.save(model_name=model_name, dimension=dimension)
        self._loaded = True

    def reset(self, dimension: int) -> None:
        self.index = self._create_index(dimension)
        self.metadata = []
        self._loaded = True

    def add(self, embeddings: np.ndarray, metadatas: List[Dict[str, Any]], *, model_name: str = "") -> None:
        if self.index is None:
            self.load(dimension=embeddings.shape[1])
        if self.index is None:
            self.reset(embeddings.shape[1])

        self.index.add(embeddings)
        self.metadata.extend(metadatas)
        self.save(model_name=model_name, dimension=embeddings.shape[1])

    def search(self, query_vector: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray]:
        self.load()
        if self.index is None or self.index.ntotal == 0 or not self.metadata:
            return np.zeros((1, 0), dtype="float32"), np.full((1, 0), -1, dtype="int64")

        k = min(top_k, self.index.ntotal)
        return self.index.search(query_vector, k)

    def has_embeddings(self) -> bool:
        self.load()
        return self.index is not None and self.index.ntotal > 0 and bool(self.metadata)

    def count(self) -> int:
        self.load()
        return self.index.ntotal if self.index else 0

    def inspect_index(self) -> Dict[str, Any]:
        self.load()
        info: Dict[str, Any] = {
            "total_vectors": self.count(),
            "metadata_entries": len(self.metadata),
            "index_exists": self.index_path.exists(),
            "metadata_exists": self.metadata_path.exists(),
            "index_path": str(self.index_path),
            "status": "ready" if self.has_embeddings() else "empty",
        }
        if self.index is not None:
            info["dimension"] = self.index.d
        if self.info_path.exists():
            info.update(json.loads(self.info_path.read_text(encoding="utf-8")))
        if self.index_path.exists():
            info["index_file_size_bytes"] = self.index_path.stat().st_size
        return info

    def clear(self) -> None:
        """Remove index files and reset in-memory state."""
        self.index = None
        self.metadata = []
        self._loaded = False
        for path in (self.index_path, self.metadata_path, self.info_path):
            if path.exists():
                path.unlink()


# Backward-compatible alias
FaissVectorStore = FAISSService
