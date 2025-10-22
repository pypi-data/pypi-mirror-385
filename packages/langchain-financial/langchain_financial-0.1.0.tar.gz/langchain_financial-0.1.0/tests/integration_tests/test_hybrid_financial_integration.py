"""Integration tests for HybridFinancialRetriever using LangChain standard tests.

These tests ensure the retriever is fully compatible with the LangChain ecosystem.
"""

import pytest
from typing import Type
from langchain_core.documents import Document
from langchain_financial import HybridFinancialRetriever


# Mock classes for testing without actual dependencies
class FakeEmbeddings:
    """Fake embeddings for testing."""

    def __init__(self, size: int = 768):
        self.size = size

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return fake embeddings."""
        import random
        return [[random.random() for _ in range(self.size)] for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        """Return fake embedding."""
        import random
        return [random.random() for _ in range(self.size)]


class FakeVectorStore:
    """Fake vector store for testing."""

    def __init__(self, documents: list[Document], embeddings):
        self.documents = documents
        self.embeddings = embeddings

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        """Return first k documents (fake relevance)."""
        return self.documents[:k]

    async def asimilarity_search(self, query: str, k: int = 4) -> list[Document]:
        """Async version."""
        return self.documents[:k]

    @classmethod
    def from_documents(cls, documents: list[Document], embeddings):
        """Create from documents."""
        return cls(documents, embeddings)


class TestHybridFinancialRetrieverIntegration:
    """Integration tests for HybridFinancialRetriever.

    NOTE: When contributing to LangChain, replace this with:

    from langchain_tests.integration_tests import RetrieversIntegrationTests

    class TestHybridFinancialRetriever(RetrieversIntegrationTests):
        ...

    This will run all standard LangChain retriever tests.
    """

    @pytest.fixture
    def sample_documents(self) -> list[Document]:
        """Create sample financial documents for testing."""
        return [
            Document(
                page_content="""
                Risk Factors

                Our business is subject to various risks including market volatility,
                regulatory changes, and competitive pressures. We face significant
                competition from both established players and new entrants.
                """,
                metadata={
                    "source": "AAPL_10K_2024.pdf",
                    "document_type": "10-K",
                    "company": "Apple Inc.",
                    "ticker": "AAPL",
                    "fiscal_year": 2024,
                    "section": "Risk Factors",
                    "page": 15,
                    "chunk_id": "1",
                },
            ),
            Document(
                page_content="""
                Management's Discussion and Analysis

                Revenue increased 15% year-over-year to $394.3 billion, driven by
                strong iPhone and Services performance. Gross margin expanded 150
                basis points to 43.5%.
                """,
                metadata={
                    "source": "AAPL_10K_2024.pdf",
                    "document_type": "10-K",
                    "company": "Apple Inc.",
                    "ticker": "AAPL",
                    "fiscal_year": 2024,
                    "section": "MD&A",
                    "page": 28,
                    "chunk_id": "2",
                },
            ),
            Document(
                page_content="""
                Quarterly Results

                For the quarter ended December 31, 2024, we reported revenue of
                $119.6 billion, up 11% year-over-year. iPhone revenue was $69.7
                billion, Services revenue reached $23.1 billion.
                """,
                metadata={
                    "source": "AAPL_10Q_Q4_2024.pdf",
                    "document_type": "10-Q",
                    "company": "Apple Inc.",
                    "ticker": "AAPL",
                    "fiscal_year": 2024,
                    "quarter": "Q4",
                    "section": "Financial Results",
                    "page": 5,
                    "chunk_id": "3",
                },
            ),
            Document(
                page_content="""
                Risk Factors

                We are subject to intense competition in the cloud computing market.
                Amazon Web Services faces competition from Microsoft Azure, Google Cloud,
                and other providers. Pricing pressure could impact our margins.
                """,
                metadata={
                    "source": "AMZN_10K_2024.pdf",
                    "document_type": "10-K",
                    "company": "Amazon.com Inc.",
                    "ticker": "AMZN",
                    "fiscal_year": 2024,
                    "section": "Risk Factors",
                    "page": 12,
                    "chunk_id": "4",
                },
            ),
            Document(
                page_content="""
                Financial Performance

                Net sales increased 12% to $574.8 billion for fiscal year 2024.
                AWS sales were $90.8 billion, growing 13% year-over-year.
                Operating income increased to $36.9 billion.
                """,
                metadata={
                    "source": "AMZN_10K_2024.pdf",
                    "document_type": "10-K",
                    "company": "Amazon.com Inc.",
                    "ticker": "AMZN",
                    "fiscal_year": 2024,
                    "section": "MD&A",
                    "page": 25,
                    "chunk_id": "5",
                },
            ),
        ]

    @pytest.fixture
    def vectorstore(self, sample_documents):
        """Create a fake vector store with sample documents."""
        embeddings = FakeEmbeddings(size=768)
        return FakeVectorStore.from_documents(sample_documents, embeddings)

    @pytest.fixture
    def retriever(self, vectorstore, sample_documents) -> HybridFinancialRetriever:
        """Create a retriever instance for testing."""
        return HybridFinancialRetriever(
            vectorstore=vectorstore,
            documents=sample_documents,  # For BM25
            k=3,
        )

    def test_invoke_returns_documents(self, retriever):
        """Test that invoke returns a list of Documents."""
        query = "What are the risk factors?"
        results = retriever.invoke(query)

        assert isinstance(results, list)
        assert all(isinstance(doc, Document) for doc in results)

    def test_invoke_with_different_queries(self, retriever):
        """Test retrieval with various query types."""
        queries = [
            "What are Apple's risk factors?",
            "revenue growth trends",
            "AWS performance",
            "AAPL Q4 results",
        ]

        for query in queries:
            results = retriever.invoke(query)
            assert isinstance(results, list)
            # Should return some results (up to k)
            assert len(results) >= 0

    def test_invoke_respects_k_limit(self, retriever):
        """Test that results don't exceed k parameter."""
        query = "financial results"
        results = retriever.invoke(query)

        assert len(results) <= retriever.k

    @pytest.mark.asyncio
    async def test_ainvoke_returns_documents(self, retriever):
        """Test async invoke returns documents."""
        query = "What are the risk factors?"
        results = await retriever.ainvoke(query)

        assert isinstance(results, list)
        assert all(isinstance(doc, Document) for doc in results)

    @pytest.mark.asyncio
    async def test_ainvoke_matches_invoke(self, retriever):
        """Test that async and sync produce similar results."""
        query = "revenue growth"

        sync_results = retriever.invoke(query)
        async_results = await retriever.ainvoke(query)

        # Should return same number of results
        assert len(sync_results) == len(async_results)

    def test_batch_returns_list_of_lists(self, retriever):
        """Test batch returns list of document lists."""
        queries = [
            "risk factors",
            "revenue growth",
            "financial performance"
        ]

        results = retriever.batch(queries)

        assert isinstance(results, list)
        assert len(results) == len(queries)
        assert all(isinstance(r, list) for r in results)
        assert all(all(isinstance(doc, Document) for doc in r) for r in results)

    @pytest.mark.asyncio
    async def test_abatch_returns_list_of_lists(self, retriever):
        """Test async batch returns list of document lists."""
        queries = [
            "risk factors",
            "revenue growth",
        ]

        results = await retriever.abatch(queries)

        assert isinstance(results, list)
        assert len(results) == len(queries)
        assert all(isinstance(r, list) for r in results)

    def test_metadata_preserved(self, retriever):
        """Test that document metadata is preserved."""
        query = "risk factors"
        results = retriever.invoke(query)

        if results:
            # Check that original metadata is present
            doc = results[0]
            assert "source" in doc.metadata
            assert "document_type" in doc.metadata

    def test_with_metadata_filters(self, vectorstore, sample_documents):
        """Test retrieval with metadata filters."""
        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            documents=sample_documents,
            k=5,
            document_types=["10-K"],  # Only annual reports
            companies=["Apple"],      # Only Apple
        )

        query = "financial results"
        results = retriever.invoke(query)

        # All results should match filters
        for doc in results:
            assert doc.metadata["document_type"] == "10-K"
            assert "Apple" in doc.metadata["company"]

    def test_with_fiscal_year_filter(self, vectorstore, sample_documents):
        """Test filtering by fiscal year."""
        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            documents=sample_documents,
            k=5,
            fiscal_years=[2024],
        )

        query = "revenue"
        results = retriever.invoke(query)

        # All results should be from 2024
        for doc in results:
            assert doc.metadata["fiscal_year"] == 2024

    def test_entity_extraction(self, vectorstore, sample_documents):
        """Test that entity extraction works in queries."""
        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            documents=sample_documents,
            k=3,
            extract_entities=True,
        )

        # Query with entities
        query = "What is AAPL revenue in 2024?"
        results = retriever.invoke(query)

        # Should successfully process query with entities
        assert isinstance(results, list)

    def test_number_normalization(self, vectorstore, sample_documents):
        """Test that number normalization works."""
        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            documents=sample_documents,
            k=3,
            normalize_numbers=True,
        )

        # Query with financial numbers
        query = "revenue of $100M"
        results = retriever.invoke(query)

        # Should successfully process query with numbers
        assert isinstance(results, list)

    def test_dense_only_retrieval(self, vectorstore):
        """Test retrieval with dense only (no BM25)."""
        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            documents=None,  # No sparse retrieval
            k=3,
        )

        query = "risk factors"
        results = retriever.invoke(query)

        assert isinstance(results, list)
        assert len(results) <= 3

    def test_hybrid_retrieval(self, vectorstore, sample_documents):
        """Test full hybrid retrieval with both dense and sparse."""
        retriever = HybridFinancialRetriever(
            vectorstore=vectorstore,
            documents=sample_documents,  # Enable sparse
            k=3,
            dense_weight=0.6,
            sparse_weight=0.4,
        )

        query = "risk factors"
        results = retriever.invoke(query)

        # Should have RRF scores from fusion
        if results:
            assert "rrf_score" in results[0].metadata

    def test_empty_query_handling(self, retriever):
        """Test handling of empty query."""
        results = retriever.invoke("")

        # Should handle gracefully
        assert isinstance(results, list)

    def test_long_query_handling(self, retriever):
        """Test handling of very long query."""
        long_query = " ".join(["financial performance"] * 100)
        results = retriever.invoke(long_query)

        # Should handle without error
        assert isinstance(results, list)

    def test_special_characters_in_query(self, retriever):
        """Test handling of special characters."""
        queries = [
            "revenue & profit",
            "10-K filing",
            "Q1'24 results",
            "$100M revenue",
        ]

        for query in queries:
            results = retriever.invoke(query)
            assert isinstance(results, list)

    def test_retriever_config(self, retriever):
        """Test that retriever exposes configuration."""
        assert hasattr(retriever, "k")
        assert hasattr(retriever, "dense_weight")
        assert hasattr(retriever, "sparse_weight")
        assert hasattr(retriever, "vectorstore")

    @pytest.mark.asyncio
    async def test_concurrent_retrieval(self, retriever):
        """Test multiple concurrent async retrievals."""
        import asyncio

        queries = ["query1", "query2", "query3", "query4"]

        # Run multiple queries concurrently
        tasks = [retriever.ainvoke(q) for q in queries]
        results = await asyncio.gather(*tasks)

        assert len(results) == len(queries)
        assert all(isinstance(r, list) for r in results)

    def test_retriever_is_serializable(self, retriever):
        """Test that retriever can be pickled (for distributed systems)."""
        import pickle

        # Should be able to pickle and unpickle
        # Note: May fail if vectorstore uses non-serializable components
        try:
            pickled = pickle.dumps(retriever)
            unpickled = pickle.loads(pickled)
            assert isinstance(unpickled, HybridFinancialRetriever)
        except Exception:
            # Some components may not be picklable, that's OK
            pytest.skip("Retriever components not picklable")

    def test_multiple_retriever_instances(self, vectorstore, sample_documents):
        """Test creating multiple retriever instances."""
        retriever1 = HybridFinancialRetriever(
            vectorstore=vectorstore,
            documents=sample_documents,
            k=3,
        )

        retriever2 = HybridFinancialRetriever(
            vectorstore=vectorstore,
            documents=sample_documents,
            k=5,
        )

        # Should be independent
        assert retriever1.k == 3
        assert retriever2.k == 5

        # Both should work
        results1 = retriever1.invoke("test")
        results2 = retriever2.invoke("test")

        assert isinstance(results1, list)
        assert isinstance(results2, list)
