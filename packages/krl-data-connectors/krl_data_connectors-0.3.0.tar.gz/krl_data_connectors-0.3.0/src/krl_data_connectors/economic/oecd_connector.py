"""OECD Data API connector.

Provides access to OECD statistical data through their SDMX-based REST API.
Supports multiple datasets, flexible dimension filtering, and various response formats.
"""

from typing import Any, Dict, List, Optional, Union

import requests

from krl_data_connectors.base_connector import BaseConnector


class OECDConnector(BaseConnector):
    """
    Connector for OECD Data API (SDMX-based).

    The OECD provides comprehensive economic and social statistics through
    a RESTful API based on the SDMX (Statistical Data and Metadata eXchange) standard.

    Features:
    - Access to hundreds of datasets (national accounts, labor statistics, prices, etc.)
    - SDMX-based query language with flexible dimension filtering
    - Time period filtering with startPeriod/endPeriod
    - Multiple response formats (JSON, XML, CSV)
    - Structural metadata queries (dataflows, dimensions, codelists)
    - No authentication required (free public access)

    Example datasets:
    - National Accounts (GDP, GNI, etc.)
    - Labour Force Statistics
    - Consumer Price Indices
    - International Trade
    - Environmental Indicators
    - And many more...

    API Documentation:
    https://data.oecd.org/api/
    https://sis-cc.gitlab.io/dotstatsuite-documentation/using-api/restful/
    """

    base_url: str = "https://sdmx.oecd.org/public/rest"

    def __init__(
        self, cache_dir: Optional[str] = None, cache_ttl: int = 3600, **kwargs: Any
    ) -> None:
        """
        Initialize OECD connector.

        Args:
            cache_dir: Directory for caching responses (optional)
            cache_ttl: Cache time-to-live in seconds (default: 3600)
            **kwargs: Additional arguments passed to BaseConnector
        """
        super().__init__(cache_dir=cache_dir, cache_ttl=cache_ttl, **kwargs)
        self.connector_name = "OECD"

    def _get_api_key(self) -> Optional[str]:
        """
        OECD API does not require authentication.

        Returns:
            None - No API key required
        """
        return None

    def connect(self) -> None:
        """
        Establish connection to OECD API.

        Tests connectivity with a simple dataflow list request.

        Raises:
            ConnectionError: If unable to connect to OECD API
        """
        self._init_session()
        assert self.session is not None

        try:
            # Test connection with a simple dataflow query
            response = self.session.get(
                f"{self.base_url}/dataflow/all/all/latest",
                params={"detail": "allstubs"},
                timeout=30,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to OECD API: {str(e)}") from e

    def fetch(self, query_params: Dict[str, Any], **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Generic fetch method for OECD API queries.

        Args:
            query_params: Dictionary containing:
                - query_type: Type of query ("data", "dataflow", "codelist", etc.)
                - path: Optional path component
                - Other query-specific parameters
            **kwargs: Additional arguments

        Returns:
            List of results

        Raises:
            ValueError: If query_type is invalid
            ConnectionError: If API request fails
        """
        query_type = query_params.get("query_type", "dataflow")

        if query_type not in ["data", "dataflow", "codelist", "datastructure"]:
            raise ValueError(
                f"Invalid query_type: {query_type}. "
                f"Must be one of: data, dataflow, codelist, datastructure"
            )

        assert self.session is not None

        endpoint = f"{self.base_url}/{query_type}"
        if "path" in query_params:
            endpoint += f"/{query_params['path']}"
        else:
            endpoint += "/all"

        try:
            response = self.session.get(endpoint, timeout=30)
            response.raise_for_status()

            # Handle different response formats
            content_type = response.headers.get("content-type", "")
            if "json" in content_type:
                return response.json()
            else:
                # For XML and other formats, return raw content
                return [{"content": response.text, "format": content_type}]

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"OECD API request failed: {str(e)}") from e

    def get_data(
        self,
        dataflow: str,
        dimensions: Optional[str] = None,
        start_period: Optional[str] = None,
        end_period: Optional[str] = None,
        dimension_at_observation: str = "AllDimensions",
        format: str = "jsondata",
        first_n_observations: Optional[int] = None,
        last_n_observations: Optional[int] = None,
    ) -> Union[List[Dict[str, Any]], str]:
        """
        Retrieve data from OECD API.

        Args:
            dataflow: Dataflow identifier in format "AGENCY,ID,VERSION" or "AGENCY.ID@DATASET.VERSION"
                     Example: "OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I" or "OECD.CFE,INBOUND@TOURISM_TRIPS,2.0"
            dimensions: Dimension filter string (e.g., "AUS.GDP..A" or "all")
                       Dimensions separated by dots, values within dimension separated by +
                       Leave dimension empty to get all values
            start_period: Start time period (inclusive), e.g., "2010", "2010-Q1", "2010-01"
            end_period: End time period (inclusive), e.g., "2020", "2020-Q4", "2020-12"
            dimension_at_observation: How to structure the data:
                                     - "AllDimensions": flat view (default)
                                     - "TIME_PERIOD": timeseries view
                                     - ID of any dimension: cross-sectional view
            format: Response format:
                   - "jsondata": JSON format (default)
                   - "csvfile": CSV format
                   - "csvfilewithlabels": CSV with labels and codes
                   - "genericdata": SDMX Generic XML
                   - "structurespecificdata": SDMX Structure-specific XML
            first_n_observations: Return only first N observations for each series
            last_n_observations: Return only last N observations for each series

        Returns:
            Data response (format depends on 'format' parameter)

        Raises:
            ValueError: If parameters are invalid
            ConnectionError: If API request fails

        Examples:
            # Get all GDP data for Australia
            data = connector.get_data(
                "OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I",
                "AUS.GDP..A"
            )

            # Get tourism data for Argentina, 2010-2020
            data = connector.get_data(
                "OECD.CFE,INBOUND@TOURISM_TRIPS,2.0",
                "AU..TOTAL_VISITORS........A",
                start_period="2010",
                end_period="2020"
            )

            # Get most recent observation for all series
            data = connector.get_data(
                "OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I",
                "all",
                last_n_observations=1
            )
        """
        assert self.session is not None

        # Validate parameters
        if not dataflow:
            raise ValueError("dataflow parameter is required")

        if first_n_observations is not None and first_n_observations <= 0:
            raise ValueError("first_n_observations must be a positive integer")

        if last_n_observations is not None and last_n_observations <= 0:
            raise ValueError("last_n_observations must be a positive integer")

        # Build endpoint URL
        key = dimensions if dimensions else "all"
        endpoint = f"{self.base_url}/data/{dataflow}/{key}"

        # Build query parameters
        params: Dict[str, Any] = {
            "dimensionAtObservation": dimension_at_observation,
            "format": format,
        }

        if start_period:
            params["startPeriod"] = start_period

        if end_period:
            params["endPeriod"] = end_period

        if first_n_observations is not None:
            params["firstNObservations"] = first_n_observations

        if last_n_observations is not None:
            params["lastNObservations"] = last_n_observations

        try:
            response = self.session.get(endpoint, params=params, timeout=60)
            response.raise_for_status()

            # Return based on format
            content_type = response.headers.get("content-type", "")

            if format == "jsondata" or "json" in content_type:
                return response.json()
            elif format in ["csvfile", "csvfilewithlabels"] or "csv" in content_type:
                return response.text
            else:
                # XML formats
                return response.text

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to retrieve data: {str(e)}") from e

    def get_dataflows(
        self, agency: str = "all", detail: str = "allstubs"
    ) -> Union[Dict[str, Any], str]:
        """
        Get list of available dataflows (datasets).

        Args:
            agency: Agency identifier (default: "all")
                   Examples: "OECD", "OECD.SDD.NAD", "all"
            detail: Level of detail:
                   - "allstubs": Basic info only (default)
                   - "full": Complete details
                   - "referencestubs": With referenced artefacts as stubs
                   - "allcompletestubs": All with stubs

        Returns:
            Dataflow metadata (XML format by default)

        Examples:
            # Get all OECD dataflows
            flows = connector.get_dataflows()

            # Get detailed info for specific agency
            flows = connector.get_dataflows(agency="OECD.SDD", detail="full")
        """
        assert self.session is not None

        endpoint = f"{self.base_url}/dataflow/{agency}/all/latest"
        params = {"detail": detail}

        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "json" in content_type:
                return response.json()
            else:
                return response.text

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to retrieve dataflows: {str(e)}") from e

    def get_dataflow_structure(self, dataflow: str, references: str = "none") -> str:
        """
        Get structural metadata for a specific dataflow.

        This retrieves information about dimensions, attributes, codelists,
        and other structural details of a dataflow.

        Args:
            dataflow: Dataflow identifier in format "AGENCY,ID,VERSION"
                     Example: "OECD.CFE,INBOUND@TOURISM_TRIPS,2.0"
            references: Level of referenced artefacts to include:
                       - "none": No references (default)
                       - "parents": Only parent artefacts
                       - "children": Only child artefacts
                       - "all": All referenced artefacts
                       - "constraint": Only content constraints
                       - "actualconstraint": Only actual content constraints

        Returns:
            Structural metadata (XML format)

        Examples:
            # Get structure with all references
            structure = connector.get_dataflow_structure(
                "OECD.CFE,INBOUND@TOURISM_TRIPS,2.0",
                references="all"
            )
        """
        assert self.session is not None

        if not dataflow:
            raise ValueError("dataflow parameter is required")

        endpoint = f"{self.base_url}/dataflow/{dataflow}"
        params = {"references": references}

        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to retrieve dataflow structure: {str(e)}") from e

    def get_codelists(self, agency: str = "all", detail: str = "allstubs") -> str:
        """
        Get available codelists (allowed values for dimensions).

        Args:
            agency: Agency identifier (default: "all")
            detail: Level of detail (see get_dataflows for options)

        Returns:
            Codelist metadata (XML format)

        Examples:
            # Get all codelists
            codelists = connector.get_codelists()

            # Get OECD codelists with full details
            codelists = connector.get_codelists(agency="OECD", detail="full")
        """
        assert self.session is not None

        endpoint = f"{self.base_url}/codelist/{agency}/all/latest"
        params = {"detail": detail}

        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to retrieve codelists: {str(e)}") from e

    def get_data_structure(
        self,
        agency: str = "all",
        structure_id: str = "all",
        version: str = "latest",
        references: str = "none",
        detail: str = "full",
    ) -> str:
        """
        Get data structure definitions (DSDs).

        DSDs define the structure of datasets including dimensions,
        attributes, measures, and their relationships.

        Args:
            agency: Agency identifier (default: "all")
            structure_id: Structure identifier (default: "all")
            version: Version (default: "latest")
            references: Referenced artefacts to include (see get_dataflow_structure)
            detail: Level of detail (see get_dataflows)

        Returns:
            Data structure definitions (XML format)

        Examples:
            # Get all data structures
            dsds = connector.get_data_structure()

            # Get specific structure with references
            dsd = connector.get_data_structure(
                agency="OECD.SDD.NAD",
                structure_id="DSD_NAAG",
                references="all"
            )
        """
        assert self.session is not None

        endpoint = f"{self.base_url}/datastructure/{agency}/{structure_id}/{version}"
        params = {"references": references, "detail": detail}

        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to retrieve data structure: {str(e)}") from e
