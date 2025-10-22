"""Utility functions for the privacy similarity package."""

import numpy as np
import pandas as pd
from typing import List, Optional, Union, Any


def normalize_text(text: str) -> str:
    """Normalize text for consistent processing.

    Args:
        text: Input text

    Returns:
        Normalized text
    """
    if not isinstance(text, str):
        return str(text)

    # Convert to lowercase
    text = text.lower().strip()

    # Remove extra whitespace
    text = " ".join(text.split())

    return text


def combine_vectors(
    vectors_list: List[np.ndarray],
    weights: Optional[List[float]] = None,
    method: str = "concatenate",
) -> np.ndarray:
    """Combine multiple vector representations.

    Args:
        vectors_list: List of vector arrays
        weights: Optional weights for each vector type
        method: Combination method ('concatenate', 'average', 'weighted_average')

    Returns:
        Combined vectors
    """
    if not vectors_list:
        raise ValueError("Empty vectors list")

    if method == "concatenate":
        return np.hstack(vectors_list)

    elif method == "average":
        # All vectors must have same dimension
        return np.mean(np.stack(vectors_list), axis=0)

    elif method == "weighted_average":
        if weights is None:
            weights = [1.0 / len(vectors_list)] * len(vectors_list)

        # Normalize weights
        weights = np.array(weights)
        weights = weights / weights.sum()

        # Weighted sum
        result = np.zeros_like(vectors_list[0], dtype=np.float64)
        for vec, weight in zip(vectors_list, weights):
            result += weight * vec

        return result

    else:
        raise ValueError(f"Unknown method: {method}")


def batch_iterator(data: Union[np.ndarray, pd.DataFrame], batch_size: int):
    """Iterate over data in batches.

    Args:
        data: Data to iterate over
        batch_size: Size of each batch

    Yields:
        Batches of data
    """
    n = len(data)
    for i in range(0, n, batch_size):
        yield data[i : i + batch_size]


def cosine_similarity_safe(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute cosine similarity with safe handling of zero vectors.

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Cosine similarity (-1 to 1)
    """
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return np.dot(v1, v2) / (norm1 * norm2)


def estimate_memory_usage(n_vectors: int, dimension: int, index_type: str = "HNSW") -> dict:
    """Estimate memory usage for different index types.

    Args:
        n_vectors: Number of vectors
        dimension: Vector dimensionality
        index_type: Type of index

    Returns:
        Dictionary with memory estimates in GB
    """
    # Base vector storage (float32)
    base_memory = n_vectors * dimension * 4 / (1024**3)

    if index_type == "Flat":
        total_memory = base_memory
        overhead = 1.0

    elif index_type == "HNSW":
        # HNSW has ~2-3x overhead for graph structure
        overhead = 2.5
        total_memory = base_memory * overhead

    elif index_type == "IVF-HNSW":
        # IVF adds cluster centroids, similar overhead
        overhead = 2.0
        total_memory = base_memory * overhead

    elif index_type == "IVF-PQ":
        # PQ reduces memory significantly (32-256x compression)
        compression_ratio = 64  # Typical
        overhead = 1.2
        total_memory = (base_memory / compression_ratio) * overhead

    else:
        total_memory = base_memory
        overhead = 1.0

    return {
        "base_memory_gb": base_memory,
        "total_memory_gb": total_memory,
        "overhead_ratio": overhead,
    }


def select_index_type(n_vectors: int, dimension: int) -> str:
    """Automatically select appropriate index type based on data size.

    Args:
        n_vectors: Number of vectors
        dimension: Vector dimensionality

    Returns:
        Recommended index type
    """
    if n_vectors < 10000:
        return "Flat"  # Exact search for small datasets

    elif n_vectors < 10_000_000:
        return "HNSW"  # Best accuracy/speed for medium datasets

    elif n_vectors < 1_000_000_000:
        return "IVF-HNSW"  # Balanced for large datasets

    else:
        return "IVF-PQ"  # Memory-efficient for billion-scale


def validate_dataframe(df: pd.DataFrame, required_columns: Optional[List[str]] = None) -> bool:
    """Validate DataFrame for processing.

    Args:
        df: DataFrame to validate
        required_columns: Required column names

    Returns:
        True if valid, raises ValueError otherwise
    """
    if df is None or len(df) == 0:
        raise ValueError("DataFrame is empty")

    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    return True


def merge_duplicate_groups(groups: List[List[int]]) -> List[List[int]]:
    """Merge overlapping duplicate groups.

    Args:
        groups: List of duplicate groups

    Returns:
        Merged groups
    """
    if not groups:
        return []

    # Convert to sets
    group_sets = [set(g) for g in groups]

    # Merge overlapping sets
    merged = []
    while group_sets:
        current = group_sets.pop(0)
        merged_any = True

        while merged_any:
            merged_any = False
            remaining = []

            for other in group_sets:
                if current & other:  # Overlap
                    current = current | other
                    merged_any = True
                else:
                    remaining.append(other)

            group_sets = remaining

        merged.append(sorted(list(current)))

    return merged


class ProgressTracker:
    """Simple progress tracker for batch operations."""

    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.description = description
        self.current = 0

    def update(self, n: int = 1):
        """Update progress.

        Args:
            n: Number of items processed
        """
        self.current += n
        percent = 100 * self.current / self.total
        print(f"\r{self.description}: {self.current}/{self.total} ({percent:.1f}%)", end="")

    def finish(self):
        """Mark as complete."""
        print()


def compute_statistics(values: List[float]) -> dict:
    """Compute basic statistics for a list of values.

    Args:
        values: List of numerical values

    Returns:
        Dictionary with statistics
    """
    if not values:
        return {}

    arr = np.array(values)

    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "count": len(values),
    }
