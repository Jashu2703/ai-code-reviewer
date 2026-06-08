import os
import numpy as np
import faiss
import json
from typing import List, Dict, Any, Optional
from loguru import logger
from app.core.config import settings

# Global embedding model
_model = None


def get_embedding_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading code embedding model...")
            _model = SentenceTransformer("microsoft/codebert-base", trust_remote_code=True)
            logger.info("CodeBERT loaded successfully")
        except Exception as e:
            logger.warning(f"CodeBERT failed: {e}. Falling back to MiniLM.")
            try:
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("MiniLM fallback loaded")
            except Exception as e2:
                logger.error(f"All embedding models failed: {e2}")
                _model = None
    return _model


def embed_code(text: str) -> List[float]:
    """Generate embedding for code snippet."""
    model = get_embedding_model()
    if model is None:
        import hashlib
        seed = int(hashlib.md5(text[:100].encode()).hexdigest(), 16) % (2**32)
        rng = np.random.RandomState(seed)
        vec = rng.rand(768).astype(float)
        return list(vec / np.linalg.norm(vec))
    try:
        embedding = model.encode(text[:512], show_progress_bar=False)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return list(np.zeros(768).astype(float))


def get_embedding_dim() -> int:
    return 768


class FAISSCodeStore:
    """FAISS vector store for code snippets and issues."""

    def __init__(self, index_path: Optional[str] = None):
        self.index_path = index_path or settings.FAISS_INDEX_PATH
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        self.dim = get_embedding_dim()
        self._load_or_create()

    def _load_or_create(self):
        index_file = os.path.join(self.index_path, "code_index.faiss")
        meta_file = os.path.join(self.index_path, "code_meta.json")
        os.makedirs(self.index_path, exist_ok=True)

        if os.path.exists(index_file) and os.path.exists(meta_file):
            try:
                self.index = faiss.read_index(index_file)
                with open(meta_file, "r") as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
                return
            except Exception as e:
                logger.warning(f"Could not load FAISS index: {e}")

        self.index = faiss.IndexFlatL2(self.dim)
        self.metadata = []
        logger.info("Created new FAISS index")

    def _save(self):
        try:
            os.makedirs(self.index_path, exist_ok=True)
            faiss.write_index(self.index, os.path.join(self.index_path, "code_index.faiss"))
            with open(os.path.join(self.index_path, "code_meta.json"), "w") as f:
                json.dump(self.metadata, f)
        except Exception as e:
            logger.error(f"Could not save FAISS index: {e}")

    def add_code_snippet(self, code: str, metadata: Dict[str, Any]):
        """Add code snippet with metadata to vector store."""
        embedding = embed_code(code)
        vector = np.array([embedding], dtype=np.float32)
        self.index.add(vector)
        self.metadata.append({**metadata, "code_preview": code[:200]})
        self._save()

    def search_similar(self, code: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar code snippets/issues from history."""
        if self.index.ntotal == 0:
            return []
        embedding = embed_code(code)
        vector = np.array([embedding], dtype=np.float32)
        distances, indices = self.index.search(vector, min(top_k, self.index.ntotal))
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0 and idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result["similarity_score"] = float(1 / (1 + dist))
                results.append(result)
        return results

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "index_path": self.index_path,
            "embedding_model": "CodeBERT / MiniLM fallback",
        }


# Global FAISS store instance
_faiss_store = None


def get_faiss_store() -> FAISSCodeStore:
    global _faiss_store
    if _faiss_store is None:
        _faiss_store = FAISSCodeStore()
    return _faiss_store
