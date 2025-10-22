# API Reference

Complete API documentation for the Privacy-Preserving Similarity Search package.

## Core API

### Class: `PrivacyPreservingSimilaritySearch`

Main interface for privacy-preserving similarity search.

**Module:** `privacy_similarity.core`

**Import:**
```python
from privacy_similarity import PrivacyPreservingSimilaritySearch
```

#### Constructor

```python
PrivacyPreservingSimilaritySearch(
    privacy_mode: str = 'differential_privacy',
    epsilon: float = 1.0,
    delta: float = 1e-5,
    encryption_key_size: int = 2048,
    salt: str = None,
    embedding_model: Union[str, object] = 'sentence-transformers/all-MiniLM-L6-v2',
    index_type: str = 'auto',
    use_gpu: bool = False,
    use_blocking: bool = False,
    blocking_method: str = 'lsh',
    n_blocks: int = 100,
    verbose: bool = True,
    **kwargs
)
```

**Parameters:**

**Privacy Parameters:**
- `privacy_mode` (str): Privacy protection method
  - `'differential_privacy'`: Statistical privacy guarantees (recommended)
  - `'homomorphic'`: Cryptographic encryption
  - `'secure_hashing'`: One-way hashing
  - `'none'`: No privacy protection
  - Default: `'differential_privacy'`

- `epsilon` (float): Differential privacy budget
  - Lower = more privacy, less accuracy
  - Range: 0.1 (high privacy) to 10.0 (low privacy)
  - Default: 1.0

- `delta` (float): DP failure probability
  - Default: 1e-5

- `encryption_key_size` (int): Homomorphic encryption key size in bits
  - Options: 1024, 2048, 4096
  - Default: 2048

- `salt` (str): Random salt for secure hashing
  - Required if `privacy_mode='secure_hashing'`
  - Default: None

**Embedding Parameters:**
- `embedding_model` (str or object): Sentence Transformer model
  - String: Hugging Face model name
  - Object: Pre-loaded SentenceTransformer instance
  - Default: `'sentence-transformers/all-MiniLM-L6-v2'`

**Search Parameters:**
- `index_type` (str): FAISS index type
  - `'auto'`: Auto-select based on dataset size
  - `'Flat'`: Exact search (small datasets)
  - `'HNSW'`: Graph-based ANN (<10M vectors)
  - `'IVF'`: Inverted file (>1M vectors)
  - `'IVF-HNSW'`: Hybrid (10M-1B vectors)
  - `'IVF-PQ'`: Compressed (>100M vectors)
  - Default: `'auto'`

- `use_gpu` (bool): Enable GPU acceleration
  - Requires `faiss-gpu` package
  - Default: False

**Blocking Parameters:**
- `use_blocking` (bool): Enable blocking for scalability
  - Default: False

- `blocking_method` (str): Blocking technique
  - `'lsh'`: Locality-sensitive hashing
  - `'clustering'`: K-means clustering
  - Default: `'lsh'`

- `n_blocks` (int): Number of blocks/clusters
  - Default: 100

**Other Parameters:**
- `verbose` (bool): Print progress messages
  - Default: True

- `**kwargs`: Additional parameters passed to index or blocking

**Example:**
```python
searcher = PrivacyPreservingSimilaritySearch(
    privacy_mode='differential_privacy',
    epsilon=1.0,
    embedding_model='sentence-transformers/all-MiniLM-L6-v2',
    index_type='HNSW',
    use_gpu=False,
    verbose=True
)
```

---

### Methods

#### `fit()`

Fits the model on a DataFrame.

```python
fit(
    df: pd.DataFrame,
    sensitive_columns: List[str] = None,
    embedding_columns: List[str] = None,
    numeric_columns: List[str] = None,
    categorical_columns: List[str] = None,
    id_column: str = None,
    batch_size: int = 1000
) -> None
```

**Parameters:**
- `df` (pd.DataFrame): Input DataFrame with records
- `sensitive_columns` (List[str]): PII columns (names, emails, etc.)
  - Will be privacy-protected and tokenized
  - Optional, default: []
- `embedding_columns` (List[str]): Text columns to embed
  - Converted to dense vectors using transformer model
  - Optional, default: []
- `numeric_columns` (List[str]): Numeric features
  - Will be scaled and normalized
  - Optional, default: []
- `categorical_columns` (List[str]): Categorical features
  - Will be one-hot or target encoded
  - Optional, default: []
- `id_column` (str): Unique identifier column
  - Used to map results back to records
  - Optional, default: uses DataFrame index
- `batch_size` (int): Batch size for processing
  - Default: 1000

**Returns:** None

**Side Effects:**
- Builds FAISS index
- Stores column mappings and encoders
- Computes privacy protections

**Example:**
```python
import pandas as pd

df = pd.DataFrame({
    'customer_id': [1, 2, 3],
    'name': ['John Smith', 'Jane Doe', 'Bob Johnson'],
    'email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
    'bio': ['Tech enthusiast', 'Avid reader', 'Sports fan'],
    'age': [25, 30, 35],
    'state': ['CA', 'NY', 'TX']
})

searcher.fit(
    df,
    sensitive_columns=['name', 'email'],
    embedding_columns=['bio'],
    numeric_columns=['age'],
    categorical_columns=['state'],
    id_column='customer_id'
)
```

**Notes:**
- At least one of `sensitive_columns`, `embedding_columns`, `numeric_columns`, or `categorical_columns` must be specified
- All specified columns must exist in DataFrame
- Missing values are handled automatically (mean imputation for numeric, mode for categorical)

---

#### `search()`

Searches for similar records.

```python
search(
    query_df: pd.DataFrame,
    k: int = 10,
    similarity_threshold: float = 0.0,
    return_distances: bool = True
) -> pd.DataFrame
```

**Parameters:**
- `query_df` (pd.DataFrame): Query records
  - Must have same columns as training data
  - Can contain one or more rows
- `k` (int): Number of neighbors to return per query
  - Default: 10
- `similarity_threshold` (float): Minimum similarity score
  - Range: 0.0 to 1.0
  - Only return results above threshold
  - Default: 0.0 (no filtering)
- `return_distances` (bool): Include distance/similarity scores
  - Default: True

**Returns:**
- pd.DataFrame with columns:
  - `query_id`: Query record identifier
  - `result_id`: Matched record identifier
  - `distance`: L2 distance (if return_distances=True)
  - `similarity`: Cosine similarity (if return_distances=True)
  - Additional columns from original DataFrame

**Example:**
```python
query = pd.DataFrame({
    'name': ['Jon Smith'],
    'email': ['j.smith@example.com'],
    'bio': ['Technology lover'],
    'age': [26],
    'state': ['CA']
})

results = searcher.search(query, k=5, similarity_threshold=0.7)
print(results)
```

**Output:**
```
   query_id  result_id  distance  similarity         name              email
0         0          1     0.234       0.876   John Smith   john@example.com
1         0          2     0.456       0.723   Jane Doe     jane@example.com
```

**Notes:**
- Automatically applies same privacy protection as training data
- Similarity = 1 - (distance / max_distance) approximately
- Results sorted by distance (ascending)

---

#### `find_duplicates()`

Finds duplicate record groups.

```python
find_duplicates(
    threshold: float = 0.85,
    max_cluster_size: int = 100
) -> List[Dict[str, Any]]
```

**Parameters:**
- `threshold` (float): Similarity threshold for duplicates
  - Range: 0.0 to 1.0
  - Higher = more strict matching
  - Default: 0.85
- `max_cluster_size` (int): Maximum records per cluster
  - Prevents huge clusters from errors
  - Default: 100

**Returns:**
- List of dictionaries, each containing:
  - `'ids'`: List of record IDs in cluster
  - `'size'`: Number of records
  - `'similarity'`: Average similarity within cluster

**Example:**
```python
duplicates = searcher.find_duplicates(threshold=0.85)

for group in duplicates:
    print(f"Found {group['size']} duplicates:")
    print(f"  IDs: {group['ids']}")
    print(f"  Avg similarity: {group['similarity']:.3f}")
```

**Output:**
```
Found 3 duplicates:
  IDs: [1, 2, 4]
  Avg similarity: 0.891
Found 2 duplicates:
  IDs: [5, 7]
  Avg similarity: 0.876
```

**Algorithm:**
1. Compute all pairwise similarities above threshold
2. Build graph of similar pairs
3. Find connected components (transitive closure)
4. Return components as duplicate groups

**Notes:**
- Runs on fitted data only (not query data)
- Computationally intensive for large datasets (use blocking)
- Uses transitive matching: if A~B and B~C, then A, B, C are all duplicates

---

#### `add_records()`

Adds new records to existing index.

```python
add_records(
    df: pd.DataFrame,
    batch_size: int = 1000
) -> None
```

**Parameters:**
- `df` (pd.DataFrame): New records to add
  - Must have same columns as original fit() data
- `batch_size` (int): Batch size for processing
  - Default: 1000

**Returns:** None

**Side Effects:**
- Adds vectors to FAISS index
- Updates ID mappings

**Example:**
```python
# Initial fit
searcher.fit(initial_df, ...)

# Later: add more records
new_df = pd.DataFrame({
    'customer_id': [100, 101],
    'name': ['Alice Brown', 'Charlie Green'],
    # ... other columns
})
searcher.add_records(new_df)

# Now can search including new records
results = searcher.search(query_df)
```

**Limitations:**
- Not all index types support adding (e.g., HNSW)
- Does not retrain quantizers (for IVF indices)
- For large additions, consider refitting from scratch

---

#### `save_index()`

Saves the fitted model to disk.

```python
save_index(
    path: str
) -> None
```

**Parameters:**
- `path` (str): File path to save
  - Can be absolute or relative
  - Recommended extension: `.index` or `.faiss`

**Returns:** None

**What's saved:**
- FAISS index
- ID mappings
- Column information
- Encoders and scalers
- Model configuration

**Example:**
```python
searcher.fit(df, ...)
searcher.save_index('models/customer_similarity.index')
```

**File size:**
- Depends on index type and data size
- Approximate: n_vectors × dimension × 4 bytes
- Example: 1M vectors × 384D = ~1.5GB

---

#### `load_index()`

Loads a saved model from disk.

```python
load_index(
    path: str
) -> None
```

**Parameters:**
- `path` (str): File path to load

**Returns:** None

**Side Effects:**
- Restores all model state
- Ready to search immediately

**Example:**
```python
# In another session
new_searcher = PrivacyPreservingSimilaritySearch()
new_searcher.load_index('models/customer_similarity.index')

# Ready to use
results = new_searcher.search(query_df)
```

**Notes:**
- Must use compatible FAISS version
- GPU/CPU compatibility: GPU index can be loaded on CPU (slower)
- Privacy mode and parameters are restored automatically

---

#### `get_statistics()`

Returns statistics about the fitted model.

```python
get_statistics() -> Dict[str, Any]
```

**Returns:**
- Dictionary with:
  - `'n_vectors'`: Number of indexed vectors
  - `'dimension'`: Vector dimension
  - `'index_type'`: FAISS index type
  - `'memory_usage'`: Approximate memory in bytes
  - `'privacy_mode'`: Privacy protection method
  - `'epsilon'`: Privacy budget (if applicable)

**Example:**
```python
stats = searcher.get_statistics()
print(f"Indexed {stats['n_vectors']} vectors")
print(f"Dimension: {stats['dimension']}")
print(f"Memory: {stats['memory_usage'] / 1e9:.2f} GB")
```

---

#### `evaluate_recall()`

Evaluates search recall against ground truth.

```python
evaluate_recall(
    queries: pd.DataFrame,
    ground_truth: List[List[int]],
    k: int = 10
) -> Dict[str, float]
```

**Parameters:**
- `queries` (pd.DataFrame): Query records
- `ground_truth` (List[List[int]]): True neighbors for each query
  - `ground_truth[i]` = list of true neighbor IDs for query i
- `k` (int): Evaluate recall@k
  - Default: 10

**Returns:**
- Dictionary with:
  - `'recall@k'`: Proportion of true neighbors found
  - `'precision@k'`: Proportion of returned neighbors that are true
  - `'f1@k'`: Harmonic mean of precision and recall

**Example:**
```python
# Ground truth: manually labeled or from exact search
ground_truth = [
    [1, 5, 7, 9],     # True neighbors for query 0
    [2, 3, 8],        # True neighbors for query 1
    # ...
]

metrics = searcher.evaluate_recall(queries, ground_truth, k=10)
print(f"Recall@10: {metrics['recall@10']:.2%}")
print(f"Precision@10: {metrics['precision@10']:.2%}")
```

---

## Workflow Examples

### Basic Workflow

```python
from privacy_similarity import PrivacyPreservingSimilaritySearch
import pandas as pd

# 1. Initialize
searcher = PrivacyPreservingSimilaritySearch(
    privacy_mode='differential_privacy',
    epsilon=1.0,
    index_type='auto'
)

# 2. Fit on data
df = pd.read_csv('customers.csv')
searcher.fit(
    df,
    sensitive_columns=['name', 'email'],
    embedding_columns=['bio', 'interests'],
    id_column='customer_id'
)

# 3. Search
query_df = pd.DataFrame({...})
results = searcher.search(query_df, k=10)

# 4. Find duplicates
duplicates = searcher.find_duplicates(threshold=0.85)

# 5. Save for later
searcher.save_index('model.index')
```

### Production Workflow

```python
# Training pipeline
def train_similarity_model(df, output_path):
    searcher = PrivacyPreservingSimilaritySearch(
        privacy_mode='differential_privacy',
        epsilon=1.0,
        index_type='IVF-HNSW',
        use_gpu=True,
        use_blocking=True,
        verbose=True
    )

    searcher.fit(
        df,
        sensitive_columns=['name', 'email', 'phone'],
        embedding_columns=['description', 'notes'],
        numeric_columns=['age', 'income'],
        categorical_columns=['state', 'segment'],
        id_column='customer_id',
        batch_size=10000
    )

    searcher.save_index(output_path)
    return searcher.get_statistics()

# Inference pipeline
def find_similar_customers(query_id, k=10):
    # Load once (cache globally in production)
    searcher = PrivacyPreservingSimilaritySearch()
    searcher.load_index('production_model.index')

    # Get query customer
    query_df = get_customer_by_id(query_id)

    # Search
    results = searcher.search(query_df, k=k, similarity_threshold=0.7)

    return results

# Deduplication pipeline
def deduplicate_database(df):
    searcher = PrivacyPreservingSimilaritySearch(
        privacy_mode='differential_privacy',
        epsilon=0.5,  # High privacy for deduplication
        index_type='HNSW'
    )

    searcher.fit(df, ...)
    duplicates = searcher.find_duplicates(threshold=0.9)

    # Merge duplicates (keep first ID in each group)
    for group in duplicates:
        primary_id = group['ids'][0]
        duplicate_ids = group['ids'][1:]
        merge_customers(primary_id, duplicate_ids)

    return duplicates
```

### Incremental Update Workflow

```python
# Initial build
searcher = PrivacyPreservingSimilaritySearch(index_type='IVF')
searcher.fit(historical_df, ...)
searcher.save_index('base_model.index')

# Daily updates
def daily_update(new_records_df):
    searcher = PrivacyPreservingSimilaritySearch()
    searcher.load_index('base_model.index')

    # Add new records
    searcher.add_records(new_records_df)

    # Save updated model
    searcher.save_index('base_model.index')

# Weekly full rebuild (for better index quality)
def weekly_rebuild():
    all_data = load_all_data()
    searcher = PrivacyPreservingSimilaritySearch(index_type='IVF')
    searcher.fit(all_data, ...)
    searcher.save_index('base_model.index')
```

## Configuration Best Practices

### Privacy Levels

**High Privacy (Healthcare, Finance):**
```python
searcher = PrivacyPreservingSimilaritySearch(
    privacy_mode='homomorphic',  # or 'differential_privacy' with low epsilon
    epsilon=0.1,
    encryption_key_size=4096
)
```

**Medium Privacy (Customer Data):**
```python
searcher = PrivacyPreservingSimilaritySearch(
    privacy_mode='differential_privacy',
    epsilon=1.0
)
```

**Low Privacy (Internal, Public Data):**
```python
searcher = PrivacyPreservingSimilaritySearch(
    privacy_mode='secure_hashing',
    salt='random-salt-string'
)
```

### Performance Optimization

**Small Dataset (<100K):**
```python
searcher = PrivacyPreservingSimilaritySearch(
    index_type='Flat',  # Exact, fast enough
    use_blocking=False
)
```

**Medium Dataset (100K-10M):**
```python
searcher = PrivacyPreservingSimilaritySearch(
    index_type='HNSW',
    use_blocking=False,
    use_gpu=True  # If available
)
```

**Large Dataset (>10M):**
```python
searcher = PrivacyPreservingSimilaritySearch(
    index_type='IVF-HNSW',
    use_blocking=True,
    blocking_method='lsh',
    n_blocks=1000,
    use_gpu=True
)
```

**Very Large Dataset (>100M):**
```python
searcher = PrivacyPreservingSimilaritySearch(
    index_type='IVF-PQ',
    use_blocking=True,
    blocking_method='clustering',
    n_blocks=10000,
    use_gpu=True
)
```

## Error Handling

Common exceptions and how to handle them:

```python
from privacy_similarity.exceptions import (
    PrivacyBudgetExhausted,
    IndexNotFittedError,
    IncompatibleDataError
)

try:
    searcher.fit(df, ...)
except IncompatibleDataError as e:
    print(f"Data validation failed: {e}")
    # Check column names, types, missing values

try:
    results = searcher.search(query_df)
except IndexNotFittedError:
    print("Must call fit() before search()")
    searcher.fit(df, ...)

try:
    # After many queries
    results = searcher.search(query_df)
except PrivacyBudgetExhausted:
    print("Privacy budget exhausted, create new index")
    # Option 1: Increase epsilon
    # Option 2: Create fresh index
    # Option 3: Use different privacy mode
```

## Performance Monitoring

Track performance in production:

```python
import time

# Search latency
start = time.time()
results = searcher.search(query_df, k=10)
latency = time.time() - start
print(f"Search latency: {latency*1000:.2f}ms")

# Throughput
n_queries = 1000
start = time.time()
for query in queries:
    searcher.search(query, k=10)
duration = time.time() - start
qps = n_queries / duration
print(f"Throughput: {qps:.0f} QPS")

# Memory usage
stats = searcher.get_statistics()
memory_gb = stats['memory_usage'] / 1e9
print(f"Memory usage: {memory_gb:.2f} GB")

# Index quality
metrics = searcher.evaluate_recall(val_queries, ground_truth, k=10)
print(f"Recall@10: {metrics['recall@10']:.2%}")
```

## Version Compatibility

This package requires:
- Python ≥ 3.8
- NumPy ≥ 1.20.0
- Pandas ≥ 1.3.0
- FAISS ≥ 1.7.0
- Sentence-Transformers ≥ 2.2.0

Check version:
```python
import privacy_similarity
print(privacy_similarity.__version__)  # e.g., '0.1.0'
```
