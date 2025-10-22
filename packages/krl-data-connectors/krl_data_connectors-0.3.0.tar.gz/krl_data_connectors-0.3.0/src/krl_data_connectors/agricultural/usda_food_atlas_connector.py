"""
USDA Food Environment Atlas Connector.

This module provides a connector to the USDA Economic Research Service (ERS)
Food Environment Atlas, which provides data on food access, food insecurity,
local food systems, and health indicators across U.S. counties.

Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
SPDX-License-Identifier: Apache-2.0
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector


class USDAFoodAtlasConnector(BaseConnector):
    """Connector for USDA Food Environment Atlas data.

    The Food Environment Atlas provides data on food access, food insecurity,
    restaurant availability, local food systems, and health indicators for
    U.S. counties. Data includes:

    - Food access and store availability
    - Food assistance programs (SNAP, WIC, school meals)
    - Food insecurity and food prices
    - Health and physical activity
    - Local food systems
    - Restaurant availability and expenditures
    - Socioeconomic characteristics

    Environment Variables:
        USDA_API_KEY: API key for USDA ERS Data API

    Attributes:
        CATEGORIES: Available data categories in the Food Atlas

    Example:
        >>> connector = USDAFoodAtlasConnector()
        >>> # Get food access data for all counties
        >>> access_data = connector.get_county_data(category="access")
        >>> # Get specific indicators
        >>> indicators = connector.get_indicators(
        ...     state_fips="06",
        ...     indicators=["PCT_LACCESS_POP15", "GROCERY14"]
        ... )
    """

    # Food Atlas data categories
    CATEGORIES = {
        "access": "Food access and store availability",
        "assistance": "Food assistance programs",
        "insecurity": "Food insecurity",
        "prices": "Food prices and taxes",
        "health": "Health and physical activity",
        "local": "Local food systems",
        "restaurants": "Restaurant availability and expenditures",
        "socioeconomic": "Socioeconomic characteristics",
    }

    # Common indicators by category
    INDICATORS = {
        "access": [
            "PCT_LACCESS_POP15",  # % low access to store
            "PCT_LACCESS_CHILD15",  # % children low access
            "PCT_LACCESS_SENIORS15",  # % seniors low access
            "GROCERY14",  # Grocery stores per 1,000 pop
            "SUPERC14",  # Supercenters per 1,000 pop
            "CONVS14",  # Convenience stores per 1,000 pop
        ],
        "assistance": [
            "PCT_SNAP16",  # % authorized SNAP stores
            "SNAP_PART_RATE16",  # SNAP participation rate
            "PCT_NSLP15",  # % free/reduced lunch eligible
            "PCT_SBP15",  # % free/reduced breakfast eligible
        ],
        "insecurity": [
            "FOODINSEC_15_17",  # Food insecurity rate
            "VLFOODSEC_15_17",  # Very low food security rate
            "CH_FOODINSEC_12_14_15_17",  # Change in food insecurity
        ],
        "health": [
            "PCT_DIABETES_ADULTS13",  # % adults with diabetes
            "PCT_OBESE_ADULTS13",  # % obese adults
            "RECFAC14",  # Recreation facilities per 1,000 pop
        ],
        "local": [
            "FMRKT16",  # Farmers markets per 1,000 pop
            "CSA07",  # CSA farms
            "FOODHUB16",  # Food hubs
        ],
        "restaurants": [
            "FFR14",  # Fast food restaurants per 1,000 pop
            "FSR14",  # Full-service restaurants per 1,000 pop
            "PCT_FFRSALES12",  # % food sales from fast food
        ],
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.ers.usda.gov/data",
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        **kwargs: Any,
    ):
        """Initialize USDA Food Atlas connector.

        Args:
            api_key: USDA API key (defaults to USDA_API_KEY env var)
            base_url: USDA ERS API base URL
            cache_dir: Cache directory path
            cache_ttl: Cache time-to-live in seconds

        Raises:
            ConfigurationError: If API key is not provided
        """
        self.base_url = base_url
        super().__init__(api_key=api_key, cache_dir=cache_dir, cache_ttl=cache_ttl, **kwargs)

    def _get_api_key(self) -> Optional[str]:
        """Get USDA API key from configuration."""
        return self.config.get("USDA_API_KEY")

    def connect(self) -> None:
        """
        Connect to USDA Food Atlas API (verify API key).

        Makes a simple API call to verify the API key is valid.
        """
        try:
            # Make a simple request to verify API key
            url = f"{self.base_url}/foodatlas/county"
            params = {"api_key": self.api_key, "state": "06"}

            self._make_request(url, params, use_cache=False)

            self.logger.info("Successfully connected to USDA Food Atlas API")

        except Exception as e:
            self.logger.error(f"Failed to connect to USDA Food Atlas API: {e}", exc_info=True)
            raise

    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """
        Fetch data from Food Atlas API.

        Alias for get_county_data() to implement abstract method.

        Args:
            **kwargs: Arguments to pass to get_county_data()

        Returns:
            DataFrame with Food Atlas data
        """
        return self.get_county_data(**kwargs)

    def get_county_data(
        self,
        category: Optional[str] = None,
        state_fips: Optional[str] = None,
        county_fips: Optional[str] = None,
    ) -> pd.DataFrame:
        """Get Food Environment Atlas data for counties.

        Args:
            category: Data category (e.g., 'access', 'assistance', 'insecurity').
                If None, returns all available data.
            state_fips: State FIPS code (2-digit, e.g., '06' for California).
                If None, returns data for all states.
            county_fips: County FIPS code (5-digit, e.g., '06037' for LA County).
                If provided, state_fips is ignored.

        Returns:
            DataFrame with Food Atlas data

        Raises:
            APIError: If API request fails
            ValueError: If category is invalid

        Example:
            >>> connector = USDAFoodAtlasConnector()
            >>> # Get all food access data
            >>> access = connector.get_county_data(category="access")
            >>> # Get California data
            >>> ca_data = connector.get_county_data(state_fips="06")
            >>> # Get specific county
            >>> la_data = connector.get_county_data(county_fips="06037")
        """
        if category and category not in self.CATEGORIES:
            valid = ", ".join(self.CATEGORIES.keys())
            raise ValueError(f"Invalid category '{category}'. Must be one of: {valid}")

        # Build URL and parameters
        url = f"{self.base_url}/foodatlas/county"
        params: Dict[str, Any] = {"api_key": self.api_key, "file_type": "json"}

        if category:
            params["category"] = category
        if county_fips:
            params["fips"] = county_fips
        elif state_fips:
            params["state"] = state_fips

        # Fetch data
        response = self._make_request(url, params)
        return self._parse_response(response)

    def get_indicators(
        self,
        indicators: List[str],
        state_fips: Optional[str] = None,
        county_fips: Optional[str] = None,
    ) -> pd.DataFrame:
        """Get specific Food Atlas indicators for counties.

        Args:
            indicators: List of indicator codes to retrieve
            state_fips: State FIPS code (2-digit). If None, returns all states.
            county_fips: County FIPS code (5-digit). If provided, state_fips is ignored.

        Returns:
            DataFrame with requested indicators

        Raises:
            APIError: If API request fails
            ValueError: If no indicators provided

        Example:
            >>> connector = USDAFoodAtlasConnector()
            >>> # Get food access indicators for California
            >>> data = connector.get_indicators(
            ...     indicators=["PCT_LACCESS_POP15", "GROCERY14"],
            ...     state_fips="06"
            ... )
        """
        if not indicators:
            raise ValueError("At least one indicator must be provided")

        url = f"{self.base_url}/foodatlas/indicators"
        params: Dict[str, Any] = {
            "api_key": self.api_key,
            "indicators": ",".join(indicators),
            "file_type": "json",
        }

        if county_fips:
            params["fips"] = county_fips
        elif state_fips:
            params["state"] = state_fips

        response = self._make_request(url, params)
        return self._parse_response(response)

    def get_category_indicators(self, category: str) -> List[str]:
        """Get list of available indicators for a category.

        Args:
            category: Data category (e.g., 'access', 'assistance')

        Returns:
            List of indicator codes for the category

        Raises:
            ValueError: If category is invalid

        Example:
            >>> connector = USDAFoodAtlasConnector()
            >>> indicators = connector.get_category_indicators("access")
            >>> print(indicators)
            ['PCT_LACCESS_POP15', 'GROCERY14', ...]
        """
        if category not in self.CATEGORIES:
            valid = ", ".join(self.CATEGORIES.keys())
            raise ValueError(f"Invalid category '{category}'. Must be one of: {valid}")

        return self.INDICATORS.get(category, [])

    def list_categories(self) -> Dict[str, str]:
        """Get available Food Atlas data categories.

        Returns:
            Dictionary mapping category codes to descriptions

        Example:
            >>> connector = USDAFoodAtlasConnector()
            >>> categories = connector.list_categories()
            >>> for code, desc in categories.items():
            ...     print(f"{code}: {desc}")
        """
        return self.CATEGORIES.copy()

    def _parse_response(self, response: Dict[str, Any]) -> pd.DataFrame:
        """Parse API response into DataFrame.

        Args:
            response: Raw API response

        Returns:
            Parsed DataFrame

        Raises:
            ValueError: If response format is invalid
        """
        if "data" not in response:
            raise ValueError("Invalid response format: missing 'data' field")

        data = response["data"]
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # Standardize column names
        if "FIPS" in df.columns:
            df["fips"] = df["FIPS"]
        if "State" in df.columns:
            df["state"] = df["State"]
        if "County" in df.columns:
            df["county"] = df["County"]

        return df
