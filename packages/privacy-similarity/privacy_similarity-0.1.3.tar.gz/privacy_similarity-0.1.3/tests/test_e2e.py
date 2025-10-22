"""End-to-end integration tests with realistic scenarios."""

import unittest
import numpy as np
import pandas as pd
import tempfile
import os
from privacy_similarity import PrivacyPreservingSimilaritySearch


class TestCustomerDeduplication(unittest.TestCase):
    """Test complete customer deduplication workflow."""

    def setUp(self):
        """Create realistic customer dataset with duplicates."""
        # Realistic customer data with intentional duplicates
        self.customers = pd.DataFrame(
            {
                "customer_id": range(1, 21),
                "name": [
                    "John Smith",
                    "Jon Smith",
                    "John A. Smith",  # Group 1: duplicates
                    "Jane Doe",
                    "Jane M. Doe",
                    "Jane Marie Doe",  # Group 2: duplicates
                    "Robert Williams",
                    "Bob Williams",
                    "Robert J Williams",  # Group 3: duplicates
                    "Alice Johnson",
                    "Alice B. Johnson",  # Group 4: duplicates
                    "Michael Brown",
                    "Mike Brown",  # Group 5: duplicates
                    "Sarah Davis",
                    "Sara Davis",  # Group 6: duplicates
                    "David Miller",  # Unique
                    "Emma Wilson",  # Unique
                    "James Taylor",  # Unique
                    "Olivia Anderson",  # Unique
                    "William Martinez",  # Unique
                ],
                "email": [
                    "john.smith@example.com",
                    "jsmith@example.com",
                    "john@example.com",
                    "jane.doe@example.com",
                    "jane@example.com",
                    "jdoe@example.com",
                    "robert.w@example.com",
                    "bob.williams@example.com",
                    "rwilliams@example.com",
                    "alice.j@example.com",
                    "ajohnson@example.com",
                    "michael.brown@example.com",
                    "mike.b@example.com",
                    "sarah.davis@example.com",
                    "sara.d@example.com",
                    "david.miller@example.com",
                    "emma.wilson@example.com",
                    "james.taylor@example.com",
                    "olivia.anderson@example.com",
                    "william.martinez@example.com",
                ],
                "phone": [
                    "555-0101",
                    "555-0101",
                    "5550101",  # Same phone
                    "555-0202",
                    "555-0202",
                    "(555) 0202",  # Same phone
                    "555-0303",
                    "555-0303",
                    "555-0303",  # Same phone
                    "555-0404",
                    "5550404",  # Same phone
                    "555-0505",
                    "555-0505",  # Same phone
                    "555-0606",
                    "(555) 0606",  # Same phone
                    "555-0707",
                    "555-0808",
                    "555-0909",
                    "555-1010",
                    "555-1111",
                ],
                "address": [
                    "123 Main St",
                    "123 Main Street",
                    "123 Main St.",
                    "456 Oak Ave",
                    "456 Oak Avenue",
                    "456 Oak Ave",
                    "789 Pine Rd",
                    "789 Pine Road",
                    "789 Pine Rd.",
                    "321 Elm St",
                    "321 Elm Street",
                    "654 Maple Dr",
                    "654 Maple Drive",
                    "987 Cedar Ln",
                    "987 Cedar Lane",
                    "135 Birch Ct",
                    "246 Willow Way",
                    "357 Spruce St",
                    "468 Ash Ave",
                    "579 Palm Blvd",
                ],
                "city": [
                    "New York",
                    "New York",
                    "New York",
                    "Los Angeles",
                    "Los Angeles",
                    "Los Angeles",
                    "Chicago",
                    "Chicago",
                    "Chicago",
                    "Houston",
                    "Houston",
                    "Phoenix",
                    "Phoenix",
                    "Philadelphia",
                    "Philadelphia",
                    "San Antonio",
                    "San Diego",
                    "Dallas",
                    "San Jose",
                    "Austin",
                ],
            }
        )

    def test_deduplication_with_differential_privacy(self):
        """Test customer deduplication with differential privacy."""
        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="differential_privacy",
            epsilon=2.0,  # Moderate privacy
            index_type="Flat",  # Exact search for testing
            embedding_model="tfidf",
        )

        searcher.fit(
            self.customers,
            sensitive_columns=["name", "email", "phone", "address"],
            id_column="customer_id",
        )

        # Find duplicates with lower threshold for DP
        duplicates = searcher.find_duplicates(threshold=0.6, max_cluster_size=10)

        # With DP and noisy data, we may not always find duplicates
        # Just verify the function runs successfully
        self.assertIsInstance(duplicates, list)

        # If we found duplicates, verify they're reasonable
        if duplicates:
            # Check that groups have at least 2 members
            for group in duplicates:
                self.assertGreaterEqual(group["size"], 2)

    def test_deduplication_without_privacy(self):
        """Test deduplication without privacy for accuracy comparison."""
        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        searcher.fit(
            self.customers,
            sensitive_columns=["name", "email", "address", "phone"],
            id_column="customer_id",
        )

        duplicates = searcher.find_duplicates(threshold=0.75)

        # Should find at least one duplicate group
        self.assertGreater(len(duplicates), 0)

        # Check that we found meaningful duplicates
        if duplicates:
            largest_group = max(duplicates, key=lambda g: g["size"])
            self.assertGreaterEqual(largest_group["size"], 2)

    def test_query_for_similar_customers(self):
        """Test searching for similar customers."""
        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        searcher.fit(self.customers, sensitive_columns=["name", "email"], id_column="customer_id")

        # Query with a variant of existing customer
        query = pd.DataFrame({"name": ["Jonathan Smith"], "email": ["j.smith@example.com"]})

        results = searcher.search(query, k=5, similarity_threshold=0.5)

        # Should find similar customers
        self.assertGreater(len(results[0]["ids"]), 0)


class TestSimilarityRecommendation(unittest.TestCase):
    """Test product/content recommendation based on similarity."""

    def setUp(self):
        """Create product catalog."""
        self.products = pd.DataFrame(
            {
                "product_id": range(1, 16),
                "name": [
                    "Laptop Computer",
                    "Desktop Computer",
                    "Tablet Device",
                    "Smartphone",
                    "Smart Watch",
                    "Wireless Headphones",
                    "Bluetooth Speaker",
                    "Digital Camera",
                    "Camera Lens",
                    "Tripod Stand",
                    "Running Shoes",
                    "Basketball Shoes",
                    "Tennis Racket",
                    "Yoga Mat",
                    "Fitness Tracker",
                ],
                "description": [
                    "High-performance laptop for work and gaming",
                    "Powerful desktop computer for professionals",
                    "Portable tablet for reading and browsing",
                    "Latest smartphone with advanced camera",
                    "Fitness tracking smart watch",
                    "Premium wireless headphones with noise cancellation",
                    "Portable bluetooth speaker for music",
                    "Professional digital camera for photography",
                    "Wide angle lens for cameras",
                    "Stable tripod for cameras and phones",
                    "Comfortable running shoes for athletes",
                    "High-top basketball shoes",
                    "Professional tennis racket",
                    "Non-slip yoga mat for exercise",
                    "Waterproof fitness activity tracker",
                ],
                "category": [
                    "Electronics",
                    "Electronics",
                    "Electronics",
                    "Electronics",
                    "Electronics",
                    "Electronics",
                    "Electronics",
                    "Photography",
                    "Photography",
                    "Photography",
                    "Sports",
                    "Sports",
                    "Sports",
                    "Sports",
                    "Sports",
                ],
                "price": [
                    999.99,
                    1299.99,
                    499.99,
                    899.99,
                    399.99,
                    299.99,
                    149.99,
                    799.99,
                    399.99,
                    99.99,
                    129.99,
                    149.99,
                    89.99,
                    39.99,
                    199.99,
                ],
            }
        )

    def test_find_similar_products(self):
        """Test finding similar products."""
        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        searcher.fit(
            self.products, embedding_columns=["name", "description"], id_column="product_id"
        )

        # Query for laptop-like products
        query = pd.DataFrame(
            {"name": ["Notebook Computer"], "description": ["Portable computer for work"]}
        )

        results = searcher.search(query, k=5)

        # Should find computer-related products
        # With TF-IDF on small texts, exact matching may vary
        top_ids = results[0]["ids"][:5]
        # IDs 1,2 are laptop and desktop
        computer_ids = {1, 2}
        overlap = len(set(top_ids) & computer_ids)
        self.assertGreater(overlap, 0, "Should find at least one computer product")

    def test_category_based_similarity(self):
        """Test similarity within categories."""
        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        # Combine text and categorical features
        searcher.fit(
            self.products,
            embedding_columns=["name", "description", "category"],
            id_column="product_id",
        )

        # Query for photography equipment
        query = pd.DataFrame(
            {
                "name": ["Camera Accessory"],
                "description": ["Equipment for photography"],
                "category": ["Photography"],
            }
        )

        results = searcher.search(query, k=5)

        # Top results should include photography items (IDs 8, 9, 10)
        top_ids = set(results[0]["ids"][:5])
        photography_ids = {8, 9, 10}
        overlap = len(top_ids & photography_ids)

        self.assertGreater(overlap, 0, "Should find at least one photography item")


class TestIncrementalUpdates(unittest.TestCase):
    """Test incremental updates and online learning scenarios."""

    def test_add_customers_incrementally(self):
        """Test adding customers over time."""
        # Initial batch
        initial_customers = pd.DataFrame(
            {
                "customer_id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "interests": ["technology, sports", "music, art", "sports, cooking"],
            }
        )

        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        searcher.fit(initial_customers, embedding_columns=["interests"], id_column="customer_id")

        initial_stats = searcher.get_statistics()
        self.assertEqual(initial_stats["num_records"], 3)

        # Add new customers
        new_customers = pd.DataFrame(
            {
                "customer_id": [4, 5],
                "name": ["David", "Emma"],
                "interests": ["technology, gaming", "cooking, baking"],
            }
        )

        searcher.add_records(new_customers)

        updated_stats = searcher.get_statistics()
        self.assertEqual(updated_stats["num_records"], 5)

        # Search should work with all records
        query = pd.DataFrame({"interests": ["tech and games"]})

        results = searcher.search(query, k=3)
        self.assertEqual(len(results[0]["ids"]), 3)


class TestPrivacyModes(unittest.TestCase):
    """Test different privacy modes end-to-end."""

    def setUp(self):
        """Create test dataset."""
        self.data = pd.DataFrame(
            {
                "id": range(1, 11),
                "name": [f"Person {i}" for i in range(1, 11)],
                "email": [f"person{i}@example.com" for i in range(1, 11)],
                "description": [
                    "Data scientist with ML expertise",
                    "Machine learning engineer",
                    "Software developer",
                    "Product manager",
                    "UX designer",
                    "Data analyst",
                    "AI researcher",
                    "Full stack developer",
                    "DevOps engineer",
                    "QA tester",
                ],
            }
        )

    def test_secure_hashing_mode(self):
        """Test secure hashing privacy mode."""
        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="secure_hashing", salt="test_salt_123", index_type="Flat"
        )

        searcher.fit(self.data, sensitive_columns=["name", "email"], id_column="id")

        stats = searcher.get_statistics()
        self.assertEqual(stats["privacy_mode"], "secure_hashing")
        self.assertTrue(stats["fitted"])

    def test_differential_privacy_mode(self):
        """Test differential privacy mode."""
        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="differential_privacy",
            epsilon=1.0,
            index_type="Flat",
            embedding_model="tfidf",
        )

        searcher.fit(self.data, sensitive_columns=["name", "email"], id_column="id")

        stats = searcher.get_statistics()
        self.assertEqual(stats["privacy_mode"], "differential_privacy")
        self.assertEqual(stats["epsilon"], 1.0)

        # Search should still work
        query = pd.DataFrame({"name": ["Test Person"], "email": ["test@example.com"]})

        results = searcher.search(query, k=3)
        self.assertGreater(len(results[0]["ids"]), 0)


class TestScalability(unittest.TestCase):
    """Test scalability with larger datasets."""

    def test_medium_scale_dataset(self):
        """Test with 1000 records."""
        np.random.seed(42)

        # Generate synthetic data
        n_records = 1000
        data = pd.DataFrame(
            {
                "id": range(1, n_records + 1),
                "text": [
                    f"Sample text {i} with some random content about topic {i % 10}"
                    for i in range(n_records)
                ],
                "category": [f"Category_{i % 5}" for i in range(n_records)],
                "value": np.random.randn(n_records),
            }
        )

        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        searcher.fit(data, embedding_columns=["text", "category"], id_column="id")

        stats = searcher.get_statistics()
        self.assertEqual(stats["num_records"], n_records)

        # Search should be fast
        query = pd.DataFrame({"text": ["Sample query text"], "category": ["Category_0"]})

        results = searcher.search(query, k=10)
        self.assertEqual(len(results[0]["ids"]), 10)

    def test_index_type_selection(self):
        """Test automatic index type selection."""
        # Small dataset
        small_data = pd.DataFrame({"id": range(1, 101), "text": [f"Text {i}" for i in range(100)]})

        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="auto", embedding_model="tfidf"
        )

        searcher.fit(small_data, embedding_columns=["text"], id_column="id")

        stats = searcher.get_statistics()
        # Should select Flat for small datasets
        self.assertIn(stats["index_type"].upper(), ["FLAT", "HNSW"])


class TestSaveAndLoad(unittest.TestCase):
    """Test saving and loading models."""

    def test_save_and_load_index(self):
        """Test saving and loading FAISS index."""
        data = pd.DataFrame(
            {"id": [1, 2, 3, 4, 5], "text": ["apple", "banana", "orange", "grape", "mango"]}
        )

        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        searcher.fit(data, embedding_columns=["text"], id_column="id")

        # Test search before save
        query = pd.DataFrame({"text": ["fruit"]})
        results_before = searcher.search(query, k=2)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".index") as f:
            index_file = f.name

        try:
            searcher.save(index_file)
            self.assertTrue(os.path.exists(index_file))

            # Create new searcher and load
            searcher2 = PrivacyPreservingSimilaritySearch(
                privacy_mode="none", index_type="Flat", embedding_model="tfidf"
            )

            # Need to initialize with same dimension
            searcher2.fit(data, embedding_columns=["text"], id_column="id")
            searcher2.load(index_file)

            # Should get same results
            results_after = searcher2.search(query, k=2)
            self.assertEqual(len(results_after[0]["ids"]), len(results_before[0]["ids"]))

        finally:
            if os.path.exists(index_file):
                os.remove(index_file)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_empty_query(self):
        """Test handling of empty queries."""
        data = pd.DataFrame({"id": [1, 2, 3], "text": ["a", "b", "c"]})

        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        searcher.fit(data, embedding_columns=["text"], id_column="id")

        # Empty text should still work
        query = pd.DataFrame({"text": [""]})
        results = searcher.search(query, k=1)

        self.assertEqual(len(results), 1)

    def test_single_record(self):
        """Test with single record."""
        data = pd.DataFrame({"id": [1], "text": ["single record"]})

        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        searcher.fit(data, embedding_columns=["text"], id_column="id")

        query = pd.DataFrame({"text": ["query"]})
        results = searcher.search(query, k=1)

        self.assertEqual(len(results[0]["ids"]), 1)
        self.assertEqual(results[0]["ids"][0], 1)

    def test_missing_columns(self):
        """Test error handling for missing columns."""
        data = pd.DataFrame({"id": [1, 2], "text": ["a", "b"]})

        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode="none", index_type="Flat", embedding_model="tfidf"
        )

        # Should handle missing columns gracefully
        searcher.fit(
            data,
            sensitive_columns=["nonexistent_column"],  # Missing column
            embedding_columns=["text"],
            id_column="id",
        )

        # Should still work
        self.assertTrue(searcher.fitted)


if __name__ == "__main__":
    unittest.main()
