"""USDA NASS QuickStats API connector.

Provides access to agricultural statistics from the National Agricultural Statistics Service.
"""

from typing import Any, Dict, List, Optional

import requests

from krl_data_connectors.base_connector import BaseConnector


class USDANASSConnector(BaseConnector):
    """
    Connector for USDA NASS QuickStats API.

    The National Agricultural Statistics Service (NASS) QuickStats database contains
    official published aggregate estimates related to U.S. agricultural production.

    Features:
    - Access to hundreds of agricultural statistics
    - Data from sample surveys and Census of Agriculture
    - State and county-level aggregates
    - Commodity, geography, and time-based filtering
    - Annual, monthly, and survey data

    Requires API key (free registration at https://quickstats.nass.usda.gov/api)

    API Documentation:
    https://quickstats.nass.usda.gov/api
    https://www.nass.usda.gov/developer/
    """

    base_url: str = "https://quickstats.nass.usda.gov/api"

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        **kwargs: Any,
    ) -> None:
        """
        Initialize USDA NASS connector.

        Args:
            api_key: USDA NASS API key (required, or set in config)
            cache_dir: Directory for caching responses (optional)
            cache_ttl: Cache time-to-live in seconds (default: 3600)
            **kwargs: Additional arguments passed to BaseConnector
        """
        super().__init__(api_key=api_key, cache_dir=cache_dir, cache_ttl=cache_ttl, **kwargs)
        self.connector_name = "USDANASS"

    def _get_api_key(self) -> Optional[str]:
        """
        Get USDA NASS API key from instance or configuration.

        Returns:
            API key string or None
        """
        # First check if API key was set during initialization
        if hasattr(self, "api_key") and self.api_key:
            return self.api_key

        # Try to get from config
        try:
            return self.config.get("api_keys", {}).get("usda_nass")
        except (AttributeError, KeyError):
            return None

    def connect(self) -> None:
        """
        Establish connection to USDA NASS API.

        Validates API key with a simple test request.

        Raises:
            ValueError: If API key is missing
            ConnectionError: If unable to connect to USDA NASS API
        """
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError(
                "USDA NASS API key is required. " "Get one at https://quickstats.nass.usda.gov/api"
            )

        self._init_session()
        assert self.session is not None

        try:
            # Test connection with param_values request
            response = self.session.get(
                f"{self.base_url}/get_param_values",
                params={"key": api_key, "param": "year"},
                timeout=30,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to USDA NASS API: {str(e)}") from e

    def fetch(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Generic fetch method for USDA NASS API queries.

        Args:
            **kwargs: Query parameters (commodity, year, state, etc.)

        Returns:
            List of data records

        Raises:
            ValueError: If API key is missing or parameters invalid
            ConnectionError: If API request fails
        """
        query_params = kwargs.pop("query_params", kwargs)
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("API key is required")

        assert self.session is not None

        params = {"key": api_key, **query_params}

        try:
            response = self.session.get(f"{self.base_url}/api_GET", params=params, timeout=60)
            response.raise_for_status()

            data = response.json()

            # Check for error in response
            if isinstance(data, dict) and "error" in data:
                raise ValueError(f"API error: {data['error']}")

            if isinstance(data, dict) and "data" in data:
                return data["data"]

            return data if isinstance(data, list) else []

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"USDA NASS API request failed: {str(e)}") from e

    def get_data(
        self,
        commodity: Optional[str] = None,
        year: Optional[int] = None,
        state: Optional[str] = None,
        county: Optional[str] = None,
        statisticcat_desc: Optional[str] = None,
        unit_desc: Optional[str] = None,
        format: str = "JSON",
        **additional_params: Any,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve agricultural statistics data.

        Args:
            commodity: Commodity name (e.g., "CORN", "WHEAT", "CATTLE")
            year: Year (e.g., 2023)
            state: State name or abbreviation (e.g., "IOWA", "IA")
            county: County name (e.g., "POLK")
            statisticcat_desc: Statistic category (e.g., "AREA HARVESTED", "PRODUCTION", "YIELD")
            unit_desc: Unit of measurement (e.g., "ACRES", "BU", "$/ACRE")
            format: Response format ("JSON" or "CSV", default: "JSON")
            **additional_params: Additional query parameters
                - agg_level_desc: Aggregation level ("NATIONAL", "STATE", "COUNTY")
                - sector_desc: Sector ("CROPS", "ANIMALS & PRODUCTS", etc.)
                - group_desc: Commodity group
                - short_desc: Short description filter
                - domain_desc: Domain description
                - freq_desc: Frequency ("ANNUAL", "MONTHLY", "WEEKLY")
                - reference_period_desc: Reference period
                - source_desc: Data source

        Returns:
            List of data records

        Raises:
            ValueError: If no filters provided or API key missing
            ConnectionError: If API request fails

        Examples:
            # Get corn production in Iowa for 2023
            data = connector.get_data(
                commodity="CORN",
                year=2023,
                state="IOWA",
                statisticcat_desc="PRODUCTION"
            )

            # Get county-level cattle inventory
            data = connector.get_data(
                commodity="CATTLE",
                year=2023,
                state="TEXAS",
                agg_level_desc="COUNTY",
                statisticcat_desc="INVENTORY"
            )
        """
        if not any([commodity, year, state, county, statisticcat_desc]):
            raise ValueError(
                "At least one filter parameter must be provided "
                "(commodity, year, state, county, or statisticcat_desc)"
            )

        params: Dict[str, Any] = {"format": format}

        if commodity:
            params["commodity_desc"] = commodity
        if year:
            params["year"] = year
        if state:
            params["state_name"] = state
        if county:
            params["county_name"] = county
        if statisticcat_desc:
            params["statisticcat_desc"] = statisticcat_desc
        if unit_desc:
            params["unit_desc"] = unit_desc

        # Add any additional parameters
        params.update(additional_params)

        return self.fetch(query_params=params)

    def get_param_values(self, param: str) -> List[str]:
        """
        Get list of valid values for a specific parameter.

        This is useful for discovering available commodities, states,
        statistic categories, etc.

        Args:
            param: Parameter name (e.g., "commodity_desc", "state_name",
                  "statisticcat_desc", "year", "agg_level_desc", "sector_desc",
                  "group_desc", "unit_desc", "freq_desc", "source_desc")

        Returns:
            List of valid values for the parameter

        Raises:
            ValueError: If API key is missing or parameter invalid
            ConnectionError: If API request fails

        Examples:
            # Get all available commodities
            commodities = connector.get_param_values("commodity_desc")

            # Get all available years
            years = connector.get_param_values("year")

            # Get all statistic categories
            stats = connector.get_param_values("statisticcat_desc")
        """
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("API key is required")

        assert self.session is not None

        try:
            response = self.session.get(
                f"{self.base_url}/get_param_values",
                params={"key": api_key, "param": param},
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            # Extract values from response
            if isinstance(data, dict) and param in data:
                return data[param]

            return []

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to get parameter values: {str(e)}") from e

    def get_counts(self, **query_params: Any) -> int:
        """
        Get count of records that would be returned for a query.

        Use this before calling get_data() to check if your query will
        return more than the 50,000 record maximum.

        Args:
            **query_params: Same parameters as get_data()
                          (commodity, year, state, etc.)

        Returns:
            Count of records

        Raises:
            ValueError: If API key is missing
            ConnectionError: If API request fails

        Examples:
            # Check record count before fetching
            count = connector.get_counts(commodity="CORN", year=2023)
            if count > 50000:
                print("Query would return too many records, add more filters")
        """
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("API key is required")

        assert self.session is not None

        params = {"key": api_key, **query_params}

        try:
            response = self.session.get(f"{self.base_url}/get_counts", params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if isinstance(data, dict) and "count" in data:
                return int(data["count"])

            return 0

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to get record count: {str(e)}") from e
