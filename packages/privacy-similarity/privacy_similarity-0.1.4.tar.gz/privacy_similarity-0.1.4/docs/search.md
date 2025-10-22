# Search Module

The search module provides fast similarity search using Facebook AI Similarity Search (FAISS) library.

## Overview

FAISS is a library for efficient similarity search and clustering of dense vectors, developed by Facebook AI Research. It powers similarity search at billion-scale for companies like Meta, Spotify, and Airbnb.

**Key Features:**
- **Multiple Index Types**: Flat (exact), HNSW (graph), IVF (inverted file)
- **GPU Support**: 5-10x speedup with CUDA
- **Scalability**: Billion-scale vector search
- **Memory Efficiency**: Quantization techniques (PQ, SQ)

### Module: `privacy_similarity.search.similarity`

## Index Types

FAISS provides several index types optimized for different use cases.

### Flat Index (Exact Search)

Brute-force exact nearest neighbor search.

**Class:** `FlatIndex`

**When to use:**
- Dataset <100K vectors
- Need 100% recall
- Have sufficient memory

**Performance:**
- Query time: O(n × d) where n=vectors, d=dimensions
- Memory: n × d × 4 bytes (for float32)
- Recall: 100%

**Example:**
```python
from privacy_similarity.search import SimilaritySearcher

searcher = SimilaritySearcher(index_type='Flat', dimension=384)
searcher.fit(vectors)  # vectors: (n_samples, 384)
distances, indices = searcher.search(query_vectors, k=10)
```

**Trade-offs:**
- ✅ Perfect accuracy
- ✅ Simple, no parameters to tune
- ❌ Slow for large datasets
- ❌ High memory usage

### HNSW Index (Hierarchical Navigable Small World)

Graph-based approximate nearest neighbor search.

**Class:** `HNSWIndex`

**Parameters:**
- `M` (int): Number of neighbors per node (default: 32)
  - Higher M = better recall, more memory
  - Typical range: 16-64
- `efConstruction` (int): Construction time accuracy (default: 200)
  - Higher = better index quality, slower build
  - Typical range: 100-500
- `efSearch` (int): Query time accuracy (default: 100)
  - Higher = better recall, slower queries
  - Typical range: 50-500

**When to use:**
- Dataset <10M vectors
- Need high recall (>95%)
- Have sufficient memory
- Real-time queries

**Example:**
```python
searcher = SimilaritySearcher(
    index_type='HNSW',
    dimension=384,
    M=32,
    efConstruction=200
)
searcher.fit(vectors)
searcher.set_ef_search(100)  # Query-time parameter
distances, indices = searcher.search(query_vectors, k=10)
```

**How it works:**
1. Builds multi-layer graph structure
2. Each node connects to M neighbors
3. Query navigates through layers (coarse to fine)
4. Greedy search at each layer

**Performance:**
```
M=32, efConstruction=200, efSearch=100:
- Build time: ~1s for 100K vectors
- Query time: ~1ms
- Recall@10: >95%
- Memory: ~2x vector data
```

**Tuning guide:**

| Use Case | M | efConstruction | efSearch | Recall | Speed |
|----------|---|----------------|----------|--------|-------|
| Fast, lower accuracy | 16 | 100 | 50 | 90% | Very Fast |
| Balanced | 32 | 200 | 100 | 95% | Fast |
| High accuracy | 64 | 400 | 200 | 98% | Medium |

**Trade-offs:**
- ✅ High recall (95-99%)
- ✅ Fast queries (1-10ms)
- ✅ Works well up to 10M vectors
- ❌ 2x memory overhead
- ❌ Slower than IVF for >10M vectors

### IVF Index (Inverted File)

Partitions vectors into Voronoi cells for fast approximate search.

**Class:** `IVFIndex`

**Parameters:**
- `nlist` (int): Number of clusters/cells (default: 100)
  - Rule of thumb: `sqrt(n_samples)`
  - Typical range: 100-10000
- `nprobe` (int): Number of cells to search (default: 10)
  - Higher = better recall, slower queries
  - Typical range: 1-100

**When to use:**
- Dataset >1M vectors
- Can tolerate 85-95% recall
- Memory constrained

**Example:**
```python
searcher = SimilaritySearcher(
    index_type='IVF',
    dimension=384,
    nlist=1000,
    nprobe=10
)
searcher.fit(vectors)  # Trains quantizer + adds vectors
distances, indices = searcher.search(query_vectors, k=10)
```

**How it works:**
1. Cluster vectors into `nlist` Voronoi cells (K-means)
2. Each vector assigned to nearest centroid
3. Query finds `nprobe` nearest centroids
4. Searches only vectors in those cells

**Performance:**
```
nlist=1000, nprobe=10 on 1M vectors:
- Build time: ~10s
- Query time: ~5ms
- Recall@10: ~90%
- Memory: ~1.1x vector data
```

**Tuning:**
- `nlist ≈ sqrt(n)` for n vectors
- Start with `nprobe = nlist / 100`, increase if recall too low

| Dataset Size | nlist | nprobe | Recall | Query Time |
|--------------|-------|--------|--------|------------|
| 100K | 100 | 5 | 85% | 1ms |
| 1M | 1000 | 10 | 90% | 5ms |
| 10M | 3000 | 20 | 92% | 15ms |
| 100M | 10000 | 50 | 94% | 50ms |

**Trade-offs:**
- ✅ Fast for large datasets
- ✅ Low memory overhead
- ✅ Scales to billions
- ❌ Lower recall than HNSW
- ❌ Requires training phase

### IVF-HNSW Index (Hybrid)

Combines IVF partitioning with HNSW for the coarse quantizer.

**Class:** `IVFHNSWIndex`

**When to use:**
- Dataset 10M-1B vectors
- Need better recall than IVF alone
- Have moderate memory

**Example:**
```python
searcher = SimilaritySearcher(
    index_type='IVF-HNSW',
    dimension=384,
    nlist=1000
)
```

**Advantages over plain IVF:**
- Faster quantizer navigation (HNSW vs Flat)
- Better recall for same nprobe
- 10-20% faster queries

### IVF-PQ Index (Product Quantization)

IVF with vector compression for memory efficiency.

**Class:** `IVFPQIndex`

**Parameters:**
- `nlist` (int): Number of IVF cells
- `m` (int): Number of PQ subquantizers (default: 8)
  - Must divide vector dimension
- `nbits` (int): Bits per subquantizer (default: 8)

**When to use:**
- Dataset >100M vectors
- Memory constrained
- Can tolerate 80-90% recall

**Example:**
```python
searcher = SimilaritySearcher(
    index_type='IVF-PQ',
    dimension=384,
    nlist=10000,
    m=96,  # 384 / 4 = 96 subvectors of size 4
    nbits=8
)
```

**How it works:**
1. Splits each vector into m subvectors
2. Quantizes each subvector independently
3. Stores only quantization codes (m × nbits total)
4. Original: 384 × 32 bits = 12KB per vector
5. Compressed: 96 × 8 bits = 96 bytes (100x smaller!)

**Performance:**
```
m=96, nbits=8 on 100M vectors:
- Memory: ~10GB (vs 1TB uncompressed)
- Query time: ~100ms
- Recall@10: ~85%
```

**Trade-offs:**
- ✅ Massive memory savings (10-100x)
- ✅ Enables billion-scale search
- ❌ Lower recall (80-90%)
- ❌ Lossy compression

## Core Class: SimilaritySearcher

Main interface for similarity search.

### Class: `SimilaritySearcher`

**Parameters:**
- `index_type` (str): 'Flat', 'HNSW', 'IVF', 'IVF-HNSW', 'IVF-PQ', or 'auto'
- `dimension` (int): Vector dimension
- `use_gpu` (bool): Enable GPU acceleration (default: False)
- `**index_params`: Index-specific parameters

**Example:**
```python
from privacy_similarity.search import SimilaritySearcher

searcher = SimilaritySearcher(
    index_type='auto',  # Auto-select based on data size
    dimension=384,
    use_gpu=False
)
```

### Methods

#### `fit(vectors: np.ndarray) -> None`

Builds the search index from vectors.

**Parameters:**
- `vectors`: Array of shape (n_samples, dimension)

**Example:**
```python
import numpy as np

vectors = np.random.randn(100000, 384)
searcher.fit(vectors)
```

**What happens:**
1. Auto-selects index type if `index_type='auto'`
2. Trains quantizer (if IVF-based)
3. Adds vectors to index
4. Builds search structures

#### `search(query_vectors: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]`

Searches for k nearest neighbors.

**Parameters:**
- `query_vectors`: Array of shape (n_queries, dimension)
- `k`: Number of neighbors to return

**Returns:**
- `distances`: Array of shape (n_queries, k)
- `indices`: Array of shape (n_queries, k)

**Example:**
```python
query = np.random.randn(1, 384)
distances, indices = searcher.search(query, k=10)

print(f'Top 10 neighbors: {indices[0]}')
print(f'Distances: {distances[0]}')
```

**Distance metric:**
- Default: L2 (Euclidean) distance
- Lower distance = more similar
- For normalized vectors: L2 distance ≈ 1 - cosine similarity

#### `add_records(vectors: np.ndarray) -> None`

Adds new vectors to existing index.

**Parameters:**
- `vectors`: New vectors to add

**Example:**
```python
# Initial index
searcher.fit(initial_vectors)

# Later: add more data
searcher.add_records(new_vectors)
```

**Note:** Not all index types support adding (e.g., HNSW doesn't support removal).

#### `find_duplicates(threshold: float = 0.9, max_cluster_size: int = 100) -> List[Dict]`

Finds duplicate groups using similarity threshold.

**Parameters:**
- `threshold`: Similarity threshold (0-1, higher = more strict)
- `max_cluster_size`: Maximum cluster size to prevent huge groups

**Returns:**
- List of duplicate groups, each with 'ids' and 'similarity'

**Example:**
```python
duplicates = searcher.find_duplicates(threshold=0.85)

for group in duplicates:
    print(f"Duplicate IDs: {group['ids']}")
    print(f"Similarity: {group['similarity']:.3f}")
```

**How it works:**
1. For each vector, find all neighbors within threshold
2. Build graph of similar pairs
3. Find connected components (groups)
4. Return groups as duplicate clusters

#### `save_index(path: str) -> None`

Saves index to disk.

**Parameters:**
- `path`: File path to save

**Example:**
```python
searcher.save_index('customer_similarity.index')
```

#### `load_index(path: str) -> None`

Loads index from disk.

**Parameters:**
- `path`: File path to load

**Example:**
```python
searcher.load_index('customer_similarity.index')
results = searcher.search(query)  # Ready to use
```

## Auto Index Selection

When `index_type='auto'`, the searcher automatically selects the best index:

```python
def auto_select_index(n_samples, dimension):
    if n_samples < 1000:
        return 'Flat'
    elif n_samples < 1_000_000:
        return 'HNSW'
    elif n_samples < 10_000_000:
        return 'IVF'
    elif n_samples < 100_000_000:
        return 'IVF-HNSW'
    else:
        return 'IVF-PQ'
```

**Override if:**
- You need exact results → use Flat
- Memory is very limited → use IVF-PQ
- Queries are very latency-sensitive → use HNSW

## GPU Acceleration

Enable GPU for 5-10x speedup on large datasets.

**Requirements:**
```bash
pip install faiss-gpu
```

**Example:**
```python
searcher = SimilaritySearcher(
    index_type='IVF',
    dimension=384,
    use_gpu=True
)

# Everything else is the same
searcher.fit(vectors)
distances, indices = searcher.search(query, k=10)
```

**Speedup by index type:**
- Flat: 5-10x faster
- HNSW: 2-3x faster
- IVF: 3-5x faster
- IVF-PQ: 5-10x faster

**Multi-GPU:**
```python
import faiss

# Shard across 4 GPUs
gpu_resources = [faiss.StandardGpuResources() for _ in range(4)]
index = faiss.index_cpu_to_all_gpus(cpu_index)
```

## Distance Metrics

FAISS supports multiple distance metrics.

### L2 (Euclidean) Distance

Default metric. Measures straight-line distance.

```python
# L2 distance
distance = sqrt(sum((a - b)^2))
```

**Properties:**
- Range: [0, ∞)
- Lower = more similar
- Sensitive to vector magnitude

### Inner Product (Cosine Similarity)

For normalized vectors, inner product = cosine similarity.

```python
searcher = SimilaritySearcher(
    index_type='Flat',
    dimension=384,
    metric='inner_product'
)
```

**Normalize vectors first:**
```python
from sklearn.preprocessing import normalize

normalized_vectors = normalize(vectors, norm='l2')
searcher.fit(normalized_vectors)
```

**Properties:**
- Range: [-1, 1] for normalized vectors
- Higher = more similar
- Invariant to vector magnitude (when normalized)

**Relationship:**
```
For normalized vectors:
cosine_similarity = inner_product
L2_distance = sqrt(2 * (1 - cosine_similarity))
```

## Performance Optimization

### Batch Queries

Query multiple vectors at once for better throughput:

```python
# Instead of:
for query in queries:
    results = searcher.search(query.reshape(1, -1), k=10)  # Slow

# Do:
results = searcher.search(queries, k=10)  # Fast
```

**Speedup:** 5-10x for batches of 100+

### Parameter Tuning

**For HNSW:**
```python
# Faster queries, lower recall
searcher.set_ef_search(50)

# Slower queries, higher recall
searcher.set_ef_search(200)
```

**For IVF:**
```python
# More cells = better recall, slower
index.nprobe = 20  # Default: 10
```

### Memory Optimization

**Use PQ compression:**
```python
# Original: 100M × 384 × 4 bytes = 150GB
# Compressed: 100M × 96 bytes = 9.6GB

searcher = SimilaritySearcher(
    index_type='IVF-PQ',
    m=96,
    nbits=8
)
```

**Use float16 (half precision):**
```python
vectors_fp16 = vectors.astype(np.float16)
# 2x memory savings, minimal accuracy loss
```

## Benchmarking

Measure search performance:

```python
import time

# Build
start = time.time()
searcher.fit(vectors)
build_time = time.time() - start
print(f'Build time: {build_time:.2f}s')

# Query
n_queries = 1000
start = time.time()
for i in range(n_queries):
    searcher.search(queries[i:i+1], k=10)
query_time = (time.time() - start) / n_queries
print(f'Query time: {query_time*1000:.2f}ms')
print(f'QPS: {1/query_time:.0f}')

# Recall (if you have ground truth)
from privacy_similarity.search import compute_recall
recall = compute_recall(results, ground_truth, k=10)
print(f'Recall@10: {recall:.2%}')
```

## Advanced: Custom Distance Functions

For specialized similarity metrics:

```python
import faiss

# Create custom index with specific distance
dimension = 384
index = faiss.IndexFlat(dimension, faiss.METRIC_L2)  # or METRIC_INNER_PRODUCT

# Wrap in searcher
searcher = SimilaritySearcher(custom_index=index)
```

## References

- Johnson et al. "Billion-scale similarity search with GPUs" (2017)
- Malkov & Yashunin. "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs" (2018)
- Jégou et al. "Product Quantization for Nearest Neighbor Search" (2011)
- FAISS Documentation: https://github.com/facebookresearch/faiss/wiki
