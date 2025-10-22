## Performance Benchmarks

This directory contains performance benchmarks for the privacy-preserving similarity search package.

### Running Benchmarks

#### Quick Run

```bash
python benchmarks/benchmark_suite.py
```

This will run all benchmarks and display results to the console.

#### Full Run with Tracking

```bash
python benchmarks/run_benchmarks.py --compare --report
```

This will:
- Run all benchmarks
- Compare results with the previous run
- Generate a markdown report
- Save results to `benchmark_results/`

### Benchmark Categories

#### 1. Differential Privacy
- Vector transformation throughput
- MinHash sketch generation
- Different epsilon values (0.1, 1.0, 10.0)

#### 2. Embeddings
- TF-IDF encoding speed
- Numeric feature encoding
- Text processing throughput

#### 3. Blocking
- LSH indexing and querying
- Clustering-based blocking
- Candidate generation speed

#### 4. FAISS Index
- Different index types (Flat, HNSW)
- Indexing throughput (vectors/sec)
- Search throughput (QPS - queries per second)

#### 5. End-to-End
- Complete workflows with different configurations
- Fit time and throughput
- Search performance
- Deduplication speed

#### 6. Scalability
- Performance with different dataset sizes (100, 1000, 5000 records)
- Scaling behavior

### Typical Results

On a modern CPU (example):

| Component | Metric | Performance |
|-----------|--------|-------------|
| Differential Privacy | Vector Transform (ε=1.0) | ~50,000 vectors/sec |
| TF-IDF | Text Encoding | ~10,000 texts/sec |
| FAISS Flat | Search QPS | ~5,000 queries/sec |
| FAISS HNSW | Search QPS | ~3,000 queries/sec |
| End-to-End | Fit Throughput | ~500 records/sec |
| End-to-End | Search QPS | ~100 queries/sec |

### Interpreting Results

#### QPS (Queries Per Second)
- Higher is better
- Measures search throughput
- Typical production target: >100 QPS

#### Indexing Throughput
- Higher is better
- Measures how fast you can build the index
- Important for batch processing

#### Fit Time
- Lower is better
- Total time to process and index dataset
- Important for initial setup

### Tracking Performance Over Time

Results are saved with timestamps in `benchmark_results/`:

```
benchmark_results/
├── benchmark_20250121_143022.json
├── benchmark_20250121_150315.json
├── benchmark_latest.json
└── benchmark_report_20250121_150315.md
```

Use `--compare` flag to see performance changes:

```bash
python benchmarks/run_benchmarks.py --compare
```

Example output:

```
PERFORMANCE COMPARISON
===============================================================================
Metric                                   Current        Previous        Change
-------------------------------------------------------------------------------
FAISS Flat QPS                          5234.56        5123.45        +2.17% ↑
FAISS HNSW QPS                          3456.78        3398.12        +1.73% ↑
E2E Search QPS                           123.45         119.87        +2.99% ↑
DP Transform                           51234.56       50987.23        +0.49% ↑
TF-IDF Encoding                        10234.56       10156.78        +0.77% ↑
```

### CI Integration

Benchmarks are automatically run on push to main branches via GitHub Actions.
See `.github/workflows/benchmark.yml` for configuration.

### Custom Benchmarks

To add your own benchmark:

```python
from benchmarks.benchmark_suite import BenchmarkSuite

suite = BenchmarkSuite()

# Add custom benchmark
def my_custom_benchmark():
    # Your benchmark code
    pass

# Run it
suite.time_function(my_custom_benchmark)
```

### Performance Tips

1. **Use HNSW for <10M records** - Best accuracy/speed tradeoff
2. **Use IVF-PQ for >100M records** - Memory efficient
3. **Adjust epsilon for privacy/accuracy** - Higher = faster but less private
4. **Use blocking for large datasets** - Reduces comparisons
5. **Batch queries** - Better throughput than single queries

### Profiling

For detailed profiling, use Python's cProfile:

```bash
python -m cProfile -o benchmark.prof benchmarks/benchmark_suite.py
python -m pstats benchmark.prof
```

### Hardware Considerations

Benchmark results vary by hardware:

- **CPU**: More cores = better for batch operations
- **GPU**: Significant speedup for FAISS search (10-100x)
- **RAM**: Important for large datasets
- **SSD**: Faster for disk-based indexes

### GPU Benchmarks

To run with GPU acceleration:

```python
searcher = PrivacyPreservingSimilaritySearch(
    use_gpu=True,  # Enable GPU
    index_type='IVF-PQ'
)
```

Note: Requires `faiss-gpu` package.
