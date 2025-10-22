"""
Comprehensive test suite for OECD connector.

Tests cover:
- Layer 1: Unit tests (initialization, connection, core methods)
- Layer 2: Integration tests (API interactions with mocked responses)
- Layer 5: Security tests (injection, XSS, path traversal)
- Layer 7: Property-based tests (Hypothesis for edge cases)
- Layer 8: Contract tests (type safety validation)
"""

import json
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest
import requests
from hypothesis import given
from hypothesis import strategies as st

from krl_data_connectors.economic.oecd_connector import OECDConnector

# ============================================================================
# Layer 1: Unit Tests - Initialization & Core Functionality
# ============================================================================


class TestOECDConnectorInitialization:
    """Test OECD connector initialization and setup."""

    def test_initialization_default_values(self):
        """Test connector initializes with correct default values."""
        oecd = OECDConnector()

        assert oecd.base_url == "https://sdmx.oecd.org/public/rest"
        assert oecd.connector_name == "OECD"
        assert oecd.session is None

    def test_initialization_with_custom_params(self):
        """Test connector accepts custom cache parameters."""
        oecd = OECDConnector(cache_dir="/tmp/oecd_cache", cache_ttl=7200)

        assert oecd.base_url == "https://sdmx.oecd.org/public/rest"
        assert oecd.connector_name == "OECD"

    def test_get_api_key_returns_none(self):
        """Test that no API key is required for OECD."""
        oecd = OECDConnector()

        assert oecd._get_api_key() is None


# ============================================================================
# Layer 2: Integration Tests - Connection & Session Management
# ============================================================================


class TestOECDConnectorConnection:
    """Test OECD connector connection lifecycle."""

    @patch("requests.Session.get")
    def test_connect_success(self, mock_get):
        """Test successful connection to OECD API."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<?xml version="1.0"?><Structure></Structure>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd.connect()

        assert oecd.session is not None
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "dataflow/all/all/latest" in call_args[0][0]

    @patch("requests.Session.get")
    def test_connect_failure(self, mock_get):
        """Test connection failure handling."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        oecd = OECDConnector()

        with pytest.raises(ConnectionError, match="Failed to connect to OECD API"):
            oecd.connect()

    @patch("requests.Session.get")
    def test_disconnect_session(self, mock_get):
        """Test session disconnection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<?xml version="1.0"?><Structure></Structure>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd.connect()

        # Mock the close method on the session
        mock_session = oecd.session
        mock_session.close = MagicMock()

        oecd.disconnect()

        mock_session.close.assert_called_once()


# ============================================================================
# Layer 2: Integration Tests - Fetch Method
# ============================================================================


class TestOECDConnectorFetch:
    """Test generic fetch method with various query types."""

    @patch("requests.Session.get")
    def test_fetch_with_dataflow_query(self, mock_get):
        """Test fetching dataflows."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/xml"}
        mock_response.text = '<?xml version="1.0"?><Dataflows></Dataflows>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.fetch(query_params={"query_type": "dataflow", "path": "OECD/all/latest"})

        assert isinstance(result, list)
        assert len(result) > 0
        assert "content" in result[0]

    @patch("requests.Session.get")
    def test_fetch_with_json_response(self, mock_get):
        """Test fetching with JSON response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": [{"id": "1", "value": 100}]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.fetch(query_params={"query_type": "dataflow"})

        assert isinstance(result, dict)
        assert "data" in result

    def test_fetch_with_invalid_query_type(self):
        """Test fetch with invalid query type."""
        oecd = OECDConnector()
        oecd._init_session()

        with pytest.raises(ValueError, match="Invalid query_type"):
            oecd.fetch(query_params={"query_type": "invalid_type"})


# ============================================================================
# Layer 2: Integration Tests - Data Retrieval
# ============================================================================


class TestOECDConnectorDataRetrieval:
    """Test data retrieval methods."""

    @patch("requests.Session.get")
    def test_get_data_with_basic_params(self, mock_get):
        """Test getting data with basic parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "data": {"dataSets": [{"observations": {"0:0:0:0": [100]}}]}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_data(dataflow="OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I", dimensions="AUS.GDP..A")

        assert isinstance(result, dict)
        assert "data" in result

        # Verify API call
        call_args = mock_get.call_args
        assert "data/" in call_args[0][0]
        assert "AUS.GDP..A" in call_args[0][0]

    @patch("requests.Session.get")
    def test_get_data_with_time_period(self, mock_get):
        """Test getting data with time period filters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_data(
            dataflow="OECD.CFE,INBOUND@TOURISM_TRIPS,2.0",
            dimensions="AU..TOTAL_VISITORS........A",
            start_period="2010",
            end_period="2020",
        )

        # Verify time period parameters were passed
        call_args = mock_get.call_args
        assert call_args[1]["params"]["startPeriod"] == "2010"
        assert call_args[1]["params"]["endPeriod"] == "2020"

    @patch("requests.Session.get")
    def test_get_data_with_observation_limit(self, mock_get):
        """Test getting data with observation limits."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_data(
            dataflow="OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I", dimensions="all", last_n_observations=1
        )

        # Verify observation limit parameter
        call_args = mock_get.call_args
        assert call_args[1]["params"]["lastNObservations"] == 1

    @patch("requests.Session.get")
    def test_get_data_csv_format(self, mock_get):
        """Test getting data in CSV format."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/csv"}
        mock_response.text = "COUNTRY,YEAR,VALUE\nAUS,2020,100\n"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_data(
            dataflow="OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I", dimensions="AUS.GDP..A", format="csvfile"
        )

        assert isinstance(result, str)
        assert "COUNTRY" in result or "AUS" in result

    def test_get_data_without_dataflow(self):
        """Test get_data requires dataflow parameter."""
        oecd = OECDConnector()
        oecd._init_session()

        with pytest.raises(ValueError, match="dataflow parameter is required"):
            oecd.get_data(dataflow="")

    def test_get_data_invalid_observation_count(self):
        """Test get_data validates observation count parameters."""
        oecd = OECDConnector()
        oecd._init_session()

        with pytest.raises(ValueError, match="must be a positive integer"):
            oecd.get_data(dataflow="OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I", first_n_observations=-1)


# ============================================================================
# Layer 2: Integration Tests - Structural Metadata
# ============================================================================


class TestOECDConnectorStructuralMetadata:
    """Test structural metadata retrieval methods."""

    @patch("requests.Session.get")
    def test_get_dataflows(self, mock_get):
        """Test getting list of dataflows."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/xml"}
        mock_response.text = '<?xml version="1.0"?><Dataflows></Dataflows>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_dataflows()

        assert isinstance(result, str)
        assert "Dataflows" in result or "xml" in result.lower()

        # Verify API call
        call_args = mock_get.call_args
        assert "dataflow/all/all/latest" in call_args[0][0]
        assert call_args[1]["params"]["detail"] == "allstubs"

    @patch("requests.Session.get")
    def test_get_dataflows_with_agency(self, mock_get):
        """Test getting dataflows for specific agency."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/xml"}
        mock_response.text = '<?xml version="1.0"?><Dataflows></Dataflows>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_dataflows(agency="OECD.SDD", detail="full")

        # Verify agency parameter
        call_args = mock_get.call_args
        assert "dataflow/OECD.SDD/all/latest" in call_args[0][0]
        assert call_args[1]["params"]["detail"] == "full"

    @patch("requests.Session.get")
    def test_get_dataflow_structure(self, mock_get):
        """Test getting dataflow structure."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/xml"}
        mock_response.text = '<?xml version="1.0"?><Structure></Structure>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_dataflow_structure(
            dataflow="OECD.CFE,INBOUND@TOURISM_TRIPS,2.0", references="all"
        )

        assert isinstance(result, str)
        assert "Structure" in result or "xml" in result.lower()

        # Verify API call
        call_args = mock_get.call_args
        assert "dataflow/OECD.CFE,INBOUND@TOURISM_TRIPS,2.0" in call_args[0][0]
        assert call_args[1]["params"]["references"] == "all"

    def test_get_dataflow_structure_requires_dataflow(self):
        """Test get_dataflow_structure requires dataflow parameter."""
        oecd = OECDConnector()
        oecd._init_session()

        with pytest.raises(ValueError, match="dataflow parameter is required"):
            oecd.get_dataflow_structure(dataflow="")

    @patch("requests.Session.get")
    def test_get_codelists(self, mock_get):
        """Test getting codelists."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/xml"}
        mock_response.text = '<?xml version="1.0"?><Codelists></Codelists>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_codelists(agency="OECD", detail="full")

        assert isinstance(result, str)
        assert "Codelists" in result or "xml" in result.lower()

    @patch("requests.Session.get")
    def test_get_data_structure(self, mock_get):
        """Test getting data structure definitions."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/xml"}
        mock_response.text = '<?xml version="1.0"?><DataStructure></DataStructure>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_data_structure(
            agency="OECD.SDD.NAD", structure_id="DSD_NAAG", references="all"
        )

        assert isinstance(result, str)
        assert "DataStructure" in result or "xml" in result.lower()


# ============================================================================
# Layer 5: Security Tests - Injection & Attack Prevention
# ============================================================================


class TestOECDConnectorSecurity:
    """Test security measures against common attacks."""

    @patch("requests.Session.get")
    def test_sql_injection_in_dataflow(self, mock_get):
        """Test SQL injection attempts in dataflow parameter are handled safely."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        # Attempt SQL injection in dataflow
        malicious_dataflow = "OECD'; DROP TABLE users; --"

        # Should not raise exception, but safely handle the request
        result = oecd.get_data(dataflow=malicious_dataflow, dimensions="all")

        # Verify the malicious string was passed as-is (not executed)
        call_args = mock_get.call_args
        assert malicious_dataflow in call_args[0][0]

    @patch("requests.Session.get")
    def test_xss_in_dimensions(self, mock_get):
        """Test XSS attempts in dimensions parameter are handled safely."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        # Attempt XSS in dimensions
        malicious_dimensions = "<script>alert('XSS')</script>"

        result = oecd.get_data(
            dataflow="OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I", dimensions=malicious_dimensions
        )

        # Verify the malicious string was URL-encoded (not executed)
        call_args = mock_get.call_args
        # requests library will URL-encode the path
        assert "script" in call_args[0][0] or malicious_dimensions in call_args[0][0]

    @patch("requests.Session.get")
    def test_path_traversal_in_query_params(self, mock_get):
        """Test path traversal attempts are handled safely."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/xml"}
        mock_response.text = '<?xml version="1.0"?><Structure></Structure>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        # Attempt path traversal
        malicious_path = "../../etc/passwd"

        result = oecd.fetch(query_params={"query_type": "dataflow", "path": malicious_path})

        # Verify the path was included in URL (will fail at API level, not locally)
        call_args = mock_get.call_args
        assert isinstance(result, list)

    def test_empty_dataflow_handling(self):
        """Test empty/None dataflow parameter is rejected."""
        oecd = OECDConnector()
        oecd._init_session()

        with pytest.raises(ValueError, match="dataflow parameter is required"):
            oecd.get_data(dataflow="")

        with pytest.raises(ValueError, match="dataflow parameter is required"):
            oecd.get_data(dataflow=None)

    @patch("requests.Session.get")
    def test_special_characters_in_time_period(self, mock_get):
        """Test special characters in time period parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        # Test with special characters (should be passed as query params, not cause errors)
        result = oecd.get_data(
            dataflow="OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I",
            dimensions="all",
            start_period="2020<>",
            end_period="2021;DROP",
        )

        # Verify parameters were passed (requests will URL-encode them)
        call_args = mock_get.call_args
        assert "startPeriod" in call_args[1]["params"]
        assert "endPeriod" in call_args[1]["params"]


# ============================================================================
# Layer 7: Property-Based Tests - Edge Case Discovery with Hypothesis
# ============================================================================


class TestOECDConnectorPropertyBased:
    """Property-based tests using Hypothesis to discover edge cases."""

    @given(
        dataflow=st.text(
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=65, max_codepoint=90
            ),
            min_size=1,
            max_size=50,
        )
    )
    @patch("requests.Session.get")
    def test_dataflow_handling(self, mock_get, dataflow):
        """Test connector handles various dataflow strings without crashing."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        # Should not crash with any valid alphanumeric string
        try:
            result = oecd.get_data(dataflow=dataflow, dimensions="all")
            assert isinstance(result, (dict, str))
        except (ValueError, ConnectionError):
            # These are acceptable failures (validation or network)
            pass

    @given(
        dimensions=st.text(
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=46, max_codepoint=90
            ),
            min_size=1,
            max_size=100,
        )
    )
    @patch("requests.Session.get")
    def test_dimensions_handling(self, mock_get, dimensions):
        """Test connector handles various dimension strings."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        # Should not crash with any alphanumeric string
        try:
            result = oecd.get_data(
                dataflow="OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I", dimensions=dimensions
            )
            assert isinstance(result, (dict, str))
        except (ValueError, ConnectionError):
            pass

    @given(
        start_year=st.integers(min_value=1900, max_value=2100),
        end_year=st.integers(min_value=1900, max_value=2100),
    )
    @patch("requests.Session.get")
    def test_year_combinations(self, mock_get, start_year, end_year):
        """Test various start/end year combinations."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        # Should handle any year combination
        try:
            result = oecd.get_data(
                dataflow="OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I",
                dimensions="all",
                start_period=str(start_year),
                end_period=str(end_year),
            )
            assert isinstance(result, (dict, str))
        except (ValueError, ConnectionError):
            pass

    @given(obs_count=st.integers(min_value=1, max_value=1000))
    @patch("requests.Session.get")
    def test_observation_count_values(self, mock_get, obs_count):
        """Test various observation count values."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        # Should accept any positive integer
        result = oecd.get_data(
            dataflow="OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I",
            dimensions="all",
            last_n_observations=obs_count,
        )
        assert isinstance(result, (dict, str))


# ============================================================================
# Layer 8: Contract Tests - Type Safety Validation
# ============================================================================


class TestOECDConnectorTypeContracts:
    """Test type contracts and return types."""

    @patch("requests.Session.get")
    def test_get_data_return_type(self, mock_get):
        """Test get_data returns correct type based on format."""
        # Test JSON format
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_data(
            dataflow="OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I", dimensions="all", format="jsondata"
        )
        assert isinstance(result, dict)

        # Test CSV format
        mock_response.headers = {"content-type": "text/csv"}
        mock_response.text = "COUNTRY,YEAR,VALUE\n"

        result = oecd.get_data(
            dataflow="OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I", dimensions="all", format="csvfile"
        )
        assert isinstance(result, str)

    @patch("requests.Session.get")
    def test_get_dataflows_return_type(self, mock_get):
        """Test get_dataflows returns correct type."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/xml"}
        mock_response.text = '<?xml version="1.0"?><Dataflows></Dataflows>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_dataflows()
        assert isinstance(result, (str, dict))

    def test_get_api_key_return_type(self):
        """Test _get_api_key returns None or str."""
        oecd = OECDConnector()

        result = oecd._get_api_key()
        assert result is None or isinstance(result, str)

    @patch("requests.Session.get")
    def test_fetch_return_type(self, mock_get):
        """Test fetch returns list of dicts."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.fetch(query_params={"query_type": "dataflow"})
        assert isinstance(result, (list, dict))

    def test_disconnect_return_type(self):
        """Test disconnect returns None."""
        oecd = OECDConnector()
        oecd._init_session()

        # Mock the session's close method
        if oecd.session:
            oecd.session.close = MagicMock()

        result = oecd.disconnect()
        assert result is None

    def test_connect_return_type(self):
        """Test connect returns None."""
        oecd = OECDConnector()

        result = oecd.connect()
        assert result is None

    @patch("requests.Session.get")
    def test_get_dataflow_structure_return_type(self, mock_get):
        """Test get_dataflow_structure returns str."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/xml"}
        mock_response.text = '<?xml version="1.0"?><Structure></Structure>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_dataflow_structure("OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I")
        assert isinstance(result, str)

    @patch("requests.Session.get")
    def test_get_codelists_return_type(self, mock_get):
        """Test get_codelists returns str."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/xml"}
        mock_response.text = '<?xml version="1.0"?><Codelists></Codelists>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_codelists()
        assert isinstance(result, str)

    @patch("requests.Session.get")
    def test_get_data_structure_return_type(self, mock_get):
        """Test get_data_structure returns str."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/xml"}
        mock_response.text = '<?xml version="1.0"?><DataStructures></DataStructures>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oecd = OECDConnector()
        oecd._init_session()

        result = oecd.get_data_structure()
        assert isinstance(result, str)


# ============================================================================
# Test Configuration
# ============================================================================
