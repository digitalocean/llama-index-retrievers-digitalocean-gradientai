# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-27

### Added

- Initial release of `llama-index-retrievers-digitalocean-gradientai` (renamed from `llama-index-retrievers-digitalocean-gradient` for consistency with `llama-index-llms-digitalocean-gradientai`)
- `GradientKBRetriever` class extending LlamaIndex `BaseRetriever`
- Synchronous and asynchronous retrieval support
- Automatic conversion of Gradient KB results to `NodeWithScore` objects
- Metadata preservation (document_id, chunk_id, source, custom metadata)
- Configurable num_results, base_url, and timeout
- Integration with `RetrieverQueryEngine` and other LlamaIndex components
- `CONTRIBUTING.md`, `CHANGELOG.md`
- GitHub Actions CI workflow (Python 3.8-3.12)

### Fixed

- `TextNode` id_ crash when `chunk_id` is `None`
- Docs and tests updated to use `DIGITALOCEAN_ACCESS_TOKEN`
