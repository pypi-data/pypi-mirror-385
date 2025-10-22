"""Unit tests for FusionRanker."""

import pytest
from langchain_core.documents import Document
from langchain_financial.fusion import FusionRanker


class TestFusionRanker:
    """Test suite for FusionRanker."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        ranker = FusionRanker()

        assert ranker.weights == [0.6, 0.4]
        assert ranker.k == 60
        assert ranker.deduplication_key == "source"

    def test_init_custom(self):
        """Test initialization with custom parameters."""
        ranker = FusionRanker(
            weights=[0.7, 0.3],
            k=100,
            deduplication_key="doc_id",
        )

        assert ranker.weights == [0.7, 0.3]
        assert ranker.k == 100
        assert ranker.deduplication_key == "doc_id"

    def test_fuse_empty_lists(self):
        """Test fusion with empty input."""
        ranker = FusionRanker()

        result = ranker.fuse([])

        assert result == []

    def test_fuse_single_list(self):
        """Test fusion with single retriever results."""
        ranker = FusionRanker()

        docs = [
            Document(page_content="A", metadata={"source": "doc1"}),
            Document(page_content="B", metadata={"source": "doc2"}),
            Document(page_content="C", metadata={"source": "doc3"}),
        ]

        result = ranker.fuse([docs])

        assert len(result) == 3
        # Check RRF scores are added
        assert "rrf_score" in result[0].metadata
        # First doc should have highest score
        assert result[0].metadata["rrf_score"] > result[1].metadata["rrf_score"]

    def test_fuse_two_lists_no_overlap(self):
        """Test fusion with no overlapping documents."""
        ranker = FusionRanker()

        dense_docs = [
            Document(page_content="A", metadata={"source": "doc1", "chunk_id": "1"}),
            Document(page_content="B", metadata={"source": "doc2", "chunk_id": "1"}),
        ]

        sparse_docs = [
            Document(page_content="C", metadata={"source": "doc3", "chunk_id": "1"}),
            Document(page_content="D", metadata={"source": "doc4", "chunk_id": "1"}),
        ]

        result = ranker.fuse([dense_docs, sparse_docs])

        assert len(result) == 4
        # All should have RRF scores
        for doc in result:
            assert "rrf_score" in doc.metadata

    def test_fuse_two_lists_with_overlap(self):
        """Test fusion with overlapping documents."""
        ranker = FusionRanker()

        # Doc with source="doc1" appears in both
        dense_docs = [
            Document(page_content="A", metadata={"source": "doc1", "chunk_id": "1"}),
            Document(page_content="B", metadata={"source": "doc2", "chunk_id": "1"}),
            Document(page_content="C", metadata={"source": "doc3", "chunk_id": "1"}),
        ]

        sparse_docs = [
            Document(page_content="A", metadata={"source": "doc1", "chunk_id": "1"}),  # Duplicate
            Document(page_content="D", metadata={"source": "doc4", "chunk_id": "1"}),
        ]

        result = ranker.fuse([dense_docs, sparse_docs])

        # Should be 4 unique docs (doc1 deduplicated)
        assert len(result) == 4

        # doc1 should rank high (appears in both lists at top)
        sources = [doc.metadata["source"] for doc in result]
        assert "doc1" in sources[:2]  # Should be in top 2

    def test_rrf_score_calculation(self):
        """Test RRF score calculation formula."""
        ranker = FusionRanker(weights=[1.0], k=60)

        docs = [
            Document(page_content="A", metadata={"source": "doc1"}),
            Document(page_content="B", metadata={"source": "doc2"}),
        ]

        result = ranker.fuse([docs])

        # RRF formula: weight / (k + rank + 1)
        # First doc (rank 0): 1.0 / (60 + 0 + 1) = 1/61 ≈ 0.0164
        # Second doc (rank 1): 1.0 / (60 + 1 + 1) = 1/62 ≈ 0.0161
        assert abs(result[0].metadata["rrf_score"] - (1.0 / 61)) < 0.0001
        assert abs(result[1].metadata["rrf_score"] - (1.0 / 62)) < 0.0001

    def test_weighted_fusion(self):
        """Test that weights affect ranking."""
        # Dense heavily weighted
        ranker_dense_heavy = FusionRanker(weights=[0.9, 0.1], k=60)

        dense_docs = [
            Document(page_content="A", metadata={"source": "doc1", "chunk_id": "1"}),
        ]
        sparse_docs = [
            Document(page_content="B", metadata={"source": "doc2", "chunk_id": "1"}),
        ]

        result = ranker_dense_heavy.fuse([dense_docs, sparse_docs])

        # Doc1 (from dense) should rank higher due to weight
        assert result[0].metadata["source"] == "doc1"

        # Sparse heavily weighted
        ranker_sparse_heavy = FusionRanker(weights=[0.1, 0.9], k=60)

        result = ranker_sparse_heavy.fuse([dense_docs, sparse_docs])

        # Doc2 (from sparse) should rank higher due to weight
        assert result[0].metadata["source"] == "doc2"

    def test_deduplication_by_source(self):
        """Test deduplication using source key."""
        ranker = FusionRanker(deduplication_key="source")

        # Same source and content in both lists
        dense_docs = [
            Document(page_content="Same content", metadata={"source": "doc1"}),
        ]
        sparse_docs = [
            Document(page_content="Same content", metadata={"source": "doc1"}),
        ]

        result = ranker.fuse([dense_docs, sparse_docs])

        # Should be only 1 document (deduplicated)
        assert len(result) == 1
        # Should keep first occurrence (from dense)
        assert result[0].page_content == "Same content"

    def test_deduplication_by_chunk_id(self):
        """Test deduplication using chunk_id."""
        ranker = FusionRanker()

        # Different sources but same chunk_id should still deduplicate
        dense_docs = [
            Document(
                page_content="A",
                metadata={"source": "doc1", "chunk_id": "chunk_1"}
            ),
        ]
        sparse_docs = [
            Document(
                page_content="A",
                metadata={"source": "doc1", "chunk_id": "chunk_1"}
            ),
        ]

        result = ranker.fuse([dense_docs, sparse_docs])

        assert len(result) == 1

    def test_no_chunk_id_fallback(self):
        """Test deduplication when chunk_id is not present."""
        ranker = FusionRanker()

        # Same source, no chunk_id, same content
        dense_docs = [
            Document(page_content="Same content", metadata={"source": "doc1"}),
        ]
        sparse_docs = [
            Document(page_content="Same content", metadata={"source": "doc1"}),
        ]

        result = ranker.fuse([dense_docs, sparse_docs])

        # Should deduplicate based on content hash
        assert len(result) == 1

    def test_get_score_breakdown(self):
        """Test score breakdown for debugging."""
        ranker = FusionRanker(weights=[0.6, 0.4], k=60)

        dense_docs = [
            Document(page_content="A", metadata={"source": "doc1", "chunk_id": "1"}),
            Document(page_content="B", metadata={"source": "doc2", "chunk_id": "1"}),
        ]
        sparse_docs = [
            Document(page_content="A", metadata={"source": "doc1", "chunk_id": "1"}),
        ]

        # Fuse first
        result = ranker.fuse([dense_docs, sparse_docs])

        # Get breakdown for doc1 (appears in both)
        doc1 = result[0]  # Should be doc1 since it appears in both
        breakdown = ranker.get_score_breakdown(doc1, [dense_docs, sparse_docs])

        assert "total_rrf_score" in breakdown
        assert "retriever_scores" in breakdown
        assert "retriever_ranks" in breakdown
        assert "appears_in" in breakdown

        # Doc1 appears in both retrievers
        assert len(breakdown["appears_in"]) == 2
        assert 0 in breakdown["appears_in"]
        assert 1 in breakdown["appears_in"]

    def test_score_breakdown_ranks(self):
        """Test that score breakdown has correct ranks."""
        ranker = FusionRanker()

        dense_docs = [
            Document(page_content="A", metadata={"source": "doc1", "chunk_id": "1"}),
            Document(page_content="B", metadata={"source": "doc2", "chunk_id": "1"}),
            Document(page_content="C", metadata={"source": "doc3", "chunk_id": "1"}),
        ]
        sparse_docs = [
            Document(page_content="C", metadata={"source": "doc3", "chunk_id": "1"}),
            Document(page_content="A", metadata={"source": "doc1", "chunk_id": "1"}),
        ]

        result = ranker.fuse([dense_docs, sparse_docs])

        # Get doc1
        doc1 = [d for d in result if d.metadata["source"] == "doc1"][0]
        breakdown = ranker.get_score_breakdown(doc1, [dense_docs, sparse_docs])

        # Doc1 is rank 0 in dense, rank 1 in sparse
        assert breakdown["retriever_ranks"][0] == 0  # Dense
        assert breakdown["retriever_ranks"][1] == 1  # Sparse

    def test_many_retrievers(self):
        """Test fusion with more than 2 retrievers."""
        ranker = FusionRanker(weights=[0.5, 0.3, 0.2], k=60)

        list1 = [Document(page_content="A", metadata={"source": "doc1", "chunk_id": "1"})]
        list2 = [Document(page_content="B", metadata={"source": "doc2", "chunk_id": "1"})]
        list3 = [Document(page_content="C", metadata={"source": "doc3", "chunk_id": "1"})]

        result = ranker.fuse([list1, list2, list3])

        assert len(result) == 3
        # All should have scores
        for doc in result:
            assert "rrf_score" in doc.metadata

    def test_unequal_list_lengths(self):
        """Test fusion with different length result lists."""
        ranker = FusionRanker()

        dense_docs = [
            Document(page_content=f"Doc{i}", metadata={"source": f"doc{i}", "chunk_id": str(i)})
            for i in range(10)
        ]
        sparse_docs = [
            Document(page_content=f"Doc{i}", metadata={"source": f"doc{i}", "chunk_id": str(i)})
            for i in range(3)
        ]

        result = ranker.fuse([dense_docs, sparse_docs])

        # Should handle different lengths
        assert len(result) == 10  # All unique docs

    def test_preserve_metadata(self):
        """Test that original metadata is preserved."""
        ranker = FusionRanker()

        docs = [
            Document(
                page_content="A",
                metadata={
                    "source": "doc1",
                    "custom_field": "value",
                    "page": 42,
                }
            ),
        ]

        result = ranker.fuse([docs])

        # Original metadata preserved
        assert result[0].metadata["source"] == "doc1"
        assert result[0].metadata["custom_field"] == "value"
        assert result[0].metadata["page"] == 42
        # RRF score added
        assert "rrf_score" in result[0].metadata

    def test_sort_order(self):
        """Test that results are sorted by RRF score descending."""
        ranker = FusionRanker()

        docs = [
            Document(page_content=f"Doc{i}", metadata={"source": f"doc{i}", "chunk_id": str(i)})
            for i in range(5)
        ]

        result = ranker.fuse([docs])

        # Check scores are in descending order
        scores = [doc.metadata["rrf_score"] for doc in result]
        assert scores == sorted(scores, reverse=True)
