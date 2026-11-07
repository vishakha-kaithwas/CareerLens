"""
Embedding Engine using Sentence Transformers.

Implements a thread-safe singleton pattern so the model (all-MiniLM-L6-v2)
is loaded exactly once in memory and reused across all requests.
Runs on CPU by default and supports configurable cosine similarity calculations.
"""

import logging
import threading
from typing import List, Optional, Union
import numpy as np

from app.core.config import settings
from app.core.errors import ModelLoadingError

logger = logging.getLogger("careerlens.embeddings")


class EmbeddingEngine:
    """Singleton service for generating dense sentence embeddings and computing cosine similarity."""

    _instance: Optional["EmbeddingEngine"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EmbeddingEngine, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        if getattr(self, "_initialized", False):
            return

        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.device = device or settings.EMBEDDING_DEVICE
        self._model = None
        self._initialized = True
        logger.info("EmbeddingEngine initialized with model=%s, device=%s", self.model_name, self.device)

    @property
    def model(self):
        """Lazy loader for SentenceTransformer model to keep startup fast."""
        if self._model is None:
            with self._lock:
                if self._model is None:
                    try:
                        from sentence_transformers import SentenceTransformer
                        logger.info("Loading SentenceTransformer model '%s' on %s...", self.model_name, self.device)
                        self._model = SentenceTransformer(self.model_name, device=self.device)
                        logger.info("SentenceTransformer model loaded successfully.")
                    except Exception as exc:
                        logger.error("Failed to load SentenceTransformer model '%s': %s", self.model_name, exc)
                        raise ModelLoadingError(
                            f"Failed to load embedding model '{self.model_name}': {str(exc)}",
                            details={"model_name": self.model_name, "error": str(exc)},
                        ) from exc
        return self._model

    def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Generates dense vector embeddings for text or list of texts.
        
        Args:
            texts: Single string or list of text strings.
            normalize: If True, vectors are L2-normalized so dot-product equals cosine similarity.
        """
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        try:
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=normalize,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            return embeddings
        except Exception as exc:
            logger.error("Failed generating embeddings: %s", exc)
            raise ModelLoadingError(
                f"Embedding generation failed: {str(exc)}",
                details={"error": str(exc)},
            ) from exc

    @staticmethod
    def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Computes cosine similarity between two 1D vectors: dot(a, b) / (||a|| * ||b||).
        Returns float clamped between 0.0 and 1.0.
        """
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        similarity = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
        return max(0.0, min(1.0, similarity))
