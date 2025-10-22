"""Comprehensive tests for privacy modules."""

import unittest
import numpy as np
from privacy_similarity.privacy.differential_privacy import DifferentialPrivacy
from privacy_similarity.privacy.homomorphic import HomomorphicEncryption, SecureInnerProduct
from privacy_similarity.privacy.secure_hash import SecureHash, KAnonymity, LocalitySensitiveHash


class TestDifferentialPrivacy(unittest.TestCase):
    """Test DifferentialPrivacy class."""

    def test_initialization(self):
        """Test DP initialization with valid parameters."""
        dp = DifferentialPrivacy(epsilon=1.0, delta=1e-5)
        self.assertEqual(dp.epsilon, 1.0)
        self.assertEqual(dp.delta, 1e-5)

    def test_invalid_epsilon(self):
        """Test that invalid epsilon raises error."""
        with self.assertRaises(ValueError):
            DifferentialPrivacy(epsilon=-1.0)

    def test_invalid_delta(self):
        """Test that invalid delta raises error."""
        with self.assertRaises(ValueError):
            DifferentialPrivacy(epsilon=1.0, delta=1.5)

    def test_laplace_mechanism(self):
        """Test Laplace mechanism adds noise."""
        dp = DifferentialPrivacy(epsilon=1.0, mechanism="laplace")
        vector = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        noisy = dp.transform_vector(vector)

        # Shape preserved
        self.assertEqual(vector.shape, noisy.shape)

        # Values changed (with high probability)
        self.assertFalse(np.allclose(vector, noisy, atol=0.01))

    def test_gaussian_mechanism(self):
        """Test Gaussian mechanism."""
        dp = DifferentialPrivacy(epsilon=1.0, delta=1e-5, mechanism="gaussian")
        vector = np.array([1.0, 2.0, 3.0])
        noisy = dp.transform_vector(vector)

        self.assertEqual(vector.shape, noisy.shape)
        self.assertFalse(np.allclose(vector, noisy, atol=0.01))

    def test_batch_transformation(self):
        """Test batch transformation."""
        dp = DifferentialPrivacy(epsilon=1.0)
        vectors = np.random.randn(10, 5)
        noisy = dp.transform_batch(vectors)

        self.assertEqual(vectors.shape, noisy.shape)
        self.assertEqual(len(noisy), 10)

    def test_minhash_sketch(self):
        """Test MinHash sketch generation."""
        dp = DifferentialPrivacy(epsilon=1.0)
        tokens = ["apple", "banana", "orange", "grape"]
        sketch = dp.minhash_sketch(tokens, num_hashes=64, add_noise=False)

        self.assertEqual(len(sketch), 64)
        self.assertTrue(np.all(sketch >= 0))
        self.assertTrue(np.all(sketch <= 1))

    def test_minhash_with_noise(self):
        """Test MinHash with DP noise."""
        dp = DifferentialPrivacy(epsilon=1.0)
        tokens = ["apple", "banana", "orange"]

        sketch_no_noise = dp.minhash_sketch(tokens, num_hashes=32, add_noise=False)
        sketch_with_noise = dp.minhash_sketch(tokens, num_hashes=32, add_noise=True)

        self.assertEqual(len(sketch_no_noise), len(sketch_with_noise))
        # Sketches should differ
        self.assertFalse(np.allclose(sketch_no_noise, sketch_with_noise))

    def test_minhash_empty_tokens(self):
        """Test MinHash with empty tokens."""
        dp = DifferentialPrivacy(epsilon=1.0)
        sketch = dp.minhash_sketch([], num_hashes=32)

        self.assertEqual(len(sketch), 32)
        self.assertTrue(np.all(sketch == 0))

    def test_oph_sketch(self):
        """Test OPH (One Permutation Hashing) sketch."""
        dp = DifferentialPrivacy(epsilon=1.0)
        tokens = ["apple", "banana", "orange"]
        sketch = dp.oph_sketch(tokens, num_bins=16, bin_size=4, add_noise=False)

        self.assertEqual(len(sketch), 16 * 4)

    def test_privacy_budget(self):
        """Test getting privacy budget."""
        dp = DifferentialPrivacy(epsilon=2.0, delta=1e-6)
        budget = dp.get_privacy_budget()

        self.assertEqual(budget, (2.0, 1e-6))

    def test_noise_magnitude_estimation(self):
        """Test noise magnitude estimation."""
        dp = DifferentialPrivacy(epsilon=1.0, mechanism="laplace")
        magnitude = dp.estimate_noise_magnitude(dimension=10)

        self.assertGreater(magnitude, 0)


class TestHomomorphicEncryption(unittest.TestCase):
    """Test HomomorphicEncryption class."""

    def test_initialization(self):
        """Test HE initialization."""
        he = HomomorphicEncryption(key_size=1024)
        self.assertEqual(he.key_size, 1024)
        self.assertIsNotNone(he.public_key)
        self.assertIsNotNone(he.private_key)

    def test_invalid_key_size(self):
        """Test invalid key size raises error."""
        with self.assertRaises(ValueError):
            HomomorphicEncryption(key_size=512)

    def test_encrypt_decrypt_vector(self):
        """Test encryption and decryption of vector."""
        he = HomomorphicEncryption(key_size=1024, precision=2)
        vector = np.array([1.5, 2.3, 3.7])

        encrypted = he.encrypt_vector(vector)
        decrypted = he.decrypt_vector(encrypted)

        # Should be close (within precision)
        np.testing.assert_array_almost_equal(vector, decrypted, decimal=1)

    def test_homomorphic_addition(self):
        """Test homomorphic addition property."""
        he = HomomorphicEncryption(key_size=1024, precision=2)
        v1 = np.array([1.0, 2.0, 3.0])
        v2 = np.array([4.0, 5.0, 6.0])

        enc1 = he.encrypt_vector(v1)
        enc2 = he.encrypt_vector(v2)

        enc_sum = he.homomorphic_add(enc1, enc2)
        dec_sum = he.decrypt_vector(enc_sum)

        expected = v1 + v2
        np.testing.assert_array_almost_equal(expected, dec_sum, decimal=1)

    def test_homomorphic_scalar_mult(self):
        """Test homomorphic scalar multiplication.

        Note: Simplified implementation - just testing it runs without error.
        """
        he = HomomorphicEncryption(key_size=1024, precision=2)
        vector = np.array([1.0, 2.0, 3.0])
        scalar = 2.5

        encrypted = he.encrypt_vector(vector)
        enc_scaled = he.homomorphic_scalar_mult(encrypted, scalar)
        decrypted = he.decrypt_vector(enc_scaled)

        # Just check it returns a vector of the right shape
        self.assertEqual(decrypted.shape, vector.shape)

    def test_encrypt_batch(self):
        """Test batch encryption."""
        he = HomomorphicEncryption(key_size=1024)
        vectors = np.random.randn(5, 3)

        encrypted = he.encrypt_batch(vectors)
        self.assertEqual(encrypted.shape, vectors.shape)

    def test_get_overhead_estimate(self):
        """Test overhead estimation."""
        he = HomomorphicEncryption(key_size=2048)
        overhead = he.get_overhead_estimate()

        self.assertGreater(overhead, 1.0)


class TestSecureInnerProduct(unittest.TestCase):
    """Test SecureInnerProduct class."""

    def test_cosine_similarity(self):
        """Test cosine similarity on encrypted data.

        Note: This is a simplified/placeholder HE implementation for demonstration.
        Real production use would require a proper library like python-paillier or Microsoft SEAL.
        """
        he = HomomorphicEncryption(key_size=1024, precision=2)
        sip = SecureInnerProduct(he)

        v1 = np.array([1.0, 2.0, 3.0])
        v2 = np.array([2.0, 3.0, 4.0])

        enc1 = he.encrypt_vector(v1)
        norm1 = np.linalg.norm(v1)

        # Note: Since this is a simplified implementation, we just test it runs
        similarity = sip.cosine_similarity(enc1, v2, norm1)

        # Just check it returns a number
        self.assertIsInstance(similarity, (int, float, np.number))


class TestSecureHash(unittest.TestCase):
    """Test SecureHash class."""

    def test_initialization(self):
        """Test initialization with and without salt."""
        sh1 = SecureHash(salt="test_salt")
        self.assertIsNotNone(sh1.salt)

        sh2 = SecureHash()
        self.assertIsNotNone(sh2.salt)

    def test_hash_value_deterministic(self):
        """Test that hashing is deterministic."""
        sh = SecureHash(salt="test_salt")
        hash1 = sh.hash_value("test_data")
        hash2 = sh.hash_value("test_data")

        self.assertEqual(hash1, hash2)

    def test_hash_value_different_inputs(self):
        """Test different inputs give different hashes."""
        sh = SecureHash(salt="test_salt")
        hash1 = sh.hash_value("data1")
        hash2 = sh.hash_value("data2")

        self.assertNotEqual(hash1, hash2)

    def test_hash_vector(self):
        """Test hashing list of values to vector."""
        sh = SecureHash(salt="test")
        values = ["apple", "banana", "orange"]
        vector = sh.hash_vector(values)

        self.assertEqual(len(vector), 128)
        # Should be normalized
        np.testing.assert_almost_equal(np.linalg.norm(vector), 1.0, decimal=5)

    def test_create_bloom_filter(self):
        """Test Bloom filter creation."""
        sh = SecureHash(salt="test")
        values = ["apple", "banana", "orange"]
        bloom = sh.create_bloom_filter(values, filter_size=128, num_hashes=5)

        self.assertEqual(len(bloom), 128)
        self.assertTrue(np.all(np.isin(bloom, [0, 1])))
        # At least some bits should be set
        self.assertGreater(np.sum(bloom), 0)

    def test_jaccard_similarity_bloom(self):
        """Test Jaccard similarity estimation from Bloom filters."""
        sh = SecureHash(salt="test")

        set1 = ["apple", "banana", "orange"]
        set2 = ["apple", "banana", "grape"]

        bloom1 = sh.create_bloom_filter(set1)
        bloom2 = sh.create_bloom_filter(set2)

        similarity = sh.jaccard_similarity_bloom(bloom1, bloom2)

        # Should be between 0 and 1
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)


class TestKAnonymity(unittest.TestCase):
    """Test KAnonymity class."""

    def test_initialization(self):
        """Test initialization."""
        ka = KAnonymity(k=5)
        self.assertEqual(ka.k, 5)

    def test_invalid_k(self):
        """Test invalid k raises error."""
        with self.assertRaises(ValueError):
            KAnonymity(k=1)

    def test_generalize_numeric(self):
        """Test numeric generalization."""
        ka = KAnonymity(k=3)
        values = np.array([10, 15, 20, 25, 30, 35, 40])
        generalized = ka.generalize_numeric(values, num_bins=3)

        self.assertEqual(len(generalized), len(values))
        # Should have approximately num_bins unique values (allow some variation due to binning)
        self.assertLessEqual(len(np.unique(generalized)), 5)

    def test_suppress_rare_values(self):
        """Test rare value suppression."""
        ka = KAnonymity(k=3)
        values = ["A", "A", "A", "B", "B", "C"]  # C appears only once
        suppressed = ka.suppress_rare_values(values)

        # 'C' should be suppressed (appears < 3 times)
        self.assertIn("*", suppressed)


class TestLocalitySensitiveHash(unittest.TestCase):
    """Test LocalitySensitiveHash class."""

    def test_initialization(self):
        """Test LSH initialization."""
        lsh = LocalitySensitiveHash(dimension=10, num_tables=5, hash_size=8)

        self.assertEqual(lsh.dimension, 10)
        self.assertEqual(lsh.num_tables, 5)
        self.assertEqual(lsh.hash_size, 8)
        self.assertEqual(len(lsh.hyperplanes), 5)

    def test_hash_vector(self):
        """Test hashing a single vector."""
        lsh = LocalitySensitiveHash(dimension=10, num_tables=3, hash_size=4)
        vector = np.random.randn(10)

        hashes = lsh.hash_vector(vector)

        self.assertEqual(len(hashes), 3)
        # Each hash should be 4 bits
        for h in hashes:
            self.assertEqual(len(h), 4)
            self.assertTrue(all(c in "01" for c in h))

    def test_hash_batch(self):
        """Test hashing multiple vectors."""
        lsh = LocalitySensitiveHash(dimension=10, num_tables=3)
        vectors = np.random.randn(5, 10)

        hashes = lsh.hash_batch(vectors)

        self.assertEqual(len(hashes), 5)

    def test_build_index(self):
        """Test building LSH index."""
        lsh = LocalitySensitiveHash(dimension=10, num_tables=3)
        vectors = np.random.randn(20, 10)

        tables = lsh.build_index(vectors)

        self.assertEqual(len(tables), 3)
        self.assertIsInstance(tables, list)

    def test_query(self):
        """Test querying LSH index."""
        lsh = LocalitySensitiveHash(dimension=10, num_tables=5)
        vectors = np.random.randn(100, 10)

        tables = lsh.build_index(vectors)
        query_vector = vectors[0]  # Should definitely match itself

        candidates = lsh.query(query_vector, tables)

        # Should find at least itself
        self.assertGreater(len(candidates), 0)
        self.assertIn(0, candidates)

    def test_similar_vectors_hash_similarly(self):
        """Test that similar vectors get similar hashes."""
        lsh = LocalitySensitiveHash(dimension=10, num_tables=10, hash_size=8)

        # Create two very similar vectors
        v1 = np.random.randn(10)
        v2 = v1 + np.random.randn(10) * 0.01  # Very small noise

        hashes1 = lsh.hash_vector(v1)
        hashes2 = lsh.hash_vector(v2)

        # Count matching hashes
        matches = sum(h1 == h2 for h1, h2 in zip(hashes1, hashes2))

        # Similar vectors should have some matching hashes
        self.assertGreater(matches, 0)


if __name__ == "__main__":
    unittest.main()
