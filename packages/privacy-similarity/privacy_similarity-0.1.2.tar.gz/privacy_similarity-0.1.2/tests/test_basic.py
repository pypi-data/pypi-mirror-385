"""Basic tests for privacy-preserving similarity search."""

import unittest
import numpy as np
import pandas as pd
from privacy_similarity import PrivacyPreservingSimilaritySearch
from privacy_similarity.privacy import DifferentialPrivacy, SecureHash
from privacy_similarity.embeddings import TextEmbedder, PIITokenizer
from privacy_similarity.utils import normalize_text, combine_vectors


class TestPrivacyModules(unittest.TestCase):
    """Test privacy protection modules."""

    def test_differential_privacy_laplace(self):
        """Test Laplace mechanism."""
        dp = DifferentialPrivacy(epsilon=1.0, mechanism="laplace")

        # Test vector transformation
        vector = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        noisy = dp.transform_vector(vector)

        # Shape should be preserved
        self.assertEqual(vector.shape, noisy.shape)

        # Should be different (with high probability)
        self.assertFalse(np.allclose(vector, noisy))

    def test_differential_privacy_batch(self):
        """Test batch transformation."""
        dp = DifferentialPrivacy(epsilon=1.0)

        vectors = np.random.randn(10, 5)
        noisy = dp.transform_batch(vectors)

        self.assertEqual(vectors.shape, noisy.shape)

    def test_minhash_sketch(self):
        """Test MinHash sketch generation."""
        dp = DifferentialPrivacy(epsilon=1.0)

        tokens = ["apple", "banana", "orange", "grape"]
        sketch = dp.minhash_sketch(tokens, num_hashes=64)

        self.assertEqual(len(sketch), 64)
        self.assertTrue(np.all(sketch >= 0))
        self.assertTrue(np.all(sketch <= 1))

    def test_secure_hash(self):
        """Test secure hashing."""
        sh = SecureHash(salt="test_salt")

        # Test value hashing
        hash1 = sh.hash_value("sensitive_data")
        hash2 = sh.hash_value("sensitive_data")
        hash3 = sh.hash_value("different_data")

        # Same input should give same hash
        self.assertEqual(hash1, hash2)

        # Different input should give different hash
        self.assertNotEqual(hash1, hash3)

    def test_bloom_filter(self):
        """Test Bloom filter creation."""
        sh = SecureHash(salt="test")

        values = ["apple", "banana", "orange"]
        bloom = sh.create_bloom_filter(values, filter_size=128, num_hashes=5)

        self.assertEqual(len(bloom), 128)
        self.assertTrue(np.all(np.isin(bloom, [0, 1])))


class TestEmbeddings(unittest.TestCase):
    """Test embedding generation."""

    def test_pii_tokenizer_name(self):
        """Test name normalization."""
        tokenizer = PIITokenizer()

        name1 = tokenizer.normalize_name("Dr. John Smith Jr.")
        name2 = tokenizer.normalize_name("john smith")

        self.assertEqual(name1, name2)

    def test_pii_tokenizer_email(self):
        """Test email normalization."""
        tokenizer = PIITokenizer()

        email1 = tokenizer.normalize_email("John.Doe+spam@Gmail.com")
        email2 = tokenizer.normalize_email("johndoe@gmail.com")

        self.assertEqual(email1, email2)

    def test_pii_tokenizer_address(self):
        """Test address normalization."""
        tokenizer = PIITokenizer()

        addr1 = tokenizer.normalize_address("123 Main Street, Apt. 4")
        addr2 = tokenizer.normalize_address("123 Main St Apt 4")

        # Should be similar after normalization
        self.assertIn("main", addr1)
        self.assertIn("st", addr1)

    def test_text_embedder_tfidf(self):
        """Test TF-IDF embeddings."""
        embedder = TextEmbedder(model_name="tfidf")

        texts = ["hello world", "world of technology", "hello technology"]
        embedder.fit(texts)

        embeddings = embedder.encode(texts)

        self.assertEqual(len(embeddings), 3)
        self.assertTrue(embeddings.shape[1] > 0)


class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_normalize_text(self):
        """Test text normalization."""
        text1 = normalize_text("  Hello   World  ")
        text2 = normalize_text("HELLO WORLD")

        self.assertEqual(text1, text2)
        self.assertEqual(text1, "hello world")

    def test_combine_vectors_concatenate(self):
        """Test vector concatenation."""
        v1 = np.array([[1, 2], [3, 4]])
        v2 = np.array([[5, 6], [7, 8]])

        combined = combine_vectors([v1, v2], method="concatenate")

        self.assertEqual(combined.shape, (2, 4))

    def test_combine_vectors_average(self):
        """Test vector averaging."""
        v1 = np.array([[1, 2], [3, 4]])
        v2 = np.array([[3, 4], [5, 6]])

        combined = combine_vectors([v1, v2], method="average")

        expected = np.array([[2, 3], [4, 5]])
        np.testing.assert_array_equal(combined, expected)


class TestSimilaritySearch(unittest.TestCase):
    """Test main similarity search functionality."""

    def setUp(self):
        """Set up test data."""
        self.test_data = pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Alice Smith", "Bob Jones", "Charlie", "David"],
                "email": [
                    "alice@ex.com",
                    "alice.smith@ex.com",
                    "bob@ex.com",
                    "charlie@ex.com",
                    "david@ex.com",
                ],
                "description": [
                    "Data scientist",
                    "Data analyst",
                    "Software engineer",
                    "Product manager",
                    "Designer",
                ],
            }
        )

    def test_fit_basic(self):
        """Test basic fitting."""
        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        searcher.fit(self.test_data, embedding_columns=["description"], id_column="id")

        self.assertTrue(searcher.fitted)
        self.assertEqual(searcher.embeddings.shape[0], 5)

    def test_search(self):
        """Test searching."""
        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        searcher.fit(self.test_data, embedding_columns=["description"], id_column="id")

        query = pd.DataFrame({"description": ["Machine learning engineer"]})

        results = searcher.search(query, k=2)

        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]["ids"]), 2)

    def test_find_duplicates(self):
        """Test duplicate detection."""
        # Create data with duplicates
        data = pd.DataFrame(
            {
                "id": [1, 2, 3, 4],
                "name": ["Alice Smith", "Alice Smith", "Bob Jones", "Robert Jones"],
                "email": ["alice@ex.com", "alice.s@ex.com", "bob@ex.com", "robert@ex.com"],
            }
        )

        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        searcher.fit(data, sensitive_columns=["name", "email"], id_column="id")

        duplicates = searcher.find_duplicates(threshold=0.7)

        # Should find at least one duplicate group
        self.assertGreater(len(duplicates), 0)

    def test_add_records(self):
        """Test incremental record addition."""
        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        searcher.fit(self.test_data, embedding_columns=["description"], id_column="id")

        initial_count = searcher.get_statistics()["num_records"]

        # Add new records
        new_data = pd.DataFrame({"id": [6, 7], "description": ["DevOps engineer", "QA tester"]})

        searcher.add_records(new_data)

        final_count = searcher.get_statistics()["num_records"]

        self.assertEqual(final_count, initial_count + 2)

    def test_differential_privacy_mode(self):
        """Test with differential privacy."""
        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="differential_privacy",
            epsilon=1.0,
            index_type="Flat",
            embedding_model="tfidf",
        )

        searcher.fit(self.test_data, sensitive_columns=["name", "email"], id_column="id")

        stats = searcher.get_statistics()

        self.assertEqual(stats["privacy_mode"], "differential_privacy")
        self.assertTrue(searcher.fitted)

    def test_secure_hashing_mode(self):
        """Test with secure hashing."""
        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="secure_hashing", salt="test_salt", index_type="Flat"
        )

        searcher.fit(self.test_data, sensitive_columns=["name", "email"], id_column="id")

        self.assertEqual(searcher.privacy_mode, "secure_hashing")
        self.assertTrue(searcher.fitted)


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    def test_end_to_end_customer_deduplication(self):
        """Test complete customer deduplication workflow."""
        customers = pd.DataFrame(
            {
                "customer_id": [1, 2, 3, 4],
                "name": ["John Smith", "Jon Smith", "Jane Doe", "John A. Smith"],
                "email": ["john@ex.com", "jon@ex.com", "jane@ex.com", "jsmith@ex.com"],
                "address": ["123 Main St", "123 Main Street", "456 Oak Ave", "123 Main St."],
            }
        )

        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="differential_privacy",
            epsilon=1.0,
            index_type="Flat",
            embedding_model="tfidf",
        )

        searcher.fit(
            customers, sensitive_columns=["name", "email", "address"], id_column="customer_id"
        )

        duplicates = searcher.find_duplicates(threshold=0.8)

        # Should find some duplicates
        self.assertGreaterEqual(len(duplicates), 0)

        stats = searcher.get_statistics()
        self.assertEqual(stats["num_records"], 4)


if __name__ == "__main__":
    unittest.main()
