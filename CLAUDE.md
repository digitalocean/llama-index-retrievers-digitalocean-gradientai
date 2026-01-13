# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LlamaIndex retriever integration package for DigitalOcean Gradient Knowledge Base as a Service (KBAas). The package wraps the official `gradient` SDK and implements the LlamaIndex `BaseRetriever` interface.

**Package name**: `llama-index-retrievers-digitalocean-gradient`
**Main class**: `GradientKBRetriever` (extends `BaseRetriever` from LlamaIndex)

## Development Commands

### Installation
```bash
# Install package in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (if configured)
pre-commit install
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_gradient_retriever.py

# Run specific test function
pytest tests/test_gradient_retriever.py::TestGradientKBRetriever::test_retrieve_basic

# Run tests without coverage reports
pytest -v --no-cov
```

**Important**: Integration tests require `MODEL_ACCESS_KEY` and `GRADIENT_KB_ID` environment variables. Tests are skipped automatically if credentials are not found.

### Linting and Formatting
```bash
# Format code with black (line length: 100)
black .

# Lint with ruff
ruff check .

# Auto-fix ruff issues
ruff check . --fix

# Type check with mypy
mypy llama_index/retrievers/digitalocean/gradient

# Run all pre-commit hooks (if configured)
pre-commit run --all-files
```

### Building and Publishing
```bash
# Build distribution packages
python -m build

# Publish to PyPI (requires credentials)
python -m twine upload dist/*
```

## Code Architecture

### Package Structure
```
llama_index/retrievers/digitalocean/gradient/
├── __init__.py     # Exports GradientKBRetriever
└── base.py         # Main GradientKBRetriever implementation
```

### GradientKBRetriever Class (base.py)

The `GradientKBRetriever` class in `llama_index/retrievers/digitalocean/gradient/base.py` is the core implementation. Key architectural points:

**Inheritance**: Extends `BaseRetriever` from LlamaIndex core, which provides the interface for retrievers.

**Client Management**:
- `_client` property: Returns synchronous `Gradient` client
- `_async_client` property: Returns asynchronous `AsyncGradient` client
- Clients are created on-demand with configured API key, base URL, and timeout

**Response Conversion**:
- `_convert_to_nodes()`: Converts Gradient SDK response to LlamaIndex `NodeWithScore` objects
- Extracts text content, scores, and metadata (document_id, chunk_id, source)
- Creates `TextNode` objects with proper metadata
- Wraps nodes in `NodeWithScore` with relevance scores

**Core Methods**:
- `_retrieve(query_bundle)`: Synchronous retrieval method (required by BaseRetriever)
- `_aretrieve(query_bundle)`: Asynchronous retrieval method (optional but recommended)
- Both methods call `gradient_client.retrieve.documents()` and convert results

### Key Design Patterns

**Dual Client Support**: The code maintains separate sync and async clients to support both retrieval modes, following LlamaIndex best practices.

**Metadata Preservation**: The retriever extracts and preserves all available metadata from Gradient responses:
- `text_content` → node text
- `score` or `relevance_score` → node score
- `document_id`, `chunk_id`, `source` → node metadata
- Additional `metadata` dict → merged into node metadata

**Default Scoring**: If Gradient doesn't provide a score, defaults to 1.0 to ensure all results have valid scores.

**Empty Result Handling**: Gracefully handles empty or missing results by returning an empty list.

## Configuration

**pyproject.toml** defines:
- Line length: 100 characters (Black, Ruff)
- Python support: 3.8-3.12
- Test coverage excludes: tests, abstract methods, type checking blocks
- Pytest configured with: coverage reports (term, HTML, XML), async mode auto, strict markers

## Integration with LlamaIndex

The retriever can be used in multiple ways:

1. **Direct Retrieval**: Call `retrieve()` or `aretrieve()` directly
2. **With Query Engine**: Use `RetrieverQueryEngine.from_args(retriever=retriever)`
3. **With Custom Retrievers**: Compose with other retrievers for hybrid search
4. **With Callbacks**: Pass `callback_manager` for tracing and monitoring

## Testing Strategy

- **Unit Tests**: Mock Gradient SDK responses to test conversion logic
- **Integration Tests**: Require real Gradient API credentials (`MODEL_ACCESS_KEY`, `GRADIENT_KB_ID`)
- **Coverage**: Target high coverage of conversion and error handling logic

## Related Packages

This package is designed to work alongside:
- `llama-index-llms-digitalocean-gradientai`: LLM integration for Gradient AI
- Together they provide complete RAG capabilities with Gradient
