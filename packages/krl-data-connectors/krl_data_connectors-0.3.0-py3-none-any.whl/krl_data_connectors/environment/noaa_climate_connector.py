# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
NOAA Climate Data Connector - Climate Data Online (CDO) API Integration

This connector provides access to NOAA's Climate Data Online (CDO) database, which includes
historical weather observations, climate normals, and environmental data from thousands of
weather stations across the United States and globally.

Data Source: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
API Type: REST API (requires free token)
Coverage: 100,000+ weather stations, 1700s to present
Update Frequency: Daily updates for recent data

Key Features:
- Weather station metadata and locations
- Historical weather observations (temperature, precipitation, etc.)
- Climate data types and categories
- Dataset information and coverage
- Location-based queries (ZIP, city, state, county, FIPS)

Datasets Available:
- GHCND: Global Historical Climatology Network Daily
- GSOM: Global Summary of the Month
- GSOY: Global Summary of the Year
- NEXRAD2/3: Weather Radar (Level II and III)
- PRECIP_HLY: Precipitation Hourly
- NORMAL_ANN: Annual Climate Normals

Data Types:
- TMAX/TMIN: Maximum and minimum temperature
- PRCP: Precipitation
- SNOW/SNWD: Snowfall and snow depth
- AWND: Average wind speed
- WSF2/WSF5: Fastest 2-minute/5-second wind speed

API Token: Required (free at https://www.ncdc.noaa.gov/cdo-web/token)
Set via environment variable: NOAA_CDO_TOKEN

Note: API has rate limits (5 requests per second, 10,000 requests per day)

Author: KR-Labs Development Team
License: Apache 2.0
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

from ..base_connector import BaseConnector

logger = logging.getLogger(__name__)


class NOAAClimateConnector(BaseConnector):
    """
    Connector for NOAA Climate Data Online (CDO) API.

    Provides access to historical weather and climate data including:
    - Weather station information
    - Temperature, precipitation, wind data
    - Climate normals and extremes
    - Location-based queries
    - Dataset and data type metadata

    Requires API token (free registration).

    Attributes:
        base_url (str): Base URL for NOAA CDO API
        api_key (str): API token for authentication
        session (requests.Session): HTTP session for API calls

    Example:
        >>> connector = NOAAClimateConnector(api_key="your_token_here")
        >>> # Or set environment variable NOAA_CDO_TOKEN
        >>> stations = connector.get_stations(locationid="FIPS:06")
        >>> print(f"Found {len(stations)} stations in California")
    """

    # API Configuration
    BASE_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2"
    DEFAULT_LIMIT = 1000
    MAX_LIMIT = 1000  # NOAA API maximum

    # Common dataset IDs
    DATASETS = {
        "GHCND": "Global Historical Climatology Network - Daily",
        "GSOM": "Global Summary of the Month",
        "GSOY": "Global Summary of the Year",
        "NEXRAD2": "Weather Radar (Level II)",
        "NEXRAD3": "Weather Radar (Level III)",
        "NORMAL_ANN": "Annual Climate Normals",
        "NORMAL_DLY": "Daily Climate Normals",
        "NORMAL_HLY": "Hourly Climate Normals",
        "NORMAL_MLY": "Monthly Climate Normals",
        "PRECIP_15": "Precipitation 15 Minute",
        "PRECIP_HLY": "Precipitation Hourly",
    }

    # Common data type categories
    DATA_CATEGORIES = {
        "TEMP": "Air Temperature",
        "PRCP": "Precipitation",
        "WIND": "Wind",
        "SNOW": "Snowfall",
        "EVAP": "Evaporation",
        "SUN": "Sunshine",
    }

    # Location type prefixes
    LOCATION_TYPES = {
        "FIPS": "FIPS Code (State/County)",
        "CITY": "City ID",
        "ZIP": "ZIP Code",
    }

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize NOAA Climate connector.

        Args:
            api_key: NOAA CDO API token (or set NOAA_CDO_TOKEN env var)
            **kwargs: Additional arguments passed to BaseConnector
        """
        super().__init__(api_key=api_key, **kwargs)
        self.base_url = self.BASE_URL
        
        if not self.api_key:
            self.logger.warning(
                "No API key provided. Get free token at: "
                "https://www.ncdc.noaa.gov/cdo-web/token"
            )

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from environment.

        Returns:
            str: API key from NOAA_CDO_TOKEN environment variable
        """
        return os.environ.get("NOAA_CDO_TOKEN")

    def connect(self) -> None:
        """
        Establish connection to NOAA CDO API.

        Raises:
            ConnectionError: If unable to connect or authenticate
            ValueError: If no API key is provided
        """
        if not self.api_key:
            raise ValueError(
                "API key required. Set NOAA_CDO_TOKEN environment variable or "
                "pass api_key parameter. Get free token at: "
                "https://www.ncdc.noaa.gov/cdo-web/token"
            )

        if self.session is not None:
            return

        try:
            self.session = self._init_session()
            # Add token to headers
            self.session.headers.update({"token": self.api_key})
            
            # Test connection
            test_url = f"{self.base_url}/datasets"
            response = self.session.get(test_url, params={"limit": 1}, timeout=self.timeout)
            response.raise_for_status()
            
            self.logger.info("Successfully connected to NOAA CDO API")
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                raise ConnectionError("Invalid API token. Get free token at: https://www.ncdc.noaa.gov/cdo-web/token")
            raise ConnectionError(f"Could not connect to NOAA CDO API: {e}")
        except Exception as e:
            self.logger.error(f"Failed to connect to NOAA CDO API: {e}")
            raise ConnectionError(f"Could not connect to NOAA CDO API: {e}")

    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from NOAA CDO API.

        Args:
            endpoint: API endpoint path (required)
            params: Query parameters (optional)

        Returns:
            dict: API response data

        Raises:
            requests.HTTPError: If API request fails
        """
        endpoint = kwargs.get('endpoint')
        params = kwargs.get('params', {})
        
        if not endpoint:
            raise ValueError("endpoint parameter is required")
        
        if not self.session:
            self.connect()

        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error fetching data: {e}")
            if e.response.status_code == 400:
                self.logger.error(f"Bad request. Response: {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            raise

    def get_datasets(self, dataset_id: Optional[str] = None, limit: int = 100) -> pd.DataFrame:
        """
        Get available datasets.

        Args:
            dataset_id: Optional specific dataset ID to retrieve
            limit: Maximum number of results (default: 100)

        Returns:
            pd.DataFrame: DataFrame containing dataset information

        Example:
            >>> connector = NOAAClimateConnector(api_key="token")
            >>> datasets = connector.get_datasets()
            >>> print(datasets[['id', 'name', 'mindate', 'maxdate']])
        """
        cache_key = f"datasets_{dataset_id}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached datasets")
            return cached_data

        # Build endpoint
        if dataset_id:
            endpoint = f"datasets/{dataset_id}"
        else:
            endpoint = "datasets"

        params = {"limit": min(limit, self.MAX_LIMIT)}

        # Fetch data
        self.logger.info(f"Fetching datasets{f' (ID: {dataset_id})' if dataset_id else ''}")
        data = self.fetch(endpoint=endpoint, params=params)

        # Convert to DataFrame
        if "results" in data:
            df = pd.DataFrame(data["results"])
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} datasets")
        return df

    def get_data_categories(self, category_id: Optional[str] = None, limit: int = 100) -> pd.DataFrame:
        """
        Get data categories.

        Args:
            category_id: Optional specific category ID
            limit: Maximum number of results (default: 100)

        Returns:
            pd.DataFrame: DataFrame containing category information

        Example:
            >>> connector = NOAAClimateConnector(api_key="token")
            >>> categories = connector.get_data_categories()
            >>> print(categories[['id', 'name']])
        """
        cache_key = f"categories_{category_id}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached data categories")
            return cached_data

        # Build endpoint
        if category_id:
            endpoint = f"datacategories/{category_id}"
        else:
            endpoint = "datacategories"

        params = {"limit": min(limit, self.MAX_LIMIT)}

        # Fetch data
        self.logger.info(f"Fetching data categories{f' (ID: {category_id})' if category_id else ''}")
        data = self.fetch(endpoint=endpoint, params=params)

        # Convert to DataFrame
        if "results" in data:
            df = pd.DataFrame(data["results"])
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} data categories")
        return df

    def get_data_types(
        self, 
        datatype_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get available data types.

        Args:
            datatype_id: Optional specific data type ID
            dataset_id: Optional filter by dataset ID
            limit: Maximum number of results (default: 100)

        Returns:
            pd.DataFrame: DataFrame containing data type information

        Example:
            >>> connector = NOAAClimateConnector(api_key="token")
            >>> types = connector.get_data_types(dataset_id="GHCND")
            >>> print(types[['id', 'name', 'mindate', 'maxdate']])
        """
        cache_key = f"datatypes_{datatype_id}_{dataset_id}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached data types")
            return cached_data

        # Build endpoint
        if datatype_id:
            endpoint = f"datatypes/{datatype_id}"
        else:
            endpoint = "datatypes"

        params = {"limit": min(limit, self.MAX_LIMIT)}
        if dataset_id:
            params["datasetid"] = dataset_id

        # Fetch data
        self.logger.info(f"Fetching data types{f' for dataset {dataset_id}' if dataset_id else ''}")
        data = self.fetch(endpoint=endpoint, params=params)

        # Convert to DataFrame
        if "results" in data:
            df = pd.DataFrame(data["results"])
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} data types")
        return df

    def get_stations(
        self,
        station_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        locationid: Optional[str] = None,
        extent: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get weather station information.

        Args:
            station_id: Optional specific station ID
            dataset_id: Optional filter by dataset
            locationid: Optional location filter (e.g., 'FIPS:06' for CA)
            extent: Optional geographic extent (lat1,lon1,lat2,lon2)
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing station information

        Example:
            >>> connector = NOAAClimateConnector(api_key="token")
            >>> stations = connector.get_stations(locationid="FIPS:06", limit=100)
            >>> print(stations[['id', 'name', 'latitude', 'longitude']])
        """
        cache_key = f"stations_{station_id}_{dataset_id}_{locationid}_{extent}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached stations")
            return cached_data

        # Build endpoint
        if station_id:
            endpoint = f"stations/{station_id}"
        else:
            endpoint = "stations"

        params = {"limit": min(limit, self.MAX_LIMIT)}
        if dataset_id:
            params["datasetid"] = dataset_id
        if locationid:
            params["locationid"] = locationid
        if extent:
            params["extent"] = extent

        # Fetch data
        self.logger.info(f"Fetching stations{f' for location {locationid}' if locationid else ''}")
        data = self.fetch(endpoint=endpoint, params=params)

        # Convert to DataFrame
        if "results" in data:
            df = pd.DataFrame(data["results"])
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} stations")
        return df

    def get_locations(
        self,
        location_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        locationcategoryid: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get location information.

        Args:
            location_id: Optional specific location ID
            dataset_id: Optional filter by dataset
            locationcategoryid: Optional location category (e.g., 'ST' for states)
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing location information

        Example:
            >>> connector = NOAAClimateConnector(api_key="token")
            >>> locations = connector.get_locations(locationcategoryid="ST")
            >>> print(locations[['id', 'name']])
        """
        cache_key = f"locations_{location_id}_{dataset_id}_{locationcategoryid}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached locations")
            return cached_data

        # Build endpoint
        if location_id:
            endpoint = f"locations/{location_id}"
        else:
            endpoint = "locations"

        params = {"limit": min(limit, self.MAX_LIMIT)}
        if dataset_id:
            params["datasetid"] = dataset_id
        if locationcategoryid:
            params["locationcategoryid"] = locationcategoryid

        # Fetch data
        self.logger.info(f"Fetching locations{f' (category: {locationcategoryid})' if locationcategoryid else ''}")
        data = self.fetch(endpoint=endpoint, params=params)

        # Convert to DataFrame
        if "results" in data:
            df = pd.DataFrame(data["results"])
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} locations")
        return df

    def get_climate_data(
        self,
        dataset_id: str,
        start_date: str,
        end_date: str,
        datatype_id: Optional[str] = None,
        locationid: Optional[str] = None,
        stationid: Optional[str] = None,
        units: str = "standard",
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get climate/weather data observations.

        Args:
            dataset_id: Dataset ID (e.g., 'GHCND')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            datatype_id: Optional data type filter (e.g., 'TMAX')
            locationid: Optional location filter
            stationid: Optional station filter
            units: Unit system ('standard' or 'metric')
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing weather observations

        Example:
            >>> connector = NOAAClimateConnector(api_key="token")
            >>> data = connector.get_climate_data(
            ...     dataset_id="GHCND",
            ...     start_date="2024-01-01",
            ...     end_date="2024-01-31",
            ...     stationid="GHCND:USW00023174",
            ...     datatype_id="TMAX"
            ... )
            >>> print(data[['date', 'datatype', 'value', 'station']])
        """
        cache_key = f"data_{dataset_id}_{start_date}_{end_date}_{datatype_id}_{locationid}_{stationid}_{units}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached climate data")
            return cached_data

        endpoint = "data"
        params = {
            "datasetid": dataset_id,
            "startdate": start_date,
            "enddate": end_date,
            "units": units,
            "limit": min(limit, self.MAX_LIMIT)
        }
        
        if datatype_id:
            params["datatypeid"] = datatype_id
        if locationid:
            params["locationid"] = locationid
        if stationid:
            params["stationid"] = stationid

        # Fetch data
        self.logger.info(f"Fetching climate data for {dataset_id} from {start_date} to {end_date}")
        data = self.fetch(endpoint=endpoint, params=params)

        # Convert to DataFrame
        if "results" in data:
            df = pd.DataFrame(data["results"])
            # Convert date strings to datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
        else:
            df = pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} climate observations")
        return df

    def get_states(self) -> pd.DataFrame:
        """
        Get all U.S. states as locations.

        Returns:
            pd.DataFrame: DataFrame containing state information

        Example:
            >>> connector = NOAAClimateConnector(api_key="token")
            >>> states = connector.get_states()
            >>> print(states[['id', 'name']])
        """
        return self.get_locations(locationcategoryid="ST", limit=self.MAX_LIMIT)

    def get_temperature_data(
        self,
        start_date: str,
        end_date: str,
        stationid: Optional[str] = None,
        locationid: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get temperature data (TMAX, TMIN, TAVG).

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            stationid: Optional station filter
            locationid: Optional location filter
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing temperature observations

        Example:
            >>> connector = NOAAClimateConnector(api_key="token")
            >>> temps = connector.get_temperature_data(
            ...     start_date="2024-01-01",
            ...     end_date="2024-01-31",
            ...     stationid="GHCND:USW00023174"
            ... )
            >>> print(temps[['date', 'datatype', 'value']])
        """
        # Query for TMAX, TMIN, TAVG data types
        return self.get_climate_data(
            dataset_id="GHCND",
            start_date=start_date,
            end_date=end_date,
            stationid=stationid,
            locationid=locationid,
            limit=limit
        )

    def get_precipitation_data(
        self,
        start_date: str,
        end_date: str,
        stationid: Optional[str] = None,
        locationid: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get precipitation data.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            stationid: Optional station filter
            locationid: Optional location filter
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing precipitation observations

        Example:
            >>> connector = NOAAClimateConnector(api_key="token")
            >>> precip = connector.get_precipitation_data(
            ...     start_date="2024-01-01",
            ...     end_date="2024-01-31",
            ...     locationid="FIPS:06"
            ... )
            >>> print(precip[['date', 'value', 'station']])
        """
        return self.get_climate_data(
            dataset_id="GHCND",
            start_date=start_date,
            end_date=end_date,
            datatype_id="PRCP",
            stationid=stationid,
            locationid=locationid,
            limit=limit
        )

    def close(self):
        """Close HTTP session."""
        if self.session:
            self.session.close()
            self.session = None
            self.logger.info("HTTP session closed")
