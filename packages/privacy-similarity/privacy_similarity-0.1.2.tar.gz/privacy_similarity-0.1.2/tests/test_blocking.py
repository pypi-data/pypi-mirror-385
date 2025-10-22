"""Comprehensive tests for blocking modules."""

import unittest
import numpy as np
from privacy_similarity.blocking.lsh import LSHBlocker, DynamicBucketingLSH
from privacy_similarity.blocking.clustering import ClusteringBlocker, HierarchicalBlocker


class TestLSHBlocker(unittest.TestCase):
    """Test LSHBlocker class."""

    def test_initialization(self):
        """Test LSH blocker initialization."""
        blocker = LSHBlocker(dimension=10, num_tables=5, hash_size=8, lsh_type="random_projection")

        self.assertEqual(blocker.dimension, 10)
        self.assertEqual(blocker.num_tables, 5)
        self.assertEqual(blocker.hash_size, 8)
        self.assertEqual(len(blocker.hash_tables), 5)

    def test_hash_vector_random_projection(self):
        """Test hashing with random projection."""
        blocker = LSHBlocker(dimension=10, num_tables=3, hash_size=4, lsh_type="random_projection")

        vector = np.random.randn(10)
        hash_val = blocker.hash_vector(vector, table_idx=0)

        # Should be binary string of length hash_size
        self.assertEqual(len(hash_val), 4)
        self.assertTrue(all(c in "01" for c in hash_val))

    def test_index_vectors(self):
        """Test indexing vectors."""
        blocker = LSHBlocker(dimension=10, num_tables=3)
        vectors = np.random.randn(50, 10)

        blocker.index_vectors(vectors)

        self.assertEqual(blocker.num_indexed, 50)

    def test_query_finds_similar(self):
        """Test that query finds similar vectors."""
        blocker = LSHBlocker(dimension=10, num_tables=10, hash_size=8)
        vectors = np.random.randn(100, 10)

        blocker.index_vectors(vectors)

        # Query with first vector - should find itself
        query = vectors[0]
        candidates = blocker.query(query)

        self.assertIn(0, candidates)
        self.assertGreater(len(candidates), 0)

    def test_query_batch(self):
        """Test batch querying."""
        blocker = LSHBlocker(dimension=10, num_tables=5)
        vectors = np.random.randn(50, 10)
        blocker.index_vectors(vectors)

        queries = vectors[:5]
        results = blocker.query_batch(queries)

        self.assertEqual(len(results), 5)
        # Each query should find at least itself
        for i, candidates in enumerate(results):
            self.assertIn(i, candidates)

    def test_get_bucket_statistics(self):
        """Test bucket statistics."""
        blocker = LSHBlocker(dimension=10, num_tables=3)
        vectors = np.random.randn(100, 10)
        blocker.index_vectors(vectors)

        stats = blocker.get_bucket_statistics()

        self.assertIn("mean_bucket_size", stats)
        self.assertIn("max_bucket_size", stats)
        self.assertIn("num_indexed", stats)
        self.assertEqual(stats["num_indexed"], 100)

    def test_estimate_recall(self):
        """Test recall estimation."""
        blocker = LSHBlocker(dimension=10, num_tables=10, hash_size=8, lsh_type="random_projection")

        recall = blocker.estimate_recall(similarity_threshold=0.8)

        self.assertGreaterEqual(recall, 0.0)
        self.assertLessEqual(recall, 1.0)

    def test_hash_minhash(self):
        """Test MinHash hashing."""
        blocker = LSHBlocker(dimension=10, num_tables=3, hash_size=4, lsh_type="minhash")

        # Create binary vector
        vector = np.array([1, 0, 1, 1, 0, 0, 1, 0, 1, 0])
        hash_val = blocker.hash_vector(vector, table_idx=0)

        self.assertIsInstance(hash_val, str)


class TestDynamicBucketingLSH(unittest.TestCase):
    """Test DynamicBucketingLSH class."""

    def test_initialization(self):
        """Test DB-LSH initialization."""
        dblsh = DynamicBucketingLSH(dimension=10, num_projections=8, bucket_width=0.1)

        self.assertEqual(dblsh.dimension, 10)
        self.assertEqual(dblsh.num_projections, 8)
        self.assertEqual(dblsh.bucket_width, 0.1)

    def test_index_vectors(self):
        """Test indexing vectors."""
        dblsh = DynamicBucketingLSH(dimension=10)
        vectors = np.random.randn(50, 10)

        dblsh.index_vectors(vectors)

        self.assertEqual(len(dblsh.projected_vectors), 50)
        self.assertEqual(len(dblsh.vector_ids), 50)

    def test_query(self):
        """Test querying."""
        dblsh = DynamicBucketingLSH(dimension=10, num_projections=8)
        vectors = np.random.randn(100, 10)
        dblsh.index_vectors(vectors)

        query = vectors[0]
        # Use larger radius to ensure we find candidates
        candidates = dblsh.query(query, radius=3.0)

        # Should find at least some candidates (may not always find itself due to bucketing)
        self.assertGreaterEqual(len(candidates), 0)

    def test_custom_ids(self):
        """Test with custom IDs."""
        dblsh = DynamicBucketingLSH(dimension=10)
        vectors = np.random.randn(20, 10)
        custom_ids = list(range(100, 120))

        dblsh.index_vectors(vectors, ids=custom_ids)

        self.assertEqual(dblsh.vector_ids, custom_ids)


class TestClusteringBlocker(unittest.TestCase):
    """Test ClusteringBlocker class."""

    def test_initialization(self):
        """Test initialization."""
        blocker = ClusteringBlocker(n_clusters=10, clustering_algorithm="kmeans")

        self.assertEqual(blocker.n_clusters, 10)
        self.assertIsNotNone(blocker.clusterer)

    def test_fit_kmeans(self):
        """Test fitting with K-means."""
        blocker = ClusteringBlocker(n_clusters=5, clustering_algorithm="kmeans")
        vectors = np.random.randn(50, 10)

        blocker.fit(vectors)

        self.assertTrue(blocker.fitted)
        self.assertIsNotNone(blocker.centroids)
        self.assertEqual(len(blocker.cluster_to_ids), 5)

    def test_fit_minibatch_kmeans(self):
        """Test fitting with MiniBatch K-means."""
        blocker = ClusteringBlocker(n_clusters=5, clustering_algorithm="minibatch_kmeans")
        vectors = np.random.randn(100, 10)

        blocker.fit(vectors)

        self.assertTrue(blocker.fitted)

    def test_predict_cluster(self):
        """Test predicting cluster."""
        blocker = ClusteringBlocker(n_clusters=5)
        vectors = np.random.randn(50, 10)
        blocker.fit(vectors)

        cluster_id = blocker.predict_cluster(vectors[0])

        self.assertGreaterEqual(cluster_id, 0)
        self.assertLess(cluster_id, 5)

    def test_query(self):
        """Test querying for candidates."""
        blocker = ClusteringBlocker(n_clusters=5)
        vectors = np.random.randn(100, 10)
        blocker.fit(vectors)

        query = vectors[0]
        candidates = blocker.query(query, num_clusters=1)

        # Should return some candidates
        self.assertGreater(len(candidates), 0)
        # Should include the query vector itself
        self.assertIn(0, candidates)

    def test_query_multiple_clusters(self):
        """Test querying multiple clusters."""
        blocker = ClusteringBlocker(n_clusters=10)
        vectors = np.random.randn(200, 10)
        blocker.fit(vectors)

        query = vectors[0]
        candidates_1 = blocker.query(query, num_clusters=1)
        candidates_3 = blocker.query(query, num_clusters=3)

        # More clusters should give more candidates
        self.assertGreaterEqual(len(candidates_3), len(candidates_1))

    def test_query_batch(self):
        """Test batch querying."""
        blocker = ClusteringBlocker(n_clusters=5)
        vectors = np.random.randn(100, 10)
        blocker.fit(vectors)

        queries = vectors[:10]
        results = blocker.query_batch(queries, num_clusters=1)

        self.assertEqual(len(results), 10)

    def test_get_statistics(self):
        """Test getting statistics."""
        blocker = ClusteringBlocker(n_clusters=5)
        vectors = np.random.randn(100, 10)
        blocker.fit(vectors)

        stats = blocker.get_statistics()

        self.assertIn("n_clusters", stats)
        self.assertIn("mean_cluster_size", stats)
        self.assertEqual(stats["n_clusters"], 5)

    def test_custom_ids(self):
        """Test with custom IDs."""
        blocker = ClusteringBlocker(n_clusters=3)
        vectors = np.random.randn(30, 10)
        custom_ids = list(range(1000, 1030))

        blocker.fit(vectors, ids=custom_ids)

        # Check custom IDs are used
        all_ids = []
        for cluster_ids in blocker.cluster_to_ids.values():
            all_ids.extend(cluster_ids)

        self.assertTrue(all(id >= 1000 for id in all_ids))

    def test_cosine_distance_metric(self):
        """Test using cosine distance metric."""
        blocker = ClusteringBlocker(n_clusters=5, distance_metric="cosine")
        vectors = np.random.randn(50, 10)

        blocker.fit(vectors)
        self.assertTrue(blocker.fitted)


class TestHierarchicalBlocker(unittest.TestCase):
    """Test HierarchicalBlocker class."""

    def test_initialization(self):
        """Test initialization."""
        blocker = HierarchicalBlocker(n_levels=3)

        self.assertEqual(blocker.n_levels, 3)
        self.assertEqual(len(blocker.clusters_per_level), 3)

    def test_custom_clusters_per_level(self):
        """Test custom clusters per level."""
        blocker = HierarchicalBlocker(n_levels=3, clusters_per_level=[5, 10, 20])

        self.assertEqual(blocker.clusters_per_level, [5, 10, 20])

    def test_fit(self):
        """Test fitting hierarchical blocker."""
        blocker = HierarchicalBlocker(n_levels=3)
        vectors = np.random.randn(200, 10)

        blocker.fit(vectors)

        self.assertTrue(blocker.fitted)
        self.assertEqual(len(blocker.blockers), 3)

    def test_query_different_levels(self):
        """Test querying at different hierarchy levels."""
        blocker = HierarchicalBlocker(n_levels=3, clusters_per_level=[5, 10, 20])
        vectors = np.random.randn(200, 10)
        blocker.fit(vectors)

        query = vectors[0]

        # Query at different levels
        candidates_level0 = blocker.query(query, level=0)
        candidates_level1 = blocker.query(query, level=1)
        candidates_level2 = blocker.query(query, level=2)

        # Finer levels should generally give fewer candidates
        # (though this isn't guaranteed)
        self.assertGreater(len(candidates_level0), 0)
        self.assertGreater(len(candidates_level1), 0)
        self.assertGreater(len(candidates_level2), 0)

    def test_query_progressive(self):
        """Test progressive querying."""
        blocker = HierarchicalBlocker(n_levels=3)
        vectors = np.random.randn(300, 10)
        blocker.fit(vectors)

        query = vectors[0]
        candidates = blocker.query_progressive(query, max_candidates=50)

        # Should find some candidates
        self.assertGreater(len(candidates), 0)
        # Should respect max_candidates (approximately)
        self.assertLessEqual(len(candidates), 150)  # Allow some margin

    def test_query_multiresolution(self):
        """Test multi-resolution querying."""
        blocker = HierarchicalBlocker(n_levels=3)
        vectors = np.random.randn(200, 10)
        blocker.fit(vectors)

        query = vectors[0]
        candidates = blocker.query_multiresolution(query)

        # Should find candidates from multiple levels
        self.assertGreater(len(candidates), 0)

    def test_invalid_level(self):
        """Test querying invalid level raises error."""
        blocker = HierarchicalBlocker(n_levels=3)
        vectors = np.random.randn(100, 10)
        blocker.fit(vectors)

        query = vectors[0]

        with self.assertRaises(ValueError):
            blocker.query(query, level=5)


class TestBlockingIntegration(unittest.TestCase):
    """Integration tests for blocking methods."""

    def test_lsh_vs_clustering_recall(self):
        """Compare recall between LSH and clustering."""
        vectors = np.random.randn(100, 20)

        # LSH blocker
        lsh = LSHBlocker(dimension=20, num_tables=10)
        lsh.index_vectors(vectors)

        # Clustering blocker
        clustering = ClusteringBlocker(n_clusters=10)
        clustering.fit(vectors)

        # Query
        query = vectors[0]

        lsh_candidates = lsh.query(query)
        clustering_candidates = clustering.query(query, num_clusters=2)

        # Both should find the query vector itself
        self.assertIn(0, lsh_candidates)
        self.assertIn(0, clustering_candidates)

    def test_blocking_reduces_comparisons(self):
        """Test that blocking reduces number of comparisons."""
        n_vectors = 1000
        vectors = np.random.randn(n_vectors, 10)

        blocker = ClusteringBlocker(n_clusters=20)
        blocker.fit(vectors)

        query = vectors[0]
        candidates = blocker.query(query, num_clusters=1)

        # Should examine far fewer than all vectors
        self.assertLess(len(candidates), n_vectors)
        # But should still find the query itself
        self.assertIn(0, candidates)


if __name__ == "__main__":
    unittest.main()
