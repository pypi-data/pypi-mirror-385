# Privacy-Preserving Similarity Search Documentation

Welcome to the comprehensive documentation for the Privacy-Preserving Similarity Search package.

## Table of Contents

1. [Getting Started](getting-started.md) - Installation, quick start, and basic usage
2. [Privacy Module](privacy.md) - Differential privacy, homomorphic encryption, and secure hashing
3. [Embeddings Module](embeddings.md) - Text embeddings, PII tokenization, and numeric features
4. [Blocking Module](blocking.md) - LSH, clustering, and dynamic bucketing
5. [Search Module](search.md) - FAISS indices and similarity search
6. [API Reference](api-reference.md) - Complete API documentation
7. [Release Process](releasing.md) - Automated releases, versioning, and package distribution

## Overview

This package provides privacy-preserving similarity search capabilities for large-scale DataFrames containing Personally Identifiable Information (PII). It implements state-of-the-art techniques from leading tech companies and academic research.

### Key Features

- **Privacy Protection**: Multiple privacy modes (differential privacy, homomorphic encryption, secure hashing)
- **Scalable Search**: FAISS-based vector similarity search for billion-scale datasets
- **Advanced Embeddings**: Deep learning embeddings using Sentence Transformers
- **Efficient Blocking**: LSH and clustering for candidate generation
- **Production Ready**: Comprehensive testing and performance benchmarks

### Architecture Layers

1. **Privacy Protection Layer** - Protects sensitive data using cryptographic and statistical techniques
2. **Embedding Generation Layer** - Converts text and structured data into vector representations
3. **Blocking/Filtering Layer** - Reduces search space for efficiency
4. **Similarity Search Layer** - Fast approximate nearest neighbor search
5. **Post-Processing Layer** - Refinement and deduplication

### Use Cases

- **Customer Deduplication**: Find duplicate customer records across databases
- **Entity Resolution**: Match records referring to the same real-world entity
- **Recommendation Systems**: Find similar customers, products, or content
- **Privacy-Preserving Analytics**: Analyze sensitive data without exposing PII

## Quick Links

- [GitHub Repository](https://github.com/alexandernicholson/python-similarity)
- [Issue Tracker](https://github.com/alexandernicholson/python-similarity/issues)
- [Contributing Guidelines](../README.md#contributing)

## Getting Help

If you encounter issues or have questions:

1. Check the [Getting Started Guide](getting-started.md)
2. Review the [API Reference](api-reference.md)
3. Search existing [GitHub Issues](https://github.com/alexandernicholson/python-similarity/issues)
4. Open a new issue with a minimal reproducible example

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{privacy_similarity,
  title={Privacy-Preserving Similarity Search},
  author={Alexander Nicholson},
  year={2025},
  url={https://github.com/alexandernicholson/python-similarity}
}
```
