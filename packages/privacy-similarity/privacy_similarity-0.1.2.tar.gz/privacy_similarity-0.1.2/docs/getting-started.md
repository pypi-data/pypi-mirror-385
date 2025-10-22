# Getting Started

This guide will help you get up and running with the Privacy-Preserving Similarity Search package.

## Installation

### Basic Installation

```bash
pip install -r requirements.txt
pip install -e .
```

### GPU Support (Optional)

For faster performance on large datasets:

```bash
pip install faiss-gpu
```

### Development Installation

For contributors and developers:

```bash
pip install -e ".[dev]"
```

This installs additional tools:
- pytest (testing)
- pytest-cov (coverage)
- black (code formatting)
- flake8 (linting)
- mypy (type checking)

## Quick Start

### Basic Example

```python
from privacy_similarity import PrivacyPreservingSimilaritySearch
import pandas as pd

# Create sample customer data
df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'name': ['John Smith', 'Jon Smith', 'Jane Doe', 'John A. Smith', 'Alice Johnson'],
    'email': ['john@example.com', 'jon@example.com', 'jane@example.com',
              'jsmith@example.com', 'alice@example.com'],
    'address': ['123 Main St', '123 Main Street', '456 Oak Ave',
                '123 Main St.', '789 Pine Rd'],
    'interests': ['sports, technology', 'tech, sports', 'reading, cooking',
                  'technology, sports', 'cooking, travel']
})

# Initialize with privacy settings
searcher = PrivacyPreservingSimilaritySearch(
    privacy_mode='differential_privacy',
    epsilon=1.0,
    embedding_model='sentence-transformers/all-MiniLM-L6-v2',
    index_type='HNSW'
)

# Fit on your data
searcher.fit(
    df,
    sensitive_columns=['name', 'email', 'address'],
    embedding_columns=['interests'],
    id_column='customer_id'
)

# Find duplicates
duplicates = searcher.find_duplicates(threshold=0.85)
print(f"Found {len(duplicates)} duplicate groups")

# Search for similar records
query_df = pd.DataFrame({
    'name': ['Jonathan Smith'],
    'email': ['j.smith@example.com'],
    'address': ['123 Main Street'],
    'interests': ['sports and tech']
})

results = searcher.search(query_df, k=3)
print(results)
```

## Core Concepts

### 1. Privacy Modes

Choose a privacy mode based on your security requirements:

#### Differential Privacy (Recommended)
- Best balance of privacy and performance
- Provides statistical privacy guarantees
- 1.5-2x overhead

```python
searcher = PrivacyPreservingSimilaritySearch(
    privacy_mode='differential_privacy',
    epsilon=1.0  # Lower = more privacy
)
```

#### Homomorphic Encryption
- Strongest cryptographic guarantees
- Best for highly sensitive data
- 10-100x overhead

```python
searcher = PrivacyPreservingSimilaritySearch(
    privacy_mode='homomorphic',
    encryption_key_size=2048
)
```

#### Secure Hashing
- Fastest option
- Suitable for internal use
- 1x overhead

```python
searcher = PrivacyPreservingSimilaritySearch(
    privacy_mode='secure_hashing',
    salt='your-random-salt-string'
)
```

### 2. Column Types

Specify which columns contain what type of data:

- **sensitive_columns**: PII data (names, emails, addresses) that need privacy protection
- **embedding_columns**: Text data to convert to embeddings (descriptions, interests)
- **numeric_columns**: Numeric features to include in similarity
- **categorical_columns**: Categorical features (will be one-hot encoded)
- **id_column**: Unique identifier for each record

```python
searcher.fit(
    df,
    sensitive_columns=['name', 'email', 'ssn'],
    embedding_columns=['bio', 'interests'],
    numeric_columns=['age', 'income'],
    categorical_columns=['state', 'gender'],
    id_column='customer_id'
)
```

### 3. Index Types

Choose an index type based on your dataset size:

| Index Type | Best For | QPS | Recall | Memory |
|------------|----------|-----|--------|--------|
| Flat | <100K records | Very High | 100% | High |
| HNSW | <10M records | High | >95% | High |
| IVF-HNSW | 10M-1B records | Medium | >90% | Medium |
| IVF-PQ | 1B+ records | Low | >85% | Low |

```python
# Auto-select based on dataset size
searcher = PrivacyPreservingSimilaritySearch(index_type='auto')

# Or specify manually
searcher = PrivacyPreservingSimilaritySearch(index_type='HNSW')
```

## Common Use Cases

### Use Case 1: Customer Deduplication

Find duplicate customer records that might be typos or variations:

```python
# Initialize
searcher = PrivacyPreservingSimilaritySearch(
    privacy_mode='differential_privacy',
    epsilon=1.0
)

# Fit on customer database
searcher.fit(
    customers_df,
    sensitive_columns=['name', 'email', 'phone', 'address'],
    id_column='customer_id'
)

# Find duplicates with 85% similarity threshold
duplicates = searcher.find_duplicates(threshold=0.85)

# Process duplicate groups
for group in duplicates:
    print(f"Duplicate IDs: {group['ids']}")
    print(f"Similarity: {group['similarity']:.2f}")
    # Merge or flag for manual review
```

### Use Case 2: Similar Customer Discovery

Find customers with similar profiles for recommendations:

```python
# Initialize
searcher = PrivacyPreservingSimilaritySearch(
    privacy_mode='differential_privacy',
    epsilon=0.5
)

# Fit on customer profiles
searcher.fit(
    customers_df,
    embedding_columns=['interests', 'purchase_history'],
    numeric_columns=['age', 'lifetime_value'],
    categorical_columns=['segment', 'preferred_category'],
    id_column='customer_id'
)

# Find similar customers
target_customer = customers_df[customers_df['customer_id'] == 12345]
similar = searcher.search(target_customer, k=10)

# Recommend products based on similar customers
print(f"Found {len(similar)} similar customers")
```

### Use Case 3: Incremental Updates

Add new records to an existing index:

```python
# Initial fit
searcher.fit(historical_df, ...)

# Save the index
searcher.save_index('customer_index.faiss')

# Later: Load and add new records
searcher.load_index('customer_index.faiss')
searcher.add_records(new_customers_df)
```

## Performance Optimization

### Batch Processing

For large datasets, process in batches:

```python
searcher.fit_batch(
    large_df,
    batch_size=10000,
    n_jobs=-1  # Use all CPU cores
)
```

### GPU Acceleration

Enable GPU support for faster FAISS operations:

```python
searcher = PrivacyPreservingSimilaritySearch(
    use_gpu=True,
    index_type='IVF-HNSW'
)
```

### Blocking/Filtering

Use blocking to reduce search space:

```python
searcher = PrivacyPreservingSimilaritySearch(
    use_blocking=True,
    blocking_method='lsh',  # or 'clustering'
    n_blocks=100
)
```

## Next Steps

- Learn about [Privacy Modes](privacy.md) in detail
- Understand [Embeddings](embeddings.md) and how they work
- Explore [Blocking Techniques](blocking.md) for scaling
- Review the [API Reference](api-reference.md) for all options

## Troubleshooting

### Common Issues

**Issue**: Out of memory errors
- Solution: Use IVF-PQ index type or increase batch size

**Issue**: Poor recall (missing similar records)
- Solution: Increase epsilon for DP, or use HNSW instead of IVF

**Issue**: Slow performance
- Solution: Enable GPU, use blocking, or switch to IVF-PQ for large datasets

**Issue**: Privacy budget exceeded
- Solution: Increase epsilon or reduce number of queries
