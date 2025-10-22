"""Numeric feature encoding and preprocessing for structured data.

Handles:
- Numerical normalization and scaling
- Categorical encoding
- Temporal features
- Missing value imputation
"""

import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any, Tuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from datetime import datetime


class NumericFeatureEncoder:
    """Encode numeric and categorical features for similarity search.

    Args:
        scaling: Scaling method ('standard', 'minmax', 'robust', or None)
        handle_missing: How to handle missing values ('mean', 'median', 'zero', 'drop')
        categorical_encoding: How to encode categorical ('onehot', 'label', 'frequency')
    """

    def __init__(
        self,
        scaling: str = "standard",
        handle_missing: str = "mean",
        categorical_encoding: str = "onehot",
    ):
        self.scaling = scaling
        self.handle_missing = handle_missing
        self.categorical_encoding = categorical_encoding

        # Initialize scalers and encoders
        self.scaler = None
        self.feature_names = []
        self.categorical_mappings = {}
        self.impute_values = {}
        self.fitted = False

        # Create scaler
        if scaling == "standard":
            self.scaler = StandardScaler()
        elif scaling == "minmax":
            self.scaler = MinMaxScaler()
        elif scaling == "robust":
            self.scaler = RobustScaler()

    def fit(
        self,
        df: pd.DataFrame,
        numeric_columns: Optional[List[str]] = None,
        categorical_columns: Optional[List[str]] = None,
    ):
        """Fit encoder on training data.

        Args:
            df: Input DataFrame
            numeric_columns: List of numeric column names
            categorical_columns: List of categorical column names
        """
        if numeric_columns is None:
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

        if categorical_columns is None:
            categorical_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()

        self.numeric_columns = numeric_columns
        self.categorical_columns = categorical_columns

        # Compute imputation values for numeric columns
        for col in numeric_columns:
            if col not in df.columns:
                continue

            if self.handle_missing == "mean":
                self.impute_values[col] = df[col].mean()
            elif self.handle_missing == "median":
                self.impute_values[col] = df[col].median()
            else:
                self.impute_values[col] = 0.0

        # Fit scaler on numeric data
        if self.scaler and numeric_columns:
            numeric_data = df[numeric_columns].copy()

            # Impute missing values
            for col in numeric_columns:
                if col in df.columns:
                    numeric_data[col] = numeric_data[col].fillna(self.impute_values[col])

            self.scaler.fit(numeric_data)

        # Build categorical mappings
        for col in categorical_columns:
            if col not in df.columns:
                continue

            unique_values = df[col].dropna().unique()

            if self.categorical_encoding == "onehot":
                # Store unique values as a list
                self.categorical_mappings[col] = list(unique_values)
            elif self.categorical_encoding == "label":
                self.categorical_mappings[col] = {val: idx for idx, val in enumerate(unique_values)}
            elif self.categorical_encoding == "frequency":
                value_counts = df[col].value_counts()
                self.categorical_mappings[col] = value_counts.to_dict()

        self.fitted = True

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform DataFrame into feature vectors.

        Args:
            df: Input DataFrame

        Returns:
            Feature matrix of shape (n_samples, n_features)
        """
        if not self.fitted:
            raise ValueError("Encoder not fitted. Call fit() first.")

        features = []

        # Process numeric columns
        if self.numeric_columns:
            numeric_data = df[self.numeric_columns].copy()

            # Impute missing values
            for col in self.numeric_columns:
                if col in numeric_data.columns:
                    numeric_data[col] = numeric_data[col].fillna(self.impute_values[col])

            # Scale
            if self.scaler:
                numeric_features = self.scaler.transform(numeric_data)
            else:
                numeric_features = numeric_data.values

            features.append(numeric_features)

        # Process categorical columns
        if self.categorical_columns:
            categorical_features = self._encode_categorical(df)
            features.append(categorical_features)

        # Concatenate all features
        if features:
            return np.hstack(features)
        else:
            return np.array([])

    def fit_transform(
        self,
        df: pd.DataFrame,
        numeric_columns: Optional[List[str]] = None,
        categorical_columns: Optional[List[str]] = None,
    ) -> np.ndarray:
        """Fit encoder and transform data in one step.

        Args:
            df: Input DataFrame
            numeric_columns: List of numeric column names
            categorical_columns: List of categorical column names

        Returns:
            Feature matrix
        """
        self.fit(df, numeric_columns, categorical_columns)
        return self.transform(df)

    def _encode_categorical(self, df: pd.DataFrame) -> np.ndarray:
        """Encode categorical features.

        Args:
            df: Input DataFrame

        Returns:
            Encoded categorical features
        """
        encoded_features = []

        for col in self.categorical_columns:
            if col not in df.columns:
                continue

            if self.categorical_encoding == "onehot":
                # One-hot encoding
                unique_values = self.categorical_mappings.get(col, [])
                n_values = len(unique_values)

                onehot = np.zeros((len(df), n_values), dtype=np.float32)

                for idx, val in enumerate(df[col]):
                    if pd.notna(val) and val in unique_values:
                        onehot[idx, unique_values.index(val)] = 1.0

                encoded_features.append(onehot)

            elif self.categorical_encoding == "label":
                # Label encoding
                labels = np.zeros(len(df), dtype=np.float32)

                for idx, val in enumerate(df[col]):
                    if pd.notna(val) and val in self.categorical_mappings[col]:
                        labels[idx] = self.categorical_mappings[col][val]

                encoded_features.append(labels.reshape(-1, 1))

            elif self.categorical_encoding == "frequency":
                # Frequency encoding
                freqs = np.zeros(len(df), dtype=np.float32)

                for idx, val in enumerate(df[col]):
                    if pd.notna(val) and val in self.categorical_mappings[col]:
                        freqs[idx] = self.categorical_mappings[col][val]

                # Normalize
                max_freq = max(self.categorical_mappings[col].values())
                if max_freq > 0:
                    freqs = freqs / max_freq

                encoded_features.append(freqs.reshape(-1, 1))

        if encoded_features:
            return np.hstack(encoded_features)
        else:
            return np.array([]).reshape(len(df), 0)


class TemporalFeatureEncoder:
    """Encode temporal features (dates, times) for similarity search.

    Extracts useful temporal patterns like:
    - Day of week
    - Month of year
    - Hour of day
    - Season
    - Time since reference date
    """

    def __init__(self, reference_date: Optional[datetime] = None):
        """Initialize temporal encoder.

        Args:
            reference_date: Reference date for computing time differences
        """
        self.reference_date = reference_date or datetime.now()

    def encode_datetime(self, dt: datetime) -> np.ndarray:
        """Encode a single datetime into features.

        Args:
            dt: Datetime object

        Returns:
            Feature vector with temporal components
        """
        features = []

        # Cyclical encoding of day of week (0-6)
        day_of_week = dt.weekday()
        features.extend([np.sin(2 * np.pi * day_of_week / 7), np.cos(2 * np.pi * day_of_week / 7)])

        # Cyclical encoding of month (1-12)
        month = dt.month
        features.extend([np.sin(2 * np.pi * month / 12), np.cos(2 * np.pi * month / 12)])

        # Cyclical encoding of hour (0-23)
        hour = dt.hour
        features.extend([np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)])

        # Time difference from reference (in days)
        time_diff = (dt - self.reference_date).total_seconds() / 86400
        features.append(time_diff)

        return np.array(features, dtype=np.float32)

    def encode_batch(self, dates: List[datetime]) -> np.ndarray:
        """Encode multiple datetimes.

        Args:
            dates: List of datetime objects

        Returns:
            Feature matrix (n_dates, n_features)
        """
        return np.array([self.encode_datetime(dt) for dt in dates])

    def encode_timedelta(self, td: pd.Timedelta) -> np.ndarray:
        """Encode a timedelta as features.

        Args:
            td: Timedelta object

        Returns:
            Feature vector
        """
        # Convert to different units
        return np.array(
            [
                td.total_seconds(),
                td.total_seconds() / 3600,  # hours
                td.total_seconds() / 86400,  # days
            ],
            dtype=np.float32,
        )


class BehaviorFeatureEncoder:
    """Encode behavioral features like purchase history, interests, etc.

    Useful for customer similarity based on actions and preferences.
    """

    def __init__(self, max_items: int = 100):
        """Initialize behavior encoder.

        Args:
            max_items: Maximum number of items to track
        """
        self.max_items = max_items
        self.item_to_idx = {}
        self.fitted = False

    def fit(self, item_lists: List[List[str]]):
        """Fit encoder on item sequences.

        Args:
            item_lists: List of item lists (e.g., purchased products)
        """
        # Count item frequencies
        from collections import Counter

        all_items = [item for items in item_lists for item in items]
        item_counts = Counter(all_items)

        # Keep most common items
        most_common = item_counts.most_common(self.max_items)
        self.item_to_idx = {item: idx for idx, (item, _) in enumerate(most_common)}

        self.fitted = True

    def encode_items(self, items: List[str]) -> np.ndarray:
        """Encode list of items as binary vector.

        Args:
            items: List of item identifiers

        Returns:
            Binary feature vector
        """
        if not self.fitted:
            raise ValueError("Encoder not fitted. Call fit() first.")

        vector = np.zeros(self.max_items, dtype=np.float32)

        for item in items:
            if item in self.item_to_idx:
                idx = self.item_to_idx[item]
                vector[idx] = 1.0

        return vector

    def encode_batch(self, item_lists: List[List[str]]) -> np.ndarray:
        """Encode multiple item lists.

        Args:
            item_lists: List of item lists

        Returns:
            Feature matrix (n_samples, max_items)
        """
        return np.array([self.encode_items(items) for items in item_lists])

    def encode_weighted_items(self, items: List[str], weights: List[float]) -> np.ndarray:
        """Encode items with weights (e.g., purchase counts, ratings).

        Args:
            items: List of item identifiers
            weights: List of weights for each item

        Returns:
            Weighted feature vector
        """
        if not self.fitted:
            raise ValueError("Encoder not fitted. Call fit() first.")

        vector = np.zeros(self.max_items, dtype=np.float32)

        for item, weight in zip(items, weights):
            if item in self.item_to_idx:
                idx = self.item_to_idx[item]
                vector[idx] += weight

        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector
