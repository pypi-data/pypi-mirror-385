"""Similarity search modules using FAISS and other backends."""

from .faiss_index import FAISSIndex
from .similarity import SimilaritySearcher

__all__ = ["FAISSIndex", "SimilaritySearcher"]
