"""FAISS-based vector similarity search with multiple index types.

Implements:
- HNSW: For <10M vectors, high accuracy
- IVF-HNSW: For 10M-1B vectors, balanced
- IVF-PQ: For 1B+ vectors, memory-efficient
"""

import numpy as np
from typing import Tuple, Optional, List, Dict
import warnings


class FAISSIndex:
    """FAISS index wrapper for similarity search.

    Provides a unified interface for different FAISS index types with
    automatic parameter tuning based on dataset size.

    Args:
        dimension: Dimensionality of vectors
        index_type: Type of index ('HNSW', 'IVF-HNSW', 'IVF-PQ', 'Flat')
        metric: Distance metric ('L2', 'IP' for inner product, 'cosine')
        use_gpu: Whether to use GPU acceleration
        nlist: Number of clusters for IVF (default: auto)
        M: HNSW parameter (default: 32)
        efConstruction: HNSW construction parameter (default: 200)
        efSearch: HNSW search parameter (default: 64)
        pq_m: Product Quantization parameter (default: 8)
    """

    def __init__(
        self,
        dimension: int,
        index_type: str = "HNSW",
        metric: str = "cosine",
        use_gpu: bool = False,
        nlist: Optional[int] = None,
        M: int = 32,
        efConstruction: int = 200,
        efSearch: int = 64,
        pq_m: int = 8,
    ):
        try:
            import faiss

            self.faiss = faiss
        except ImportError:
            raise ImportError(
                "faiss is required. Install with: pip install faiss-cpu "
                "or pip install faiss-gpu for GPU support"
            )

        self.dimension = dimension
        self.index_type = index_type.upper()
        self.metric = metric.upper()
        self.use_gpu = use_gpu
        self.M = M
        self.efConstruction = efConstruction
        self.efSearch = efSearch
        self.pq_m = pq_m

        # Auto-configure nlist based on expected dataset size
        self.nlist = nlist

        # Create index
        self.index = None
        self.is_trained = False
        self.num_vectors = 0

        # GPU resources
        self.gpu_resources = None
        if use_gpu:
            self._initialize_gpu()

    def _initialize_gpu(self):
        """Initialize GPU resources."""
        try:
            self.gpu_resources = self.faiss.StandardGpuResources()
        except Exception as e:
            warnings.warn(f"Failed to initialize GPU: {e}. Falling back to CPU.")
            self.use_gpu = False

    def _create_index(self, n_vectors: Optional[int] = None):
        """Create FAISS index based on configuration.

        Args:
            n_vectors: Number of vectors (for auto-tuning)
        """
        # Auto-configure parameters based on dataset size
        if n_vectors and self.nlist is None:
            if n_vectors < 10000:
                self.nlist = 100
            elif n_vectors < 1000000:
                self.nlist = int(np.sqrt(n_vectors))
            else:
                self.nlist = min(65536, int(np.sqrt(n_vectors)))

        # Determine metric
        if self.metric == "COSINE":
            # For cosine, normalize vectors and use IP
            metric = self.faiss.METRIC_INNER_PRODUCT
        elif self.metric == "IP":
            metric = self.faiss.METRIC_INNER_PRODUCT
        else:  # L2
            metric = self.faiss.METRIC_L2

        # Create index based on type
        if self.index_type == "FLAT":
            self.index = self.faiss.IndexFlat(self.dimension, metric)

        elif self.index_type == "HNSW":
            self.index = self.faiss.IndexHNSWFlat(self.dimension, self.M, metric)
            self.index.hnsw.efConstruction = self.efConstruction
            self.index.hnsw.efSearch = self.efSearch

        elif self.index_type == "IVF-HNSW":
            # Create quantizer (HNSW for better quality)
            quantizer = self.faiss.IndexHNSWFlat(self.dimension, self.M, metric)

            # Create IVF index with HNSW quantizer
            self.index = self.faiss.IndexIVFFlat(
                quantizer, self.dimension, self.nlist or 100, metric
            )

        elif self.index_type == "IVF-PQ":
            # Create quantizer
            quantizer = self.faiss.IndexFlatL2(self.dimension)

            # Create IVF-PQ index
            self.index = self.faiss.IndexIVFPQ(
                quantizer, self.dimension, self.nlist or 100, self.pq_m, 8  # 8 bits per code
            )

        else:
            raise ValueError(f"Unknown index type: {self.index_type}")

        # Move to GPU if requested
        if self.use_gpu and self.gpu_resources:
            try:
                self.index = self.faiss.index_cpu_to_gpu(self.gpu_resources, 0, self.index)
            except Exception as e:
                warnings.warn(f"Failed to move index to GPU: {e}")

    def train(self, vectors: np.ndarray):
        """Train index on vectors (required for IVF indices).

        Args:
            vectors: Training vectors of shape (n, d)
        """
        if self.index is None:
            self._create_index(len(vectors))

        # Normalize for cosine similarity
        if self.metric == "COSINE":
            vectors = self._normalize(vectors)

        # Train if needed
        if not self.index.is_trained:
            self.index.train(vectors)

        self.is_trained = True

    def add(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None):
        """Add vectors to index.

        Args:
            vectors: Vectors to add, shape (n, d)
            ids: Optional IDs for vectors (default: 0, 1, 2, ...)
        """
        if self.index is None:
            self._create_index(len(vectors))

        # Train if needed
        if not self.is_trained:
            self.train(vectors)

        # Normalize for cosine similarity
        if self.metric == "COSINE":
            vectors = self._normalize(vectors)

        # Add vectors
        if ids is not None:
            # Use IndexIDMap for custom IDs
            if not isinstance(self.index, self.faiss.IndexIDMap):
                self.index = self.faiss.IndexIDMap(self.index)
            self.index.add_with_ids(vectors, ids)
        else:
            self.index.add(vectors)

        self.num_vectors += len(vectors)

    def search(
        self, queries: np.ndarray, k: int = 10, nprobe: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search for k nearest neighbors.

        Args:
            queries: Query vectors, shape (n, d)
            k: Number of neighbors to return
            nprobe: Number of clusters to probe for IVF (default: auto)

        Returns:
            distances: Array of distances, shape (n, k)
            indices: Array of indices, shape (n, k)
        """
        if self.index is None or not self.is_trained:
            raise ValueError("Index not trained. Call train() or add() first.")

        # Set nprobe for IVF indices
        if nprobe and hasattr(self.index, "nprobe"):
            self.index.nprobe = nprobe
        elif hasattr(self.index, "nprobe"):
            # Auto-configure nprobe
            self.index.nprobe = min(self.nlist or 100, max(1, int(0.1 * (self.nlist or 100))))

        # Normalize queries for cosine similarity
        if self.metric == "COSINE":
            queries = self._normalize(queries)

        # Search
        distances, indices = self.index.search(queries, k)

        return distances, indices

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        """L2-normalize vectors for cosine similarity.

        Args:
            vectors: Input vectors

        Returns:
            Normalized vectors
        """
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return vectors / norms

    def remove(self, ids: np.ndarray):
        """Remove vectors by ID.

        Args:
            ids: IDs to remove
        """
        if isinstance(self.index, self.faiss.IndexIDMap):
            id_selector = self.faiss.IDSelectorArray(ids)
            self.index.remove_ids(id_selector)
            self.num_vectors -= len(ids)
        else:
            warnings.warn("Remove operation requires IndexIDMap")

    def reset(self):
        """Clear all vectors from index."""
        if self.index:
            self.index.reset()
        self.num_vectors = 0
        self.is_trained = False

    def save(self, filepath: str):
        """Save index to disk.

        Args:
            filepath: Path to save index
        """
        if self.index is None:
            raise ValueError("No index to save")

        # Move to CPU if on GPU
        index_to_save = self.index
        if self.use_gpu:
            index_to_save = self.faiss.index_gpu_to_cpu(self.index)

        self.faiss.write_index(index_to_save, filepath)

    def load(self, filepath: str):
        """Load index from disk.

        Args:
            filepath: Path to index file
        """
        self.index = self.faiss.read_index(filepath)
        self.is_trained = True

        # Move to GPU if requested
        if self.use_gpu and self.gpu_resources:
            self.index = self.faiss.index_cpu_to_gpu(self.gpu_resources, 0, self.index)

    def get_statistics(self) -> Dict[str, any]:
        """Get index statistics.

        Returns:
            Dictionary with statistics
        """
        stats = {
            "index_type": self.index_type,
            "dimension": self.dimension,
            "metric": self.metric,
            "num_vectors": self.num_vectors,
            "is_trained": self.is_trained,
            "use_gpu": self.use_gpu,
        }

        if self.index:
            stats["ntotal"] = self.index.ntotal

        if hasattr(self.index, "nlist"):
            stats["nlist"] = self.index.nlist

        if hasattr(self.index, "nprobe"):
            stats["nprobe"] = self.index.nprobe

        return stats

    def optimize_search_params(
        self, queries: np.ndarray, ground_truth: np.ndarray, k: int = 10, target_recall: float = 0.9
    ) -> Dict[str, int]:
        """Optimize search parameters to achieve target recall.

        Args:
            queries: Query vectors
            ground_truth: Ground truth neighbors
            k: Number of neighbors
            target_recall: Target recall (default: 0.9)

        Returns:
            Optimized parameters
        """
        if not hasattr(self.index, "nprobe"):
            return {}

        # Binary search for optimal nprobe
        best_nprobe = 1
        best_recall = 0.0

        for nprobe in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
            if nprobe > (self.nlist or 100):
                break

            self.index.nprobe = nprobe
            _, indices = self.search(queries, k)

            # Calculate recall
            recall = self._calculate_recall(indices, ground_truth, k)

            if recall >= target_recall and recall > best_recall:
                best_nprobe = nprobe
                best_recall = recall

        return {"nprobe": best_nprobe, "recall": best_recall}

    def _calculate_recall(self, retrieved: np.ndarray, ground_truth: np.ndarray, k: int) -> float:
        """Calculate recall@k.

        Args:
            retrieved: Retrieved indices
            ground_truth: Ground truth indices
            k: Number of neighbors

        Returns:
            Recall@k
        """
        recalls = []

        for ret, gt in zip(retrieved, ground_truth):
            ret_set = set(ret[:k])
            gt_set = set(gt[:k])
            recall = len(ret_set & gt_set) / len(gt_set) if len(gt_set) > 0 else 0
            recalls.append(recall)

        return np.mean(recalls)
