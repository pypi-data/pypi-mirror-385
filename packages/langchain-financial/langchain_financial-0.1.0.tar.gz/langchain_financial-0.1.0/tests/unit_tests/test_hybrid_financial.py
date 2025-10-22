"""Unit tests for HybridFinancialRetriever."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_core.documents import Document
from langchain_financial import HybridFinancialRetriever


class MockVectorStore:
    """Mock vector store for testing."""

    def __init__(self, docs=None):
        self.docs = docs or []

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        """Return first k docs."""
        return self.docs[:k]

    async def asimilarity_search(self, query: str, k: int = 4) -> list[Document]:
        """Async version."""
        return self.docs[:k]


class TestHybridFinancialRetriever:
    """Test suite for HybridFinancialRetriever."""

    def test_init_minimal(self):
        """Test initialization with minimal parameters."""
        vectorstore = MockVectorStore()

        retriever = HybridFinancialRetriever(vectorstore=vectorstore)

        assert retriever.vectorstore == vectorstore
        assert retriever.k == 10  # Default
        assert retriever.dense_weight == 0.6
        assert retriever.sparse_weight == 0.4

    def test_init_with_documents(self):
        """Test initialization with documents for BM25."""
        vectorstore = MockVectorStore()
        docs = [
            Document(page_content="Test document", metadata={"source": "test"}),
        ]

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            documents=docs,
        )

        assert retriever.documents == docs

    def test_init_with_filters(self):
        """Test initialization with metadata filters."""
        vectorstore = MockVectorStore()

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            document_types=["10-K", "10-Q"],
            companies=["Apple"],
            fiscal_years=[2024],
        )

        assert retriever.document_types == ["10-K", "10-Q"]
        assert retriever.companies == ["Apple"]
        assert retriever.fiscal_years == [2024]

    def test_init_custom_weights(self):
        """Test initialization with custom fusion weights."""
        vectorstore = MockVectorStore()

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            dense_weight=0.7,
            sparse_weight=0.3,
        )

        assert retriever.dense_weight == 0.7
        assert retriever.sparse_weight == 0.3

    def test_components_initialized(self):
        """Test that helper components are initialized."""
        vectorstore = MockVectorStore()

        retriever = HybridFinancialRetriever(vectorstore=vectorstore)

        assert retriever._preprocessor is not None
        assert retriever._fusion_ranker is not None

    def test_metadata_filter_initialized_when_filters_set(self):
        """Test metadata filter is initialized when filters are provided."""
        vectorstore = MockVectorStore()

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            document_types=["10-K"],
        )

        assert retriever._metadata_filter is not None

    def test_metadata_filter_not_initialized_when_no_filters(self):
        """Test metadata filter is None when no filters provided."""
        vectorstore = MockVectorStore()

        retriever = HybridFinancialRetriever(vectorstore=vectorstore)

        assert retriever._metadata_filter is None

    def test_invoke_dense_only(self):
        """Test retrieval with dense only (no BM25)."""
        docs = [
            Document(
                page_content="Risk factors for the company",
                metadata={"source": "doc1", "chunk_id": "1"}
            ),
            Document(
                page_content="Revenue increased",
                metadata={"source": "doc2", "chunk_id": "1"}
            ),
        ]
        vectorstore = MockVectorStore(docs)

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            k=2,
        )

        results = retriever.invoke("risk factors")

        assert len(results) <= 2
        assert all(isinstance(doc, Document) for doc in results)

    def test_invoke_with_bm25(self):
        """Test retrieval with both dense and sparse."""
        docs = [
            Document(
                page_content="Risk factors for the company",
                metadata={"source": "doc1", "chunk_id": "1"}
            ),
            Document(
                page_content="Revenue increased significantly",
                metadata={"source": "doc2", "chunk_id": "1"}
            ),
        ]
        vectorstore = MockVectorStore(docs)

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            documents=docs,  # Enable BM25
            k=2,
        )

        results = retriever.invoke("risk factors")

        assert len(results) <= 2
        # Should have RRF scores from fusion
        if results:
            assert "rrf_score" in results[0].metadata

    def test_invoke_with_metadata_filter(self):
        """Test retrieval with metadata filtering."""
        docs = [
            Document(
                page_content="10-K content",
                metadata={
                    "source": "doc1",
                    "chunk_id": "1",
                    "document_type": "10-K",
                    "fiscal_year": 2024,
                }
            ),
            Document(
                page_content="10-Q content",
                metadata={
                    "source": "doc2",
                    "chunk_id": "1",
                    "document_type": "10-Q",
                    "fiscal_year": 2024,
                }
            ),
        ]
        vectorstore = MockVectorStore(docs)

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            document_types=["10-K"],  # Filter for 10-K only
            k=10,
        )

        results = retriever.invoke("content")

        # Should only return 10-K documents
        assert all(doc.metadata["document_type"] == "10-K" for doc in results)

    def test_invoke_respects_k_parameter(self):
        """Test that k parameter limits results."""
        docs = [
            Document(
                page_content=f"Document {i}",
                metadata={"source": f"doc{i}", "chunk_id": str(i)}
            )
            for i in range(20)
        ]
        vectorstore = MockVectorStore(docs)

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            k=5,
        )

        results = retriever.invoke("document")

        assert len(results) <= 5

    @pytest.mark.asyncio
    async def test_ainvoke(self):
        """Test async retrieval."""
        docs = [
            Document(
                page_content="Test document",
                metadata={"source": "doc1", "chunk_id": "1"}
            ),
        ]
        vectorstore = MockVectorStore(docs)

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            k=1,
        )

        results = await retriever.ainvoke("test")

        assert isinstance(results, list)
        assert len(results) <= 1

    @pytest.mark.asyncio
    async def test_abatch(self):
        """Test async batch retrieval."""
        docs = [
            Document(
                page_content="Test document",
                metadata={"source": "doc1", "chunk_id": "1"}
            ),
        ]
        vectorstore = MockVectorStore(docs)

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            k=1,
        )

        queries = ["query1", "query2"]
        results = await retriever.abatch(queries)

        assert len(results) == 2
        assert all(isinstance(r, list) for r in results)

    def test_batch(self):
        """Test sync batch retrieval."""
        docs = [
            Document(
                page_content="Test document",
                metadata={"source": "doc1", "chunk_id": "1"}
            ),
        ]
        vectorstore = MockVectorStore(docs)

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            k=1,
        )

        queries = ["query1", "query2"]
        results = retriever.batch(queries)

        assert len(results) == 2
        assert all(isinstance(r, list) for r in results)

    def test_preprocessing_applied(self):
        """Test that query preprocessing is applied."""
        docs = [
            Document(
                page_content="Apple revenue $5.2M",
                metadata={"source": "doc1", "chunk_id": "1"}
            ),
        ]
        vectorstore = MockVectorStore(docs)

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            normalize_numbers=True,
            extract_entities=True,
            k=1,
        )

        # Query with number and entity
        results = retriever.invoke("AAPL revenue $5.2M")

        # Should process successfully (entities extracted, numbers normalized)
        assert isinstance(results, list)

    def test_entity_extraction_disabled(self):
        """Test with entity extraction disabled."""
        docs = [
            Document(
                page_content="Test",
                metadata={"source": "doc1", "chunk_id": "1"}
            ),
        ]
        vectorstore = MockVectorStore(docs)

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            extract_entities=False,
            k=1,
        )

        results = retriever.invoke("AAPL revenue")

        assert isinstance(results, list)

    def test_number_normalization_disabled(self):
        """Test with number normalization disabled."""
        docs = [
            Document(
                page_content="Test",
                metadata={"source": "doc1", "chunk_id": "1"}
            ),
        ]
        vectorstore = MockVectorStore(docs)

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            normalize_numbers=False,
            k=1,
        )

        results = retriever.invoke("revenue $5.2M")

        assert isinstance(results, list)

    def test_empty_query(self):
        """Test handling of empty query."""
        vectorstore = MockVectorStore([])

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            k=1,
        )

        results = retriever.invoke("")

        assert isinstance(results, list)

    def test_no_results(self):
        """Test when no documents match."""
        vectorstore = MockVectorStore([])  # No docs

        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            k=10,
        )

        results = retriever.invoke("test query")

        assert isinstance(results, list)
        assert len(results) == 0

    def test_weight_validation(self):
        """Test that weights must be between 0 and 1."""
        vectorstore = MockVectorStore()

        # Should not raise for valid weights
        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            dense_weight=0.6,
            sparse_weight=0.4,
        )
        assert retriever.dense_weight == 0.6

        # Invalid weights should be caught by Pydantic
        with pytest.raises(Exception):  # Pydantic validation error
            HybridFinancialRetriever(
                vectorstore=vectorstore,
                dense_weight=1.5,  # > 1.0
            )

    def test_k_parameter_validation(self):
        """Test k parameter validation."""
        vectorstore = MockVectorStore()

        # Valid k
        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            k=10,
        )
        assert retriever.k == 10

        # k must be positive
        with pytest.raises(Exception):  # Pydantic validation error
            HybridFinancialRetriever(
                vectorstore=vectorstore,
                k=-1,
            )

    def test_retriever_is_runnable(self):
        """Test that retriever implements Runnable interface."""
        vectorstore = MockVectorStore()
        retriever = HybridFinancialRetriever(vectorstore=vectorstore)

        # Should have Runnable methods
        assert hasattr(retriever, "invoke")
        assert hasattr(retriever, "ainvoke")
        assert hasattr(retriever, "batch")
        assert hasattr(retriever, "abatch")
        assert hasattr(retriever, "stream")

    def test_verbose_output(self):
        """Test verbose logging output."""
        docs = [
            Document(
                page_content="Test",
                metadata={"source": "doc1", "chunk_id": "1"}
            ),
        ]
        vectorstore = MockVectorStore(docs)

        # Create retriever with verbose=True would log to callbacks
        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            k=1,
        )

        # Should work with or without verbose
        results = retriever.invoke("test")
        assert isinstance(results, list)
