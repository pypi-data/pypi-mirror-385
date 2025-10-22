# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Automated release workflow on merge to main
- Multi-architecture package builds
- PyPI publishing support

## [0.1.0] - 2025-10-21

### Added
- Initial release
- Privacy-preserving similarity search with three privacy modes:
  - Differential Privacy (DP-MinHash, DP-OPH)
  - Homomorphic Encryption
  - Secure Hashing (Bloom filters, k-anonymity)
- Text embeddings using Sentence Transformers
- PII tokenization for names, emails, addresses, and phone numbers
- Numeric and categorical feature encoding
- Blocking techniques (LSH, clustering, dynamic bucketing)
- FAISS-based similarity search with multiple index types:
  - Flat (exact search)
  - HNSW (graph-based ANN)
  - IVF (inverted file)
  - IVF-HNSW (hybrid)
  - IVF-PQ (compressed)
- GPU acceleration support
- Comprehensive test suite (183 tests)
- End-to-end tests for realistic scenarios
- Performance benchmarks
- Complete documentation with MermaidJS diagrams
- GitHub Actions CI/CD pipeline

### Features
- Find duplicate records across databases
- Search for similar customers, products, or entities
- Privacy-preserving analytics on sensitive data
- Incremental index updates
- Save/load trained models
- Multi-OS support (Ubuntu, macOS, Windows)
- Python 3.8-3.11 support

[Unreleased]: https://github.com/alexandernicholson/python-similarity/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/alexandernicholson/python-similarity/releases/tag/v0.1.0
