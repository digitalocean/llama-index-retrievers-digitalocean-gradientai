# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-01

### Added

- Initial release of `llama-index-retrievers-digitalocean-gradient`
- `GradientKBRetriever` class extending LlamaIndex `BaseRetriever`
- Synchronous and asynchronous retrieval support
- Automatic conversion of Gradient KB results to `NodeWithScore` objects
- Metadata preservation (document_id, chunk_id, source, custom metadata)
- Configurable num_results, base_url, and timeout
- Integration with `RetrieverQueryEngine` and other LlamaIndex components
