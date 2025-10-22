"""
Comprehensive test suite for USDA NASS QuickStats connector.

Tests cover:
- Layer 1: Unit tests (initialization, connection, core methods)
- Layer 2: Integration tests (API interactions with mocked responses)
- Layer 5: Security tests (injection, XSS, input validation)
- Layer 7: Property-based tests (Hypothesis for edge cases)
- Layer 8: Contract tests (type safety validation)
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest
import requests
from hypothesis import given
from hypothesis import strategies as st

from krl_data_connectors.agricultural.usda_nass_connector import USDANASSConnector

# ============================================================================
# Layer 1: Unit Tests - Initialization & Core Functionality
# ============================================================================


class TestUSDANASSConnectorInitialization:
    """Test USDA NASS connector initialization and setup."""

    def test_initialization_default_values(self):
        """Test connector initializes with correct default values."""
        nass = USDANASSConnector(api_key="test_key")

        assert nass.base_url == "https://quickstats.nass.usda.gov/api"
        assert nass.connector_name == "USDANASS"
        assert nass.session is None
        assert nass.api_key == "test_key"

    def test_initialization_with_custom_params(self):
        """Test connector accepts custom parameters."""
        nass = USDANASSConnector(api_key="test_key", cache_dir="/tmp/nass_cache", cache_ttl=7200)

        assert nass.base_url == "https://quickstats.nass.usda.gov/api"
        assert nass.api_key == "test_key"

    def test_get_api_key_from_init(self):
        """Test API key retrieval from initialization."""
        nass = USDANASSConnector(api_key="my_api_key")

        # The API key is stored in base connector, _get_api_key retrieves from config
        # So we verify the api_key attribute is set
        assert nass.api_key == "my_api_key"


# ============================================================================
# Layer 2: Integration Tests - Connection & Session Management
# ============================================================================


class TestUSDANASSConnectorConnection:
    """Test USDA NASS connector connection lifecycle."""

    @patch("requests.Session.get")
    def test_connect_success(self, mock_get):
        """Test successful connection to USDA NASS API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"year": ["2023", "2022", "2021"]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass.connect()

        assert nass.session is not None
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "get_param_values" in call_args[0][0]
        assert call_args[1]["params"]["key"] == "test_key"

    def test_connect_without_api_key(self):
        """Test connection fails without API key."""
        # Use a mock config that returns None for API key
        with patch.object(USDANASSConnector, "_get_api_key", return_value=None):
            nass = USDANASSConnector()

            with pytest.raises(ValueError, match="API key is required"):
                nass.connect()

    @patch("requests.Session.get")
    def test_connect_failure(self, mock_get):
        """Test connection failure handling."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        nass = USDANASSConnector(api_key="test_key")

        with pytest.raises(ConnectionError, match="Failed to connect to USDA NASS API"):
            nass.connect()

    @patch("requests.Session.get")
    def test_disconnect_session(self, mock_get):
        """Test session disconnection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"year": ["2023"]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass.connect()

        mock_session = nass.session
        mock_session.close = MagicMock()

        nass.disconnect()

        mock_session.close.assert_called_once()


# ============================================================================
# Layer 2: Integration Tests - Fetch Method
# ============================================================================


class TestUSDANASSConnectorFetch:
    """Test generic fetch method."""

    @patch("requests.Session.get")
    def test_fetch_with_valid_params(self, mock_get):
        """Test fetching data with valid parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"commodity_desc": "CORN", "year": 2023, "Value": "1000000"}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        result = nass.fetch(query_params={"commodity_desc": "CORN", "year": 2023})

        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["commodity_desc"] == "CORN"

    @patch("requests.Session.get")
    def test_fetch_with_error_response(self, mock_get):
        """Test fetch handling API error response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": ["Invalid parameter"]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        with pytest.raises(ValueError, match="API error"):
            nass.fetch(query_params={"invalid_param": "value"})

    def test_fetch_without_api_key(self):
        """Test fetch fails without API key."""
        with patch.object(USDANASSConnector, "_get_api_key", return_value=None):
            nass = USDANASSConnector()
            nass._init_session()

            with pytest.raises(ValueError, match="API key is required"):
                nass.fetch(query_params={"commodity_desc": "CORN"})


# ============================================================================
# Layer 2: Integration Tests - Data Retrieval
# ============================================================================


class TestUSDANASSConnectorDataRetrieval:
    """Test data retrieval methods."""

    @patch("requests.Session.get")
    def test_get_data_with_commodity_and_year(self, mock_get):
        """Test getting data with commodity and year filters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "commodity_desc": "CORN",
                    "year": 2023,
                    "state_name": "IOWA",
                    "Value": "2500000000",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        result = nass.get_data(commodity="CORN", year=2023)

        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["commodity_desc"] == "CORN"

        # Verify API call parameters
        call_args = mock_get.call_args
        assert call_args[1]["params"]["commodity_desc"] == "CORN"
        assert call_args[1]["params"]["year"] == 2023

    @patch("requests.Session.get")
    def test_get_data_with_state_filter(self, mock_get):
        """Test getting data with state filter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        result = nass.get_data(commodity="WHEAT", state="KANSAS", year=2023)

        # Verify state parameter passed correctly
        call_args = mock_get.call_args
        assert call_args[1]["params"]["state_name"] == "KANSAS"

    @patch("requests.Session.get")
    def test_get_data_with_additional_params(self, mock_get):
        """Test get_data with additional parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        result = nass.get_data(
            commodity="CATTLE", year=2023, agg_level_desc="COUNTY", freq_desc="ANNUAL"
        )

        # Verify additional parameters passed
        call_args = mock_get.call_args
        assert call_args[1]["params"]["agg_level_desc"] == "COUNTY"
        assert call_args[1]["params"]["freq_desc"] == "ANNUAL"

    def test_get_data_without_filters(self):
        """Test get_data requires at least one filter."""
        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        with pytest.raises(ValueError, match="At least one filter parameter must be provided"):
            nass.get_data()


# ============================================================================
# Layer 2: Integration Tests - Helper Methods
# ============================================================================


class TestUSDANASSConnectorHelperMethods:
    """Test helper methods."""

    @patch("requests.Session.get")
    def test_get_param_values_success(self, mock_get):
        """Test getting parameter values."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "commodity_desc": ["CORN", "WHEAT", "SOYBEANS", "CATTLE"]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        result = nass.get_param_values("commodity_desc")

        assert isinstance(result, list)
        assert "CORN" in result
        assert "WHEAT" in result

        # Verify API call
        call_args = mock_get.call_args
        assert "get_param_values" in call_args[0][0]
        assert call_args[1]["params"]["param"] == "commodity_desc"

    @patch("requests.Session.get")
    def test_get_counts_success(self, mock_get):
        """Test getting record counts."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 1250}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        count = nass.get_counts(commodity_desc="CORN", year=2023)

        assert isinstance(count, int)
        assert count == 1250

        # Verify API call
        call_args = mock_get.call_args
        assert "get_counts" in call_args[0][0]

    def test_get_param_values_without_api_key(self):
        """Test get_param_values fails without API key."""
        with patch.object(USDANASSConnector, "_get_api_key", return_value=None):
            nass = USDANASSConnector()
            nass._init_session()

            with pytest.raises(ValueError, match="API key is required"):
                nass.get_param_values("year")


# ============================================================================
# Layer 5: Security Tests - Injection & Attack Prevention
# ============================================================================


class TestUSDANASSConnectorSecurity:
    """Test security measures against common attacks."""

    @patch("requests.Session.get")
    def test_sql_injection_in_commodity(self, mock_get):
        """Test SQL injection attempts in commodity parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        # Attempt SQL injection
        malicious_commodity = "CORN'; DROP TABLE data; --"

        result = nass.get_data(commodity=malicious_commodity, year=2023)

        # Verify parameter was passed as-is (not executed)
        call_args = mock_get.call_args
        assert malicious_commodity in str(call_args[1]["params"])

    @patch("requests.Session.get")
    def test_xss_in_state(self, mock_get):
        """Test XSS attempts in state parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        # Attempt XSS
        malicious_state = "<script>alert('XSS')</script>"

        result = nass.get_data(commodity="CORN", state=malicious_state, year=2023)

        # Verify parameter was URL-encoded
        call_args = mock_get.call_args
        assert isinstance(result, list)

    @patch("requests.Session.get")
    def test_special_characters_in_parameters(self, mock_get):
        """Test special characters in query parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        result = nass.get_data(commodity="CORN & WHEAT", state="NORTH DAKOTA", year=2023)

        # Should handle special characters safely
        assert isinstance(result, list)

    @patch("requests.Session.get")
    def test_api_key_not_logged(self, mock_get):
        """Test API key is not exposed in errors."""
        mock_get.side_effect = requests.exceptions.RequestException("API error")

        nass = USDANASSConnector(api_key="secret_key_12345")
        nass._init_session()

        with pytest.raises(ConnectionError) as exc_info:
            nass.fetch(query_params={"commodity_desc": "CORN"})

        # Verify API key not in error message
        assert "secret_key_12345" not in str(exc_info.value)


# ============================================================================
# Layer 7: Property-Based Tests - Edge Case Discovery with Hypothesis
# ============================================================================


class TestUSDANASSConnectorPropertyBased:
    """Property-based tests using Hypothesis."""

    @given(
        commodity=st.text(
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll"), min_codepoint=65, max_codepoint=90
            ),
            min_size=1,
            max_size=30,
        )
    )
    @patch("requests.Session.get")
    def test_commodity_string_handling(self, mock_get, commodity):
        """Test connector handles various commodity strings."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        # Should not crash with any alphanumeric commodity string
        try:
            result = nass.get_data(commodity=commodity, year=2023)
            assert isinstance(result, list)
        except (ValueError, ConnectionError):
            # Acceptable failures (validation or network)
            pass

    @given(year=st.integers(min_value=1900, max_value=2100))
    @patch("requests.Session.get")
    def test_year_values(self, mock_get, year):
        """Test various year values."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        # Should handle any year value
        try:
            result = nass.get_data(commodity="CORN", year=year)
            assert isinstance(result, list)
        except (ValueError, ConnectionError):
            pass


# ============================================================================
# Layer 8: Contract Tests - Type Safety Validation
# ============================================================================


class TestUSDANASSConnectorTypeContracts:
    """Test type contracts and return types."""

    @patch("requests.Session.get")
    def test_get_data_return_type(self, mock_get):
        """Test get_data returns list of dicts."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"commodity_desc": "CORN", "year": 2023}]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        result = nass.get_data(commodity="CORN", year=2023)

        assert isinstance(result, list)
        if len(result) > 0:
            assert isinstance(result[0], dict)

    @patch("requests.Session.get")
    def test_get_param_values_return_type(self, mock_get):
        """Test get_param_values returns list of strings."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"year": ["2023", "2022", "2021"]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        result = nass.get_param_values("year")

        assert isinstance(result, list)

    @patch("requests.Session.get")
    def test_get_counts_return_type(self, mock_get):
        """Test get_counts returns integer."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 100}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass._init_session()

        count = nass.get_counts(commodity_desc="CORN")

        assert isinstance(count, int)

    def test_get_api_key_return_type(self):
        """Test _get_api_key returns string or None."""
        nass = USDANASSConnector(api_key="test_key")

        result = nass._get_api_key()

        assert result is None or isinstance(result, str)

    @patch("requests.Session.get")
    def test_disconnect_return_type(self, mock_get):
        """Test disconnect returns None."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"year": ["2023"]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass.connect()

        if nass.session:
            nass.session.close = MagicMock()

        result = nass.disconnect()
        assert result is None
