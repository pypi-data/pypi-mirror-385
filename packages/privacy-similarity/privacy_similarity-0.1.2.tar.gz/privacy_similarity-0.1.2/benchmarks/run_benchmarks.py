"""Script to run benchmarks and track performance over time."""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from benchmark_suite import BenchmarkSuite


def load_historical_results(results_dir: str) -> list:
    """Load all historical benchmark results."""
    results_path = Path(results_dir)
    if not results_path.exists():
        return []

    historical = []
    for file in sorted(results_path.glob('benchmark_*.json')):
        with open(file, 'r') as f:
            historical.append(json.load(f))

    return historical


def compare_results(current: dict, previous: dict):
    """Compare current results with previous run."""
    print("\n" + "="*80)
    print("PERFORMANCE COMPARISON")
    print("="*80)

    def get_metric(results, path):
        """Get metric from nested dict."""
        try:
            value = results['results']
            for key in path.split('.'):
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None

    # Define metrics to compare
    metrics = [
        ('faiss_index.flat_search.qps', 'FAISS Flat QPS', 'higher'),
        ('faiss_index.hnsw_search.qps', 'FAISS HNSW QPS', 'higher'),
        ('end_to_end.no_privacy_flat_search.queries_per_sec', 'E2E Search QPS', 'higher'),
        ('differential_privacy.vector_transform_eps_1.0.vectors_per_sec', 'DP Transform', 'higher'),
        ('embeddings.tfidf.texts_per_sec', 'TF-IDF Encoding', 'higher'),
    ]

    print(f"\nCurrent run: {current.get('timestamp', 'N/A')}")
    print(f"Previous run: {previous.get('timestamp', 'N/A')}")
    print("\n{:<40} {:<15} {:<15} {:<15}".format('Metric', 'Current', 'Previous', 'Change'))
    print("-" * 85)

    for metric_path, metric_name, direction in metrics:
        current_val = get_metric(current, metric_path)
        previous_val = get_metric(previous, metric_path)

        if current_val is not None and previous_val is not None:
            change_pct = ((current_val - previous_val) / previous_val) * 100
            change_str = f"{change_pct:+.2f}%"

            # Color code the change
            if direction == 'higher':
                indicator = '↑' if change_pct > 0 else '↓'
            else:
                indicator = '↓' if change_pct > 0 else '↑'

            print(f"{metric_name:<40} {current_val:>13.2f} {previous_val:>13.2f} {change_str:>13} {indicator}")
        elif current_val is not None:
            print(f"{metric_name:<40} {current_val:>13.2f} {'N/A':>13} {'N/A':>13}")

    print("-" * 85)


def generate_report(results: dict, historical: list, output_file: str):
    """Generate a markdown report."""
    with open(output_file, 'w') as f:
        f.write("# Benchmark Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Summary\n\n")

        # Extract key metrics
        if 'faiss_index' in results['results']:
            f.write("### FAISS Index Performance\n\n")
            f.write("| Index Type | Indexing (vec/s) | Search (QPS) |\n")
            f.write("|------------|------------------|---------------|\n")

            faiss_results = results['results']['faiss_index']
            for index_type in ['flat', 'hnsw']:
                index_key = f'{index_type}_indexing'
                search_key = f'{index_type}_search'

                if index_key in faiss_results and search_key in faiss_results:
                    index_throughput = faiss_results[index_key]['vectors_per_sec']
                    search_qps = faiss_results[search_key]['qps']
                    f.write(f"| {index_type.upper()} | {index_throughput:.2f} | {search_qps:.2f} |\n")

        if 'end_to_end' in results['results']:
            f.write("\n### End-to-End Performance\n\n")
            f.write("| Configuration | Fit (rec/s) | Search (QPS) |\n")
            f.write("|--------------|-------------|---------------|\n")

            e2e_results = results['results']['end_to_end']
            configs = set(key.split('_fit')[0] for key in e2e_results if '_fit' in key)

            for config in configs:
                fit_key = f'{config}_fit'
                search_key = f'{config}_search'

                if fit_key in e2e_results and search_key in e2e_results:
                    fit_throughput = e2e_results[fit_key]['records_per_sec']
                    search_qps = e2e_results[search_key]['queries_per_sec']
                    f.write(f"| {config} | {fit_throughput:.2f} | {search_qps:.2f} |\n")

        if 'scalability' in results['results']:
            f.write("\n### Scalability\n\n")
            f.write("| Dataset Size | Fit Time (s) | Search QPS |\n")
            f.write("|--------------|--------------|-------------|\n")

            scale_results = results['results']['scalability']
            for key in sorted(scale_results.keys()):
                n = key.split('_')[1]
                fit_time = scale_results[key]['fit_time']
                search_qps = scale_results[key]['search_qps']
                f.write(f"| {n} | {fit_time:.3f} | {search_qps:.2f} |\n")

        # Historical comparison
        if historical:
            f.write("\n## Historical Trends\n\n")
            f.write("### FAISS Flat Search QPS Over Time\n\n")
            f.write("| Date | QPS |\n")
            f.write("|------|-----|\n")

            for hist_result in historical[-5:]:  # Last 5 runs
                timestamp = hist_result.get('timestamp', 'N/A')
                date = timestamp.split('T')[0] if 'T' in timestamp else timestamp

                try:
                    qps = hist_result['results']['faiss_index']['flat_search']['qps']
                    f.write(f"| {date} | {qps:.2f} |\n")
                except (KeyError, TypeError):
                    pass

        f.write("\n## Full Results\n\n")
        f.write("```json\n")
        f.write(json.dumps(results, indent=2))
        f.write("\n```\n")

    print(f"\nReport saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Run performance benchmarks')
    parser.add_argument(
        '--output-dir',
        default='benchmark_results',
        help='Directory to store results'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare with previous run'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate markdown report'
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Load historical results
    historical = load_historical_results(str(output_dir))

    # Run benchmarks
    print("Running benchmarks...")
    suite = BenchmarkSuite()
    suite.run_all_benchmarks()
    suite.print_summary()

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = output_dir / f'benchmark_{timestamp}.json'
    suite.save_results(str(results_file))

    # Also save as latest
    latest_file = output_dir / 'benchmark_latest.json'
    suite.save_results(str(latest_file))

    # Compare with previous
    if args.compare and historical:
        current_results = json.loads(open(results_file).read())
        compare_results(current_results, historical[-1])

    # Generate report
    if args.report:
        current_results = json.loads(open(results_file).read())
        report_file = output_dir / f'benchmark_report_{timestamp}.md'
        generate_report(current_results, historical, str(report_file))


if __name__ == '__main__':
    main()
