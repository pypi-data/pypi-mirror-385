"""
EPA Air Quality Connector - AirNow API Integration

This connector provides access to real-time and historical air quality data from the
EPA AirNow program, which aggregates data from over 2,500 monitoring stations across
the United States, Canada, and Mexico.

Data Source: https://docs.airnowapi.org/
API Type: REST API (requires free API key)
Coverage: 2,500+ monitoring stations, 500+ cities with forecasts
Update Frequency: Real-time (hourly updates)

Key Features:
- Current air quality observations (AQI and pollutant concentrations)
- Air quality forecasts (daily predictions)
- Historical observations (past AQI data)
- Monitoring site queries (geographic searches)
- Contour maps (spatial visualization via KML)

AQI Scale (Air Quality Index):
- 0-50: Good (Green)
- 51-100: Moderate (Yellow)
- 101-150: Unhealthy for Sensitive Groups (Orange)
- 151-200: Unhealthy (Red)
- 201-300: Very Unhealthy (Purple)
- 301-500: Hazardous (Maroon)

Parameters Supported:
- PM2.5 (Fine particulate matter)
- PM10 (Coarse particulate matter)
- Ozone (O3)
- Carbon Monoxide (CO)
- Nitrogen Dioxide (NO2)
- Sulfur Dioxide (SO2)

Note: AirNow data is preliminary and unverified. For regulatory decisions,
use EPA's Air Quality System (AQS) API instead.

Author: KR-Labs Development Team
License: MIT
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

from ..base_connector import BaseConnector

logger = logging.getLogger(__name__)


class EPAAirQualityConnector(BaseConnector):
    """
    Connector for EPA AirNow Air Quality API.

    Provides access to real-time and historical air quality data including:
    - Current AQI observations
    - Air quality forecasts
    - Historical AQI data
    - Monitoring site information
    - Spatial contour maps

    Attributes:
        base_url (str): Base URL for AirNow API
        api_key (str): API key for authentication

    Example:
        >>> connector = EPAAirQualityConnector(api_key="your_api_key")
        >>> current_aqi = connector.get_current_by_zip("94102")
        >>> print(current_aqi)
    """

    # API Configuration
    BASE_URL = "https://www.airnowapi.org/aq"

    # AQI Categories
    AQI_CATEGORIES = {
        "Good": (0, 50),
        "Moderate": (51, 100),
        "Unhealthy for Sensitive Groups": (101, 150),
        "Unhealthy": (151, 200),
        "Very Unhealthy": (201, 300),
        "Hazardous": (301, 500),
    }

    # Parameter codes
    PARAMETERS = {
        "PM25": "PM2.5",
        "PM10": "PM10",
        "OZONE": "OZONE",
        "O3": "OZONE",
        "CO": "CO",
        "NO2": "NO2",
        "SO2": "SO2",
    }

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize EPA Air Quality connector.

        Args:
            api_key: AirNow API key. If not provided, will look for AIRNOW_API_KEY
                    environment variable.
            **kwargs: Additional arguments passed to BaseConnector

        Raises:
            ValueError: If no API key provided or found in environment
        """
        super().__init__(**kwargs)

        self.api_key = api_key or os.getenv("AIRNOW_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Provide via api_key parameter or "
                "set AIRNOW_API_KEY environment variable. "
                "Register for free at https://docs.airnowapi.org/login"
            )

        self.base_url = self.BASE_URL
        self._session = None

        logger.info("EPA Air Quality connector initialized")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from environment or configuration.

        Returns:
            API key or None if not found
        """
        return os.getenv("AIRNOW_API_KEY")

    def fetch(self, endpoint: str = "", **kwargs: Any) -> Any:
        """
        Not used for AirNow API. Use specific methods like get_current_by_zip().

        Raises:
            NotImplementedError: Always raised, use specific methods instead
        """
        raise NotImplementedError(
            "Use specific methods like get_current_by_zip(), get_forecast_by_zip(), etc."
        )

    def connect(self) -> None:
        """
        Establish connection and verify API key.

        Tests the API key by making a simple request.

        Raises:
            ConnectionError: If API key is invalid or service unavailable
        """
        try:
            # Test API key with a simple request (current AQI for a valid ZIP)
            test_url = f"{self.base_url}/observation/zipCode/current/"
            params = {
                "format": "application/json",
                "zipCode": "20001",  # Washington DC
                "distance": "25",
                "API_KEY": self.api_key,
            }

            response = requests.get(test_url, params=params, timeout=10)

            if response.status_code == 403:
                raise ConnectionError(
                    "Invalid API key. Register at https://docs.airnowapi.org/login"
                )
            elif response.status_code != 200:
                raise ConnectionError(f"API connection failed: {response.status_code}")

            # Create session for subsequent requests
            self._session = requests.Session()
            self._session.headers.update({"User-Agent": "KR-Labs-Data-Connectors/1.0"})

            logger.info("Successfully connected to AirNow API")

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to AirNow API: {str(e)}")

    def disconnect(self) -> None:
        """Close the API session."""
        if self._session:
            self._session.close()
            self._session = None
        logger.info("Disconnected from AirNow API")

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Union[List[Dict], Dict]:
        """
        Make API request with error handling.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response as dict or list

        Raises:
            requests.exceptions.RequestException: For API errors
        """
        # Add API key and format to params
        params["API_KEY"] = self.api_key
        params["format"] = "application/json"

        url = f"{self.base_url}/{endpoint}"

        session = self._session or requests
        response = session.get(url, params=params, timeout=30)

        if response.status_code == 403:
            raise requests.exceptions.HTTPError("Invalid API key")
        elif response.status_code == 404:
            logger.warning(f"No data found for request: {endpoint}")
            return []

        response.raise_for_status()

        return response.json()

    def get_current_by_zip(self, zip_code: str, distance: int = 25) -> pd.DataFrame:
        """
        Get current air quality observations by ZIP code.

        Args:
            zip_code: 5-digit US ZIP code
            distance: Search radius in miles (default: 25)

        Returns:
            DataFrame with columns:
                - DateObserved: Observation date
                - HourObserved: Observation hour
                - LocalTimeZone: Time zone
                - ReportingArea: Geographic area name
                - StateCode: State abbreviation
                - Latitude: Monitoring site latitude
                - Longitude: Monitoring site longitude
                - ParameterName: Pollutant (PM2.5, Ozone, etc.)
                - AQI: Air Quality Index value
                - Category.Number: AQI category number (1-6)
                - Category.Name: AQI category name

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> current = connector.get_current_by_zip("94102")
            >>> print(current[['ReportingArea', 'ParameterName', 'AQI', 'Category.Name']])
        """
        if not zip_code or len(zip_code) != 5:
            raise ValueError("ZIP code must be 5 digits")

        params = {"zipCode": zip_code, "distance": str(distance)}

        data = self._make_request("observation/zipCode/current/", params)

        if not data:
            logger.warning(f"No current observations found for ZIP {zip_code}")
            return pd.DataFrame()

        return pd.DataFrame(data)

    def get_current_by_latlon(
        self, latitude: float, longitude: float, distance: int = 25
    ) -> pd.DataFrame:
        """
        Get current air quality observations by latitude/longitude.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            distance: Search radius in miles (default: 25)

        Returns:
            DataFrame with current AQI observations (same format as get_current_by_zip)

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> current = connector.get_current_by_latlon(37.7749, -122.4194)
        """
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        params = {"latitude": str(latitude), "longitude": str(longitude), "distance": str(distance)}

        data = self._make_request("observation/latLong/current/", params)

        if not data:
            logger.warning(f"No current observations found for {latitude}, {longitude}")
            return pd.DataFrame()

        return pd.DataFrame(data)

    def get_forecast_by_zip(
        self, zip_code: str, date: Optional[Union[str, datetime]] = None, distance: int = 25
    ) -> pd.DataFrame:
        """
        Get air quality forecast by ZIP code.

        Args:
            zip_code: 5-digit US ZIP code
            date: Forecast date (YYYY-MM-DD). If None, returns today's forecast.
            distance: Search radius in miles (default: 25)

        Returns:
            DataFrame with forecast data:
                - DateForecast: Forecast date
                - StateCode: State abbreviation
                - ReportingArea: Geographic area
                - ParameterName: Pollutant
                - AQI: Forecasted Air Quality Index
                - Category.Number: AQI category number
                - Category.Name: AQI category name
                - ActionDay: Boolean indicating action day (high pollution)
                - Discussion: Forecast discussion text

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> forecast = connector.get_forecast_by_zip("94102", date="2025-10-20")
        """
        if not zip_code or len(zip_code) != 5:
            raise ValueError("ZIP code must be 5 digits")

        params = {"zipCode": zip_code, "distance": str(distance)}

        if date:
            if isinstance(date, datetime):
                params["date"] = date.strftime("%Y-%m-%d")
            else:
                params["date"] = date

        data = self._make_request("forecast/zipCode/", params)

        if not data:
            logger.warning(f"No forecast found for ZIP {zip_code}")
            return pd.DataFrame()

        return pd.DataFrame(data)

    def get_forecast_by_latlon(
        self,
        latitude: float,
        longitude: float,
        date: Optional[Union[str, datetime]] = None,
        distance: int = 25,
    ) -> pd.DataFrame:
        """
        Get air quality forecast by latitude/longitude.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            date: Forecast date (YYYY-MM-DD). If None, returns today's forecast.
            distance: Search radius in miles (default: 25)

        Returns:
            DataFrame with forecast data (same format as get_forecast_by_zip)

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> forecast = connector.get_forecast_by_latlon(37.7749, -122.4194)
        """
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        params = {"latitude": str(latitude), "longitude": str(longitude), "distance": str(distance)}

        if date:
            if isinstance(date, datetime):
                params["date"] = date.strftime("%Y-%m-%d")
            else:
                params["date"] = date

        data = self._make_request("forecast/latLong/", params)

        if not data:
            logger.warning(f"No forecast found for {latitude}, {longitude}")
            return pd.DataFrame()

        return pd.DataFrame(data)

    def get_historical_by_zip(
        self,
        zip_code: str,
        start_date: Union[str, datetime],
        end_date: Optional[Union[str, datetime]] = None,
        distance: int = 25,
    ) -> pd.DataFrame:
        """
        Get historical air quality observations by ZIP code.

        Args:
            zip_code: 5-digit US ZIP code
            start_date: Start date (YYYY-MM-DD or YYYY-MM-DDTHH format)
            end_date: End date (YYYY-MM-DD or YYYY-MM-DDTHH). If None, uses start_date.
            distance: Search radius in miles (default: 25)

        Returns:
            DataFrame with historical observations

        Note:
            Historical data typically available for past 1-2 years.

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> historical = connector.get_historical_by_zip(
            ...     "94102",
            ...     start_date="2025-10-01",
            ...     end_date="2025-10-15"
            ... )
        """
        if not zip_code or len(zip_code) != 5:
            raise ValueError("ZIP code must be 5 digits")

        if isinstance(start_date, datetime):
            start_str = start_date.strftime("%Y-%m-%dT00")
        else:
            start_str = start_date

        if end_date:
            if isinstance(end_date, datetime):
                end_str = end_date.strftime("%Y-%m-%dT23")
            else:
                end_str = end_date
        else:
            end_str = start_str

        params = {"zipCode": zip_code, "date": start_str, "distance": str(distance)}

        # For date ranges, make multiple requests
        data = self._make_request("observation/zipCode/historical/", params)

        if not data:
            logger.warning(f"No historical data found for ZIP {zip_code}")
            return pd.DataFrame()

        return pd.DataFrame(data)

    def get_historical_by_latlon(
        self,
        latitude: float,
        longitude: float,
        start_date: Union[str, datetime],
        end_date: Optional[Union[str, datetime]] = None,
        distance: int = 25,
    ) -> pd.DataFrame:
        """
        Get historical air quality observations by latitude/longitude.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            start_date: Start date (YYYY-MM-DD or YYYY-MM-DDTHH format)
            end_date: End date (YYYY-MM-DD or YYYY-MM-DDTHH). If None, uses start_date.
            distance: Search radius in miles (default: 25)

        Returns:
            DataFrame with historical observations

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> historical = connector.get_historical_by_latlon(
            ...     37.7749, -122.4194,
            ...     start_date="2025-10-01"
            ... )
        """
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        if isinstance(start_date, datetime):
            start_str = start_date.strftime("%Y-%m-%dT00")
        else:
            start_str = start_date

        params = {
            "latitude": str(latitude),
            "longitude": str(longitude),
            "date": start_str,
            "distance": str(distance),
        }

        data = self._make_request("observation/latLong/historical/", params)

        if not data:
            logger.warning(f"No historical data found for {latitude}, {longitude}")
            return pd.DataFrame()

        return pd.DataFrame(data)

    def get_aqi_category(self, aqi_value: int) -> str:
        """
        Get AQI category name from AQI value.

        Args:
            aqi_value: Air Quality Index value (0-500)

        Returns:
            Category name (e.g., 'Good', 'Moderate', 'Unhealthy')

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> category = connector.get_aqi_category(75)
            >>> print(category)  # 'Moderate'
        """
        for category, (min_val, max_val) in self.AQI_CATEGORIES.items():
            if min_val <= aqi_value <= max_val:
                return category
        return "Unknown"

    def filter_by_parameter(self, data: pd.DataFrame, parameter: str) -> pd.DataFrame:
        """
        Filter observations by pollutant parameter.

        Args:
            data: DataFrame with air quality data
            parameter: Parameter name (PM2.5, PM10, OZONE, CO, NO2, SO2)

        Returns:
            Filtered DataFrame

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> current = connector.get_current_by_zip("94102")
            >>> pm25_only = connector.filter_by_parameter(current, "PM2.5")
        """
        if data.empty:
            return data

        # Normalize parameter name
        parameter_upper = parameter.upper()
        if parameter_upper in self.PARAMETERS:
            parameter_normalized = self.PARAMETERS[parameter_upper]
        else:
            parameter_normalized = parameter

        if "ParameterName" not in data.columns:
            raise ValueError("Data does not contain 'ParameterName' column")

        return data[data["ParameterName"].str.upper() == parameter_normalized.upper()].copy()

    def filter_by_aqi_threshold(
        self, data: pd.DataFrame, threshold: int, above: bool = True
    ) -> pd.DataFrame:
        """
        Filter observations by AQI threshold.

        Args:
            data: DataFrame with air quality data
            threshold: AQI threshold value
            above: If True, return AQI >= threshold. If False, return AQI < threshold.

        Returns:
            Filtered DataFrame

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> current = connector.get_current_by_zip("94102")
            >>> unhealthy = connector.filter_by_aqi_threshold(current, 101)
        """
        if data.empty:
            return data

        if "AQI" not in data.columns:
            raise ValueError("Data does not contain 'AQI' column")

        if above:
            return data[data["AQI"] >= threshold].copy()
        else:
            return data[data["AQI"] < threshold].copy()

    def summarize_by_parameter(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Summarize air quality statistics by parameter.

        Args:
            data: DataFrame with air quality observations

        Returns:
            DataFrame with statistics for each parameter:
                - ParameterName: Pollutant name
                - Count: Number of observations
                - Mean_AQI: Average AQI
                - Max_AQI: Maximum AQI
                - Min_AQI: Minimum AQI

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> current = connector.get_current_by_zip("94102")
            >>> summary = connector.summarize_by_parameter(current)
        """
        if data.empty:
            return pd.DataFrame()

        if "ParameterName" not in data.columns or "AQI" not in data.columns:
            raise ValueError("Data must contain 'ParameterName' and 'AQI' columns")

        return (
            data.groupby("ParameterName")["AQI"]
            .agg(Count="count", Mean_AQI="mean", Max_AQI="max", Min_AQI="min")
            .reset_index()
        )
