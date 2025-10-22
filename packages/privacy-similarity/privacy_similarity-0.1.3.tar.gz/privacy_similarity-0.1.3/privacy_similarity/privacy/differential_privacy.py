"""Differential Privacy mechanisms for privacy-preserving similarity search.

Implements DP-MinHash, DP-OPH (One Permutation Hashing), and Laplace mechanism
based on research from industry and academia.
"""

import numpy as np
from typing import List, Optional, Union
import hashlib
import mmh3


class DifferentialPrivacy:
    """Differential Privacy transformer for sensitive data.

    Implements multiple DP mechanisms optimized for similarity search:
    - Laplace Mechanism: For numerical data
    - DP-MinHash: For set similarity (Jaccard)
    - DP-OPH: Efficient One Permutation Hashing with DP guarantees

    Args:
        epsilon: Privacy budget parameter. Lower = more private. Typical: 0.1-10.0
        delta: Privacy parameter for (epsilon, delta)-DP. Default: 1e-5
        sensitivity: Global sensitivity of the function. Default: 1.0
        mechanism: Type of DP mechanism ('laplace', 'gaussian', 'minhash', 'oph')
    """

    def __init__(
        self,
        epsilon: float = 1.0,
        delta: float = 1e-5,
        sensitivity: float = 1.0,
        mechanism: str = "laplace",
    ):
        if epsilon <= 0:
            raise ValueError("Epsilon must be positive")
        if delta < 0 or delta >= 1:
            raise ValueError("Delta must be in [0, 1)")

        self.epsilon = epsilon
        self.delta = delta
        self.sensitivity = sensitivity
        self.mechanism = mechanism.lower()

    def transform_vector(self, vector: np.ndarray) -> np.ndarray:
        """Apply differential privacy to a numerical vector.

        Args:
            vector: Input vector of shape (d,)

        Returns:
            DP-protected vector of same shape
        """
        if self.mechanism == "laplace":
            return self._laplace_mechanism(vector)
        elif self.mechanism == "gaussian":
            return self._gaussian_mechanism(vector)
        else:
            raise ValueError(f"Unknown mechanism for vectors: {self.mechanism}")

    def transform_batch(self, vectors: np.ndarray) -> np.ndarray:
        """Apply differential privacy to a batch of vectors.

        Args:
            vectors: Input vectors of shape (n, d)

        Returns:
            DP-protected vectors of same shape
        """
        return np.array([self.transform_vector(v) for v in vectors])

    def _laplace_mechanism(self, vector: np.ndarray) -> np.ndarray:
        """Add Laplace noise to vector.

        Scale = sensitivity / epsilon
        """
        scale = self.sensitivity / self.epsilon
        noise = np.random.laplace(0, scale, size=vector.shape)
        return vector + noise

    def _gaussian_mechanism(self, vector: np.ndarray) -> np.ndarray:
        """Add Gaussian noise to vector for (epsilon, delta)-DP.

        Standard deviation = sensitivity * sqrt(2 * log(1.25/delta)) / epsilon
        """
        sigma = self.sensitivity * np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
        noise = np.random.normal(0, sigma, size=vector.shape)
        return vector + noise

    def minhash_sketch(
        self, tokens: List[str], num_hashes: int = 128, add_noise: bool = True
    ) -> np.ndarray:
        """Create DP-MinHash sketch for set similarity.

        Based on "Differentially Private MinHash for Large-Scale Set Similarity Queries"

        Args:
            tokens: List of tokens/n-grams from text
            num_hashes: Number of hash functions (sketch size)
            add_noise: Whether to add DP noise

        Returns:
            MinHash signature of shape (num_hashes,)
        """
        if not tokens:
            return np.zeros(num_hashes, dtype=np.float32)

        # Generate MinHash signature
        signature = np.full(num_hashes, np.inf, dtype=np.float32)

        for token in tokens:
            for i in range(num_hashes):
                # Use MurmurHash3 with different seeds
                hash_val = abs(mmh3.hash(token, seed=i)) / (2**31 - 1)  # Normalize to [0, 1]
                signature[i] = min(signature[i], hash_val)

        if add_noise:
            # Add DP noise using Generalized Randomized Response
            signature = self._add_minhash_noise(signature)

        return signature

    def _add_minhash_noise(self, signature: np.ndarray) -> np.ndarray:
        """Add differential privacy noise to MinHash signature.

        Uses Generalized Randomized Response mechanism.
        """
        # Probability of keeping original value
        p_keep = np.exp(self.epsilon) / (1 + np.exp(self.epsilon))

        # Randomly flip some hash values
        mask = np.random.random(len(signature)) < p_keep
        noisy_signature = signature.copy()

        # Replace flipped values with random hashes
        noisy_signature[~mask] = np.random.random(np.sum(~mask))

        return noisy_signature

    def oph_sketch(
        self, tokens: List[str], num_bins: int = 128, bin_size: int = 4, add_noise: bool = True
    ) -> np.ndarray:
        """Create DP-OPH (One Permutation Hashing) sketch.

        More efficient than DP-MinHash while maintaining similar guarantees.
        Based on "Privacy-Preserving MinHash and Consistent Weighted Sampling"

        Args:
            tokens: List of tokens/n-grams from text
            num_bins: Number of bins to split data into
            bin_size: Size of each bin
            add_noise: Whether to add DP noise

        Returns:
            OPH signature of shape (num_bins * bin_size,)
        """
        if not tokens:
            return np.zeros(num_bins * bin_size, dtype=np.float32)

        # Initialize bins
        bins = [[] for _ in range(num_bins)]

        # Hash each token into a bin
        for token in tokens:
            bin_idx = mmh3.hash(token, seed=0) % num_bins
            hash_val = mmh3.hash(token, seed=1) / (2**31 - 1)
            bins[bin_idx].append(hash_val)

        # Create signature from minimum values in each bin
        signature = []
        for bin_vals in bins:
            if bin_vals:
                sorted_vals = sorted(bin_vals)[:bin_size]
                # Pad if needed
                while len(sorted_vals) < bin_size:
                    sorted_vals.append(1.0)  # Maximum hash value
                signature.extend(sorted_vals)
            else:
                signature.extend([1.0] * bin_size)

        signature = np.array(signature, dtype=np.float32)

        if add_noise:
            # Add DP noise
            signature = self._add_minhash_noise(signature)

        return signature

    def get_privacy_budget(self) -> tuple:
        """Return the privacy budget (epsilon, delta)."""
        return (self.epsilon, self.delta)

    def estimate_noise_magnitude(self, dimension: int) -> float:
        """Estimate the magnitude of noise added to vectors.

        Args:
            dimension: Dimensionality of vectors

        Returns:
            Expected L2 norm of noise
        """
        if self.mechanism == "laplace":
            scale = self.sensitivity / self.epsilon
            # Expected L2 norm of Laplace noise
            return scale * np.sqrt(2 * dimension)
        elif self.mechanism == "gaussian":
            sigma = self.sensitivity * np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
            # Expected L2 norm of Gaussian noise
            return sigma * np.sqrt(dimension)
        else:
            return 0.0
