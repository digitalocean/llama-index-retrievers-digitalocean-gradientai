"""Tests for GradientKBRetriever."""

import os
from unittest.mock import MagicMock, patch

import pytest
from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore, TextNode

from llama_index.retrievers.digitalocean.gradient import GradientKBRetriever


class TestGradientKBRetriever:
    """Test suite for GradientKBRetriever."""

    def test_init_validation(self):
        """Test initialization validation."""
        # Missing knowledge_base_id
        with pytest.raises(ValueError, match="knowledge_base_id is required"):
            GradientKBRetriever(knowledge_base_id="", api_token="test-token")

        # Missing api_token
        with pytest.raises(ValueError, match="api_token is required"):
            GradientKBRetriever(knowledge_base_id="kb-123", api_token="")

    def test_init_success(self):
        """Test successful initialization."""
        retriever = GradientKBRetriever(
            knowledge_base_id="kb-test-123",
            api_token="test-token",
            num_results=10,
            timeout=30.0,
        )

        assert retriever._knowledge_base_id == "kb-test-123"
        assert retriever._api_token == "test-token"
        assert retriever._num_results == 10
        assert retriever._timeout == 30.0

    @patch("llama_index.retrievers.digitalocean.gradient.base.Gradient")
    def test_retrieve_basic(self, mock_gradient_class):
        """Test basic retrieval functionality."""
        # Mock response
        mock_result = MagicMock()
        mock_result.text_content = "Machine learning is a subset of AI."
        mock_result.score = 0.95
        mock_result.document_id = "doc-123"
        mock_result.chunk_id = "chunk-456"
        mock_result.source = "ml_textbook.pdf"
        mock_result.metadata = {"page": 42}

        mock_response = MagicMock()
        mock_response.results = [mock_result]

        mock_client = MagicMock()
        mock_client.retrieve.documents.return_value = mock_response
        mock_gradient_class.return_value = mock_client

        # Create retriever
        retriever = GradientKBRetriever(
            knowledge_base_id="kb-test",
            api_token="test-token",
            num_results=5,
        )

        # Retrieve
        query_bundle = QueryBundle(query_str="What is machine learning?")
        nodes = retriever.retrieve(query_bundle)

        # Verify API call
        mock_client.retrieve.documents.assert_called_once_with(
            knowledge_base_id="kb-test",
            num_results=5,
            query="What is machine learning?",
        )

        # Verify results
        assert len(nodes) == 1
        assert isinstance(nodes[0], NodeWithScore)
        assert isinstance(nodes[0].node, TextNode)
        assert nodes[0].node.text == "Machine learning is a subset of AI."
        assert nodes[0].score == 0.95
        assert nodes[0].node.metadata["document_id"] == "doc-123"
        assert nodes[0].node.metadata["chunk_id"] == "chunk-456"
        assert nodes[0].node.metadata["source"] == "ml_textbook.pdf"
        assert nodes[0].node.metadata["page"] == 42

    @patch("llama_index.retrievers.digitalocean.gradient.base.Gradient")
    def test_retrieve_empty_results(self, mock_gradient_class):
        """Test retrieval with empty results."""
        mock_response = MagicMock()
        mock_response.results = []

        mock_client = MagicMock()
        mock_client.retrieve.documents.return_value = mock_response
        mock_gradient_class.return_value = mock_client

        retriever = GradientKBRetriever(
            knowledge_base_id="kb-test",
            api_token="test-token",
        )

        query_bundle = QueryBundle(query_str="nonexistent query")
        nodes = retriever.retrieve(query_bundle)

        assert len(nodes) == 0

    @patch("llama_index.retrievers.digitalocean.gradient.base.Gradient")
    def test_retrieve_multiple_results(self, mock_gradient_class):
        """Test retrieval with multiple results."""
        # Create multiple mock results
        results = []
        for i in range(3):
            mock_result = MagicMock()
            mock_result.text_content = f"Content {i}"
            mock_result.score = 0.9 - (i * 0.1)
            mock_result.document_id = f"doc-{i}"
            mock_result.chunk_id = f"chunk-{i}"
            results.append(mock_result)

        mock_response = MagicMock()
        mock_response.results = results

        mock_client = MagicMock()
        mock_client.retrieve.documents.return_value = mock_response
        mock_gradient_class.return_value = mock_client

        retriever = GradientKBRetriever(
            knowledge_base_id="kb-test",
            api_token="test-token",
            num_results=3,
        )

        query_bundle = QueryBundle(query_str="test query")
        nodes = retriever.retrieve(query_bundle)

        assert len(nodes) == 3
        for i, node in enumerate(nodes):
            assert node.node.text == f"Content {i}"
            assert node.score == 0.9 - (i * 0.1)

    def test_init_custom_base_url_and_timeout(self):
        """Test initialization with custom base_url and timeout."""
        retriever = GradientKBRetriever(
            knowledge_base_id="kb-test-123",
            api_token="test-token",
            base_url="https://custom.api.example.com",
            timeout=120.0,
        )

        assert retriever._base_url == "https://custom.api.example.com"
        assert retriever._timeout == 120.0

    @patch("llama_index.retrievers.digitalocean.gradient.base.Gradient")
    def test_client_passes_base_url_and_timeout(self, mock_gradient_class):
        """Test that custom base_url and timeout are passed to the Gradient client."""
        mock_client = MagicMock()
        mock_gradient_class.return_value = mock_client

        retriever = GradientKBRetriever(
            knowledge_base_id="kb-test",
            api_token="test-token",
            base_url="https://custom.example.com",
            timeout=90.0,
        )

        # Access the client property to trigger creation
        _ = retriever._client

        mock_gradient_class.assert_called_once_with(
            model_access_key="test-token",
            base_url="https://custom.example.com",
            timeout=90.0,
        )

    @patch("llama_index.retrievers.digitalocean.gradient.base.Gradient")
    def test_retrieve_none_metadata_values(self, mock_gradient_class):
        """Test retrieval when metadata fields are None."""
        mock_result = MagicMock()
        mock_result.text_content = "Content with None metadata"
        mock_result.score = 0.8
        mock_result.document_id = None
        mock_result.chunk_id = None
        mock_result.source = None
        mock_result.metadata = None

        mock_response = MagicMock()
        mock_response.results = [mock_result]

        mock_client = MagicMock()
        mock_client.retrieve.documents.return_value = mock_response
        mock_gradient_class.return_value = mock_client

        retriever = GradientKBRetriever(
            knowledge_base_id="kb-test",
            api_token="test-token",
        )

        query_bundle = QueryBundle(query_str="test")
        nodes = retriever.retrieve(query_bundle)

        assert len(nodes) == 1
        assert nodes[0].node.text == "Content with None metadata"
        assert nodes[0].score == 0.8
        # None values should still be stored in metadata
        assert nodes[0].node.metadata["document_id"] is None
        assert nodes[0].node.metadata["chunk_id"] is None
        assert nodes[0].node.metadata["source"] is None

    @patch("llama_index.retrievers.digitalocean.gradient.base.Gradient")
    def test_retrieve_missing_score(self, mock_gradient_class):
        """Test retrieval when score is missing."""
        mock_result = MagicMock()
        mock_result.text_content = "Some content"
        mock_result.document_id = "doc-no-score"
        mock_result.chunk_id = "chunk-no-score"
        mock_result.source = "test.pdf"
        mock_result.metadata = None
        # No score attribute
        delattr(mock_result, "score")

        mock_response = MagicMock()
        mock_response.results = [mock_result]

        mock_client = MagicMock()
        mock_client.retrieve.documents.return_value = mock_response
        mock_gradient_class.return_value = mock_client

        retriever = GradientKBRetriever(
            knowledge_base_id="kb-test",
            api_token="test-token",
        )

        query_bundle = QueryBundle(query_str="test")
        nodes = retriever.retrieve(query_bundle)

        # Should default to score of 1.0
        assert len(nodes) == 1
        assert nodes[0].score == 1.0


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("DIGITALOCEAN_ACCESS_TOKEN"), reason="DIGITALOCEAN_ACCESS_TOKEN not set"
)
class TestGradientKBRetrieverIntegration:
    """Integration tests requiring actual Gradient API access."""

    @pytest.mark.asyncio
    async def test_async_retrieve(self):
        """Test async retrieval."""
        kb_id = os.getenv("GRADIENT_KB_ID")
        if not kb_id:
            pytest.skip("GRADIENT_KB_ID not set")

        retriever = GradientKBRetriever(
            knowledge_base_id=kb_id,
            api_token=os.getenv("DIGITALOCEAN_ACCESS_TOKEN"),
            num_results=3,
        )

        query_bundle = QueryBundle(query_str="test query")
        nodes = await retriever.aretrieve(query_bundle)

        assert isinstance(nodes, list)
        if nodes:
            assert isinstance(nodes[0], NodeWithScore)
            assert hasattr(nodes[0], "score")
            assert hasattr(nodes[0].node, "text")

    def test_sync_retrieve(self):
        """Test synchronous retrieval."""
        kb_id = os.getenv("GRADIENT_KB_ID")
        if not kb_id:
            pytest.skip("GRADIENT_KB_ID not set")

        retriever = GradientKBRetriever(
            knowledge_base_id=kb_id,
            api_token=os.getenv("DIGITALOCEAN_ACCESS_TOKEN"),
            num_results=3,
        )

        query_bundle = QueryBundle(query_str="test query")
        nodes = retriever.retrieve(query_bundle)

        assert isinstance(nodes, list)
        if nodes:
            assert isinstance(nodes[0], NodeWithScore)
            assert hasattr(nodes[0], "score")
            assert hasattr(nodes[0].node, "text")
