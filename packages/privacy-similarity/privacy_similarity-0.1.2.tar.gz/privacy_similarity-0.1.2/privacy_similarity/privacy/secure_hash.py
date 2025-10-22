"""Secure hashing mechanisms for privacy-preserving data transformation.

Implements salted hashing, Bloom filters, and k-anonymity techniques
for protecting PII while maintaining similarity search capabilities.
"""

import numpy as np
import hashlib
import hmac
from typing import List, Set, Optional, Union
import mmh3


class SecureHash:
    """Secure hashing for sensitive data transformation.

    Implements multiple hashing strategies:
    - Salted SHA-256 for deterministic anonymization
    - Bloom filters for multi-attribute encoding
    - k-anonymity through generalization

    Args:
        salt: Random salt for hashing (keep secret!)
        hash_algorithm: Hash algorithm to use ('sha256', 'sha512', 'blake2b')
        use_hmac: Whether to use HMAC for additional security
    """

    def __init__(
        self, salt: Optional[str] = None, hash_algorithm: str = "sha256", use_hmac: bool = True
    ):
        if salt is None:
            # Generate random salt
            import secrets

            salt = secrets.token_hex(32)

        self.salt = salt.encode("utf-8") if isinstance(salt, str) else salt
        self.hash_algorithm = hash_algorithm
        self.use_hmac = use_hmac

    def hash_value(self, value: str) -> str:
        """Hash a single value with salt.

        Args:
            value: String value to hash

        Returns:
            Hexadecimal hash string
        """
        if self.use_hmac:
            return hmac.new(self.salt, value.encode("utf-8"), hashlib.sha256).hexdigest()
        else:
            h = hashlib.new(self.hash_algorithm)
            h.update(self.salt)
            h.update(value.encode("utf-8"))
            return h.hexdigest()

    def hash_vector(self, values: List[str]) -> np.ndarray:
        """Hash a list of values into a numerical vector.

        Uses feature hashing to create a fixed-size vector representation.

        Args:
            values: List of string values

        Returns:
            Numerical vector of fixed size
        """
        # Use feature hashing with 128 dimensions
        vector_size = 128
        vector = np.zeros(vector_size, dtype=np.float32)

        for value in values:
            # Hash to get index
            idx = mmh3.hash(value + self.salt.decode("utf-8")) % vector_size
            # Hash to get sign
            sign = 1 if mmh3.hash(value, seed=1) % 2 == 0 else -1
            vector[idx] += sign

        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector

    def create_bloom_filter(
        self, values: List[str], filter_size: int = 1024, num_hashes: int = 7
    ) -> np.ndarray:
        """Create a Bloom filter for a set of values.

        Bloom filters enable privacy-preserving set membership testing
        and approximate Jaccard similarity computation.

        Args:
            values: List of values to insert
            filter_size: Size of Bloom filter bit array
            num_hashes: Number of hash functions

        Returns:
            Bloom filter as binary vector
        """
        bloom = np.zeros(filter_size, dtype=np.int8)

        for value in values:
            for i in range(num_hashes):
                # Use different hash functions (different seeds)
                idx = mmh3.hash(value + self.salt.decode("utf-8"), seed=i) % filter_size
                bloom[idx] = 1

        return bloom

    def jaccard_similarity_bloom(self, bloom1: np.ndarray, bloom2: np.ndarray) -> float:
        """Estimate Jaccard similarity from Bloom filters.

        Args:
            bloom1: First Bloom filter
            bloom2: Second Bloom filter

        Returns:
            Estimated Jaccard similarity (0-1)
        """
        intersection = np.sum(np.logical_and(bloom1, bloom2))
        union = np.sum(np.logical_or(bloom1, bloom2))

        if union == 0:
            return 0.0

        return intersection / union


class KAnonymity:
    """K-anonymity through generalization and suppression.

    Ensures each record is indistinguishable from at least k-1 other records
    by generalizing quasi-identifiers.
    """

    def __init__(self, k: int = 5):
        if k < 2:
            raise ValueError("k must be at least 2")
        self.k = k

    def generalize_numeric(self, values: np.ndarray, num_bins: Optional[int] = None) -> np.ndarray:
        """Generalize numerical values into bins.

        Args:
            values: Numerical values to generalize
            num_bins: Number of bins (default: len(values) // k)

        Returns:
            Generalized bin indices
        """
        if num_bins is None:
            num_bins = max(1, len(values) // self.k)

        # Create bins
        bins = np.linspace(values.min(), values.max(), num_bins + 1)
        generalized = np.digitize(values, bins) - 1

        return generalized

    def generalize_categorical(
        self, values: List[str], hierarchy: Optional[dict] = None
    ) -> List[str]:
        """Generalize categorical values using hierarchy.

        Args:
            values: Categorical values
            hierarchy: Generalization hierarchy (value -> parent)

        Returns:
            Generalized values
        """
        if hierarchy is None:
            # Simple suppression if no hierarchy provided
            from collections import Counter

            counts = Counter(values)

            # Suppress rare values
            generalized = [v if counts[v] >= self.k else "*" for v in values]
            return generalized

        # Use hierarchy for generalization
        generalized = []
        for value in values:
            if value in hierarchy:
                generalized.append(hierarchy[value])
            else:
                generalized.append(value)

        return generalized

    def suppress_rare_values(self, values: List[str], suppression_char: str = "*") -> List[str]:
        """Suppress values that appear fewer than k times.

        Args:
            values: List of values
            suppression_char: Character to use for suppression

        Returns:
            Values with rare items suppressed
        """
        from collections import Counter

        counts = Counter(values)

        return [v if counts[v] >= self.k else suppression_char for v in values]


class LocalitySensitiveHash:
    """Locality-Sensitive Hashing for approximate similarity search.

    LSH maps similar items to the same buckets with high probability,
    enabling efficient candidate generation for similarity search.
    """

    def __init__(self, dimension: int, num_tables: int = 10, hash_size: int = 8):
        """Initialize LSH.

        Args:
            dimension: Dimensionality of input vectors
            num_tables: Number of hash tables (more = higher recall)
            hash_size: Number of hash bits per table (more = higher precision)
        """
        self.dimension = dimension
        self.num_tables = num_tables
        self.hash_size = hash_size

        # Generate random hyperplanes for each hash table
        self.hyperplanes = [np.random.randn(hash_size, dimension) for _ in range(num_tables)]

    def hash_vector(self, vector: np.ndarray) -> List[str]:
        """Hash a vector into LSH buckets.

        Args:
            vector: Input vector of shape (d,)

        Returns:
            List of hash strings (one per table)
        """
        hashes = []

        for hyperplanes in self.hyperplanes:
            # Compute dot products
            projections = np.dot(hyperplanes, vector)

            # Convert to binary hash
            binary = (projections >= 0).astype(int)

            # Convert to string
            hash_str = "".join(map(str, binary))
            hashes.append(hash_str)

        return hashes

    def hash_batch(self, vectors: np.ndarray) -> List[List[str]]:
        """Hash a batch of vectors.

        Args:
            vectors: Input vectors of shape (n, d)

        Returns:
            List of hash lists (one per vector)
        """
        return [self.hash_vector(v) for v in vectors]

    def build_index(self, vectors: np.ndarray) -> dict:
        """Build LSH index from vectors.

        Args:
            vectors: Input vectors of shape (n, d)

        Returns:
            Hash tables mapping hash strings to vector indices
        """
        tables = [{} for _ in range(self.num_tables)]

        for idx, vector in enumerate(vectors):
            hashes = self.hash_vector(vector)

            for table_idx, hash_str in enumerate(hashes):
                if hash_str not in tables[table_idx]:
                    tables[table_idx][hash_str] = []
                tables[table_idx][hash_str].append(idx)

        return tables

    def query(self, vector: np.ndarray, tables: dict) -> Set[int]:
        """Query LSH index for candidate matches.

        Args:
            vector: Query vector
            tables: LSH hash tables from build_index()

        Returns:
            Set of candidate vector indices
        """
        hashes = self.hash_vector(vector)
        candidates = set()

        for table_idx, hash_str in enumerate(hashes):
            if hash_str in tables[table_idx]:
                candidates.update(tables[table_idx][hash_str])

        return candidates
