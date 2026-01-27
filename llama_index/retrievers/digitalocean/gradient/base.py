"""DigitalOcean Gradient Knowledge Base retriever implementation."""

from typing import Any, List, Optional

from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore, QueryBundle, TextNode

try:
    from gradient import AsyncGradient, Gradient
except ImportError as exc:  # pragma: no cover - surfaced at runtime for users
    raise ImportError(
        "gradient is required for GradientKBRetriever. Install with: pip install gradient"
    ) from exc


class GradientKBRetriever(BaseRetriever):
    """DigitalOcean Gradient Knowledge Base Retriever.

    Native LlamaIndex retriever for DigitalOcean Gradient's Knowledge Base as a Service (KBAas).
    Automatically converts Gradient KB results to LlamaIndex NodeWithScore objects for seamless
    integration with query engines, retrievers, and other LlamaIndex components.

    Example:
        >>> from llama_index.retrievers.digitalocean.gradient import GradientKBRetriever
        >>> from llama_index.core.query_engine import RetrieverQueryEngine
        >>>
        >>> retriever = GradientKBRetriever(
        ...     knowledge_base_id="kb-uuid",
        ...     api_token="your-gradient-api-key",
        ...     num_results=5
        ... )
        >>>
        >>> # Use directly
        >>> nodes = retriever.retrieve("What is machine learning?")
        >>>
        >>> # Or with query engine
        >>> query_engine = RetrieverQueryEngine(retriever=retriever)
        >>> response = query_engine.query("What is machine learning?")
    """

    def __init__(
        self,
        knowledge_base_id: str,
        api_token: str,
        num_results: int = 5,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
        **kwargs: Any,
    ) -> None:
        """Initialize DigitalOcean Gradient KB Retriever.

        Args:
            knowledge_base_id: Gradient Knowledge Base UUID.
            api_token: DigitalOcean API token for authentication.
            num_results: Number of results to retrieve per query (default: 5).
            base_url: Optional custom API base URL.
            timeout: Request timeout in seconds (default: 60.0).
            **kwargs: Additional arguments passed to BaseRetriever.

        Raises:
            ValueError: If knowledge_base_id or api_token is not provided.
        """
        if not knowledge_base_id:
            raise ValueError("knowledge_base_id is required and must be provided.")
        if not api_token:
            raise ValueError("api_token is required and must be provided.")

        self._knowledge_base_id = knowledge_base_id
        self._api_token = api_token
        self._num_results = num_results
        self._base_url = base_url
        self._timeout = timeout

        super().__init__(**kwargs)

    @property
    def _client(self) -> Gradient:
        """Synchronous Gradient client."""
        return Gradient(
            model_access_key=self._api_token,
            base_url=self._base_url,
            timeout=self._timeout,
        )

    @property
    def _async_client(self) -> AsyncGradient:
        """Asynchronous Gradient client."""
        return AsyncGradient(
            model_access_key=self._api_token,
            base_url=self._base_url,
            timeout=self._timeout,
        )

    def _convert_to_nodes(self, response: Any) -> List[NodeWithScore]:
        """Convert Gradient KB response to LlamaIndex NodeWithScore objects.

        Args:
            response: Response from Gradient retrieve.documents() API.

        Returns:
            List of NodeWithScore objects with retrieved content and scores.
        """
        nodes = []

        if not hasattr(response, "results") or not response.results:
            return nodes

        for idx, result in enumerate(response.results):
            # Extract text content
            text_content = ""
            if hasattr(result, "text_content"):
                text_content = result.text_content or ""

            # Skip empty results
            if not text_content:
                continue

            # Extract metadata from result
            metadata = {}

            # Add document ID if available
            if hasattr(result, "document_id"):
                metadata["document_id"] = result.document_id

            # Add chunk ID if available
            if hasattr(result, "chunk_id"):
                metadata["chunk_id"] = result.chunk_id

            # Add source if available
            if hasattr(result, "source"):
                metadata["source"] = result.source

            # Add any additional metadata from result
            if hasattr(result, "metadata") and result.metadata:
                metadata.update(result.metadata)

            # Extract score if available (default to 1.0 if not provided)
            score = 1.0
            if hasattr(result, "score"):
                score = float(result.score) if result.score is not None else 1.0
            elif hasattr(result, "relevance_score"):
                score = float(result.relevance_score) if result.relevance_score is not None else 1.0

            # Create TextNode
            node = TextNode(
                text=text_content,
                metadata=metadata,
                id_=str(metadata.get("chunk_id") or f"gradient_kb_{idx}"),
            )

            # Create NodeWithScore
            node_with_score = NodeWithScore(node=node, score=score)
            nodes.append(node_with_score)

        return nodes

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve nodes from Gradient Knowledge Base.

        Args:
            query_bundle: Query bundle containing the search query.

        Returns:
            List of NodeWithScore objects ranked by relevance.
        """
        # Extract query string from bundle
        query_str = query_bundle.query_str

        # Call Gradient KB retrieval API
        response = self._client.retrieve.documents(
            knowledge_base_id=self._knowledge_base_id,
            num_results=self._num_results,
            query=query_str,
        )

        # Convert to NodeWithScore objects
        return self._convert_to_nodes(response)

    async def _aretrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Asynchronously retrieve nodes from Gradient Knowledge Base.

        Args:
            query_bundle: Query bundle containing the search query.

        Returns:
            List of NodeWithScore objects ranked by relevance.
        """
        # Extract query string from bundle
        query_str = query_bundle.query_str

        # Call Gradient KB retrieval API asynchronously
        response = await self._async_client.retrieve.documents(
            knowledge_base_id=self._knowledge_base_id,
            num_results=self._num_results,
            query=query_str,
        )

        # Convert to NodeWithScore objects
        return self._convert_to_nodes(response)
