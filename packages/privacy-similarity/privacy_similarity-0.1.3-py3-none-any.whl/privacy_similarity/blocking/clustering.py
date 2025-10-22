"""Clustering-based blocking for candidate generation.

Implements:
- Canopy clustering for initial grouping
- K-means based blocking
- Hierarchical blocking with multiple levels
"""

import numpy as np
from typing import List, Set, Dict, Optional, Tuple
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances


class ClusteringBlocker:
    """Clustering-based blocking for similarity search.

    Groups similar vectors into clusters, reducing comparison space from
    O(N²) to O(N²/k) where k is the number of clusters.

    Args:
        n_clusters: Number of clusters
        clustering_algorithm: 'kmeans', 'minibatch_kmeans', or 'canopy'
        distance_metric: 'euclidean' or 'cosine'
    """

    def __init__(
        self,
        n_clusters: int = 100,
        clustering_algorithm: str = "kmeans",
        distance_metric: str = "euclidean",
    ):
        self.n_clusters = n_clusters
        self.clustering_algorithm = clustering_algorithm
        self.distance_metric = distance_metric

        # Initialize clusterer
        if clustering_algorithm == "kmeans":
            self.clusterer = KMeans(n_clusters=n_clusters, random_state=42)
        elif clustering_algorithm == "minibatch_kmeans":
            self.clusterer = MiniBatchKMeans(
                n_clusters=n_clusters, random_state=42, batch_size=1000
            )
        elif clustering_algorithm == "canopy":
            self.clusterer = None  # Custom implementation
        else:
            raise ValueError(f"Unknown clustering algorithm: {clustering_algorithm}")

        # Cluster assignments
        self.cluster_assignments = None
        self.cluster_to_ids = {}
        self.centroids = None
        self.fitted = False

    def fit(self, vectors: np.ndarray, ids: Optional[List[int]] = None):
        """Fit clustering model on vectors.

        Args:
            vectors: Input vectors of shape (n, d)
            ids: Optional vector IDs
        """
        if ids is None:
            ids = list(range(len(vectors)))

        if self.clustering_algorithm == "canopy":
            self._fit_canopy(vectors, ids)
        else:
            # Use sklearn clusterer
            self.clusterer.fit(vectors)
            self.cluster_assignments = self.clusterer.labels_
            self.centroids = self.clusterer.cluster_centers_

            # Build cluster to IDs mapping
            self.cluster_to_ids = {}
            for vector_id, cluster_id in zip(ids, self.cluster_assignments):
                if cluster_id not in self.cluster_to_ids:
                    self.cluster_to_ids[cluster_id] = []
                self.cluster_to_ids[cluster_id].append(vector_id)

        self.fitted = True

    def _fit_canopy(self, vectors: np.ndarray, ids: List[int]):
        """Fit using Canopy clustering.

        Args:
            vectors: Input vectors
            ids: Vector IDs
        """
        # Canopy clustering parameters
        t1 = 0.5  # Loose threshold
        t2 = 0.3  # Tight threshold

        canopies = []
        remaining_indices = set(range(len(vectors)))

        while remaining_indices:
            # Pick a random center
            center_idx = remaining_indices.pop()
            center = vectors[center_idx]

            # Find points within t1 (loose threshold)
            if self.distance_metric == "cosine":
                similarities = cosine_similarity([center], vectors)[0]
                loose_points = set(np.where(similarities >= t1)[0])
                tight_points = set(np.where(similarities >= t2)[0])
            else:  # euclidean
                distances = euclidean_distances([center], vectors)[0]
                loose_points = set(np.where(distances <= t1)[0])
                tight_points = set(np.where(distances <= t2)[0])

            # Create canopy
            canopy = {"center_idx": center_idx, "center": center, "points": loose_points}
            canopies.append(canopy)

            # Remove tight points from remaining
            remaining_indices -= tight_points

        # Assign vectors to canopies
        self.centroids = np.array([c["center"] for c in canopies])
        self.cluster_to_ids = {}

        for canopy_idx, canopy in enumerate(canopies):
            self.cluster_to_ids[canopy_idx] = [ids[idx] for idx in canopy["points"]]

        self.n_clusters = len(canopies)

    def predict_cluster(self, vector: np.ndarray) -> int:
        """Predict cluster for a single vector.

        Args:
            vector: Input vector

        Returns:
            Cluster ID
        """
        if not self.fitted:
            raise ValueError("Blocker not fitted. Call fit() first.")

        if self.clustering_algorithm == "canopy":
            # Find nearest centroid
            if self.distance_metric == "cosine":
                similarities = cosine_similarity([vector], self.centroids)[0]
                return int(np.argmax(similarities))
            else:
                distances = euclidean_distances([vector], self.centroids)[0]
                return int(np.argmin(distances))
        else:
            return int(self.clusterer.predict([vector])[0])

    def query(self, vector: np.ndarray, num_clusters: int = 1) -> Set[int]:
        """Query for candidate vectors from nearby clusters.

        Args:
            vector: Query vector
            num_clusters: Number of nearest clusters to check

        Returns:
            Set of candidate vector IDs
        """
        if not self.fitted:
            raise ValueError("Blocker not fitted. Call fit() first.")

        # Find nearest clusters
        if self.distance_metric == "cosine":
            similarities = cosine_similarity([vector], self.centroids)[0]
            nearest_clusters = np.argsort(similarities)[-num_clusters:][::-1]
        else:
            distances = euclidean_distances([vector], self.centroids)[0]
            nearest_clusters = np.argsort(distances)[:num_clusters]

        # Collect candidates from these clusters
        candidates = set()
        for cluster_id in nearest_clusters:
            if cluster_id in self.cluster_to_ids:
                candidates.update(self.cluster_to_ids[cluster_id])

        return candidates

    def query_batch(self, vectors: np.ndarray, num_clusters: int = 1) -> List[Set[int]]:
        """Query for candidates for multiple vectors.

        Args:
            vectors: Query vectors (n, d)
            num_clusters: Number of clusters to check per query

        Returns:
            List of candidate sets
        """
        return [self.query(v, num_clusters) for v in vectors]

    def get_statistics(self) -> Dict[str, float]:
        """Get clustering statistics.

        Returns:
            Dictionary with statistics
        """
        if not self.fitted:
            return {}

        cluster_sizes = [len(self.cluster_to_ids.get(i, [])) for i in range(self.n_clusters)]

        return {
            "n_clusters": self.n_clusters,
            "mean_cluster_size": np.mean(cluster_sizes),
            "max_cluster_size": np.max(cluster_sizes),
            "min_cluster_size": np.min(cluster_sizes),
            "std_cluster_size": np.std(cluster_sizes),
        }


class HierarchicalBlocker:
    """Hierarchical blocking with multiple levels.

    Creates a hierarchy of blocks at different granularities,
    enabling flexible precision-recall trade-offs.
    """

    def __init__(self, n_levels: int = 3, clusters_per_level: Optional[List[int]] = None):
        """Initialize hierarchical blocker.

        Args:
            n_levels: Number of hierarchy levels
            clusters_per_level: Number of clusters at each level
        """
        self.n_levels = n_levels

        if clusters_per_level is None:
            # Exponentially increasing clusters
            clusters_per_level = [10 * (2**i) for i in range(n_levels)]

        self.clusters_per_level = clusters_per_level
        self.blockers = []
        self.fitted = False

    def fit(self, vectors: np.ndarray, ids: Optional[List[int]] = None):
        """Fit hierarchical blocking.

        Args:
            vectors: Input vectors (n, d)
            ids: Optional vector IDs
        """
        if ids is None:
            ids = list(range(len(vectors)))

        # Fit blocker at each level
        self.blockers = []
        for n_clusters in self.clusters_per_level:
            blocker = ClusteringBlocker(
                n_clusters=min(n_clusters, len(vectors)), clustering_algorithm="minibatch_kmeans"
            )
            blocker.fit(vectors, ids)
            self.blockers.append(blocker)

        self.fitted = True

    def query(self, vector: np.ndarray, level: int = 0, num_clusters: int = 1) -> Set[int]:
        """Query at a specific hierarchy level.

        Args:
            vector: Query vector
            level: Hierarchy level (0 = coarsest, n_levels-1 = finest)
            num_clusters: Number of clusters to check

        Returns:
            Set of candidate IDs
        """
        if not self.fitted:
            raise ValueError("Blocker not fitted. Call fit() first.")

        if level < 0 or level >= self.n_levels:
            raise ValueError(f"Level must be in [0, {self.n_levels-1}]")

        return self.blockers[level].query(vector, num_clusters)

    def query_progressive(self, vector: np.ndarray, max_candidates: int = 1000) -> Set[int]:
        """Progressive query starting from coarse level.

        Progressively refines by querying finer levels until
        enough candidates are found.

        Args:
            vector: Query vector
            max_candidates: Maximum number of candidates

        Returns:
            Set of candidate IDs
        """
        candidates = set()

        for level in range(self.n_levels):
            # Query current level
            num_clusters = 1
            while len(candidates) < max_candidates and num_clusters <= 10:
                level_candidates = self.query(vector, level, num_clusters)
                candidates.update(level_candidates)
                num_clusters += 1

                if len(candidates) >= max_candidates:
                    break

            if len(candidates) >= max_candidates:
                break

        return candidates

    def query_multiresolution(
        self, vector: np.ndarray, clusters_per_level: Optional[List[int]] = None
    ) -> Set[int]:
        """Query all levels and combine results.

        Args:
            vector: Query vector
            clusters_per_level: Number of clusters to check at each level

        Returns:
            Combined set of candidates
        """
        if clusters_per_level is None:
            # Default: more clusters at coarser levels
            clusters_per_level = list(range(self.n_levels, 0, -1))

        candidates = set()

        for level, num_clusters in enumerate(clusters_per_level):
            if level < self.n_levels:
                level_candidates = self.query(vector, level, num_clusters)
                candidates.update(level_candidates)

        return candidates
