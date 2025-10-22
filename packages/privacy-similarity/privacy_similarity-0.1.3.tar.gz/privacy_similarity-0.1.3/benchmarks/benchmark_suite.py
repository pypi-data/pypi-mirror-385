"""Performance benchmark suite for privacy-preserving similarity search."""

import time
import numpy as np
import pandas as pd
from typing import Dict, Any, Callable
import json
from datetime import datetime
from privacy_similarity import PrivacyPreservingSimilaritySearch
from privacy_similarity.privacy import DifferentialPrivacy, SecureHash
from privacy_similarity.embeddings import TextEmbedder, NumericFeatureEncoder
from privacy_similarity.blocking import LSHBlocker, ClusteringBlocker
from privacy_similarity.search import FAISSIndex


class BenchmarkSuite:
    """Comprehensive benchmark suite for performance tracking."""

    def __init__(self):
        self.results = {}

    def time_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Time a function and return execution time and result."""
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        return {
            'duration': end - start,
            'result': result
        }

    def benchmark_differential_privacy(self):
        """Benchmark differential privacy operations."""
        print("\n" + "="*60)
        print("Benchmarking Differential Privacy")
        print("="*60)

        results = {}

        # Test different epsilon values
        for epsilon in [0.1, 1.0, 10.0]:
            dp = DifferentialPrivacy(epsilon=epsilon)

            # Benchmark vector transformation
            vectors = np.random.randn(1000, 128)
            bench_result = self.time_function(dp.transform_batch, vectors)

            results[f'vector_transform_eps_{epsilon}'] = {
                'duration': bench_result['duration'],
                'vectors_per_sec': 1000 / bench_result['duration']
            }

            print(f"  ε={epsilon}: {1000 / bench_result['duration']:.2f} vectors/sec")

        # Benchmark MinHash
        dp = DifferentialPrivacy(epsilon=1.0)
        tokens_list = [['word' + str(i) for i in range(100)] for _ in range(100)]

        start = time.time()
        for tokens in tokens_list:
            dp.minhash_sketch(tokens, num_hashes=128)
        duration = time.time() - start

        results['minhash_sketches'] = {
            'duration': duration,
            'sketches_per_sec': 100 / duration
        }

        print(f"  MinHash: {100 / duration:.2f} sketches/sec")

        self.results['differential_privacy'] = results
        return results

    def benchmark_embeddings(self):
        """Benchmark embedding generation."""
        print("\n" + "="*60)
        print("Benchmarking Embeddings")
        print("="*60)

        results = {}

        # Generate test texts
        texts = [f"Sample text {i} with some content" for i in range(1000)]

        # Benchmark TF-IDF
        embedder = TextEmbedder(model_name='tfidf')
        embedder.fit(texts[:500])

        bench_result = self.time_function(embedder.encode, texts)
        results['tfidf'] = {
            'duration': bench_result['duration'],
            'texts_per_sec': 1000 / bench_result['duration']
        }

        print(f"  TF-IDF: {1000 / bench_result['duration']:.2f} texts/sec")

        # Benchmark numeric encoding
        df = pd.DataFrame({
            'x': np.random.randn(10000),
            'y': np.random.randn(10000),
            'z': np.random.randn(10000)
        })

        encoder = NumericFeatureEncoder()
        encoder.fit(df)

        bench_result = self.time_function(encoder.transform, df)
        results['numeric_encoding'] = {
            'duration': bench_result['duration'],
            'rows_per_sec': 10000 / bench_result['duration']
        }

        print(f"  Numeric: {10000 / bench_result['duration']:.2f} rows/sec")

        self.results['embeddings'] = results
        return results

    def benchmark_blocking(self):
        """Benchmark blocking methods."""
        print("\n" + "="*60)
        print("Benchmarking Blocking")
        print("="*60)

        results = {}
        vectors = np.random.randn(10000, 128)

        # Benchmark LSH
        lsh = LSHBlocker(dimension=128, num_tables=10, hash_size=8)

        # Index building
        bench_result = self.time_function(lsh.index_vectors, vectors)
        results['lsh_indexing'] = {
            'duration': bench_result['duration'],
            'vectors_per_sec': 10000 / bench_result['duration']
        }

        print(f"  LSH Indexing: {10000 / bench_result['duration']:.2f} vectors/sec")

        # Querying
        queries = vectors[:100]
        bench_result = self.time_function(lsh.query_batch, queries)
        results['lsh_query'] = {
            'duration': bench_result['duration'],
            'queries_per_sec': 100 / bench_result['duration']
        }

        print(f"  LSH Query: {100 / bench_result['duration']:.2f} queries/sec")

        # Benchmark Clustering
        clusterer = ClusteringBlocker(n_clusters=100, clustering_algorithm='minibatch_kmeans')

        bench_result = self.time_function(clusterer.fit, vectors)
        results['clustering_fit'] = {
            'duration': bench_result['duration'],
            'vectors_per_sec': 10000 / bench_result['duration']
        }

        print(f"  Clustering Fit: {10000 / bench_result['duration']:.2f} vectors/sec")

        # Query
        bench_result = self.time_function(clusterer.query_batch, queries, num_clusters=2)
        results['clustering_query'] = {
            'duration': bench_result['duration'],
            'queries_per_sec': 100 / bench_result['duration']
        }

        print(f"  Clustering Query: {100 / bench_result['duration']:.2f} queries/sec")

        self.results['blocking'] = results
        return results

    def benchmark_faiss_index(self):
        """Benchmark FAISS index types."""
        print("\n" + "="*60)
        print("Benchmarking FAISS Index")
        print("="*60)

        results = {}
        dimension = 128
        n_vectors = 10000
        n_queries = 100

        vectors = np.random.randn(n_vectors, dimension).astype('float32')
        queries = np.random.randn(n_queries, dimension).astype('float32')

        for index_type in ['Flat', 'HNSW']:
            print(f"\n  Testing {index_type}:")

            index = FAISSIndex(
                dimension=dimension,
                index_type=index_type,
                metric='cosine',
                use_gpu=False
            )

            # Benchmark indexing
            bench_result = self.time_function(index.add, vectors)
            indexing_time = bench_result['duration']

            results[f'{index_type.lower()}_indexing'] = {
                'duration': indexing_time,
                'vectors_per_sec': n_vectors / indexing_time
            }

            print(f"    Indexing: {n_vectors / indexing_time:.2f} vectors/sec")

            # Benchmark search
            bench_result = self.time_function(index.search, queries, k=10)
            search_time = bench_result['duration']

            results[f'{index_type.lower()}_search'] = {
                'duration': search_time,
                'queries_per_sec': n_queries / search_time,
                'qps': n_queries / search_time
            }

            print(f"    Search: {n_queries / search_time:.2f} QPS")

        self.results['faiss_index'] = results
        return results

    def benchmark_end_to_end(self):
        """Benchmark complete end-to-end workflows."""
        print("\n" + "="*60)
        print("Benchmarking End-to-End Workflows")
        print("="*60)

        results = {}

        # Create realistic dataset
        n_customers = 1000
        customers = pd.DataFrame({
            'customer_id': range(1, n_customers + 1),
            'name': [f'Customer {i}' for i in range(n_customers)],
            'email': [f'customer{i}@example.com' for i in range(n_customers)],
            'description': [
                f'Customer description {i} with interests in topic {i % 10}'
                for i in range(n_customers)
            ]
        })

        # Benchmark different configurations
        configs = [
            ('no_privacy_flat', {'privacy_mode': 'none', 'index_type': 'Flat'}),
            ('dp_flat', {'privacy_mode': 'differential_privacy', 'epsilon': 1.0, 'index_type': 'Flat'}),
            ('no_privacy_hnsw', {'privacy_mode': 'none', 'index_type': 'HNSW'}),
        ]

        for name, config in configs:
            print(f"\n  Testing {name}:")

            searcher = PrivacyPreservingSimilaritySearch(
                embedding_model='tfidf',
                **config
            )

            # Benchmark fit
            start = time.time()
            searcher.fit(
                customers,
                sensitive_columns=['name', 'email'],
                embedding_columns=['description'],
                id_column='customer_id'
            )
            fit_time = time.time() - start

            results[f'{name}_fit'] = {
                'duration': fit_time,
                'records_per_sec': n_customers / fit_time
            }

            print(f"    Fit: {n_customers / fit_time:.2f} records/sec")

            # Benchmark search
            query = pd.DataFrame({
                'name': ['Test Customer'],
                'email': ['test@example.com'],
                'description': ['Customer interested in topic 5']
            })

            start = time.time()
            for _ in range(100):
                searcher.search(query, k=10)
            search_time = time.time() - start

            results[f'{name}_search'] = {
                'duration': search_time,
                'queries_per_sec': 100 / search_time
            }

            print(f"    Search: {100 / search_time:.2f} queries/sec")

            # Benchmark duplicate finding
            start = time.time()
            duplicates = searcher.find_duplicates(threshold=0.8)
            dedup_time = time.time() - start

            results[f'{name}_deduplication'] = {
                'duration': dedup_time,
                'found_groups': len(duplicates)
            }

            print(f"    Dedup: {dedup_time:.3f}s ({len(duplicates)} groups)")

        self.results['end_to_end'] = results
        return results

    def benchmark_scalability(self):
        """Benchmark scalability with different dataset sizes."""
        print("\n" + "="*60)
        print("Benchmarking Scalability")
        print("="*60)

        results = {}

        for n_records in [100, 1000, 5000]:
            print(f"\n  Testing with {n_records} records:")

            data = pd.DataFrame({
                'id': range(1, n_records + 1),
                'text': [f'Sample text {i}' for i in range(n_records)]
            })

            searcher = PrivacyPreservingSimilaritySearch(
                privacy_mode='none',
                index_type='Flat',
                embedding_model='tfidf'
            )

            # Benchmark fit
            start = time.time()
            searcher.fit(data, embedding_columns=['text'], id_column='id')
            fit_time = time.time() - start

            # Benchmark search
            query = pd.DataFrame({'text': ['query text']})
            start = time.time()
            for _ in range(100):
                searcher.search(query, k=min(10, n_records))
            search_time = time.time() - start

            results[f'n_{n_records}'] = {
                'fit_time': fit_time,
                'search_time': search_time,
                'fit_throughput': n_records / fit_time,
                'search_qps': 100 / search_time
            }

            print(f"    Fit: {fit_time:.3f}s ({n_records / fit_time:.2f} records/sec)")
            print(f"    Search: {100 / search_time:.2f} QPS")

        self.results['scalability'] = results
        return results

    def run_all_benchmarks(self):
        """Run all benchmarks."""
        print("\n" + "="*80)
        print("PRIVACY-PRESERVING SIMILARITY SEARCH - PERFORMANCE BENCHMARKS")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Run all benchmark categories
        self.benchmark_differential_privacy()
        self.benchmark_embeddings()
        self.benchmark_blocking()
        self.benchmark_faiss_index()
        self.benchmark_end_to_end()
        self.benchmark_scalability()

        print("\n" + "="*80)
        print("BENCHMARKS COMPLETED")
        print("="*80)

        return self.results

    def save_results(self, filename: str):
        """Save benchmark results to JSON file."""
        output = {
            'timestamp': datetime.now().isoformat(),
            'results': self.results
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\nResults saved to: {filename}")

    def print_summary(self):
        """Print summary of key metrics."""
        print("\n" + "="*80)
        print("PERFORMANCE SUMMARY")
        print("="*80)

        if 'differential_privacy' in self.results:
            dp_results = self.results['differential_privacy']
            best_throughput = max(
                v['vectors_per_sec']
                for k, v in dp_results.items()
                if 'vectors_per_sec' in v
            )
            print(f"\nDifferential Privacy:")
            print(f"  Best throughput: {best_throughput:.2f} vectors/sec")

        if 'faiss_index' in self.results:
            faiss_results = self.results['faiss_index']
            for index_type in ['flat', 'hnsw']:
                key = f'{index_type}_search'
                if key in faiss_results:
                    qps = faiss_results[key]['qps']
                    print(f"\nFAISS {index_type.upper()}:")
                    print(f"  Search QPS: {qps:.2f}")

        if 'end_to_end' in self.results:
            e2e_results = self.results['end_to_end']
            print(f"\nEnd-to-End Performance:")
            for key in e2e_results:
                if '_search' in key:
                    config_name = key.replace('_search', '')
                    qps = e2e_results[key]['queries_per_sec']
                    print(f"  {config_name}: {qps:.2f} queries/sec")

        print("\n" + "="*80)


if __name__ == '__main__':
    suite = BenchmarkSuite()
    suite.run_all_benchmarks()
    suite.print_summary()
    suite.save_results('benchmark_results.json')
