"""Locality-Sensitive Hashing (LSH) for blocking and candidate generation.

Implements:
- Random Projection LSH (for cosine similarity)
- MinHash LSH (for Jaccard similarity)
- DB-LSH (Dynamic Bucketing LSH) for improved efficiency
"""

import numpy as np
from typing import List, Set, Dict, Tuple, Optional
import mmh3
from collections import defaultdict


class LSHBlocker:
    """Locality-Sensitive Hashing for blocking.

    Maps similar vectors to the same hash buckets with high probability,
    reducing the O(N²) comparison problem to O(N^ρ) where ρ < 1.

    Args:
        dimension: Dimensionality of input vectors
        num_tables: Number of hash tables (more = higher recall)
        hash_size: Hash size per table (more = higher precision)
        lsh_type: Type of LSH ('random_projection', 'minhash')
    """

    def __init__(
        self,
        dimension: int,
        num_tables: int = 10,
        hash_size: int = 8,
        lsh_type: str = "random_projection",
    ):
        self.dimension = dimension
        self.num_tables = num_tables
        self.hash_size = hash_size
        self.lsh_type = lsh_type

        # Initialize hash tables
        self.hash_tables = [defaultdict(list) for _ in range(num_tables)]

        # Generate random projections for random_projection LSH
        if lsh_type == "random_projection":
            self.hyperplanes = [np.random.randn(hash_size, dimension) for _ in range(num_tables)]
        else:
            self.hyperplanes = None

        # Statistics
        self.num_indexed = 0
        self.collision_stats = defaultdict(int)

    def hash_vector(self, vector: np.ndarray, table_idx: int) -> str:
        """Hash a single vector for a specific table.

        Args:
            vector: Input vector of shape (d,)
            table_idx: Index of hash table to use

        Returns:
            Hash string
        """
        if self.lsh_type == "random_projection":
            return self._hash_random_projection(vector, table_idx)
        elif self.lsh_type == "minhash":
            return self._hash_minhash(vector, table_idx)
        else:
            raise ValueError(f"Unknown LSH type: {self.lsh_type}")

    def _hash_random_projection(self, vector: np.ndarray, table_idx: int) -> str:
        """Hash using random projection (for cosine similarity).

        Args:
            vector: Input vector
            table_idx: Table index

        Returns:
            Binary hash string
        """
        # Compute dot products with random hyperplanes
        projections = np.dot(self.hyperplanes[table_idx], vector)

        # Convert to binary
        binary = (projections >= 0).astype(int)

        # Convert to string
        return "".join(map(str, binary))

    def _hash_minhash(self, vector: np.ndarray, table_idx: int) -> str:
        """Hash using MinHash (for Jaccard similarity).

        Assumes vector is a binary indicator or token counts.

        Args:
            vector: Input vector
            table_idx: Table index

        Returns:
            MinHash signature as string
        """
        # Get non-zero indices (active features)
        active_indices = np.where(vector > 0)[0]

        if len(active_indices) == 0:
            return "empty"

        # Compute min hash for multiple hash functions
        min_hashes = []
        for i in range(self.hash_size):
            min_hash = min(
                mmh3.hash(f"{idx}", seed=table_idx * self.hash_size + i) for idx in active_indices
            )
            min_hashes.append(min_hash % 1000)  # Keep reasonably small

        return "-".join(map(str, min_hashes))

    def index_vectors(self, vectors: np.ndarray, ids: Optional[List[int]] = None):
        """Build LSH index from vectors.

        Args:
            vectors: Input vectors of shape (n, d)
            ids: Optional IDs for vectors (default: 0, 1, 2, ...)
        """
        if ids is None:
            ids = list(range(len(vectors)))

        # Clear existing index
        self.hash_tables = [defaultdict(list) for _ in range(self.num_tables)]

        # Index each vector
        for vector_id, vector in zip(ids, vectors):
            for table_idx in range(self.num_tables):
                hash_val = self.hash_vector(vector, table_idx)
                self.hash_tables[table_idx][hash_val].append(vector_id)

                # Track collision statistics
                bucket_size = len(self.hash_tables[table_idx][hash_val])
                self.collision_stats[bucket_size] += 1

        self.num_indexed = len(vectors)

    def query(self, vector: np.ndarray, k: Optional[int] = None) -> Set[int]:
        """Query LSH index for candidate matches.

        Args:
            vector: Query vector
            k: Optional limit on number of candidates

        Returns:
            Set of candidate vector IDs
        """
        candidates = set()

        # Query each hash table
        for table_idx in range(self.num_tables):
            hash_val = self.hash_vector(vector, table_idx)

            if hash_val in self.hash_tables[table_idx]:
                candidates.update(self.hash_tables[table_idx][hash_val])

        # Limit candidates if requested
        if k is not None and len(candidates) > k:
            candidates = set(list(candidates)[:k])

        return candidates

    def query_batch(self, vectors: np.ndarray, k: Optional[int] = None) -> List[Set[int]]:
        """Query multiple vectors.

        Args:
            vectors: Query vectors of shape (n, d)
            k: Optional limit on candidates per query

        Returns:
            List of candidate sets
        """
        return [self.query(v, k) for v in vectors]

    def get_bucket_statistics(self) -> Dict[str, float]:
        """Get statistics about hash bucket sizes.

        Returns:
            Dictionary with statistics
        """
        all_bucket_sizes = []

        for table in self.hash_tables:
            bucket_sizes = [len(bucket) for bucket in table.values()]
            all_bucket_sizes.extend(bucket_sizes)

        if not all_bucket_sizes:
            return {
                "mean_bucket_size": 0.0,
                "max_bucket_size": 0,
                "num_buckets": 0,
                "empty_buckets": 0,
            }

        return {
            "mean_bucket_size": np.mean(all_bucket_sizes),
            "max_bucket_size": np.max(all_bucket_sizes),
            "median_bucket_size": np.median(all_bucket_sizes),
            "num_buckets": len(all_bucket_sizes),
            "num_indexed": self.num_indexed,
        }

    def estimate_recall(self, similarity_threshold: float = 0.8) -> float:
        """Estimate recall for a given similarity threshold.

        Based on LSH theory for cosine similarity.

        Args:
            similarity_threshold: Minimum cosine similarity

        Returns:
            Estimated recall (0-1)
        """
        if self.lsh_type != "random_projection":
            return -1.0  # Unknown for other LSH types

        # For random projection LSH with cosine similarity:
        # P(hash match) = 1 - arccos(similarity) / π
        # Recall with L tables = 1 - (1 - P^k)^L
        # where k = hash_size, L = num_tables

        p = 1 - np.arccos(similarity_threshold) / np.pi
        recall = 1 - (1 - p**self.hash_size) ** self.num_tables

        return recall


class DynamicBucketingLSH:
    """Dynamic Bucketing LSH (DB-LSH) for improved efficiency.

    Based on "Dynamic Bucketing LSH" paper that achieves better
    query cost: O(n^ρ* d log n) where ρ* ≤ 1/c^α

    Uses multi-dimensional indexing instead of fixed-width buckets.
    """

    def __init__(self, dimension: int, num_projections: int = 16, bucket_width: float = 0.1):
        """Initialize DB-LSH.

        Args:
            dimension: Input vector dimensionality
            num_projections: Number of random projections
            bucket_width: Width of buckets in projected space
        """
        self.dimension = dimension
        self.num_projections = num_projections
        self.bucket_width = bucket_width

        # Generate random projection matrix
        self.projection_matrix = np.random.randn(num_projections, dimension)

        # Multi-dimensional index structure
        self.index = defaultdict(list)
        self.projected_vectors = []
        self.vector_ids = []

    def _project_vector(self, vector: np.ndarray) -> np.ndarray:
        """Project vector to lower-dimensional space.

        Args:
            vector: Input vector

        Returns:
            Projected vector
        """
        return np.dot(self.projection_matrix, vector)

    def _get_bucket_key(self, projected: np.ndarray) -> Tuple[int, ...]:
        """Get bucket key for projected vector.

        Args:
            projected: Projected vector

        Returns:
            Bucket key (tuple of integers)
        """
        # Discretize each dimension
        bucket_coords = tuple(int(val / self.bucket_width) for val in projected)
        return bucket_coords

    def index_vectors(self, vectors: np.ndarray, ids: Optional[List[int]] = None):
        """Build DB-LSH index.

        Args:
            vectors: Input vectors (n, d)
            ids: Optional vector IDs
        """
        if ids is None:
            ids = list(range(len(vectors)))

        self.index.clear()
        self.projected_vectors = []
        self.vector_ids = []

        for vector_id, vector in zip(ids, vectors):
            # Project vector
            projected = self._project_vector(vector)
            self.projected_vectors.append(projected)
            self.vector_ids.append(vector_id)

            # Get bucket and insert
            bucket_key = self._get_bucket_key(projected)
            self.index[bucket_key].append(len(self.projected_vectors) - 1)

    def query(self, vector: np.ndarray, radius: float = 1.0) -> Set[int]:
        """Query DB-LSH with dynamic bucket construction.

        Args:
            vector: Query vector
            radius: Search radius in projected space

        Returns:
            Set of candidate vector IDs
        """
        # Project query
        projected = self._project_vector(vector)
        base_bucket = self._get_bucket_key(projected)

        # Determine neighboring buckets to check
        radius_buckets = int(np.ceil(radius / self.bucket_width))

        candidates = set()

        # Check buckets within radius
        for offset in self._get_bucket_offsets(radius_buckets):
            neighbor_bucket = tuple(base_bucket[i] + offset[i] for i in range(len(base_bucket)))

            if neighbor_bucket in self.index:
                for idx in self.index[neighbor_bucket]:
                    candidates.add(self.vector_ids[idx])

        return candidates

    def _get_bucket_offsets(self, radius: int) -> List[Tuple[int, ...]]:
        """Get all bucket offsets within radius.

        Args:
            radius: Radius in buckets

        Returns:
            List of offset tuples
        """
        # For simplicity, check all buckets in hypercube
        # More sophisticated version would check L2 ball

        offsets = []
        ranges = [range(-radius, radius + 1) for _ in range(self.num_projections)]

        # Generate all combinations (warning: exponential in num_projections)
        # In practice, limit to first few dimensions or use pruning
        max_offsets = 1000  # Limit to prevent explosion

        from itertools import product

        for offset in product(*ranges[: min(4, self.num_projections)]):
            # Pad with zeros if needed
            full_offset = offset + (0,) * (self.num_projections - len(offset))
            offsets.append(full_offset)

            if len(offsets) >= max_offsets:
                break

        return offsets
