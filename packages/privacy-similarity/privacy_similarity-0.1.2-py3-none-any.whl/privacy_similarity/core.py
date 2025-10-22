"""Main API for privacy-preserving similarity search."""

import numpy as np
import pandas as pd
from typing import List, Optional, Union, Dict, Any
import warnings

from .privacy import DifferentialPrivacy, HomomorphicEncryption, SecureHash
from .embeddings import TextEmbedder, NumericFeatureEncoder, PIITokenizer
from .blocking import LSHBlocker, ClusteringBlocker
from .search import FAISSIndex, SimilaritySearcher
from .utils import (
    normalize_text,
    combine_vectors,
    batch_iterator,
    select_index_type,
    validate_dataframe,
    ProgressTracker,
)


class PrivacyPreservingSimilaritySearch:
    """Privacy-preserving similarity search for massive DataFrames.

    Main class that orchestrates privacy protection, embedding generation,
    blocking, and similarity search for PII-containing DataFrames.

    Args:
        privacy_mode: Privacy protection mode ('differential_privacy', 'homomorphic', 'secure_hashing', 'none')
        epsilon: Differential privacy parameter (lower = more private)
        delta: DP delta parameter
        embedding_model: Sentence transformer model name or 'tfidf'
        index_type: FAISS index type ('HNSW', 'IVF-HNSW', 'IVF-PQ', 'Flat', 'auto')
        use_gpu: Whether to use GPU acceleration
        use_blocking: Whether to use blocking for efficiency
        blocking_method: Blocking method ('lsh', 'clustering')
        salt: Salt for secure hashing (required if privacy_mode='secure_hashing')
        encryption_key_size: Key size for homomorphic encryption

    Example:
        >>> searcher = PrivacyPreservingSimilaritySearch(
        ...     privacy_mode='differential_privacy',
        ...     epsilon=1.0,
        ...     index_type='HNSW'
        ... )
        >>> searcher.fit(df, sensitive_columns=['name', 'email'])
        >>> duplicates = searcher.find_duplicates(threshold=0.85)
    """

    def __init__(
        self,
        privacy_mode: str = "differential_privacy",
        epsilon: float = 1.0,
        delta: float = 1e-5,
        embedding_model: Union[str, Any] = "sentence-transformers/all-MiniLM-L6-v2",
        index_type: str = "auto",
        use_gpu: bool = False,
        use_blocking: bool = False,
        blocking_method: str = "lsh",
        salt: Optional[str] = None,
        encryption_key_size: int = 2048,
    ):
        self.privacy_mode = privacy_mode.lower()
        self.epsilon = epsilon
        self.delta = delta
        self.embedding_model_name = embedding_model
        self.index_type = index_type
        self.use_gpu = use_gpu
        self.use_blocking = use_blocking
        self.blocking_method = blocking_method

        # Initialize privacy module
        if self.privacy_mode == "differential_privacy":
            self.privacy_module = DifferentialPrivacy(
                epsilon=epsilon, delta=delta, mechanism="laplace"
            )
        elif self.privacy_mode == "homomorphic":
            self.privacy_module = HomomorphicEncryption(key_size=encryption_key_size)
        elif self.privacy_mode == "secure_hashing":
            self.privacy_module = SecureHash(salt=salt)
        elif self.privacy_mode == "none":
            self.privacy_module = None
        else:
            raise ValueError(f"Unknown privacy mode: {privacy_mode}")

        # Initialize components (will be configured during fit)
        self.text_embedder = None
        self.numeric_encoder = None
        self.pii_tokenizer = PIITokenizer()
        self.blocker = None
        self.index = None
        self.searcher = None

        # Data storage
        self.fitted = False
        self.embeddings = None
        self.id_mapping = {}
        self.sensitive_columns = []
        self.embedding_columns = []
        self.id_column = None

    def fit(
        self,
        df: pd.DataFrame,
        sensitive_columns: Optional[List[str]] = None,
        embedding_columns: Optional[List[str]] = None,
        numeric_columns: Optional[List[str]] = None,
        id_column: Optional[str] = None,
        batch_size: int = 1000,
    ):
        """Fit the similarity search system on a DataFrame.

        Args:
            df: Input DataFrame
            sensitive_columns: Columns containing PII (names, emails, addresses)
            embedding_columns: Columns to embed (text descriptions, interests)
            numeric_columns: Numeric columns to include
            id_column: Column to use as ID (default: index)
            batch_size: Batch size for processing
        """
        validate_dataframe(df)

        self.sensitive_columns = sensitive_columns or []
        self.embedding_columns = embedding_columns or []
        self.id_column = id_column

        # Extract IDs
        if id_column and id_column in df.columns:
            ids = df[id_column].values
        else:
            ids = np.arange(len(df))

        # Initialize embedders
        if self.embedding_columns:
            self.text_embedder = TextEmbedder(model_name=self.embedding_model_name, normalize=True)

            # Fit TF-IDF if needed
            if self.embedding_model_name == "tfidf":
                all_texts = []
                for col in self.embedding_columns:
                    all_texts.extend(df[col].astype(str).tolist())
                self.text_embedder.fit(all_texts)

        if numeric_columns:
            self.numeric_encoder = NumericFeatureEncoder(scaling="standard", handle_missing="mean")
            self.numeric_encoder.fit(df, numeric_columns=numeric_columns)

        # Generate embeddings
        print("Generating embeddings...")
        all_embeddings = []

        # Process sensitive columns with privacy protection
        if self.sensitive_columns:
            sensitive_embeddings = self._process_sensitive_columns(df, batch_size)
            all_embeddings.append(sensitive_embeddings)

        # Process embedding columns
        if self.embedding_columns:
            embedding_vectors = self._process_embedding_columns(df, batch_size)
            all_embeddings.append(embedding_vectors)

        # Process numeric columns
        if numeric_columns and self.numeric_encoder:
            numeric_vectors = self.numeric_encoder.transform(df)
            all_embeddings.append(numeric_vectors)

        # Combine all embeddings
        if not all_embeddings:
            raise ValueError(
                "No columns to process. Specify sensitive_columns, embedding_columns, or numeric_columns."
            )

        self.embeddings = combine_vectors(all_embeddings, method="concatenate")

        # Select index type if auto
        if self.index_type == "auto":
            self.index_type = select_index_type(len(df), self.embeddings.shape[1])
            print(f"Auto-selected index type: {self.index_type}")

        # Initialize FAISS index
        print(f"Building {self.index_type} index...")
        self.index = FAISSIndex(
            dimension=self.embeddings.shape[1],
            index_type=self.index_type,
            metric="cosine",
            use_gpu=self.use_gpu,
        )

        # Add embeddings to index
        self.index.add(self.embeddings, ids=ids)

        # Build ID mapping
        for i, original_id in enumerate(ids):
            self.id_mapping[i] = original_id

        # Initialize searcher
        self.searcher = SimilaritySearcher(self.index, self.id_mapping)
        self.searcher.store_vectors(self.embeddings, ids.tolist())

        # Initialize blocking if requested
        if self.use_blocking:
            print("Building blocking structure...")
            if self.blocking_method == "lsh":
                self.blocker = LSHBlocker(
                    dimension=self.embeddings.shape[1], num_tables=10, hash_size=8
                )
                self.blocker.index_vectors(self.embeddings, ids.tolist())
            elif self.blocking_method == "clustering":
                n_clusters = min(1000, len(df) // 10)
                self.blocker = ClusteringBlocker(
                    n_clusters=n_clusters, clustering_algorithm="minibatch_kmeans"
                )
                self.blocker.fit(self.embeddings, ids.tolist())

        self.fitted = True
        print(f"✓ Fitted on {len(df)} records")

    def _process_sensitive_columns(self, df: pd.DataFrame, batch_size: int) -> np.ndarray:
        """Process sensitive columns with privacy protection.

        Args:
            df: Input DataFrame
            batch_size: Batch size

        Returns:
            Protected embeddings
        """
        # Combine sensitive fields into single text
        sensitive_texts = []
        for _, row in df.iterrows():
            parts = []
            for col in self.sensitive_columns:
                if col in df.columns:
                    value = str(row[col])

                    # Normalize based on column type
                    if "name" in col.lower():
                        value = self.pii_tokenizer.normalize_name(value)
                    elif "email" in col.lower():
                        value = self.pii_tokenizer.normalize_email(value)
                    elif "address" in col.lower():
                        value = self.pii_tokenizer.normalize_address(value)
                    elif "phone" in col.lower():
                        value = self.pii_tokenizer.normalize_phone(value)

                    parts.append(value)

            sensitive_texts.append(" ".join(parts))

        # Initialize text embedder if needed
        if self.text_embedder is None:
            self.text_embedder = TextEmbedder(
                model_name="tfidf", normalize=True  # Use TF-IDF for PII
            )
            self.text_embedder.fit(sensitive_texts)

        # Generate embeddings
        embeddings = self.text_embedder.encode(sensitive_texts, batch_size=batch_size)

        # Apply privacy protection
        if self.privacy_module:
            if self.privacy_mode == "differential_privacy":
                embeddings = self.privacy_module.transform_batch(embeddings)
            elif self.privacy_mode == "homomorphic":
                # Note: HE is expensive, use selectively
                warnings.warn("Homomorphic encryption adds significant overhead (10-100x)")
                embeddings = self.privacy_module.encrypt_batch(embeddings)
            elif self.privacy_mode == "secure_hashing":
                # Create hash-based representations
                hash_embeddings = []
                for text in sensitive_texts:
                    tokens = text.split()
                    bloom = self.privacy_module.create_bloom_filter(tokens)
                    hash_embeddings.append(bloom / np.linalg.norm(bloom))
                embeddings = np.array(hash_embeddings)

        return embeddings

    def _process_embedding_columns(self, df: pd.DataFrame, batch_size: int) -> np.ndarray:
        """Process embedding columns (non-sensitive text).

        Args:
            df: Input DataFrame
            batch_size: Batch size

        Returns:
            Embeddings
        """
        # Combine embedding columns
        texts = []
        for _, row in df.iterrows():
            parts = [str(row[col]) for col in self.embedding_columns if col in df.columns]
            texts.append(" ".join(parts))

        # Generate embeddings
        embeddings = self.text_embedder.encode(texts, batch_size=batch_size)

        return embeddings

    def search(
        self,
        query_df: pd.DataFrame,
        k: int = 10,
        similarity_threshold: Optional[float] = None,
        return_distances: bool = True,
    ) -> List[Dict]:
        """Search for similar records.

        Args:
            query_df: Query DataFrame with same structure as training data
            k: Number of neighbors to return
            similarity_threshold: Optional threshold to filter results
            return_distances: Whether to return distances

        Returns:
            List of search results
        """
        if not self.fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        # Generate query embeddings (same process as fit)
        query_embeddings = self._generate_query_embeddings(query_df)

        # Search
        results = self.searcher.search(
            query_embeddings,
            k=k,
            similarity_threshold=similarity_threshold,
            return_distances=return_distances,
        )

        return results

    def _generate_query_embeddings(self, df: pd.DataFrame) -> np.ndarray:
        """Generate embeddings for query DataFrame.

        Args:
            df: Query DataFrame

        Returns:
            Query embeddings
        """
        all_embeddings = []

        # Process in same order as fit
        if self.sensitive_columns:
            sensitive_embeddings = self._process_sensitive_columns(df, batch_size=len(df))
            all_embeddings.append(sensitive_embeddings)

        if self.embedding_columns:
            embedding_vectors = self._process_embedding_columns(df, batch_size=len(df))
            all_embeddings.append(embedding_vectors)

        if self.numeric_encoder:
            numeric_vectors = self.numeric_encoder.transform(df)
            all_embeddings.append(numeric_vectors)

        return combine_vectors(all_embeddings, method="concatenate")

    def find_duplicates(self, threshold: float = 0.9, max_cluster_size: int = 100) -> List[Dict]:
        """Find duplicate records.

        Args:
            threshold: Similarity threshold (0-1)
            max_cluster_size: Maximum duplicate cluster size

        Returns:
            List of duplicate groups
        """
        if not self.fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        return self.searcher.find_duplicates(
            threshold=threshold, k=20, max_cluster_size=max_cluster_size
        )

    def add_records(self, df: pd.DataFrame):
        """Add new records to existing index.

        Args:
            df: DataFrame with new records
        """
        if not self.fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        # Generate embeddings for new records
        new_embeddings = self._generate_query_embeddings(df)

        # Extract IDs
        if self.id_column and self.id_column in df.columns:
            ids = df[self.id_column].values
        else:
            # Generate new IDs
            max_id = max(self.id_mapping.values()) if self.id_mapping else 0
            ids = np.arange(max_id + 1, max_id + 1 + len(df))

        # Add to index
        self.index.add(new_embeddings, ids=ids)

        # Update ID mapping
        for i, original_id in enumerate(ids):
            self.id_mapping[len(self.embeddings) + i] = original_id

        # Update stored embeddings
        self.embeddings = np.vstack([self.embeddings, new_embeddings])

        print(f"✓ Added {len(df)} records")

    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics.

        Returns:
            Dictionary with statistics
        """
        stats = {
            "fitted": self.fitted,
            "privacy_mode": self.privacy_mode,
            "index_type": self.index_type,
            "num_records": len(self.embeddings) if self.embeddings is not None else 0,
            "embedding_dimension": self.embeddings.shape[1] if self.embeddings is not None else 0,
        }

        if self.privacy_mode == "differential_privacy" and self.privacy_module:
            stats["epsilon"] = self.epsilon
            stats["delta"] = self.delta

        if self.index:
            stats.update(self.index.get_statistics())

        if self.blocker and self.use_blocking:
            if hasattr(self.blocker, "get_statistics"):
                stats["blocking"] = self.blocker.get_statistics()
            elif hasattr(self.blocker, "get_bucket_statistics"):
                stats["blocking"] = self.blocker.get_bucket_statistics()

        return stats

    def save(self, filepath: str):
        """Save index to disk.

        Args:
            filepath: Path to save index
        """
        if not self.fitted:
            raise ValueError("Model not fitted. Nothing to save.")

        self.index.save(filepath)
        print(f"✓ Saved index to {filepath}")

    def load(self, filepath: str):
        """Load index from disk.

        Args:
            filepath: Path to index file
        """
        if self.index is None:
            # Need to know dimension
            raise ValueError("Initialize with correct dimension first")

        self.index.load(filepath)
        self.fitted = True
        print(f"✓ Loaded index from {filepath}")
