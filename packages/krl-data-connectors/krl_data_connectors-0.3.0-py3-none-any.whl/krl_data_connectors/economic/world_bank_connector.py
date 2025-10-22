"""
World Bank Indicators API Connector

This connector provides access to the World Bank's Indicators API (v2), which includes
nearly 16,000 time series indicators across 45+ databases including World Development
Indicators, International Debt Statistics, Doing Business, Human Capital Index, and more.

API Documentation: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
API v2: https://api.worldbank.org/v2/

Key Features:
- 16,000+ indicators across 200+ countries
- 50+ years of historical data
- Multiple data sources (WDI, IDS, Doing Business, etc.)
- Support for country groups, income levels, and regions
- Time series data with various frequencies (yearly, quarterly, monthly)
- No authentication required

Example Usage:
    ```python
    from krl_data_connectors.economic import WorldBankConnector

    # Initialize connector
    wb = WorldBankConnector()
    wb.connect()

    # Get GDP data for multiple countries
    gdp_data = wb.get_indicator_data(
        indicator="NY.GDP.MKTP.CD",  # GDP (current US$)
        countries=["USA", "CHN", "IND"],
        date_range="2010:2020"
    )

    # Get most recent values
    poverty_data = wb.get_indicator_data(
        indicator="SI.POV.DDAY",  # Poverty headcount ratio
        countries=["all"],
        mrv=5  # Most recent 5 values
    )

    # Search for indicators
    indicators = wb.search_indicators("unemployment rate")

    # Get country metadata
    countries = wb.get_countries(income_level="HIC")  # High income countries
    ```

Author: KR Labs
Date: October 2025
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union

import requests

from ..base_connector import BaseConnector

logger = logging.getLogger(__name__)


class WorldBankConnector(BaseConnector):
    """
    Connector for World Bank Indicators API v2.

    Provides access to nearly 16,000 indicators across 45+ databases covering
    development, economics, health, education, environment, and more.

    Attributes:
        base_url: Base URL for World Bank API v2
        default_format: Default response format (json or xml)
        default_per_page: Default number of results per page
    """

    def __init__(self, **kwargs: Any):
        """Initialize the World Bank connector."""
        super().__init__(**kwargs)
        self.base_url = "https://api.worldbank.org/v2"
        self.default_format = "json"
        self.default_per_page = 50

    def _get_api_key(self) -> Optional[str]:
        """
        World Bank API does not require authentication.

        Returns:
            None (no API key required)
        """
        return None

    def connect(self) -> None:
        """
        Establish connection to World Bank API.

        No authentication required, but sets up session for connection pooling.
        """
        try:
            # Initialize session using base connector method
            session = self._init_session()

            # Test connection with a simple query
            response = session.get(
                f"{self.base_url}/country", params={"format": "json", "per_page": "1"}, timeout=10
            )
            response.raise_for_status()

            logger.info("Successfully connected to World Bank API")

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to connect to World Bank API: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

    def fetch(self, **kwargs: Any) -> Any:
        """
        Generic fetch method - delegates to specific methods based on query type.

        Args:
            **kwargs: Query parameters

        Returns:
            Query results

        Raises:
            DataError: If query type is not specified or invalid
        """
        query_type = kwargs.get("query_type")

        if query_type == "indicator":
            return self.get_indicator_data(**kwargs)
        elif query_type == "countries":
            return self.get_countries(**kwargs)
        elif query_type == "indicators_list":
            return self.get_indicators(**kwargs)
        elif query_type == "sources":
            return self.get_sources(**kwargs)
        elif query_type == "search":
            return self.search_indicators(**kwargs)
        else:
            raise ValueError(
                f"Invalid query_type: {query_type}. "
                f"Must be one of: indicator, countries, indicators_list, sources, search"
            )

    def _make_paginated_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Make paginated API request and collect all results.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            List of all results across all pages

        Raises:
            APIError: If request fails
        """
        if params is None:
            params = {}

        # Ensure JSON format
        params["format"] = "json"
        params.setdefault("per_page", self.default_per_page)

        all_results = []
        page = 1
        total_pages = 1

        while page <= total_pages:
            params["page"] = page

            try:
                url = f"{self.base_url}/{endpoint}"

                # Ensure session is initialized
                session = self._init_session()

                response = session.get(url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()

                # World Bank API returns [metadata, results]
                if isinstance(data, list) and len(data) >= 2:
                    metadata = data[0]
                    results = data[1]

                    # Update pagination info from metadata
                    if isinstance(metadata, dict):
                        total_pages = int(metadata.get("pages", 1))
                        current_page = int(metadata.get("page", page))

                        logger.debug(
                            f"Retrieved page {current_page} of {total_pages} "
                            f"({len(results)} results)"
                        )

                    # Collect results
                    if isinstance(results, list):
                        all_results.extend(results)
                    elif results is not None:
                        all_results.append(results)

                page += 1

                # Rate limiting: be respectful
                if page <= total_pages:
                    time.sleep(0.1)

            except requests.exceptions.RequestException as e:
                error_msg = f"API request failed for {endpoint}: {str(e)}"
                logger.error(error_msg)
                raise ConnectionError(error_msg) from e

        return all_results

    def get_indicator_data(
        self,
        indicator: str,
        countries: Union[str, List[str]] = "all",
        date_range: Optional[str] = None,
        mrv: Optional[int] = None,
        mrnev: Optional[int] = None,
        gap_fill: bool = False,
        frequency: Optional[str] = None,
        source: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch time series data for a specific indicator.

        Args:
            indicator: Indicator code (e.g., "SP.POP.TOTL" for population)
            countries: Country code(s) or "all". Can be:
                - Single string: "USA"
                - List: ["USA", "CHN", "IND"]
                - "all" for all countries
            date_range: Date range in various formats:
                - Single year: "2020"
                - Year range: "2010:2020"
                - Month: "2020M01"
                - Month range: "2020M01:2020M12"
                - Quarter: "2020Q1"
                - Quarter range: "2020Q1:2020Q4"
                - Year-to-date: "YTD:2020"
            mrv: Most Recent Values - number of most recent values to fetch
            mrnev: Most Recent Non-Empty Values
            gap_fill: If True, fills missing values by backtracking (works with mrv)
            frequency: Data frequency - "Y" (yearly), "Q" (quarterly), "M" (monthly)
            source: Data source ID (optional)

        Returns:
            List of data points, each containing:
                - indicator: {id, value}
                - country: {id, value}
                - countryiso3code: ISO 3-letter code
                - date: Year or period
                - value: Indicator value
                - unit: Unit of measurement
                - obs_status: Observation status
                - decimal: Number of decimals

        Example:
            >>> wb = WorldBankConnector()
            >>> wb.connect()
            >>> # Get GDP for USA and China, 2010-2020
            >>> data = wb.get_indicator_data(
            ...     indicator="NY.GDP.MKTP.CD",
            ...     countries=["USA", "CHN"],
            ...     date_range="2010:2020"
            ... )
            >>> # Get most recent 5 poverty values
            >>> data = wb.get_indicator_data(
            ...     indicator="SI.POV.DDAY",
            ...     countries="all",
            ...     mrv=5
            ... )
        """
        # Format countries parameter
        if isinstance(countries, list):
            countries_str = ";".join(countries)
        else:
            countries_str = countries

        # Build endpoint
        endpoint = f"country/{countries_str}/indicator/{indicator}"

        # Build query parameters
        params: Dict[str, Any] = {}

        if date_range:
            params["date"] = date_range
        if mrv:
            params["mrv"] = mrv
        if mrnev:
            params["mrnev"] = mrnev
        if gap_fill:
            params["gapfill"] = "Y"
        if frequency:
            params["frequency"] = frequency
        if source:
            params["source"] = source

        logger.info(f"Fetching indicator {indicator} for {countries_str} " f"with params: {params}")

        results = self._make_paginated_request(endpoint, params)

        logger.info(f"Retrieved {len(results)} data points")

        return results

    def get_multiple_indicators(
        self,
        indicators: List[str],
        countries: Union[str, List[str]] = "all",
        source: int = 2,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Fetch data for multiple indicators at once.

        Note: Maximum 60 indicators per request.

        Args:
            indicators: List of indicator codes
            countries: Country code(s) or "all"
            source: Data source ID (required for multiple indicators)
            **kwargs: Additional parameters (date_range, mrv, etc.)

        Returns:
            List of data points for all indicators

        Raises:
            DataError: If more than 60 indicators requested
        """
        if len(indicators) > 60:
            raise ValueError(f"Maximum 60 indicators allowed per request, got {len(indicators)}")

        # Format parameters
        if isinstance(countries, list):
            countries_str = ";".join(countries)
        else:
            countries_str = countries

        indicators_str = ";".join(indicators)

        # Build endpoint
        endpoint = f"country/{countries_str}/indicator/{indicators_str}"

        # Build params
        params = {"source": source}
        params.update(kwargs)

        logger.info(f"Fetching {len(indicators)} indicators for {countries_str}")

        results = self._make_paginated_request(endpoint, params)

        logger.info(f"Retrieved {len(results)} data points")

        return results

    def get_countries(
        self,
        income_level: Optional[str] = None,
        lending_type: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get list of countries with optional filtering.

        Args:
            income_level: Filter by income level:
                - LIC: Low income
                - LMC: Lower middle income
                - UMC: Upper middle income
                - HIC: High income
            lending_type: Filter by lending type:
                - IBD: IBRD
                - IDB: Blend
                - IDX: IDA
            region: Filter by region code (e.g., "EAS" for East Asia & Pacific)

        Returns:
            List of countries with metadata:
                - id: Country code
                - iso2Code: ISO 2-letter code
                - name: Country name
                - region: {id, iso2code, value}
                - adminregion: Admin region info
                - incomeLevel: {id, iso2code, value}
                - lendingType: {id, iso2code, value}
                - capitalCity: Capital city name
                - longitude: Longitude coordinate
                - latitude: Latitude coordinate

        Example:
            >>> wb = WorldBankConnector()
            >>> wb.connect()
            >>> # Get all high-income countries
            >>> countries = wb.get_countries(income_level="HIC")
            >>> # Get countries in East Asia & Pacific
            >>> countries = wb.get_countries(region="EAS")
        """
        params: Dict[str, Any] = {}

        if income_level:
            params["incomeLevel"] = income_level
        if lending_type:
            params["lendingType"] = lending_type
        if region:
            params["region"] = region

        logger.info(f"Fetching countries with filters: {params}")

        results = self._make_paginated_request("country", params)

        logger.info(f"Retrieved {len(results)} countries")

        return results

    def get_indicators(self, source: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get list of available indicators.

        Args:
            source: Optional source ID to filter indicators

        Returns:
            List of indicators with metadata:
                - id: Indicator code
                - name: Indicator name
                - unit: Unit of measurement
                - source: {id, value}
                - sourceNote: Description
                - sourceOrganization: Data source organization
                - topics: List of related topics

        Example:
            >>> wb = WorldBankConnector()
            >>> wb.connect()
            >>> # Get all indicators
            >>> indicators = wb.get_indicators()
            >>> # Get indicators from World Development Indicators (source 2)
            >>> indicators = wb.get_indicators(source=2)
        """
        params: Dict[str, Any] = {}

        if source:
            params["source"] = source

        logger.info(f"Fetching indicators with params: {params}")

        results = self._make_paginated_request("indicator", params)

        logger.info(f"Retrieved {len(results)} indicators")

        return results

    def search_indicators(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for indicators by keyword in name or description.

        Note: This is a client-side search through all indicators.
        For large result sets, this may take some time.

        Args:
            query: Search query (case-insensitive)

        Returns:
            List of matching indicators

        Example:
            >>> wb = WorldBankConnector()
            >>> wb.connect()
            >>> # Search for unemployment indicators
            >>> indicators = wb.search_indicators("unemployment")
            >>> # Search for GDP indicators
            >>> indicators = wb.search_indicators("GDP")
        """
        logger.info(f"Searching indicators for: {query}")

        # Get all indicators
        all_indicators = self.get_indicators()

        # Filter by query (case-insensitive)
        query_lower = query.lower()
        matching = [
            ind
            for ind in all_indicators
            if query_lower in ind.get("name", "").lower()
            or query_lower in ind.get("sourceNote", "").lower()
        ]

        logger.info(f"Found {len(matching)} matching indicators")

        return matching

    def get_sources(self) -> List[Dict[str, Any]]:
        """
        Get list of all data sources available in the API.

        Returns:
            List of sources with metadata:
                - id: Source ID
                - name: Source name
                - description: Source description
                - url: Source URL
                - dataavailability: Data availability status
                - metadataavailability: Metadata availability status

        Example:
            >>> wb = WorldBankConnector()
            >>> wb.connect()
            >>> sources = wb.get_sources()
            >>> for source in sources:
            ...     print(f"{source['id']}: {source['name']}")
        """
        logger.info("Fetching data sources")

        results = self._make_paginated_request("sources")

        logger.info(f"Retrieved {len(results)} sources")

        return results

    def get_indicator_metadata(self, indicator: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific indicator.

        Args:
            indicator: Indicator code

        Returns:
            Indicator metadata dictionary

        Example:
            >>> wb = WorldBankConnector()
            >>> wb.connect()
            >>> metadata = wb.get_indicator_metadata("SP.POP.TOTL")
            >>> print(metadata["name"])  # "Population, total"
        """
        logger.info(f"Fetching metadata for indicator: {indicator}")

        results = self._make_paginated_request(f"indicator/{indicator}")

        if results:
            return results[0]
        else:
            raise ValueError(f"Indicator not found: {indicator}")

    def close(self) -> None:
        """Close the connection session."""
        if self.session:
            self.session.close()
            self.session = None
            logger.info("World Bank API session closed")
