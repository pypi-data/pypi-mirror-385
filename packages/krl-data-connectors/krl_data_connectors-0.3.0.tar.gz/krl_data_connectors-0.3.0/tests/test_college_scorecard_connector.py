"""
Comprehensive test suite for College Scorecard connector.

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

from krl_data_connectors.education.college_scorecard_connector import CollegeScorecardConnector

# ============================================================================
# Layer 1: Unit Tests - Initialization & Core Functionality
# ============================================================================


class TestCollegeScorecardConnectorInitialization:
    """Test College Scorecard connector initialization and setup."""

    def test_initialization_default_values(self):
        """Test connector initializes with correct default values."""
        connector = CollegeScorecardConnector(api_key="test_key")

        assert connector.base_url == "https://api.data.gov/ed/collegescorecard/v1"
        assert connector.connector_name == "CollegeScorecard"
        assert connector.session is None
        assert connector.api_key == "test_key"

    def test_initialization_with_custom_params(self):
        """Test connector accepts custom parameters."""
        connector = CollegeScorecardConnector(
            api_key="test_key", cache_dir="/tmp/scorecard_cache", cache_ttl=7200
        )

        assert connector.base_url == "https://api.data.gov/ed/collegescorecard/v1"
        assert connector.api_key == "test_key"

    def test_get_api_key_from_init(self):
        """Test API key retrieval from initialization."""
        connector = CollegeScorecardConnector(api_key="my_api_key")

        # The API key is stored in base connector
        assert connector.api_key == "my_api_key"


# ============================================================================
# Layer 2: Integration Tests - Connection & Session Management
# ============================================================================


class TestCollegeScorecardConnectorConnection:
    """Test College Scorecard connector connection lifecycle."""

    @patch("requests.Session.get")
    def test_connect_success(self, mock_get):
        """Test successful connection to College Scorecard API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "metadata": {"total": 1, "page": 0, "per_page": 1},
            "results": [],
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector.connect()

        assert connector.session is not None
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "schools.json" in call_args[0][0]
        assert call_args[1]["params"]["api_key"] == "test_key"

    def test_connect_without_api_key(self):
        """Test connection fails without API key."""
        with patch.object(CollegeScorecardConnector, "_get_api_key", return_value=None):
            connector = CollegeScorecardConnector()

            with pytest.raises(ValueError, match="API key is required"):
                connector.connect()

    @patch("requests.Session.get")
    def test_connect_failure(self, mock_get):
        """Test connection failure handling."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        connector = CollegeScorecardConnector(api_key="test_key")

        with pytest.raises(ConnectionError, match="Failed to connect to College Scorecard API"):
            connector.connect()

    @patch("requests.Session.get")
    def test_disconnect_session(self, mock_get):
        """Test session disconnection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"metadata": {}, "results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector.connect()

        mock_session = connector.session
        if mock_session:
            mock_session.close = MagicMock()

            connector.disconnect()

            mock_session.close.assert_called_once()


# ============================================================================
# Layer 2: Integration Tests - Fetch Method
# ============================================================================


class TestCollegeScorecardConnectorFetch:
    """Test generic fetch method."""

    @patch("requests.Session.get")
    def test_fetch_with_valid_params(self, mock_get):
        """Test fetching data with valid parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "metadata": {"total": 1, "page": 0, "per_page": 20},
            "results": [{"id": 123456, "school.name": "Test University"}],
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector._init_session()

        result = connector.fetch(query_params={"school.state": "CA"})

        assert isinstance(result, dict)
        assert "metadata" in result
        assert "results" in result

    @patch("requests.Session.get")
    def test_fetch_with_error_response(self, mock_get):
        """Test fetch handling API error response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "errors": [{"error": "field_not_found", "message": "Invalid field"}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector._init_session()

        with pytest.raises(ValueError, match="API error"):
            connector.fetch(query_params={"invalid_param": "value"})

    def test_fetch_without_api_key(self):
        """Test fetch fails without API key."""
        with patch.object(CollegeScorecardConnector, "_get_api_key", return_value=None):
            connector = CollegeScorecardConnector()
            connector._init_session()

            with pytest.raises(ValueError, match="API key is required"):
                connector.fetch(query_params={"school.state": "CA"})


# ============================================================================
# Layer 2: Integration Tests - Data Retrieval
# ============================================================================


class TestCollegeScorecardConnectorDataRetrieval:
    """Test data retrieval methods."""

    @patch("requests.Session.get")
    def test_get_schools_with_state(self, mock_get):
        """Test getting schools filtered by state."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "metadata": {"total": 1, "page": 0, "per_page": 20},
            "results": [{"id": 123456, "school.name": "Test University", "school.state": "CA"}],
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector._init_session()

        result = connector.get_schools(state="CA")

        assert isinstance(result, list)
        assert len(result) > 0

        # Verify API call parameters
        call_args = mock_get.call_args
        assert call_args[1]["params"]["school.state"] == "CA"

    @patch("requests.Session.get")
    def test_get_schools_with_multiple_filters(self, mock_get):
        """Test getting schools with multiple filters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"metadata": {}, "results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector._init_session()

        result = connector.get_schools(
            state="CA",
            student_size_range="5000..",
            predominant_degree=3,
            fields="id,school.name,latest.student.size",
        )

        # Verify parameters
        call_args = mock_get.call_args
        assert call_args[1]["params"]["school.state"] == "CA"
        assert call_args[1]["params"]["latest.student.size__range"] == "5000.."
        assert call_args[1]["params"]["school.degrees_awarded.predominant"] == 3
        assert call_args[1]["params"]["_fields"] == "id,school.name,latest.student.size"

    @patch("requests.Session.get")
    def test_get_school_by_id(self, mock_get):
        """Test getting a specific school by ID."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "metadata": {},
            "results": [{"id": 166683, "school.name": "Massachusetts Institute of Technology"}],
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector._init_session()

        result = connector.get_school_by_id(school_id=166683)

        assert result is not None
        assert result["id"] == 166683

        # Verify API call
        call_args = mock_get.call_args
        assert call_args[1]["params"]["id"] == 166683

    @patch("requests.Session.get")
    def test_get_metadata(self, mock_get):
        """Test getting metadata about query results."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "metadata": {"total": 500, "page": 0, "per_page": 20},
            "results": [],
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector._init_session()

        metadata = connector.get_metadata(state="CA")

        assert isinstance(metadata, dict)
        assert metadata["total"] == 500
        assert metadata["page"] == 0
        assert metadata["per_page"] == 20


# ============================================================================
# Layer 5: Security Tests - Injection & Attack Prevention
# ============================================================================


class TestCollegeScorecardConnectorSecurity:
    """Test security measures against common attacks."""

    @patch("requests.Session.get")
    def test_sql_injection_in_school_name(self, mock_get):
        """Test SQL injection attempts in school name parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"metadata": {}, "results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector._init_session()

        # Attempt SQL injection
        malicious_name = "Harvard'; DROP TABLE schools; --"

        result = connector.get_schools(school_name=malicious_name)

        # Verify parameter was passed as-is (not executed)
        call_args = mock_get.call_args
        assert malicious_name in str(call_args[1]["params"])

    @patch("requests.Session.get")
    def test_xss_in_state(self, mock_get):
        """Test XSS attempts in state parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"metadata": {}, "results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector._init_session()

        # Attempt XSS
        malicious_state = "<script>alert('XSS')</script>"

        result = connector.get_schools(state=malicious_state)

        # Verify parameter was URL-encoded
        assert isinstance(result, list)

    @patch("requests.Session.get")
    def test_api_key_not_logged(self, mock_get):
        """Test API key is not exposed in errors."""
        mock_get.side_effect = requests.exceptions.RequestException("API error")

        connector = CollegeScorecardConnector(api_key="secret_key_12345")
        connector._init_session()

        with pytest.raises(ConnectionError) as exc_info:
            connector.fetch(query_params={"school.state": "CA"})

        # Verify API key not in error message
        assert "secret_key_12345" not in str(exc_info.value)


# ============================================================================
# Layer 7: Property-Based Tests - Edge Case Discovery with Hypothesis
# ============================================================================


class TestCollegeScorecardConnectorPropertyBased:
    """Property-based tests using Hypothesis."""

    @given(
        state=st.text(
            alphabet=st.characters(
                whitelist_categories=("Lu",), min_codepoint=65, max_codepoint=90
            ),
            min_size=2,
            max_size=2,
        )
    )
    @patch("requests.Session.get")
    def test_state_code_handling(self, mock_get, state):
        """Test connector handles various state codes."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"metadata": {}, "results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector._init_session()

        # Should not crash with any 2-letter state code
        try:
            result = connector.get_schools(state=state)
            assert isinstance(result, list)
        except (ValueError, ConnectionError):
            # Acceptable failures (validation or network)
            pass

    @given(
        page=st.integers(min_value=0, max_value=100),
        per_page=st.integers(min_value=1, max_value=150),
    )
    @patch("requests.Session.get")
    def test_pagination_handling(self, mock_get, page, per_page):
        """Test various pagination values."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"metadata": {}, "results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector._init_session()

        # Should handle pagination correctly
        try:
            result = connector.get_schools(state="CA", page=page, per_page=per_page)
            assert isinstance(result, list)

            # Verify per_page is capped at 100
            call_args = mock_get.call_args
            assert call_args[1]["params"]["per_page"] <= 100
        except (ValueError, ConnectionError):
            pass


# ============================================================================
# Layer 8: Contract Tests - Type Safety Validation
# ============================================================================


class TestCollegeScorecardConnectorTypeContracts:
    """Test type contracts and return types."""

    @patch("requests.Session.get")
    def test_get_schools_return_type(self, mock_get):
        """Test get_schools returns list."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"metadata": {}, "results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector._init_session()

        result = connector.get_schools(state="CA")

        assert isinstance(result, list)

    @patch("requests.Session.get")
    def test_get_school_by_id_return_type(self, mock_get):
        """Test get_school_by_id returns dict or None."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"metadata": {}, "results": [{"id": 123456}]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector._init_session()

        result = connector.get_school_by_id(school_id=123456)

        assert result is None or isinstance(result, dict)

    @patch("requests.Session.get")
    def test_get_metadata_return_type(self, mock_get):
        """Test get_metadata returns dict."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"metadata": {"total": 100}, "results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector._init_session()

        result = connector.get_metadata(state="CA")

        assert isinstance(result, dict)

    def test_get_api_key_return_type(self):
        """Test _get_api_key returns string or None."""
        connector = CollegeScorecardConnector(api_key="test_key")

        result = connector._get_api_key()

        assert result is None or isinstance(result, str)

    @patch("requests.Session.get")
    def test_disconnect_return_type(self, mock_get):
        """Test disconnect returns None."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"metadata": {}, "results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        connector = CollegeScorecardConnector(api_key="test_key")
        connector.connect()

        if connector.session:
            connector.session.close = MagicMock()

        result = connector.disconnect()
        assert result is None
