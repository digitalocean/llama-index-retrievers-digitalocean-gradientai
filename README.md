# LlamaIndex Retrievers Integration: DigitalOcean Gradient

[![PyPI version](https://badge.fury.io/py/llama-index-retrievers-digitalocean-gradientai.svg)](https://badge.fury.io/py/llama-index-retrievers-digitalocean-gradientai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Native LlamaIndex retriever integration for **DigitalOcean Gradient Knowledge Base as a Service (KBAas)**. This package provides seamless integration between Gradient's knowledge base retrieval and the LlamaIndex ecosystem.

## Features

- 🔌 **Native LlamaIndex Integration** - Works seamlessly with `RetrieverQueryEngine` and other LlamaIndex components
- 📦 **Automatic Format Conversion** - Converts Gradient KB results to `NodeWithScore` objects
- 🎯 **Preserves Metadata** - Maintains document IDs, chunk IDs, sources, and relevance scores
- ⚡ **Async Support** - Full support for both synchronous and asynchronous retrieval
- 🔄 **Simple API** - Clean, intuitive interface following LlamaIndex patterns

## Installation

```bash
pip install llama-index-retrievers-digitalocean-gradientai
```

## Quick Start

### Basic Usage

```python
from llama_index.retrievers.digitalocean.gradientai import GradientKBRetriever

# Initialize retriever
retriever = GradientKBRetriever(
    knowledge_base_id="kb-your-uuid-here",
    api_token="your-digitalocean-access-token",  # DIGITALOCEAN_ACCESS_TOKEN
    num_results=5
)

# Direct retrieval
nodes = retriever.retrieve("What is machine learning?")

# Access results
for node in nodes:
    print(f"Score: {node.score}")
    print(f"Content: {node.node.text}")
    print(f"Metadata: {node.node.metadata}")
```

### End-to-End RAG with Gradient LLM

Build a complete RAG pipeline using both the retriever and LLM packages from DigitalOcean Gradient.

**Install both packages:**

```bash
pip install llama-index-retrievers-digitalocean-gradientai llama-index-llms-digitalocean-gradientai
```

**Full example:**

```python
from llama_index.retrievers.digitalocean.gradientai import GradientKBRetriever
from llama_index.llms.digitalocean.gradientai import GradientAI
from llama_index.core.query_engine import RetrieverQueryEngine

# Initialize retriever (uses DIGITALOCEAN_ACCESS_TOKEN)
retriever = GradientKBRetriever(
    knowledge_base_id="kb-your-uuid-here",
    api_token="your-digitalocean-access-token",
    num_results=5
)

# Initialize LLM (uses MODEL_ACCESS_KEY)
llm = GradientAI(
    model="llama3.3-70b-instruct",
    model_access_key="your-model-access-key"
)

# Create query engine - retrieves relevant docs and generates a response
query_engine = RetrieverQueryEngine.from_args(
    retriever=retriever,
    llm=llm
)

# Query: retriever fetches context from KB, LLM generates the answer
response = query_engine.query("Explain quantum computing")
print(response)
```

This gives you a full RAG pipeline where:
1. The **retriever** searches your Gradient Knowledge Base for relevant documents
2. The **LLM** uses those documents as context to generate a grounded response

### Async Usage

```python
import asyncio
from llama_index.core import QueryBundle

async def async_retrieve():
    retriever = GradientKBRetriever(
        knowledge_base_id="kb-your-uuid-here",
        api_token="your-digitalocean-access-token"  # DIGITALOCEAN_ACCESS_TOKEN
    )

    query = QueryBundle(query_str="What is neural networks?")
    nodes = await retriever.aretrieve(query)

    return nodes

nodes = asyncio.run(async_retrieve())
```

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `knowledge_base_id` | `str` | *Required* | Gradient Knowledge Base UUID |
| `api_token` | `str` | *Required* | DigitalOcean access token (`DIGITALOCEAN_ACCESS_TOKEN`) |
| `num_results` | `int` | `5` | Number of results to retrieve (1-100) |
| `alpha` | `float` | `None` | Hybrid search weight: 0=keyword/BM25, 1=semantic/vector |
| `filters` | `dict` | `None` | Metadata filters (see below) |
| `base_url` | `str` | `None` | Custom API base URL (optional) |
| `timeout` | `float` | `60.0` | Request timeout in seconds |

### Hybrid Search (alpha)

Control the balance between keyword and semantic search:

```python
# Pure keyword/BM25 search (good for exact matches, technical terms)
retriever = GradientKBRetriever(..., alpha=0.0)

# Balanced hybrid search
retriever = GradientKBRetriever(..., alpha=0.5)

# Pure semantic/vector search (good for conceptual queries)
retriever = GradientKBRetriever(..., alpha=1.0)
```

### Metadata Filtering

Filter results based on document metadata:

```python
# Only retrieve from documents with source="docs"
retriever = GradientKBRetriever(
    ...,
    filters={
        "must": [{"key": "source", "operator": "eq", "value": "docs"}]
    }
)

# Exclude certain document types
retriever = GradientKBRetriever(
    ...,
    filters={
        "must_not": [{"key": "type", "operator": "eq", "value": "draft"}]
    }
)
```

Supported filter operators: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `contains`

## Why Use This Instead of Manual SDK Calls?

**Before (Manual SDK Integration):**

```python
# ❌ Manual approach - lots of boilerplate
response = gradient_client.retrieve.documents(
    knowledge_base_id=kb_id,
    num_results=5,
    query=query
)

# Extract text manually
docs = [result.text_content for result in response.results
        if hasattr(result, 'text_content')]

# ❌ Loses scores, metadata, and can't use with LlamaIndex components
```

**After (Native Retriever):**

```python
# ✅ Clean, native integration
retriever = GradientKBRetriever(knowledge_base_id=kb_id, api_token=token)
nodes = retriever.retrieve(query)

# ✅ Full NodeWithScore objects with metadata and scores
# ✅ Works with all LlamaIndex retrieval patterns
# ✅ Supports re-ranking, filtering, composition
```

## What Gets Preserved

The retriever automatically captures and preserves:

- **Text Content** - The retrieved document/chunk text
- **Relevance Score** - Similarity/relevance score from Gradient
- **Document ID** - Source document identifier
- **Chunk ID** - Specific chunk identifier
- **Source** - Document source/origin
- **Custom Metadata** - Any additional metadata from Gradient

## Advanced Usage

### Combining with Other Retrievers

```python
from llama_index.core.retrievers import BaseRetriever

class HybridGradientRetriever(BaseRetriever):
    """Combine Gradient KB with another retriever."""

    def __init__(self, gradient_retriever, other_retriever):
        self.gradient = gradient_retriever
        self.other = other_retriever
        super().__init__()

    def _retrieve(self, query_bundle):
        gradient_nodes = self.gradient.retrieve(query_bundle)
        other_nodes = self.other.retrieve(query_bundle)
        # Combine, deduplicate, rerank...
        return gradient_nodes + other_nodes
```

### Using with Callbacks/Tracing

```python
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler

debug_handler = LlamaDebugHandler()
callback_manager = CallbackManager([debug_handler])

retriever = GradientKBRetriever(
    knowledge_base_id="kb-uuid",
    api_token="token",
    callback_manager=callback_manager
)

nodes = retriever.retrieve("query")
# View retrieval events in debug_handler
```

## Requirements

- Python 3.8+
- `llama-index-core>=0.10.0`
- `gradient>=3.8.0`

## Related Packages

- [llama-index-llms-digitalocean-gradientai](https://pypi.org/project/llama-index-llms-digitalocean-gradientai/) - LLM integration for Gradient AI

## Development

```bash
# Clone repository
git clone https://github.com/digitalocean/llama-index-retrievers-digitalocean-gradientai
cd llama-index-retrievers-digitalocean-gradientai

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
ruff check . --fix
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/digitalocean/llama-index-retrievers-digitalocean-gradientai/issues)
- **Documentation**: [README](https://github.com/digitalocean/llama-index-retrievers-digitalocean-gradientai#readme)

## Acknowledgments

Built with ❤️ for the LlamaIndex and DigitalOcean communities.
