"""Comprehensive tests for embedding modules."""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from privacy_similarity.embeddings.text_embeddings import (
    TextEmbedder,
    PIITokenizer,
    CharacterNGramEmbedder,
)
from privacy_similarity.embeddings.numeric_features import (
    NumericFeatureEncoder,
    TemporalFeatureEncoder,
    BehaviorFeatureEncoder,
)


class TestTextEmbedder(unittest.TestCase):
    """Test TextEmbedder class."""

    def test_initialization_tfidf(self):
        """Test TF-IDF embedder initialization."""
        embedder = TextEmbedder(model_name="tfidf")
        self.assertEqual(embedder.backend, "tfidf")
        self.assertIsNotNone(embedder.tfidf)

    def test_fit_tfidf(self):
        """Test fitting TF-IDF."""
        embedder = TextEmbedder(model_name="tfidf")
        texts = ["hello world", "world of python", "python programming"]

        embedder.fit(texts)
        self.assertTrue(embedder.fitted)

    def test_encode_single_text(self):
        """Test encoding single text."""
        embedder = TextEmbedder(model_name="tfidf")
        texts = ["hello world", "world of python"]
        embedder.fit(texts)

        embedding = embedder.encode("hello python")

        self.assertEqual(embedding.ndim, 1)
        self.assertGreater(len(embedding), 0)

    def test_encode_batch(self):
        """Test encoding batch of texts."""
        embedder = TextEmbedder(model_name="tfidf")
        texts = ["hello world", "world of python", "python programming"]
        embedder.fit(texts)

        embeddings = embedder.encode(texts)

        self.assertEqual(len(embeddings), 3)
        self.assertEqual(embeddings.shape[0], 3)

    def test_normalization(self):
        """Test L2 normalization."""
        embedder = TextEmbedder(model_name="tfidf", normalize=True)
        texts = ["hello world", "python"]
        embedder.fit(texts)

        embeddings = embedder.encode(texts)

        # Check L2 norms are close to 1
        norms = np.linalg.norm(embeddings, axis=1)
        np.testing.assert_array_almost_equal(norms, np.ones(len(texts)), decimal=5)

    def test_embedding_dimension(self):
        """Test getting embedding dimension."""
        embedder = TextEmbedder(model_name="tfidf")
        texts = ["hello world"]
        embedder.fit(texts)

        dim = embedder.embedding_dimension
        self.assertGreater(dim, 0)


class TestPIITokenizer(unittest.TestCase):
    """Test PIITokenizer class."""

    def test_normalize_name_case(self):
        """Test name normalization - case."""
        tokenizer = PIITokenizer()
        name1 = tokenizer.normalize_name("JOHN SMITH")
        name2 = tokenizer.normalize_name("john smith")

        self.assertEqual(name1, name2)

    def test_normalize_name_prefix(self):
        """Test name normalization - prefix removal."""
        tokenizer = PIITokenizer()
        name1 = tokenizer.normalize_name("Dr. John Smith")
        name2 = tokenizer.normalize_name("John Smith")

        self.assertEqual(name1, name2)

    def test_normalize_name_suffix(self):
        """Test name normalization - suffix removal."""
        tokenizer = PIITokenizer()
        name1 = tokenizer.normalize_name("John Smith Jr.")
        name2 = tokenizer.normalize_name("John Smith")

        self.assertEqual(name1, name2)

    def test_normalize_email_case(self):
        """Test email normalization - case."""
        tokenizer = PIITokenizer()
        email1 = tokenizer.normalize_email("John.Doe@Example.COM")
        email2 = tokenizer.normalize_email("john.doe@example.com")

        self.assertEqual(email1, email2)

    def test_normalize_email_alias(self):
        """Test email normalization - alias removal."""
        tokenizer = PIITokenizer()
        email1 = tokenizer.normalize_email("john+spam@example.com")
        email2 = tokenizer.normalize_email("john@example.com")

        self.assertEqual(email1, email2)

    def test_normalize_email_gmail_dots(self):
        """Test Gmail dot removal."""
        tokenizer = PIITokenizer()
        email1 = tokenizer.normalize_email("john.doe@gmail.com")
        email2 = tokenizer.normalize_email("johndoe@gmail.com")

        self.assertEqual(email1, email2)

    def test_normalize_address_abbreviations(self):
        """Test address abbreviation normalization."""
        tokenizer = PIITokenizer()
        addr1 = tokenizer.normalize_address("123 Main Street")
        addr2 = tokenizer.normalize_address("123 Main St")

        self.assertEqual(addr1, addr2)

    def test_normalize_phone(self):
        """Test phone normalization."""
        tokenizer = PIITokenizer()
        phone1 = tokenizer.normalize_phone("(123) 456-7890")
        phone2 = tokenizer.normalize_phone("123-456-7890")
        phone3 = tokenizer.normalize_phone("1234567890")

        self.assertEqual(phone1, phone2)
        self.assertEqual(phone2, phone3)

    def test_tokenize_name(self):
        """Test name tokenization."""
        tokenizer = PIITokenizer()
        tokens = tokenizer.tokenize_name("John Smith")

        self.assertIn("john", tokens)
        self.assertIn("smith", tokens)
        # Should include character n-grams
        self.assertGreater(len(tokens), 2)


class TestCharacterNGramEmbedder(unittest.TestCase):
    """Test CharacterNGramEmbedder class."""

    def test_initialization(self):
        """Test initialization."""
        embedder = CharacterNGramEmbedder(n=3, vector_size=128)
        self.assertEqual(embedder.n, 3)
        self.assertEqual(embedder.vector_size, 128)

    def test_fit(self):
        """Test fitting on texts."""
        embedder = CharacterNGramEmbedder(n=3)
        texts = ["hello", "world", "python"]

        embedder.fit(texts)
        self.assertTrue(embedder.fitted)
        self.assertGreater(len(embedder.vocab), 0)

    def test_encode(self):
        """Test encoding text."""
        embedder = CharacterNGramEmbedder(n=3, vector_size=64)
        texts = ["hello", "world", "python"]
        embedder.fit(texts)

        vector = embedder.encode("hello")

        self.assertEqual(len(vector), 64)
        # Should be normalized
        np.testing.assert_almost_equal(np.linalg.norm(vector), 1.0, decimal=5)

    def test_encode_batch(self):
        """Test batch encoding."""
        embedder = CharacterNGramEmbedder(n=3)
        texts = ["hello", "world"]
        embedder.fit(texts)

        vectors = embedder.encode_batch(texts)

        self.assertEqual(vectors.shape[0], 2)

    def test_similar_words_similar_vectors(self):
        """Test that similar words get similar vectors."""
        embedder = CharacterNGramEmbedder(n=3, vector_size=128)
        texts = ["smith", "smyth", "jones"]
        embedder.fit(texts)

        v_smith = embedder.encode("smith")
        v_smyth = embedder.encode("smyth")
        v_jones = embedder.encode("jones")

        # smith and smyth should be more similar than smith and jones
        sim_smith_smyth = np.dot(v_smith, v_smyth)
        sim_smith_jones = np.dot(v_smith, v_jones)

        self.assertGreater(sim_smith_smyth, sim_smith_jones)


class TestNumericFeatureEncoder(unittest.TestCase):
    """Test NumericFeatureEncoder class."""

    def test_initialization(self):
        """Test initialization with different scalers."""
        encoder1 = NumericFeatureEncoder(scaling="standard")
        self.assertIsNotNone(encoder1.scaler)

        encoder2 = NumericFeatureEncoder(scaling="minmax")
        self.assertIsNotNone(encoder2.scaler)

        encoder3 = NumericFeatureEncoder(scaling=None)
        self.assertIsNone(encoder3.scaler)

    def test_fit_numeric_columns(self):
        """Test fitting on numeric columns."""
        df = pd.DataFrame(
            {
                "age": [25, 30, 35, 40],
                "salary": [50000, 60000, 70000, 80000],
                "name": ["Alice", "Bob", "Charlie", "David"],
            }
        )

        encoder = NumericFeatureEncoder()
        encoder.fit(df, numeric_columns=["age", "salary"])

        self.assertTrue(encoder.fitted)
        self.assertEqual(len(encoder.numeric_columns), 2)

    def test_transform_numeric(self):
        """Test transforming numeric data."""
        df = pd.DataFrame({"age": [25, 30, 35, 40], "salary": [50000, 60000, 70000, 80000]})

        encoder = NumericFeatureEncoder(scaling="standard")
        encoder.fit(df)

        transformed = encoder.transform(df)

        self.assertEqual(transformed.shape[0], 4)
        self.assertEqual(transformed.shape[1], 2)

    def test_fit_transform(self):
        """Test fit_transform."""
        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [10, 20, 30, 40]})

        encoder = NumericFeatureEncoder()
        transformed = encoder.fit_transform(df)

        self.assertEqual(transformed.shape, (4, 2))
        self.assertTrue(encoder.fitted)

    def test_handle_missing_mean(self):
        """Test missing value imputation with mean."""
        df = pd.DataFrame({"x": [1, 2, np.nan, 4]})

        encoder = NumericFeatureEncoder(handle_missing="mean")
        encoder.fit(df, numeric_columns=["x"])

        transformed = encoder.transform(df)

        # No NaN in output
        self.assertFalse(np.any(np.isnan(transformed)))

    def test_categorical_encoding_onehot(self):
        """Test one-hot encoding of categorical variables."""
        df = pd.DataFrame({"category": ["A", "B", "A", "C"]})

        encoder = NumericFeatureEncoder(categorical_encoding="onehot")
        encoder.fit(df, numeric_columns=[], categorical_columns=["category"])

        transformed = encoder.transform(df)

        # Should have 3 columns (3 unique categories)
        self.assertEqual(transformed.shape[1], 3)

    def test_categorical_encoding_label(self):
        """Test label encoding."""
        df = pd.DataFrame({"category": ["A", "B", "A", "C"]})

        encoder = NumericFeatureEncoder(categorical_encoding="label")
        encoder.fit(df, numeric_columns=[], categorical_columns=["category"])

        transformed = encoder.transform(df)

        self.assertEqual(transformed.shape[1], 1)


class TestTemporalFeatureEncoder(unittest.TestCase):
    """Test TemporalFeatureEncoder class."""

    def test_initialization(self):
        """Test initialization."""
        encoder = TemporalFeatureEncoder()
        self.assertIsNotNone(encoder.reference_date)

    def test_encode_datetime(self):
        """Test encoding single datetime."""
        encoder = TemporalFeatureEncoder()
        dt = datetime(2024, 1, 15, 14, 30)

        features = encoder.encode_datetime(dt)

        # Should have cyclical encodings + time diff
        self.assertEqual(len(features), 7)

    def test_cyclical_encoding_range(self):
        """Test cyclical encodings are in valid range."""
        encoder = TemporalFeatureEncoder()
        dt = datetime(2024, 6, 15, 12, 0)

        features = encoder.encode_datetime(dt)

        # Cyclical features should be in [-1, 1]
        for i in range(6):  # First 6 features are cyclical
            self.assertGreaterEqual(features[i], -1.0)
            self.assertLessEqual(features[i], 1.0)

    def test_encode_batch(self):
        """Test batch encoding."""
        encoder = TemporalFeatureEncoder()
        dates = [datetime(2024, 1, 1), datetime(2024, 6, 15), datetime(2024, 12, 31)]

        features = encoder.encode_batch(dates)

        self.assertEqual(features.shape[0], 3)

    def test_encode_timedelta(self):
        """Test timedelta encoding."""
        encoder = TemporalFeatureEncoder()
        td = pd.Timedelta(days=7, hours=3)

        features = encoder.encode_timedelta(td)

        self.assertEqual(len(features), 3)
        self.assertGreater(features[0], 0)  # Seconds


class TestBehaviorFeatureEncoder(unittest.TestCase):
    """Test BehaviorFeatureEncoder class."""

    def test_initialization(self):
        """Test initialization."""
        encoder = BehaviorFeatureEncoder(max_items=50)
        self.assertEqual(encoder.max_items, 50)

    def test_fit(self):
        """Test fitting on item lists."""
        encoder = BehaviorFeatureEncoder(max_items=10)
        item_lists = [["apple", "banana"], ["apple", "orange"], ["banana", "grape"]]

        encoder.fit(item_lists)
        self.assertTrue(encoder.fitted)
        self.assertGreater(len(encoder.item_to_idx), 0)

    def test_encode_items(self):
        """Test encoding item list."""
        encoder = BehaviorFeatureEncoder(max_items=10)
        item_lists = [["apple", "banana", "orange"], ["apple", "grape"]]
        encoder.fit(item_lists)

        vector = encoder.encode_items(["apple", "banana"])

        self.assertEqual(len(vector), 10)
        # Apple and banana should be present
        self.assertGreater(np.sum(vector), 0)

    def test_encode_batch(self):
        """Test batch encoding."""
        encoder = BehaviorFeatureEncoder(max_items=10)
        item_lists = [["apple", "banana"], ["orange", "grape"], ["apple", "orange"]]
        encoder.fit(item_lists)

        vectors = encoder.encode_batch(item_lists)

        self.assertEqual(vectors.shape[0], 3)
        self.assertEqual(vectors.shape[1], 10)

    def test_encode_weighted_items(self):
        """Test weighted item encoding."""
        encoder = BehaviorFeatureEncoder(max_items=10)
        item_lists = [["apple", "banana", "orange"]]
        encoder.fit(item_lists)

        items = ["apple", "banana"]
        weights = [2.0, 1.0]  # Apple has double weight

        vector = encoder.encode_weighted_items(items, weights)

        self.assertEqual(len(vector), 10)
        # Should be normalized
        np.testing.assert_almost_equal(np.linalg.norm(vector), 1.0, decimal=5)


if __name__ == "__main__":
    unittest.main()
