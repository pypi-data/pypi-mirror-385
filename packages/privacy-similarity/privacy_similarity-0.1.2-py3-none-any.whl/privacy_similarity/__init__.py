"""Privacy-Preserving Similarity Search Package.

A comprehensive package for privacy-preserving similarity search on massive DataFrames
containing PII. Supports differential privacy, homomorphic encryption, and secure hashing.
"""

from .core import PrivacyPreservingSimilaritySearch

__version__ = "0.1.2"
__all__ = ["PrivacyPreservingSimilaritySearch"]
