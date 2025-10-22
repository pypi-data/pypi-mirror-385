"""Text embedding generation using pre-trained models and traditional methods.

Supports:
- Sentence Transformers (BERT, RoBERTa, etc.)
- TF-IDF
- Character n-grams for fuzzy matching
- Custom tokenization for PII fields
"""

import numpy as np
from typing import List, Optional, Union
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter


class TextEmbedder:
    """Text embedding generator with multiple backend options.

    Args:
        model_name: Name of sentence-transformers model or 'tfidf'
        normalize: Whether to L2-normalize embeddings
        max_length: Maximum sequence length for transformers
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        normalize: bool = True,
        max_length: int = 128,
    ):
        self.model_name = model_name
        self.normalize = normalize
        self.max_length = max_length
        self.model = None
        self.tfidf = None
        self.fitted = False

        # Initialize model
        if model_name == "tfidf":
            self.backend = "tfidf"
            self.tfidf = TfidfVectorizer(
                max_features=512,
                ngram_range=(1, 3),
                analyzer="char_wb",  # Character n-grams for fuzzy matching
            )
        else:
            self.backend = "transformer"
            self._load_transformer_model()

    def _load_transformer_model(self):
        """Load sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(self.model_name)
            self.fitted = True
        except ImportError:
            raise ImportError(
                "sentence-transformers is required. "
                "Install with: pip install sentence-transformers"
            )

    def fit(self, texts: List[str]):
        """Fit the embedder on training texts (required for TF-IDF).

        Args:
            texts: List of text strings
        """
        if self.backend == "tfidf":
            self.tfidf.fit(texts)
            self.fitted = True
        # Transformer models don't need fitting

    def encode(
        self, texts: Union[str, List[str]], batch_size: int = 32, show_progress: bool = False
    ) -> np.ndarray:
        """Encode texts into embeddings.

        Args:
            texts: Single text or list of texts
            batch_size: Batch size for processing
            show_progress: Show progress bar

        Returns:
            Embeddings of shape (n, d) or (d,) for single text
        """
        if isinstance(texts, str):
            texts = [texts]
            single = True
        else:
            single = False

        if not self.fitted:
            raise ValueError("Model not fitted. Call fit() first for TF-IDF.")

        # Generate embeddings
        if self.backend == "transformer":
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                normalize_embeddings=self.normalize,
            )
        else:  # tfidf
            embeddings = self.tfidf.transform(texts).toarray()
            if self.normalize:
                norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                norms[norms == 0] = 1  # Avoid division by zero
                embeddings = embeddings / norms

        if single:
            return embeddings[0]

        return embeddings

    def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode a batch of texts efficiently.

        Args:
            texts: List of text strings
            batch_size: Batch size for processing

        Returns:
            Embeddings of shape (n, d)
        """
        return self.encode(texts, batch_size=batch_size)

    @property
    def embedding_dimension(self) -> int:
        """Get dimensionality of embeddings."""
        if self.backend == "transformer":
            return self.model.get_sentence_embedding_dimension()
        else:
            if not self.fitted:
                raise ValueError("TF-IDF not fitted yet")
            return self.tfidf.max_features


class PIITokenizer:
    """Specialized tokenizer for PII fields like names, addresses, emails.

    Handles:
    - Name normalization (case, punctuation, titles)
    - Address parsing (street, city, zip)
    - Email normalization
    - Phone number normalization
    """

    def __init__(self):
        # Common name prefixes and suffixes
        self.name_prefixes = {"mr", "mrs", "ms", "dr", "prof"}
        self.name_suffixes = {"jr", "sr", "ii", "iii", "iv", "phd", "md"}

    def normalize_name(self, name: str) -> str:
        """Normalize a person's name.

        Args:
            name: Raw name string

        Returns:
            Normalized name
        """
        # Convert to lowercase
        name = name.lower().strip()

        # Remove punctuation except hyphens
        name = re.sub(r"[^\w\s\-]", "", name)

        # Remove prefixes and suffixes
        tokens = name.split()
        tokens = [t for t in tokens if t not in self.name_prefixes and t not in self.name_suffixes]

        return " ".join(tokens)

    def normalize_email(self, email: str) -> str:
        """Normalize email address.

        Args:
            email: Raw email string

        Returns:
            Normalized email
        """
        email = email.lower().strip()

        # Remove common aliases (everything after +)
        if "+" in email:
            local, domain = email.split("@")
            local = local.split("+")[0]
            email = f"{local}@{domain}"

        # Remove dots from Gmail addresses
        if email.endswith("@gmail.com"):
            local = email.split("@")[0].replace(".", "")
            email = f"{local}@gmail.com"

        return email

    def normalize_address(self, address: str) -> str:
        """Normalize street address.

        Args:
            address: Raw address string

        Returns:
            Normalized address
        """
        # Convert to lowercase
        address = address.lower().strip()

        # Standardize common abbreviations
        abbreviations = {
            "street": "st",
            "avenue": "ave",
            "road": "rd",
            "boulevard": "blvd",
            "drive": "dr",
            "lane": "ln",
            "court": "ct",
            "place": "pl",
            "apartment": "apt",
            "suite": "ste",
        }

        for full, abbr in abbreviations.items():
            address = re.sub(rf"\b{full}\b", abbr, address)

        # Remove extra whitespace and punctuation
        address = re.sub(r"[^\w\s]", "", address)
        address = re.sub(r"\s+", " ", address)

        return address

    def normalize_phone(self, phone: str) -> str:
        """Normalize phone number.

        Args:
            phone: Raw phone number

        Returns:
            Normalized phone (digits only)
        """
        # Keep only digits
        digits = re.sub(r"\D", "", phone)

        # Remove country code if present (assume US)
        if len(digits) == 11 and digits[0] == "1":
            digits = digits[1:]

        return digits

    def tokenize_name(self, name: str) -> List[str]:
        """Tokenize name into components.

        Args:
            name: Normalized name

        Returns:
            List of name tokens
        """
        normalized = self.normalize_name(name)
        tokens = normalized.split()

        # Add character n-grams for fuzzy matching
        char_ngrams = []
        for token in tokens:
            if len(token) >= 3:
                for i in range(len(token) - 2):
                    char_ngrams.append(token[i : i + 3])

        return tokens + char_ngrams


class CharacterNGramEmbedder:
    """Character n-gram based embeddings for fuzzy string matching.

    Useful for matching names, addresses with typos or variations.
    """

    def __init__(self, n: int = 3, vector_size: int = 256):
        """Initialize n-gram embedder.

        Args:
            n: N-gram size (default: 3 for trigrams)
            vector_size: Dimensionality of output vectors
        """
        self.n = n
        self.vector_size = vector_size
        self.vocab = {}
        self.fitted = False

    def fit(self, texts: List[str]):
        """Build n-gram vocabulary from texts.

        Args:
            texts: List of text strings
        """
        all_ngrams = []

        for text in texts:
            text = text.lower()
            ngrams = self._extract_ngrams(text)
            all_ngrams.extend(ngrams)

        # Keep most common n-grams
        ngram_counts = Counter(all_ngrams)
        most_common = ngram_counts.most_common(self.vector_size)

        self.vocab = {ngram: idx for idx, (ngram, _) in enumerate(most_common)}
        self.fitted = True

    def _extract_ngrams(self, text: str) -> List[str]:
        """Extract character n-grams from text.

        Args:
            text: Input text

        Returns:
            List of n-grams
        """
        # Pad text
        padded = f"_{text}_"
        ngrams = []

        for i in range(len(padded) - self.n + 1):
            ngrams.append(padded[i : i + self.n])

        return ngrams

    def encode(self, text: str) -> np.ndarray:
        """Encode text as n-gram vector.

        Args:
            text: Input text

        Returns:
            Binary vector indicating n-gram presence
        """
        if not self.fitted:
            raise ValueError("Embedder not fitted. Call fit() first.")

        vector = np.zeros(self.vector_size, dtype=np.float32)
        text = text.lower()
        ngrams = self._extract_ngrams(text)

        for ngram in ngrams:
            if ngram in self.vocab:
                idx = self.vocab[ngram]
                vector[idx] = 1.0

        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector

    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode multiple texts.

        Args:
            texts: List of text strings

        Returns:
            Matrix of n-gram vectors (n, vector_size)
        """
        return np.array([self.encode(text) for text in texts])
