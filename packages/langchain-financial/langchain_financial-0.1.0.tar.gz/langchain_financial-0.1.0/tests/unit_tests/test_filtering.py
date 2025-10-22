"""Unit tests for MetadataFilter."""

import pytest
from langchain_core.documents import Document
from langchain_financial.filtering import MetadataFilter


class TestMetadataFilter:
    """Test suite for MetadataFilter."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        filter = MetadataFilter()

        assert filter.document_types is None
        assert filter.companies is None
        assert filter.tickers is None
        assert filter.fiscal_years is None
        assert filter.quarters is None
        assert filter.sections is None
        assert filter.min_confidence is None
        assert len(filter.custom_filters) == 0

    def test_init_with_filters(self):
        """Test initialization with filter parameters."""
        filter = MetadataFilter(
            document_types=["10-K", "10-Q"],
            companies=["Apple"],
            fiscal_years=[2024],
        )

        assert filter.document_types == ["10-K", "10-Q"]
        assert filter.companies == ["apple"]  # Lowercase
        assert filter.fiscal_years == [2024]

    def test_filter_by_document_type(self):
        """Test filtering by document type."""
        filter = MetadataFilter(document_types=["10-K"])

        docs = [
            Document(page_content="A", metadata={"document_type": "10-K"}),
            Document(page_content="B", metadata={"document_type": "10-Q"}),
            Document(page_content="C", metadata={"document_type": "10-K"}),
        ]

        result = filter.filter(docs)

        assert len(result) == 2
        assert all(doc.metadata["document_type"] == "10-K" for doc in result)

    def test_filter_by_document_type_case_insensitive(self):
        """Test document type filtering is case insensitive."""
        filter = MetadataFilter(document_types=["10-k"])

        docs = [
            Document(page_content="A", metadata={"document_type": "10-K"}),
            Document(page_content="B", metadata={"document_type": "10-Q"}),
        ]

        result = filter.filter(docs)

        assert len(result) == 1

    def test_filter_by_company(self):
        """Test filtering by company name."""
        filter = MetadataFilter(companies=["Apple"])

        docs = [
            Document(page_content="A", metadata={"company": "Apple Inc."}),
            Document(page_content="B", metadata={"company": "Microsoft Corp."}),
            Document(page_content="C", metadata={"company": "Apple Computer"}),
        ]

        result = filter.filter(docs)

        assert len(result) == 2
        assert all("apple" in doc.metadata["company"].lower() for doc in result)

    def test_filter_by_ticker(self):
        """Test filtering by ticker symbol."""
        filter = MetadataFilter(tickers=["AAPL", "MSFT"])

        docs = [
            Document(page_content="A", metadata={"ticker": "AAPL"}),
            Document(page_content="B", metadata={"ticker": "GOOGL"}),
            Document(page_content="C", metadata={"ticker": "MSFT"}),
        ]

        result = filter.filter(docs)

        assert len(result) == 2
        assert set(doc.metadata["ticker"] for doc in result) == {"AAPL", "MSFT"}

    def test_filter_by_ticker_case_insensitive(self):
        """Test ticker filtering is case insensitive."""
        filter = MetadataFilter(tickers=["aapl"])

        docs = [
            Document(page_content="A", metadata={"ticker": "AAPL"}),
            Document(page_content="B", metadata={"ticker": "MSFT"}),
        ]

        result = filter.filter(docs)

        assert len(result) == 1

    def test_filter_by_fiscal_year(self):
        """Test filtering by fiscal year."""
        filter = MetadataFilter(fiscal_years=[2024, 2023])

        docs = [
            Document(page_content="A", metadata={"fiscal_year": 2024}),
            Document(page_content="B", metadata={"fiscal_year": 2022}),
            Document(page_content="C", metadata={"fiscal_year": 2023}),
        ]

        result = filter.filter(docs)

        assert len(result) == 2
        assert all(doc.metadata["fiscal_year"] in [2024, 2023] for doc in result)

    def test_filter_by_quarter(self):
        """Test filtering by quarter."""
        filter = MetadataFilter(quarters=["Q1", "Q2"])

        docs = [
            Document(page_content="A", metadata={"quarter": "Q1"}),
            Document(page_content="B", metadata={"quarter": "Q3"}),
            Document(page_content="C", metadata={"quarter": "Q2"}),
        ]

        result = filter.filter(docs)

        assert len(result) == 2
        assert all(doc.metadata["quarter"] in ["Q1", "Q2"] for doc in result)

    def test_filter_by_section(self):
        """Test filtering by section."""
        filter = MetadataFilter(sections=["Risk Factors", "MD&A"])

        docs = [
            Document(page_content="A", metadata={"section": "Risk Factors"}),
            Document(page_content="B", metadata={"section": "Financial Statements"}),
            Document(page_content="C", metadata={"section": "MD&A"}),
        ]

        result = filter.filter(docs)

        assert len(result) == 2
        assert all(doc.metadata["section"] in ["Risk Factors", "MD&A"] for doc in result)

    def test_filter_by_min_confidence(self):
        """Test filtering by minimum confidence score."""
        filter = MetadataFilter(min_confidence=0.5)

        docs = [
            Document(page_content="A", metadata={"confidence": 0.8}),
            Document(page_content="B", metadata={"confidence": 0.3}),
            Document(page_content="C", metadata={"confidence": 0.6}),
        ]

        result = filter.filter(docs)

        assert len(result) == 2
        assert all(doc.metadata["confidence"] >= 0.5 for doc in result)

    def test_filter_confidence_uses_highest_score(self):
        """Test that confidence filter uses highest available score."""
        filter = MetadataFilter(min_confidence=0.5)

        docs = [
            # Has rerank_score (highest)
            Document(
                page_content="A",
                metadata={"confidence": 0.3, "rerank_score": 0.9}
            ),
            # Only has confidence
            Document(page_content="B", metadata={"confidence": 0.3}),
        ]

        result = filter.filter(docs)

        # First doc should pass (rerank_score 0.9 > 0.5)
        # Second should fail (confidence 0.3 < 0.5)
        assert len(result) == 1
        assert result[0].page_content == "A"

    def test_multiple_filters_combined(self):
        """Test that multiple filters are AND-ed together."""
        filter = MetadataFilter(
            document_types=["10-K"],
            companies=["Apple"],
            fiscal_years=[2024],
        )

        docs = [
            # Matches all
            Document(
                page_content="A",
                metadata={
                    "document_type": "10-K",
                    "company": "Apple Inc.",
                    "fiscal_year": 2024,
                }
            ),
            # Wrong type
            Document(
                page_content="B",
                metadata={
                    "document_type": "10-Q",
                    "company": "Apple Inc.",
                    "fiscal_year": 2024,
                }
            ),
            # Wrong year
            Document(
                page_content="C",
                metadata={
                    "document_type": "10-K",
                    "company": "Apple Inc.",
                    "fiscal_year": 2023,
                }
            ),
        ]

        result = filter.filter(docs)

        # Only first doc matches all criteria
        assert len(result) == 1
        assert result[0].page_content == "A"

    def test_custom_filter(self):
        """Test custom filter function."""
        def custom_filter(doc: Document) -> bool:
            # Only allow docs with page number > 10
            return doc.metadata.get("page", 0) > 10

        filter = MetadataFilter(custom_filters=[custom_filter])

        docs = [
            Document(page_content="A", metadata={"page": 5}),
            Document(page_content="B", metadata={"page": 15}),
            Document(page_content="C", metadata={"page": 20}),
        ]

        result = filter.filter(docs)

        assert len(result) == 2
        assert all(doc.metadata["page"] > 10 for doc in result)

    def test_multiple_custom_filters(self):
        """Test multiple custom filters."""
        def filter1(doc: Document) -> bool:
            return doc.metadata.get("page", 0) > 10

        def filter2(doc: Document) -> bool:
            return len(doc.page_content) > 5

        filter = MetadataFilter(custom_filters=[filter1, filter2])

        docs = [
            Document(page_content="Short", metadata={"page": 15}),  # Fails filter2
            Document(page_content="Long content", metadata={"page": 5}),  # Fails filter1
            Document(page_content="Long content", metadata={"page": 15}),  # Passes both
        ]

        result = filter.filter(docs)

        assert len(result) == 1

    def test_get_filter_stats(self):
        """Test get_filter_stats method."""
        filter = MetadataFilter(
            document_types=["10-K"],
            fiscal_years=[2024],
        )

        docs = [
            Document(
                page_content="A",
                metadata={
                    "document_type": "10-K",
                    "company": "Apple Inc.",
                    "fiscal_year": 2024,
                }
            ),
            Document(
                page_content="B",
                metadata={
                    "document_type": "10-Q",
                    "company": "Apple Inc.",
                    "fiscal_year": 2024,
                }
            ),
            Document(
                page_content="C",
                metadata={
                    "document_type": "10-K",
                    "company": "Microsoft Corp.",
                    "fiscal_year": 2024,
                }
            ),
        ]

        stats = filter.get_filter_stats(docs)

        assert stats["total_docs"] == 3
        assert stats["filtered_docs"] == 2  # Two 10-Ks
        assert "10-K" in stats["doc_types"]
        assert stats["doc_types"]["10-K"] == 2

    def test_empty_filter_returns_all(self):
        """Test that filter with no criteria returns all docs."""
        filter = MetadataFilter()  # No filters

        docs = [
            Document(page_content="A", metadata={"source": "doc1"}),
            Document(page_content="B", metadata={"source": "doc2"}),
        ]

        result = filter.filter(docs)

        assert len(result) == 2

    def test_filter_empty_list(self):
        """Test filtering empty document list."""
        filter = MetadataFilter(document_types=["10-K"])

        result = filter.filter([])

        assert result == []

    def test_missing_metadata_fields(self):
        """Test handling of documents with missing metadata."""
        filter = MetadataFilter(
            document_types=["10-K"],
            companies=["Apple"],
        )

        docs = [
            # Has all fields
            Document(
                page_content="A",
                metadata={"document_type": "10-K", "company": "Apple Inc."}
            ),
            # Missing document_type
            Document(page_content="B", metadata={"company": "Apple Inc."}),
            # Missing company
            Document(page_content="C", metadata={"document_type": "10-K"}),
            # Missing both
            Document(page_content="D", metadata={}),
        ]

        result = filter.filter(docs)

        # Only first doc has all required fields
        assert len(result) == 1
        assert result[0].page_content == "A"

    def test_alternative_metadata_keys(self):
        """Test that filter checks alternative metadata keys."""
        filter = MetadataFilter(document_types=["10-K"])

        docs = [
            # Uses 'document_type' key
            Document(page_content="A", metadata={"document_type": "10-K"}),
            # Uses 'doc_type' key
            Document(page_content="B", metadata={"doc_type": "10-K"}),
            # Uses 'type' key
            Document(page_content="C", metadata={"type": "10-K"}),
        ]

        result = filter.filter(docs)

        # All should match
        assert len(result) == 3

    def test_fiscal_year_string_conversion(self):
        """Test fiscal year filter handles string years."""
        filter = MetadataFilter(fiscal_years=[2024])

        docs = [
            Document(page_content="A", metadata={"fiscal_year": "2024"}),  # String
            Document(page_content="B", metadata={"fiscal_year": 2024}),    # Int
            Document(page_content="C", metadata={"fiscal_year": "2023"}),
        ]

        result = filter.filter(docs)

        # Both string and int "2024" should match
        assert len(result) == 2
