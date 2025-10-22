"""Comprehensive tests for search modules."""

import unittest
import numpy as np
import tempfile
import os
from privacy_similarity.search.similarity import SimilaritySearcher


class TestSimilaritySearcherMock(unittest.TestCase):
    """Test SimilaritySearcher with mock index."""

    class MockIndex:
        """Mock FAISS index for testing."""

        def __init__(self):
            self.metric = "COSINE"
            self.vectors = None

        def search(self, queries, k):
            """Mock search returning dummy results."""
            n_queries = len(queries)
            # Return mock distances and indices
            distances = np.random.rand(n_queries, k)
            indices = np.tile(np.arange(k), (n_queries, 1))
            return distances, indices

    def test_initialization(self):
        """Test searcher initialization."""
        mock_index = self.MockIndex()
        searcher = SimilaritySearcher(mock_index)

        self.assertIsNotNone(searcher.index)
        self.assertEqual(searcher.id_mapping, {})

    def test_search_basic(self):
        """Test basic search."""
        mock_index = self.MockIndex()
        searcher = SimilaritySearcher(mock_index)

        queries = np.random.randn(3, 10)
        results = searcher.search(queries, k=5)

        self.assertEqual(len(results), 3)
        self.assertEqual(len(results[0]["ids"]), 5)

    def test_search_with_threshold(self):
        """Test search with similarity threshold."""
        mock_index = self.MockIndex()
        searcher = SimilaritySearcher(mock_index)

        queries = np.random.randn(2, 10)
        results = searcher.search(queries, k=10, similarity_threshold=0.8)

        self.assertEqual(len(results), 2)

    def test_store_vectors(self):
        """Test storing vectors."""
        mock_index = self.MockIndex()
        searcher = SimilaritySearcher(mock_index)

        vectors = np.random.randn(50, 10)
        ids = list(range(50))

        searcher.store_vectors(vectors, ids)

        self.assertEqual(len(searcher.vectors), 50)
        self.assertEqual(len(searcher.vector_ids), 50)

    def test_find_duplicates_requires_vectors(self):
        """Test that find_duplicates requires stored vectors."""
        mock_index = self.MockIndex()
        searcher = SimilaritySearcher(mock_index)

        with self.assertRaises(ValueError):
            searcher.find_duplicates()

    def test_compute_pairwise_similarity_cosine(self):
        """Test pairwise cosine similarity."""
        mock_index = self.MockIndex()
        searcher = SimilaritySearcher(mock_index)

        v1 = np.array([[1, 0], [0, 1]])
        v2 = np.array([[1, 0], [0, 1]])

        similarity = searcher.compute_pairwise_similarity(v1, v2, metric="cosine")

        self.assertEqual(similarity.shape, (2, 2))
        # Diagonal should be 1 (same vectors)
        np.testing.assert_almost_equal(similarity[0, 0], 1.0, decimal=5)

    def test_compute_pairwise_similarity_euclidean(self):
        """Test pairwise Euclidean similarity."""
        mock_index = self.MockIndex()
        searcher = SimilaritySearcher(mock_index)

        v1 = np.random.randn(5, 10)
        v2 = np.random.randn(3, 10)

        similarity = searcher.compute_pairwise_similarity(v1, v2, metric="euclidean")

        self.assertEqual(similarity.shape, (5, 3))

    def test_cluster_similar_items_kmeans(self):
        """Test clustering with k-means."""
        mock_index = self.MockIndex()
        searcher = SimilaritySearcher(mock_index)

        vectors = np.random.randn(100, 10)
        searcher.store_vectors(vectors)

        labels = searcher.cluster_similar_items(n_clusters=5, method="kmeans")

        self.assertEqual(len(labels), 100)
        # Should have 5 clusters
        self.assertLessEqual(len(np.unique(labels)), 5)

    def test_cluster_similar_items_agglomerative(self):
        """Test clustering with agglomerative."""
        mock_index = self.MockIndex()
        searcher = SimilaritySearcher(mock_index)

        vectors = np.random.randn(50, 10)
        searcher.store_vectors(vectors)

        labels = searcher.cluster_similar_items(n_clusters=3, method="agglomerative")

        self.assertEqual(len(labels), 50)


class TestSimilaritySearcherDuplicates(unittest.TestCase):
    """Test duplicate detection functionality."""

    class MockIndex:
        """Mock index that returns specific neighbors."""

        def __init__(self, neighbors_map):
            self.neighbors_map = neighbors_map
            self.metric = "COSINE"

        def search(self, queries, k):
            n = len(queries)
            distances = []
            indices = []

            for i in range(n):
                if i in self.neighbors_map:
                    neighs = self.neighbors_map[i][:k]
                else:
                    neighs = [i]  # Return self

                # High similarity for neighbors
                dists = [0.9] * len(neighs)

                indices.append(neighs)
                distances.append(dists)

            # Pad to k
            max_len = max(len(ind) for ind in indices)
            for i in range(len(indices)):
                while len(indices[i]) < max_len:
                    indices[i].append(-1)
                    distances[i].append(0.0)

            return np.array(distances), np.array(indices)

    def test_find_duplicates_simple(self):
        """Test finding simple duplicates."""
        # Create mock where 0,1,2 are duplicates and 3,4 are duplicates
        neighbors_map = {
            0: [0, 1, 2],
            1: [1, 0, 2],
            2: [2, 0, 1],
            3: [3, 4],
            4: [4, 3],
            5: [5],  # No duplicates
        }

        mock_index = self.MockIndex(neighbors_map)
        searcher = SimilaritySearcher(mock_index, {i: i for i in range(6)})

        # Create dummy vectors
        vectors = np.random.randn(6, 10)
        searcher.store_vectors(vectors, list(range(6)))

        duplicates = searcher.find_duplicates(threshold=0.85, k=5)

        # Should find at least 2 duplicate groups
        self.assertGreaterEqual(len(duplicates), 2)


class TestConnectedComponents(unittest.TestCase):
    """Test connected components algorithm."""

    def test_find_connected_components_simple(self):
        """Test finding connected components."""
        from privacy_similarity.search.similarity import SimilaritySearcher

        class MockIndex:
            metric = "COSINE"

        searcher = SimilaritySearcher(MockIndex())

        # Graph: 0-1-2, 3-4, 5
        edges = [(0, 1, 0.9), (1, 2, 0.9), (3, 4, 0.9)]

        components = searcher._find_connected_components(edges, n_nodes=6)

        # Should have 3 components
        self.assertEqual(len(components), 3)

        # Find component sizes
        sizes = sorted([len(c) for c in components], reverse=True)
        self.assertEqual(sizes, [3, 2, 1])


if __name__ == "__main__":
    unittest.main()
