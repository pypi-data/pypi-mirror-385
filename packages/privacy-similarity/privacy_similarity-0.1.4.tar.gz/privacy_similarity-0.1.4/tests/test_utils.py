"""Comprehensive tests for utility functions."""

import unittest
import numpy as np
import pandas as pd
from privacy_similarity.utils import (
    normalize_text,
    combine_vectors,
    batch_iterator,
    cosine_similarity_safe,
    estimate_memory_usage,
    select_index_type,
    validate_dataframe,
    merge_duplicate_groups,
    compute_statistics,
)


class TestNormalizeText(unittest.TestCase):
    """Test text normalization."""

    def test_lowercase(self):
        """Test conversion to lowercase."""
        result = normalize_text("HELLO WORLD")
        self.assertEqual(result, "hello world")

    def test_strip_whitespace(self):
        """Test whitespace stripping."""
        result = normalize_text("  hello  world  ")
        self.assertEqual(result, "hello world")

    def test_non_string_input(self):
        """Test handling non-string input."""
        result = normalize_text(123)
        self.assertEqual(result, "123")


class TestCombineVectors(unittest.TestCase):
    """Test vector combination."""

    def test_concatenate(self):
        """Test concatenation method."""
        v1 = np.array([[1, 2], [3, 4]])
        v2 = np.array([[5, 6], [7, 8]])

        result = combine_vectors([v1, v2], method="concatenate")

        expected = np.array([[1, 2, 5, 6], [3, 4, 7, 8]])
        np.testing.assert_array_equal(result, expected)

    def test_average(self):
        """Test averaging method."""
        v1 = np.array([[1, 2], [3, 4]])
        v2 = np.array([[3, 4], [5, 6]])

        result = combine_vectors([v1, v2], method="average")

        expected = np.array([[2, 3], [4, 5]])
        np.testing.assert_array_equal(result, expected)

    def test_weighted_average(self):
        """Test weighted averaging."""
        v1 = np.array([[1, 2], [3, 4]])
        v2 = np.array([[3, 4], [5, 6]])

        result = combine_vectors([v1, v2], weights=[0.25, 0.75], method="weighted_average")

        expected = np.array([[2.5, 3.5], [4.5, 5.5]])
        np.testing.assert_array_almost_equal(result, expected)

    def test_empty_list(self):
        """Test empty vector list raises error."""
        with self.assertRaises(ValueError):
            combine_vectors([])

    def test_invalid_method(self):
        """Test invalid method raises error."""
        v1 = np.array([[1, 2]])
        with self.assertRaises(ValueError):
            combine_vectors([v1], method="invalid")


class TestBatchIterator(unittest.TestCase):
    """Test batch iterator."""

    def test_numpy_array(self):
        """Test iterating over numpy array."""
        data = np.arange(10)
        batches = list(batch_iterator(data, batch_size=3))

        self.assertEqual(len(batches), 4)
        self.assertEqual(len(batches[0]), 3)
        self.assertEqual(len(batches[-1]), 1)

    def test_dataframe(self):
        """Test iterating over DataFrame."""
        df = pd.DataFrame({"x": range(10)})
        batches = list(batch_iterator(df, batch_size=4))

        self.assertEqual(len(batches), 3)
        self.assertEqual(len(batches[0]), 4)


class TestCosineSimilaritySafe(unittest.TestCase):
    """Test safe cosine similarity."""

    def test_normal_vectors(self):
        """Test with normal vectors."""
        v1 = np.array([1, 0, 0])
        v2 = np.array([1, 0, 0])

        sim = cosine_similarity_safe(v1, v2)
        self.assertAlmostEqual(sim, 1.0, places=5)

    def test_orthogonal_vectors(self):
        """Test with orthogonal vectors."""
        v1 = np.array([1, 0, 0])
        v2 = np.array([0, 1, 0])

        sim = cosine_similarity_safe(v1, v2)
        self.assertAlmostEqual(sim, 0.0, places=5)

    def test_zero_vector(self):
        """Test with zero vector."""
        v1 = np.array([1, 2, 3])
        v2 = np.array([0, 0, 0])

        sim = cosine_similarity_safe(v1, v2)
        self.assertEqual(sim, 0.0)

    def test_both_zero(self):
        """Test with both zero vectors."""
        v1 = np.array([0, 0, 0])
        v2 = np.array([0, 0, 0])

        sim = cosine_similarity_safe(v1, v2)
        self.assertEqual(sim, 0.0)


class TestEstimateMemoryUsage(unittest.TestCase):
    """Test memory usage estimation."""

    def test_flat_index(self):
        """Test Flat index memory estimate."""
        result = estimate_memory_usage(n_vectors=1000000, dimension=128, index_type="Flat")

        self.assertIn("base_memory_gb", result)
        self.assertIn("total_memory_gb", result)
        self.assertGreater(result["total_memory_gb"], 0)

    def test_hnsw_index(self):
        """Test HNSW index has overhead."""
        result = estimate_memory_usage(n_vectors=1000000, dimension=128, index_type="HNSW")

        # HNSW should have overhead
        self.assertGreater(result["overhead_ratio"], 1.0)

    def test_ivf_pq_compression(self):
        """Test IVF-PQ has compression."""
        result = estimate_memory_usage(n_vectors=1000000, dimension=128, index_type="IVF-PQ")

        # IVF-PQ should use less memory than base
        self.assertLess(result["total_memory_gb"], result["base_memory_gb"])


class TestSelectIndexType(unittest.TestCase):
    """Test automatic index type selection."""

    def test_small_dataset(self):
        """Test selection for small dataset."""
        index_type = select_index_type(n_vectors=5000, dimension=128)
        self.assertEqual(index_type, "Flat")

    def test_medium_dataset(self):
        """Test selection for medium dataset."""
        index_type = select_index_type(n_vectors=1000000, dimension=128)
        self.assertEqual(index_type, "HNSW")

    def test_large_dataset(self):
        """Test selection for large dataset."""
        index_type = select_index_type(n_vectors=100000000, dimension=128)
        self.assertEqual(index_type, "IVF-HNSW")

    def test_billion_scale(self):
        """Test selection for billion-scale."""
        index_type = select_index_type(n_vectors=2000000000, dimension=128)
        self.assertEqual(index_type, "IVF-PQ")


class TestValidateDataFrame(unittest.TestCase):
    """Test DataFrame validation."""

    def test_valid_dataframe(self):
        """Test valid DataFrame passes."""
        df = pd.DataFrame({"x": [1, 2, 3]})
        result = validate_dataframe(df)
        self.assertTrue(result)

    def test_empty_dataframe(self):
        """Test empty DataFrame raises error."""
        df = pd.DataFrame()
        with self.assertRaises(ValueError):
            validate_dataframe(df)

    def test_required_columns_present(self):
        """Test with required columns present."""
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        result = validate_dataframe(df, required_columns=["x", "y"])
        self.assertTrue(result)

    def test_required_columns_missing(self):
        """Test missing required columns raises error."""
        df = pd.DataFrame({"x": [1, 2]})
        with self.assertRaises(ValueError):
            validate_dataframe(df, required_columns=["x", "y"])


class TestMergeDuplicateGroups(unittest.TestCase):
    """Test merging duplicate groups."""

    def test_no_overlap(self):
        """Test groups with no overlap."""
        groups = [[1, 2], [3, 4], [5, 6]]
        result = merge_duplicate_groups(groups)

        self.assertEqual(len(result), 3)

    def test_with_overlap(self):
        """Test merging overlapping groups."""
        groups = [[1, 2], [2, 3], [4, 5]]
        result = merge_duplicate_groups(groups)

        # [1,2] and [2,3] should merge to [1,2,3]
        self.assertEqual(len(result), 2)

        # Find the merged group
        merged = [g for g in result if len(g) == 3][0]
        self.assertEqual(set(merged), {1, 2, 3})

    def test_complete_overlap(self):
        """Test complete overlap merges all."""
        groups = [[1, 2], [2, 3], [3, 4]]
        result = merge_duplicate_groups(groups)

        # All should merge into one
        self.assertEqual(len(result), 1)
        self.assertEqual(set(result[0]), {1, 2, 3, 4})

    def test_empty_groups(self):
        """Test empty groups list."""
        result = merge_duplicate_groups([])
        self.assertEqual(result, [])


class TestComputeStatistics(unittest.TestCase):
    """Test statistics computation."""

    def test_basic_statistics(self):
        """Test computing basic statistics."""
        values = [1, 2, 3, 4, 5]
        stats = compute_statistics(values)

        self.assertEqual(stats["mean"], 3.0)
        self.assertEqual(stats["median"], 3.0)
        self.assertEqual(stats["min"], 1.0)
        self.assertEqual(stats["max"], 5.0)
        self.assertEqual(stats["count"], 5)

    def test_empty_values(self):
        """Test with empty list."""
        stats = compute_statistics([])
        self.assertEqual(stats, {})

    def test_single_value(self):
        """Test with single value."""
        stats = compute_statistics([42])

        self.assertEqual(stats["mean"], 42.0)
        self.assertEqual(stats["median"], 42.0)
        self.assertEqual(stats["std"], 0.0)


class TestProgressTracker(unittest.TestCase):
    """Test progress tracker."""

    def test_initialization(self):
        """Test tracker initialization."""
        from privacy_similarity.utils import ProgressTracker

        tracker = ProgressTracker(total=100, description="Testing")
        self.assertEqual(tracker.total, 100)
        self.assertEqual(tracker.current, 0)

    def test_update(self):
        """Test updating progress."""
        from privacy_similarity.utils import ProgressTracker

        tracker = ProgressTracker(total=100)
        tracker.update(10)

        self.assertEqual(tracker.current, 10)

    def test_multiple_updates(self):
        """Test multiple updates."""
        from privacy_similarity.utils import ProgressTracker

        tracker = ProgressTracker(total=100)
        tracker.update(25)
        tracker.update(25)
        tracker.update(25)

        self.assertEqual(tracker.current, 75)


if __name__ == "__main__":
    unittest.main()
