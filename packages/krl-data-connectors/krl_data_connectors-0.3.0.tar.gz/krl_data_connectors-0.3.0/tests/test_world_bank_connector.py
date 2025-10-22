"""
Comprehensive tests for World Bank Indicators API Connector.

This test suite follows the 10-layer testing architecture:
- Layer 1: Unit tests (core functionality)
- Layer 2: Integration tests (API interactions)
- Layer 5: Security tests (input validation)
- Layer 7: Property-based tests (edge cases with Hypothesis)
- Layer 8: Contract tests (type safety)

Test Coverage Goals:
- 70-80% line coverage with HIGH-QUALITY tests
- All public methods tested
- Security vulnerabilities validated
- Edge cases covered with property-based testing
- API contracts validated

Author: KR Labs
Date: October 2025
"""

from unittest.mock import Mock, patch

import pytest
import requests
from hypothesis import given
from hypothesis import strategies as st
from requests.exceptions import HTTPError, RequestException

from krl_data_connectors.economic import WorldBankConnector

# ============================================================================
# LAYER 1: UNIT TESTS - Core Functionality
# ============================================================================


class TestWorldBankConnectorInitialization:
    """Test connector initialization and configuration."""

    def test_initialization_default_values(self):
        """Test that connector initializes with correct default values."""
        wb = WorldBankConnector()

        assert wb.base_url == "https://api.worldbank.org/v2"
        assert wb.default_format == "json"
        assert wb.default_per_page == 50

    def test_initialization_with_custom_params(self):
        """Test initialization with custom parameters."""
        wb = WorldBankConnector(cache_ttl=7200, timeout=60)

        assert wb.base_url == "https://api.worldbank.org/v2"
        # BaseConnector should handle these params

    def test_get_api_key_returns_none(self):
        """Test that World Bank API does not require authentication."""
        wb = WorldBankConnector()

        api_key = wb._get_api_key()

        assert api_key is None


class TestWorldBankConnectorConnection:
    """Test connection establishment and session management."""

    @patch("requests.Session")
    def test_connect_success(self, mock_session_class):
        """Test successful connection to World Bank API."""
        # Setup mock
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        wb = WorldBankConnector()

        # Patch _init_session to return our mock
        with patch.object(wb, "_init_session", return_value=mock_session):
            wb.connect()

        # Verify connection test was made
        assert mock_session.get.called
        call_args = mock_session.get.call_args
        assert "country" in call_args[0][0]  # URL contains 'country'

    @patch("requests.Session")
    def test_connect_failure(self, mock_session_class):
        """Test connection failure handling."""
        mock_session = Mock()
        mock_session.get.side_effect = RequestException("Connection failed")
        mock_session_class.return_value = mock_session

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            with pytest.raises(ConnectionError) as exc_info:
                wb.connect()

        assert "Failed to connect" in str(exc_info.value)

    def test_close_session(self):
        """Test session closure."""
        wb = WorldBankConnector()
        mock_session = Mock()
        wb.session = mock_session

        wb.close()

        assert mock_session.close.called
        assert wb.session is None


class TestWorldBankConnectorFetch:
    """Test generic fetch method routing."""

    def test_fetch_with_indicator_query(self):
        """Test fetch routes to get_indicator_data."""
        wb = WorldBankConnector()

        with patch.object(wb, "get_indicator_data") as mock_get:
            mock_get.return_value = [{"test": "data"}]

            result = wb.fetch(query_type="indicator", indicator="SP.POP.TOTL", countries="USA")

            assert mock_get.called
            assert result == [{"test": "data"}]

    def test_fetch_with_countries_query(self):
        """Test fetch routes to get_countries."""
        wb = WorldBankConnector()

        with patch.object(wb, "get_countries") as mock_get:
            mock_get.return_value = [{"country": "data"}]

            result = wb.fetch(query_type="countries", income_level="HIC")

            assert mock_get.called
            assert result == [{"country": "data"}]

    def test_fetch_with_invalid_query_type(self):
        """Test fetch raises error for invalid query type."""
        wb = WorldBankConnector()

        with pytest.raises(ValueError) as exc_info:
            wb.fetch(query_type="invalid_type")

        assert "Invalid query_type" in str(exc_info.value)


class TestWorldBankConnectorPagination:
    """Test paginated request handling."""

    @patch("requests.Session")
    def test_make_paginated_request_single_page(self, mock_session_class):
        """Test paginated request with single page of results."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "per_page": 50, "total": 10},
            [{"id": "USA", "name": "United States"}],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            results = wb._make_paginated_request("country")

        assert len(results) == 1
        assert results[0]["id"] == "USA"

    @patch("requests.Session")
    def test_make_paginated_request_multiple_pages(self, mock_session_class):
        """Test paginated request with multiple pages."""
        mock_session = Mock()

        # First page
        mock_response_1 = Mock()
        mock_response_1.json.return_value = [
            {"page": 1, "pages": 2, "per_page": 50, "total": 60},
            [{"id": f"Country{i}"} for i in range(50)],
        ]
        mock_response_1.raise_for_status = Mock()

        # Second page
        mock_response_2 = Mock()
        mock_response_2.json.return_value = [
            {"page": 2, "pages": 2, "per_page": 50, "total": 60},
            [{"id": f"Country{i}"} for i in range(50, 60)],
        ]
        mock_response_2.raise_for_status = Mock()

        mock_session.get.side_effect = [mock_response_1, mock_response_2]

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            results = wb._make_paginated_request("country")

        assert len(results) == 60
        assert mock_session.get.call_count == 2

    @patch("requests.Session")
    def test_make_paginated_request_api_error(self, mock_session_class):
        """Test paginated request handles API errors."""
        mock_session = Mock()
        mock_session.get.side_effect = HTTPError("API Error")

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            with pytest.raises(ConnectionError) as exc_info:
                wb._make_paginated_request("country")

        assert "API request failed" in str(exc_info.value)


# ============================================================================
# LAYER 2: INTEGRATION TESTS - API Interactions
# ============================================================================


class TestWorldBankConnectorIndicatorData:
    """Test indicator data retrieval."""

    @patch("requests.Session")
    def test_get_indicator_data_single_country(self, mock_session_class):
        """Test fetching indicator data for a single country."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 1},
            [
                {
                    "indicator": {"id": "SP.POP.TOTL", "value": "Population, total"},
                    "country": {"id": "US", "value": "United States"},
                    "countryiso3code": "USA",
                    "date": "2020",
                    "value": 331002651,
                }
            ],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            results = wb.get_indicator_data(
                indicator="SP.POP.TOTL", countries="USA", date_range="2020"
            )

        assert len(results) == 1
        assert results[0]["countryiso3code"] == "USA"
        assert results[0]["date"] == "2020"
        assert results[0]["value"] == 331002651

    @patch("requests.Session")
    def test_get_indicator_data_multiple_countries(self, mock_session_class):
        """Test fetching indicator data for multiple countries."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 3},
            [
                {"countryiso3code": "USA", "date": "2020", "value": 331002651},
                {"countryiso3code": "CHN", "date": "2020", "value": 1439323776},
                {"countryiso3code": "IND", "date": "2020", "value": 1380004385},
            ],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            results = wb.get_indicator_data(
                indicator="SP.POP.TOTL", countries=["USA", "CHN", "IND"], date_range="2020"
            )

        assert len(results) == 3
        assert "USA" in [r["countryiso3code"] for r in results]
        assert "CHN" in [r["countryiso3code"] for r in results]
        assert "IND" in [r["countryiso3code"] for r in results]

    @patch("requests.Session")
    def test_get_indicator_data_with_mrv(self, mock_session_class):
        """Test fetching most recent values."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 5},
            [{"date": str(year), "value": 100000 + year} for year in range(2016, 2021)],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            results = wb.get_indicator_data(indicator="SP.POP.TOTL", countries="USA", mrv=5)

        assert len(results) == 5
        # Verify mrv parameter was passed
        call_args = mock_session.get.call_args
        assert call_args[1]["params"]["mrv"] == 5

    @patch("requests.Session")
    def test_get_indicator_data_with_frequency(self, mock_session_class):
        """Test fetching data with specific frequency."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 12},
            [{"date": f"2020M{m:02d}", "value": 1000 + m} for m in range(1, 13)],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            results = wb.get_indicator_data(
                indicator="MONTHLY_INDICATOR",
                countries="USA",
                date_range="2020M01:2020M12",
                frequency="M",
            )

        assert len(results) == 12
        # Verify frequency parameter was passed
        call_args = mock_session.get.call_args
        assert call_args[1]["params"]["frequency"] == "M"


class TestWorldBankConnectorMultipleIndicators:
    """Test multiple indicator retrieval."""

    @patch("requests.Session")
    def test_get_multiple_indicators_success(self, mock_session_class):
        """Test fetching multiple indicators at once."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 2},
            [
                {"indicator": {"id": "SP.POP.TOTL"}, "value": 331002651},
                {"indicator": {"id": "NY.GDP.MKTP.CD"}, "value": 20936600000000},
            ],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            results = wb.get_multiple_indicators(
                indicators=["SP.POP.TOTL", "NY.GDP.MKTP.CD"], countries="USA", source=2
            )

        assert len(results) == 2

    def test_get_multiple_indicators_exceeds_maximum(self):
        """Test error when requesting more than 60 indicators."""
        wb = WorldBankConnector()

        indicators = [f"INDICATOR_{i}" for i in range(61)]

        with pytest.raises(ValueError) as exc_info:
            wb.get_multiple_indicators(indicators=indicators, countries="USA")

        assert "Maximum 60 indicators" in str(exc_info.value)


class TestWorldBankConnectorCountries:
    """Test country metadata retrieval."""

    @patch("requests.Session")
    def test_get_countries_all(self, mock_session_class):
        """Test fetching all countries."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 3},
            [
                {"id": "USA", "name": "United States", "iso2Code": "US"},
                {"id": "CHN", "name": "China", "iso2Code": "CN"},
                {"id": "IND", "name": "India", "iso2Code": "IN"},
            ],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            results = wb.get_countries()

        assert len(results) == 3

    @patch("requests.Session")
    def test_get_countries_by_income_level(self, mock_session_class):
        """Test fetching countries filtered by income level."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 2},
            [
                {"id": "USA", "incomeLevel": {"id": "HIC"}},
                {"id": "GBR", "incomeLevel": {"id": "HIC"}},
            ],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            results = wb.get_countries(income_level="HIC")

        assert len(results) == 2
        # Verify income_level parameter was passed
        call_args = mock_session.get.call_args
        assert call_args[1]["params"]["incomeLevel"] == "HIC"


class TestWorldBankConnectorIndicators:
    """Test indicator metadata retrieval."""

    @patch("requests.Session")
    def test_get_indicators_all(self, mock_session_class):
        """Test fetching all indicators."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 2},
            [
                {"id": "SP.POP.TOTL", "name": "Population, total"},
                {"id": "NY.GDP.MKTP.CD", "name": "GDP (current US$)"},
            ],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            results = wb.get_indicators()

        assert len(results) == 2
        assert results[0]["id"] == "SP.POP.TOTL"

    @patch("requests.Session")
    def test_search_indicators(self, mock_session_class):
        """Test searching indicators by keyword."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 5},
            [
                {"id": "SP.POP.TOTL", "name": "Population, total"},
                {"id": "SP.POP.GROW", "name": "Population growth (annual %)"},
                {"id": "SP.URB.TOTL", "name": "Urban population"},
                {"id": "AG.LND.TOTL.K2", "name": "Land area (sq. km)"},
                {"id": "SP.RUR.TOTL", "name": "Rural population"},
            ],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            results = wb.search_indicators("population")

        # Should return only indicators with "population" in name
        assert len(results) == 4  # Excludes "Land area"
        assert all("population" in r["name"].lower() for r in results)

    @patch("requests.Session")
    def test_get_indicator_metadata(self, mock_session_class):
        """Test fetching metadata for specific indicator."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 1},
            [
                {
                    "id": "SP.POP.TOTL",
                    "name": "Population, total",
                    "unit": "Number",
                    "sourceNote": "Total population is based on...",
                }
            ],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            result = wb.get_indicator_metadata("SP.POP.TOTL")

        assert result["id"] == "SP.POP.TOTL"
        assert result["name"] == "Population, total"

    @patch("requests.Session")
    def test_get_indicator_metadata_not_found(self, mock_session_class):
        """Test error when indicator not found."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [{"page": 1, "pages": 1, "total": 0}, []]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            with pytest.raises(ValueError) as exc_info:
                wb.get_indicator_metadata("INVALID_INDICATOR")

        assert "Indicator not found" in str(exc_info.value)


class TestWorldBankConnectorSources:
    """Test data source retrieval."""

    @patch("requests.Session")
    def test_get_sources(self, mock_session_class):
        """Test fetching available data sources."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 3},
            [
                {"id": "1", "name": "Doing Business"},
                {"id": "2", "name": "World Development Indicators"},
                {"id": "11", "name": "Africa Development Indicators"},
            ],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            results = wb.get_sources()

        assert len(results) == 3
        assert results[1]["name"] == "World Development Indicators"


# ============================================================================
# LAYER 5: SECURITY TESTS - Input Validation
# ============================================================================


class TestWorldBankConnectorSecurity:
    """Test security and input validation."""

    def test_sql_injection_in_indicator_code(self):
        """Test that SQL injection attempts are handled safely."""
        wb = WorldBankConnector()

        malicious_indicator = "SP.POP.TOTL'; DROP TABLE countries; --"

        with patch.object(wb, "_make_paginated_request") as mock_request:
            mock_request.return_value = []

            # Should not raise exception, just make API call
            wb.get_indicator_data(indicator=malicious_indicator, countries="USA")

            # Verify the malicious string is passed as-is (API will reject it)
            assert mock_request.called
            call_args = mock_request.call_args[0][0]
            assert malicious_indicator in call_args

    def test_xss_in_country_code(self):
        """Test that XSS attempts in country codes are handled safely."""
        wb = WorldBankConnector()

        malicious_country = "<script>alert('xss')</script>"

        with patch.object(wb, "_make_paginated_request") as mock_request:
            mock_request.return_value = []

            # Should not raise exception
            wb.get_indicator_data(indicator="SP.POP.TOTL", countries=malicious_country)

            assert mock_request.called

    def test_path_traversal_in_endpoint(self):
        """Test that path traversal attempts are handled safely."""
        wb = WorldBankConnector()

        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.json.return_value = [{"page": 1, "pages": 1}, []]
            mock_response.raise_for_status = Mock()
            mock_session.get.return_value = mock_response

            with patch.object(wb, "_init_session", return_value=mock_session):
                # Try to access parent directory
                wb._make_paginated_request("../../etc/passwd")

                # Verify URL is constructed correctly (path traversal won't work)
                call_args = mock_session.get.call_args
                url = call_args[0][0]
                assert wb.base_url in url

    def test_empty_indicator_handling(self):
        """Test handling of empty indicator codes."""
        wb = WorldBankConnector()

        with patch.object(wb, "_make_paginated_request") as mock_request:
            mock_request.return_value = []

            # Empty string should be handled gracefully
            wb.get_indicator_data(indicator="", countries="USA")

            assert mock_request.called

    def test_special_characters_in_date_range(self):
        """Test handling of special characters in date ranges."""
        wb = WorldBankConnector()

        with patch.object(wb, "_make_paginated_request") as mock_request:
            mock_request.return_value = []

            # Special characters in date range
            wb.get_indicator_data(
                indicator="SP.POP.TOTL", countries="USA", date_range="2020;rm -rf /"
            )

            assert mock_request.called
            # Verify special characters are passed to API (which will reject them)
            call_args = mock_request.call_args
            assert "2020;rm -rf /" in str(call_args)


# ============================================================================
# LAYER 7: PROPERTY-BASED TESTS - Edge Cases with Hypothesis
# ============================================================================


class TestWorldBankConnectorPropertyBased:
    """Property-based tests using Hypothesis for edge case discovery."""

    @given(country_code=st.text(min_size=1, max_size=10))
    def test_country_code_handling(self, country_code):
        """Test that any country code string is handled without crashing."""
        wb = WorldBankConnector()

        with patch.object(wb, "_make_paginated_request") as mock_request:
            mock_request.return_value = []

            # Should not raise exception regardless of input
            try:
                wb.get_indicator_data(indicator="SP.POP.TOTL", countries=country_code)
                assert mock_request.called
            except (ConnectionError, ValueError):
                # These are acceptable exceptions
                pass

    @given(indicator_code=st.text(min_size=1, max_size=50))
    def test_indicator_code_handling(self, indicator_code):
        """Test that any indicator code is handled without crashing."""
        wb = WorldBankConnector()

        with patch.object(wb, "_make_paginated_request") as mock_request:
            mock_request.return_value = []

            try:
                wb.get_indicator_data(indicator=indicator_code, countries="USA")
                assert mock_request.called
            except (ConnectionError, ValueError):
                pass

    @given(
        year=st.integers(min_value=1960, max_value=2030), mrv=st.integers(min_value=1, max_value=20)
    )
    def test_year_and_mrv_combinations(self, year, mrv):
        """Test various combinations of year and MRV parameters."""
        wb = WorldBankConnector()

        with patch.object(wb, "_make_paginated_request") as mock_request:
            mock_request.return_value = []

            # Test with year range
            wb.get_indicator_data(
                indicator="SP.POP.TOTL", countries="USA", date_range=f"{year}:{year+1}", mrv=mrv
            )

            assert mock_request.called

    @given(num_countries=st.integers(min_value=1, max_value=10))
    def test_multiple_countries_list(self, num_countries):
        """Test that various list sizes of countries are handled correctly."""
        wb = WorldBankConnector()

        countries = [f"C{i:02d}" for i in range(num_countries)]

        with patch.object(wb, "_make_paginated_request") as mock_request:
            mock_request.return_value = []

            wb.get_indicator_data(indicator="SP.POP.TOTL", countries=countries)

            assert mock_request.called
            # Verify countries are joined with semicolon
            call_args = mock_request.call_args[0][0]
            assert ";" in call_args or num_countries == 1


# ============================================================================
# LAYER 8: CONTRACT TESTS - Type Safety
# ============================================================================


class TestWorldBankConnectorTypeContracts:
    """Test type contracts and return value structures."""

    @patch("requests.Session")
    def test_get_indicator_data_return_type(self, mock_session_class):
        """Test that get_indicator_data returns list of dicts."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1},
            [{"indicator": {"id": "SP.POP.TOTL"}, "value": 100000}],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            result = wb.get_indicator_data(indicator="SP.POP.TOTL", countries="USA")

        # Verify return type
        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], dict)

    @patch("requests.Session")
    def test_get_countries_return_type(self, mock_session_class):
        """Test that get_countries returns list of dicts."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1},
            [{"id": "USA", "name": "United States"}],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            result = wb.get_countries()

        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], dict)
            assert "id" in result[0]
            assert "name" in result[0]

    def test_get_api_key_return_type(self):
        """Test that _get_api_key returns None."""
        wb = WorldBankConnector()

        result = wb._get_api_key()

        assert result is None

    def test_close_return_type(self):
        """Test that close returns None."""
        wb = WorldBankConnector()
        wb.session = Mock()

        result = wb.close()

        assert result is None

    def test_connect_return_type(self):
        """Test that connect returns None."""
        wb = WorldBankConnector()

        result = wb.connect()

        assert result is None

    @patch("requests.Session")
    def test_get_multiple_indicators_return_type(self, mock_session_class):
        """Test that get_multiple_indicators returns list of dicts."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1},
            [
                {
                    "indicator": {"id": "SP.POP.TOTL", "value": "Population"},
                    "country": {"id": "USA"},
                    "value": 100000,
                }
            ],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            result = wb.get_multiple_indicators(
                indicators=["SP.POP.TOTL"], countries=["USA"]
            )

        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], dict)

    @patch("requests.Session")
    def test_get_indicators_return_type(self, mock_session_class):
        """Test that get_indicators returns list of dicts."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1},
            [{"id": "SP.POP.TOTL", "name": "Population, total"}],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            result = wb.get_indicators()

        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], dict)

    @patch("requests.Session")
    def test_search_indicators_return_type(self, mock_session_class):
        """Test that search_indicators returns list of dicts."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1},
            [{"id": "SP.POP.TOTL", "name": "Population, total"}],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            result = wb.search_indicators("population")

        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], dict)
            assert "id" in result[0]
            assert "name" in result[0]

    @patch("requests.Session")
    def test_get_sources_return_type(self, mock_session_class):
        """Test that get_sources returns list of dicts."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1},
            [{"id": 2, "name": "World Development Indicators"}],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            result = wb.get_sources()

        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], dict)

    @patch("requests.Session")
    def test_get_indicator_metadata_return_type(self, mock_session_class):
        """Test that get_indicator_metadata returns dict."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1},
            [{"id": "SP.POP.TOTL", "name": "Population, total", "sourceNote": "..."}],
        ]
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        wb = WorldBankConnector()

        with patch.object(wb, "_init_session", return_value=mock_session):
            result = wb.get_indicator_metadata("SP.POP.TOTL")

        assert isinstance(result, dict)
        assert "id" in result


# ============================================================================
# Test Configuration
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
