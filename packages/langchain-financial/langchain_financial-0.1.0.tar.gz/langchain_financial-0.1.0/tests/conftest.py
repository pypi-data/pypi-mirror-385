"""Pytest configuration and shared fixtures."""

import pytest
from langchain_core.documents import Document


@pytest.fixture
def sample_financial_documents():
    """Provide sample financial documents for testing.

    Returns a list of Document objects with realistic financial content
    and metadata for testing retrieval functionality.
    """
    return [
        Document(
            page_content="""
            Risk Factors

            Our business is subject to various risks including market volatility,
            regulatory changes, and competitive pressures. We face significant
            competition from both established players and new entrants in the
            technology sector. Economic downturns could materially affect our
            revenue and profitability. Supply chain disruptions may impact our
            ability to manufacture and deliver products.
            """,
            metadata={
                "source": "AAPL_10K_2024.pdf",
                "document_type": "10-K",
                "company": "Apple Inc.",
                "ticker": "AAPL",
                "fiscal_year": 2024,
                "section": "Risk Factors",
                "page": 15,
                "chunk_id": "aapl_10k_2024_1",
            },
        ),
        Document(
            page_content="""
            Management's Discussion and Analysis

            Revenue increased 15% year-over-year to $394.3 billion, driven by
            strong iPhone and Services performance. Gross margin expanded 150
            basis points to 43.5%. Operating expenses as a percentage of revenue
            decreased to 9.5% from 10.2% in the prior year. We generated $99.6
            billion in operating cash flow.
            """,
            metadata={
                "source": "AAPL_10K_2024.pdf",
                "document_type": "10-K",
                "company": "Apple Inc.",
                "ticker": "AAPL",
                "fiscal_year": 2024,
                "section": "MD&A",
                "page": 28,
                "chunk_id": "aapl_10k_2024_2",
            },
        ),
        Document(
            page_content="""
            Quarterly Results

            For the quarter ended December 31, 2024, we reported revenue of
            $119.6 billion, up 11% year-over-year. iPhone revenue was $69.7
            billion, Services revenue reached $23.1 billion, and Mac revenue
            was $10.4 billion. Earnings per diluted share were $2.18, up 13%
            from Q4 2023. We returned $27 billion to shareholders.
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
                "chunk_id": "aapl_10q_q4_2024_1",
            },
        ),
        Document(
            page_content="""
            Risk Factors

            We are subject to intense competition in the cloud computing market.
            Amazon Web Services faces competition from Microsoft Azure, Google Cloud,
            and other providers. Pricing pressure could impact our margins. We also
            face risks related to data security, privacy regulations, and potential
            service disruptions. Cybersecurity threats continue to evolve.
            """,
            metadata={
                "source": "AMZN_10K_2024.pdf",
                "document_type": "10-K",
                "company": "Amazon.com Inc.",
                "ticker": "AMZN",
                "fiscal_year": 2024,
                "section": "Risk Factors",
                "page": 12,
                "chunk_id": "amzn_10k_2024_1",
            },
        ),
        Document(
            page_content="""
            Financial Performance

            Net sales increased 12% to $574.8 billion for fiscal year 2024.
            North America segment sales were $352.8 billion, International
            segment sales were $131.2 billion, and AWS sales were $90.8 billion,
            growing 13% year-over-year. Operating income increased to $36.9 billion.
            Free cash flow was $35.5 billion.
            """,
            metadata={
                "source": "AMZN_10K_2024.pdf",
                "document_type": "10-K",
                "company": "Amazon.com Inc.",
                "ticker": "AMZN",
                "fiscal_year": 2024,
                "section": "MD&A",
                "page": 25,
                "chunk_id": "amzn_10k_2024_2",
            },
        ),
        Document(
            page_content="""
            Business Overview

            Microsoft Corporation is a technology company. Our products include
            operating systems, productivity applications, cloud services, and
            gaming platforms. We operate through three segments: Productivity and
            Business Processes, Intelligent Cloud, and More Personal Computing.
            Azure is our cloud computing platform.
            """,
            metadata={
                "source": "MSFT_10K_2024.pdf",
                "document_type": "10-K",
                "company": "Microsoft Corporation",
                "ticker": "MSFT",
                "fiscal_year": 2024,
                "section": "Business",
                "page": 8,
                "chunk_id": "msft_10k_2024_1",
            },
        ),
    ]


@pytest.fixture
def sample_queries():
    """Provide sample queries for testing."""
    return [
        "What are the risk factors?",
        "revenue growth trends",
        "AWS performance metrics",
        "What is AAPL's quarterly revenue?",
        "cloud computing competition",
        "operating expenses as percentage of revenue",
        "cash flow generation",
    ]


@pytest.fixture
def financial_entities():
    """Provide sample financial entities for testing."""
    return {
        "tickers": ["AAPL", "MSFT", "AMZN", "GOOGL"],
        "companies": ["Apple Inc.", "Microsoft Corporation", "Amazon.com Inc."],
        "years": [2024, 2023, 2022],
        "quarters": ["Q1", "Q2", "Q3", "Q4"],
        "document_types": ["10-K", "10-Q", "8-K", "earnings_call"],
        "sections": ["Risk Factors", "MD&A", "Financial Statements", "Business"],
    }


class FakeEmbeddings:
    """Fake embeddings for testing without external dependencies."""

    def __init__(self, size: int = 768):
        self.size = size

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return fake embeddings for documents."""
        import random
        return [[random.random() for _ in range(self.size)] for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        """Return fake embedding for query."""
        import random
        return [random.random() for _ in range(self.size)]


class FakeVectorStore:
    """Fake vector store for testing without external dependencies."""

    def __init__(self, documents: list[Document], embeddings):
        self.documents = documents
        self.embeddings = embeddings

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        """Return first k documents (simulates relevance search)."""
        return self.documents[:k]

    async def asimilarity_search(self, query: str, k: int = 4) -> list[Document]:
        """Async version of similarity search."""
        return self.documents[:k]

    @classmethod
    def from_documents(cls, documents: list[Document], embeddings):
        """Create vector store from documents."""
        return cls(documents, embeddings)


@pytest.fixture
def fake_embeddings():
    """Provide fake embeddings for testing."""
    return FakeEmbeddings(size=768)


@pytest.fixture
def fake_vectorstore(sample_financial_documents, fake_embeddings):
    """Provide fake vector store for testing."""
    return FakeVectorStore.from_documents(
        sample_financial_documents,
        fake_embeddings
    )


# Pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (may use external services)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "asyncio: Async tests requiring event loop"
    )
