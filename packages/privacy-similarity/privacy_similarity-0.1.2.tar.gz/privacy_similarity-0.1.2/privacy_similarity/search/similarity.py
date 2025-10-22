"""High-level similarity search interface with deduplication support."""

import numpy as np
import pandas as pd
from typing import List, Dict, Set, Tuple, Optional
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity


class SimilaritySearcher:
    """High-level similarity search with deduplication and clustering.

    Provides convenient methods for:
    - Finding similar records
    - Deduplicating datasets
    - Clustering similar items
    - Computing pairwise similarities
    """

    def __init__(self, index, id_mapping: Optional[Dict] = None):
        """Initialize similarity searcher.

        Args:
            index: FAISS index or similar
            id_mapping: Mapping from index IDs to original IDs
        """
        self.index = index
        self.id_mapping = id_mapping or {}
        self.vectors = None
        self.vector_ids = None

    def search(
        self,
        query_vectors: np.ndarray,
        k: int = 10,
        similarity_threshold: Optional[float] = None,
        return_distances: bool = True,
    ) -> List[Dict]:
        """Search for similar vectors.

        Args:
            query_vectors: Query vectors (n, d)
            k: Number of neighbors to return
            similarity_threshold: Optional threshold to filter results
            return_distances: Whether to return distance/similarity scores

        Returns:
            List of result dictionaries
        """
        # Search index
        distances, indices = self.index.search(query_vectors, k)

        # Convert to results
        results = []
        for i, (dists, idxs) in enumerate(zip(distances, indices)):
            # Filter by threshold if provided
            if similarity_threshold is not None:
                # Convert distance to similarity (assumes cosine/inner product)
                if self.index.metric == "COSINE" or self.index.metric == "IP":
                    similarities = dists
                else:  # L2 distance - convert to similarity
                    similarities = 1 / (1 + dists)

                mask = similarities >= similarity_threshold
                idxs = idxs[mask]
                dists = dists[mask]

            # Map to original IDs
            result_ids = [self.id_mapping.get(idx, idx) for idx in idxs if idx != -1]

            result = {"query_idx": i, "ids": result_ids}

            if return_distances:
                result["distances"] = dists.tolist()

            results.append(result)

        return results

    def find_duplicates(
        self, threshold: float = 0.9, k: int = 20, max_cluster_size: int = 100
    ) -> List[Dict]:
        """Find duplicate records based on similarity.

        Uses connected components to group similar items.

        Args:
            threshold: Similarity threshold for duplicates
            k: Number of neighbors to check
            max_cluster_size: Maximum size of duplicate clusters

        Returns:
            List of duplicate groups
        """
        if self.vectors is None:
            raise ValueError("Vectors not stored. Set store_vectors=True when adding.")

        # Create reverse mapping from FAISS ID to position
        # id_mapping is {position: original_id}, we need {faiss_id: position}
        reverse_mapping = {}
        for pos, original_id in self.id_mapping.items():
            # FAISS uses the IDs we gave it, which are the original IDs
            reverse_mapping[original_id] = pos

        # Search for neighbors of all vectors
        distances, indices = self.index.search(self.vectors, k + 1)

        # Build similarity graph
        edges = []
        for i, (dists, idxs) in enumerate(zip(distances, indices)):
            # Get the FAISS ID for position i
            my_faiss_id = self.id_mapping.get(i, i)

            for dist, idx in zip(dists, idxs):
                idx = int(idx)
                # Skip invalid indices
                if idx == -1 or idx < 0:
                    continue

                # Map FAISS index to position
                idx_pos = reverse_mapping.get(idx, idx)

                # Skip self-edges and out of range
                if idx_pos == i or idx_pos >= len(self.vectors):
                    continue

                # Convert to similarity
                if self.index.metric == "COSINE" or self.index.metric == "IP":
                    similarity = dist
                else:
                    similarity = 1 / (1 + dist)

                if similarity >= threshold:
                    edges.append((i, idx_pos, similarity))

        # Find connected components
        clusters = self._find_connected_components(edges, len(self.vectors))

        # Convert to duplicate groups
        duplicate_groups = []
        for cluster in clusters:
            if len(cluster) > 1 and len(cluster) <= max_cluster_size:
                # Get original IDs
                original_ids = [self.id_mapping.get(idx, idx) for idx in cluster]

                # Compute average similarity within cluster
                avg_similarity = self._compute_cluster_similarity(cluster, edges)

                duplicate_groups.append(
                    {"ids": original_ids, "size": len(original_ids), "similarity": avg_similarity}
                )

        # Sort by size (largest first)
        duplicate_groups.sort(key=lambda x: x["size"], reverse=True)

        return duplicate_groups

    def _find_connected_components(self, edges: List[Tuple], n_nodes: int) -> List[Set[int]]:
        """Find connected components in graph.

        Args:
            edges: List of (node1, node2, weight) tuples
            n_nodes: Number of nodes

        Returns:
            List of sets, each containing node IDs in a component
        """
        # Build adjacency list
        adj = [set() for _ in range(n_nodes)]
        for u, v, _ in edges:
            adj[u].add(v)
            adj[v].add(u)

        # DFS to find components
        visited = set()
        components = []

        def dfs(node, component):
            visited.add(node)
            component.add(node)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    dfs(neighbor, component)

        for node in range(n_nodes):
            if node not in visited:
                component = set()
                dfs(node, component)
                components.append(component)

        return components

    def _compute_cluster_similarity(self, cluster: Set[int], edges: List[Tuple]) -> float:
        """Compute average similarity within cluster.

        Args:
            cluster: Set of node IDs
            edges: List of edges

        Returns:
            Average similarity
        """
        similarities = []
        cluster_list = list(cluster)

        # Get all edges within cluster
        for u, v, sim in edges:
            if u in cluster and v in cluster:
                similarities.append(sim)

        if similarities:
            return float(np.mean(similarities))
        else:
            return 1.0

    def compute_pairwise_similarity(
        self,
        vectors1: np.ndarray,
        vectors2: Optional[np.ndarray] = None,
        metric: str = "cosine",
        batch_size: int = 1000,
    ) -> np.ndarray:
        """Compute pairwise similarity matrix.

        Args:
            vectors1: First set of vectors (n, d)
            vectors2: Second set of vectors (m, d). If None, use vectors1
            metric: Similarity metric ('cosine', 'euclidean')
            batch_size: Batch size for computation

        Returns:
            Similarity matrix of shape (n, m)
        """
        if vectors2 is None:
            vectors2 = vectors1

        if metric == "cosine":
            return cosine_similarity(vectors1, vectors2)
        elif metric == "euclidean":
            from sklearn.metrics.pairwise import euclidean_distances

            distances = euclidean_distances(vectors1, vectors2)
            return 1 / (1 + distances)
        else:
            raise ValueError(f"Unknown metric: {metric}")

    def cluster_similar_items(self, n_clusters: int = 10, method: str = "kmeans") -> np.ndarray:
        """Cluster similar items.

        Args:
            n_clusters: Number of clusters
            method: Clustering method ('kmeans', 'agglomerative')

        Returns:
            Cluster labels
        """
        if self.vectors is None:
            raise ValueError("Vectors not stored.")

        if method == "kmeans":
            from sklearn.cluster import KMeans

            clusterer = KMeans(n_clusters=n_clusters, random_state=42)
            return clusterer.fit_predict(self.vectors)
        elif method == "agglomerative":
            from sklearn.cluster import AgglomerativeClustering

            clusterer = AgglomerativeClustering(n_clusters=n_clusters)
            return clusterer.fit_predict(self.vectors)
        else:
            raise ValueError(f"Unknown method: {method}")

    def get_nearest_neighbors(self, vector_id: int, k: int = 10) -> Tuple[List[int], List[float]]:
        """Get k nearest neighbors of a vector by ID.

        Args:
            vector_id: ID of vector
            k: Number of neighbors

        Returns:
            neighbor_ids: List of neighbor IDs
            distances: List of distances
        """
        if self.vectors is None:
            raise ValueError("Vectors not stored.")

        # Find index
        if vector_id in self.id_mapping.values():
            # Reverse lookup
            idx = [k for k, v in self.id_mapping.items() if v == vector_id][0]
        else:
            idx = vector_id

        # Get vector
        vector = self.vectors[idx : idx + 1]

        # Search
        distances, indices = self.index.search(vector, k + 1)

        # Remove self
        mask = indices[0] != idx
        neighbor_indices = indices[0][mask][:k]
        neighbor_distances = distances[0][mask][:k]

        # Map to original IDs
        neighbor_ids = [self.id_mapping.get(nidx, nidx) for nidx in neighbor_indices]

        return neighbor_ids, neighbor_distances.tolist()

    def recommend_similar(
        self, positive_ids: List[int], negative_ids: Optional[List[int]] = None, k: int = 10
    ) -> List[Dict]:
        """Recommend similar items based on positive and negative examples.

        Args:
            positive_ids: IDs of positive examples
            negative_ids: IDs of negative examples
            k: Number of recommendations

        Returns:
            List of recommendations
        """
        if self.vectors is None:
            raise ValueError("Vectors not stored.")

        # Get vectors for positive and negative examples
        positive_vectors = []
        for pid in positive_ids:
            idx = [k for k, v in self.id_mapping.items() if v == pid][0]
            positive_vectors.append(self.vectors[idx])

        positive_vectors = np.array(positive_vectors)

        # Compute query vector as average of positives
        query_vector = np.mean(positive_vectors, axis=0, keepdims=True)

        # Subtract negatives if provided
        if negative_ids:
            negative_vectors = []
            for nid in negative_ids:
                idx = [k for k, v in self.id_mapping.items() if v == nid][0]
                negative_vectors.append(self.vectors[idx])

            negative_vectors = np.array(negative_vectors)
            negative_mean = np.mean(negative_vectors, axis=0, keepdims=True)

            # Move away from negatives
            query_vector = query_vector - 0.5 * negative_mean

        # Normalize
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm

        # Search
        results = self.search(query_vector, k=k * 2)

        # Filter out positive and negative IDs
        exclude_ids = set(positive_ids)
        if negative_ids:
            exclude_ids.update(negative_ids)

        filtered_results = []
        for result in results[0]["ids"]:
            if result not in exclude_ids:
                filtered_results.append(result)
                if len(filtered_results) >= k:
                    break

        return filtered_results

    def store_vectors(self, vectors: np.ndarray, ids: Optional[List] = None):
        """Store vectors for later use.

        Args:
            vectors: Vectors to store
            ids: Optional IDs for vectors
        """
        self.vectors = vectors
        self.vector_ids = ids if ids else list(range(len(vectors)))

        # Update ID mapping
        for i, vid in enumerate(self.vector_ids):
            self.id_mapping[i] = vid
