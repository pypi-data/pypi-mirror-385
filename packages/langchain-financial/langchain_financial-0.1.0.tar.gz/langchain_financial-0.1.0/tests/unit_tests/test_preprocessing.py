"""Unit tests for QueryPreprocessor."""

import pytest
from langchain_financial.preprocessing import QueryPreprocessor


class TestQueryPreprocessor:
    """Test suite for QueryPreprocessor."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        preprocessor = QueryPreprocessor()

        assert preprocessor.extract_entities is True
        assert preprocessor.normalize_numbers is True
        assert preprocessor.expand_synonyms is True
        assert preprocessor.patterns is not None
        assert preprocessor.synonyms is not None

    def test_init_custom(self):
        """Test initialization with custom parameters."""
        preprocessor = QueryPreprocessor(
            extract_entities=False,
            normalize_numbers=False,
            expand_synonyms=False,
        )

        assert preprocessor.extract_entities is False
        assert preprocessor.normalize_numbers is False
        assert preprocessor.expand_synonyms is False

    def test_extract_ticker(self):
        """Test ticker extraction."""
        preprocessor = QueryPreprocessor()

        query = "What is AAPL revenue?"
        result = preprocessor.preprocess(query)

        assert "ticker" in result["entities"]
        assert "AAPL" in result["entities"]["ticker"]

    def test_extract_multiple_tickers(self):
        """Test extraction of multiple tickers."""
        preprocessor = QueryPreprocessor()

        query = "Compare AAPL and MSFT performance"
        result = preprocessor.preprocess(query)

        assert "ticker" in result["entities"]
        assert "AAPL" in result["entities"]["ticker"]
        assert "MSFT" in result["entities"]["ticker"]

    def test_extract_year(self):
        """Test year extraction."""
        preprocessor = QueryPreprocessor()

        query = "What happened in 2024?"
        result = preprocessor.preprocess(query)

        assert "year" in result["entities"]
        assert "2024" in result["entities"]["year"]

    def test_extract_quarter(self):
        """Test quarter extraction."""
        preprocessor = QueryPreprocessor()

        query = "Q4 results"
        result = preprocessor.preprocess(query)

        assert "quarter" in result["entities"]
        assert "Q4" in result["entities"]["quarter"]

    def test_extract_money(self):
        """Test money amount extraction."""
        preprocessor = QueryPreprocessor()

        query = "Revenue was $5.2M"
        result = preprocessor.preprocess(query)

        assert "money" in result["entities"]
        assert "$5.2M" in result["entities"]["money"]

    def test_extract_percentage(self):
        """Test percentage extraction."""
        preprocessor = QueryPreprocessor()

        query = "Growth of 15.5% year-over-year"
        result = preprocessor.preprocess(query)

        assert "percentage" in result["entities"]
        assert "15.5%" in result["entities"]["percentage"]

    def test_normalize_millions(self):
        """Test normalization of millions."""
        preprocessor = QueryPreprocessor()

        query = "Revenue of $5.2M"
        result = preprocessor.preprocess(query)

        assert "$5.2M" in result["normalized_numbers"]
        assert result["normalized_numbers"]["$5.2M"] == 5_200_000.0
        assert "5200000" in result["processed_query"]

    def test_normalize_billions(self):
        """Test normalization of billions."""
        preprocessor = QueryPreprocessor()

        query = "Market cap $2.5B"
        result = preprocessor.preprocess(query)

        assert "$2.5B" in result["normalized_numbers"]
        assert result["normalized_numbers"]["$2.5B"] == 2_500_000_000.0

    def test_normalize_thousands(self):
        """Test normalization of thousands."""
        preprocessor = QueryPreprocessor()

        query = "Salary $100K"
        result = preprocessor.preprocess(query)

        assert "$100K" in result["normalized_numbers"]
        assert result["normalized_numbers"]["$100K"] == 100_000.0

    def test_normalize_multiple_numbers(self):
        """Test normalization of multiple numbers."""
        preprocessor = QueryPreprocessor()

        query = "Revenue grew from $5.2M to $10.5M"
        result = preprocessor.preprocess(query)

        assert len(result["normalized_numbers"]) == 2
        assert result["normalized_numbers"]["$5.2M"] == 5_200_000.0
        assert result["normalized_numbers"]["$10.5M"] == 10_500_000.0

    def test_expand_revenue_synonyms(self):
        """Test query expansion for revenue."""
        preprocessor = QueryPreprocessor()

        query = "revenue growth"
        result = preprocessor.preprocess(query)

        assert len(result["expanded_terms"]) > 0
        # Should include synonyms like "sales", "top line"
        expanded_lower = [term.lower() for term in result["expanded_terms"]]
        assert any("sales" in term for term in expanded_lower)

    def test_expand_profit_synonyms(self):
        """Test query expansion for profit."""
        preprocessor = QueryPreprocessor()

        query = "profit margins"
        result = preprocessor.preprocess(query)

        assert len(result["expanded_terms"]) > 0
        expanded_lower = [term.lower() for term in result["expanded_terms"]]
        assert any("earnings" in term or "net income" in term for term in expanded_lower)

    def test_detect_financial_metrics(self):
        """Test detection of financial metrics."""
        preprocessor = QueryPreprocessor()

        query = "What is the EBITDA and EPS?"
        result = preprocessor.preprocess(query)

        assert "ebitda" in result["detected_metrics"]
        assert "eps" in result["detected_metrics"]

    def test_detect_revenue_metric(self):
        """Test detection of revenue as metric."""
        preprocessor = QueryPreprocessor()

        query = "revenue growth trends"
        result = preprocessor.preprocess(query)

        assert "revenue" in result["detected_metrics"]

    def test_no_entities_found(self):
        """Test query with no entities."""
        preprocessor = QueryPreprocessor()

        query = "general question about business"
        result = preprocessor.preprocess(query)

        assert len(result["entities"]) == 0

    def test_disabled_entity_extraction(self):
        """Test with entity extraction disabled."""
        preprocessor = QueryPreprocessor(extract_entities=False)

        query = "What is AAPL revenue in Q4 2024?"
        result = preprocessor.preprocess(query)

        assert len(result["entities"]) == 0

    def test_disabled_number_normalization(self):
        """Test with number normalization disabled."""
        preprocessor = QueryPreprocessor(normalize_numbers=False)

        query = "Revenue of $5.2M"
        result = preprocessor.preprocess(query)

        assert len(result["normalized_numbers"]) == 0
        assert "$5.2M" in result["processed_query"]

    def test_disabled_synonym_expansion(self):
        """Test with synonym expansion disabled."""
        preprocessor = QueryPreprocessor(expand_synonyms=False)

        query = "revenue growth"
        result = preprocessor.preprocess(query)

        assert len(result["expanded_terms"]) == 0

    def test_complex_query(self):
        """Test complex query with multiple features."""
        preprocessor = QueryPreprocessor()

        query = "Compare AAPL and MSFT revenue growth in Q4 2024, around $5.2M and $10.5B"
        result = preprocessor.preprocess(query)

        # Should extract tickers
        assert "ticker" in result["entities"]
        assert len(result["entities"]["ticker"]) == 2

        # Should extract quarter and year
        assert "quarter" in result["entities"]
        assert "year" in result["entities"]

        # Should normalize numbers
        assert len(result["normalized_numbers"]) == 2

        # Should detect metrics
        assert "revenue" in result["detected_metrics"]
        assert "growth" in result["detected_metrics"]

    def test_custom_patterns(self):
        """Test with custom entity patterns."""
        custom_patterns = {
            "custom": r"\b[A-Z]{2,3}\d{2,4}\b",  # Match codes like ABC123
        }

        preprocessor = QueryPreprocessor(
            financial_entity_patterns=custom_patterns
        )

        query = "Code ABC123 reported"
        result = preprocessor.preprocess(query)

        assert "custom" in result["entities"]
        assert "ABC123" in result["entities"]["custom"]

    def test_original_query_preserved(self):
        """Test that original query is preserved."""
        preprocessor = QueryPreprocessor()

        query = "Original query with $5.2M"
        result = preprocessor.preprocess(query)

        assert result["original_query"] == query
        assert result["processed_query"] != query  # Should be normalized

    def test_empty_query(self):
        """Test handling of empty query."""
        preprocessor = QueryPreprocessor()

        query = ""
        result = preprocessor.preprocess(query)

        assert result["original_query"] == ""
        assert result["processed_query"] == ""
        assert len(result["entities"]) == 0
        assert len(result["normalized_numbers"]) == 0

    def test_case_insensitive_metrics(self):
        """Test case-insensitive metric detection."""
        preprocessor = QueryPreprocessor()

        query = "What is the EBITDA and ebitda?"
        result = preprocessor.preprocess(query)

        # Should detect both (deduplicated)
        assert "ebitda" in result["detected_metrics"]
        # Check it's not duplicated
        assert result["detected_metrics"].count("ebitda") == 1
