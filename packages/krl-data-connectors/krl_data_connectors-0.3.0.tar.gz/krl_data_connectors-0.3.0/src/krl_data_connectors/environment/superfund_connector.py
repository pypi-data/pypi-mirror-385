# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
EPA Superfund Connector - Envirofacts API Integration

This connector provides access to Superfund site data from the EPA Envirofacts
database, which contains information about hazardous waste sites designated for
cleanup under the Comprehensive Environmental Response, Compensation, and Liability
Act (CERCLA), commonly known as Superfund.

Data Source: https://www.epa.gov/enviro/envirofacts-data-service-api
API Type: REST API (no authentication required)
Coverage: 1,800+ National Priorities List (NPL) sites nationwide
Update Frequency: Quarterly updates

Key Features:
- Site identification and location data
- Cleanup status and milestones
- Contamination details (chemicals, media)
- Responsible parties information
- Remedial actions and ROD (Record of Decision) data
- Site assessment scores (HRS - Hazard Ranking System)

Site Status Categories:
- Proposed: Site proposed for NPL listing
- Final: Site on the Final NPL
- Deleted: Site removed from NPL after cleanup
- Construction Complete: Remedial construction finished
- Site Assessment: Initial investigation phase

Contamination Media:
- Soil
- Groundwater
- Surface water
- Sediment
- Air

Note: Data is updated quarterly. For real-time enforcement data, use EPA ECHO API.

Author: KR-Labs Development Team
License: Apache 2.0
"""

import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

from ..base_connector import BaseConnector

logger = logging.getLogger(__name__)


class SuperfundConnector(BaseConnector):
    """
    Connector for EPA Superfund Sites (Envirofacts API).

    Provides access to Superfund site data including:
    - Site identification and location
    - Cleanup status and progress
    - Contamination details
    - Responsible parties
    - Remedial actions

    No API key required for EPA Envirofacts.

    Attributes:
        base_url (str): Base URL for Envirofacts API
        session (requests.Session): HTTP session for API calls

    Example:
        >>> connector = SuperfundConnector()
        >>> sites = connector.get_sites_by_state("CA")
        >>> print(f"Found {len(sites)} Superfund sites in California")
    """

    # API Configuration
    BASE_URL = "https://data.epa.gov/efservice"

    # Site status codes
    STATUS_CODES = {
        "P": "Proposed",
        "F": "Final NPL",
        "D": "Deleted from NPL",
        "N": "Not on NPL",
    }

    # Cleanup phase codes
    CLEANUP_PHASES = {
        "1": "Preliminary Assessment",
        "2": "Site Inspection",
        "3": "NPL Listing",
        "4": "Remedial Investigation/Feasibility Study",
        "5": "Record of Decision",
        "6": "Remedial Design",
        "7": "Remedial Action",
        "8": "Construction Complete",
        "9": "Post-Construction Complete",
        "10": "Site Deletion",
    }

    def __init__(self, **kwargs):
        """
        Initialize Superfund connector.

        Args:
            **kwargs: Additional arguments passed to BaseConnector
        """
        # EPA Envirofacts doesn't require an API key
        super().__init__(api_key=None, **kwargs)
        self.base_url = self.BASE_URL
        self.logger.info("SuperfundConnector initialized (no API key required)")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration.

        Returns:
            None (EPA Envirofacts doesn't require API key)
        """
        return None

    def connect(self) -> None:
        """
        Establish connection to EPA Envirofacts API.

        Raises:
            ConnectionError: If unable to connect to API
        """
        if self.session is not None:
            return

        try:
            self.session = self._init_session()
            # Test connection
            test_url = f"{self.base_url}/SEMS/SITE_NAME/ROWS/0:1/JSON"
            response = self.session.get(test_url, timeout=self.timeout)
            response.raise_for_status()
            self.logger.info("Successfully connected to EPA Envirofacts API")
        except Exception as e:
            self.logger.error(f"Failed to connect to EPA Envirofacts API: {e}")
            raise ConnectionError(f"Could not connect to EPA Envirofacts API: {e}")

    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from EPA Envirofacts API.

        Args:
            endpoint: API endpoint path (required)
            params: Query parameters (optional)

        Returns:
            dict: API response data

        Raises:
            requests.HTTPError: If API request fails
        """
        endpoint = kwargs.get('endpoint')
        params = kwargs.get('params')
        
        if not endpoint:
            raise ValueError("endpoint parameter is required")
        
        if not self.session:
            self.connect()

        url = f"{self.base_url}/{endpoint}"
        session = self._init_session()
        
        try:
            response = session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # Try JSON first
            try:
                return response.json()
            except ValueError:
                # Fall back to text for non-JSON responses
                return {"data": response.text}
                
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error fetching data: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            raise

    def get_sites_by_state(
        self, state: str, status: Optional[str] = None, limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get Superfund sites by state.

        Args:
            state: Two-letter state code (e.g., 'CA', 'NY')
            status: Site status filter ('P', 'F', 'D', or None for all)
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing site information

        Example:
            >>> connector = SuperfundConnector()
            >>> ca_sites = connector.get_sites_by_state("CA", status="F")
            >>> print(ca_sites[['SITE_NAME', 'CITY', 'NPL_STATUS']])
        """
        state = state.upper()
        cache_key = f"sites_state_{state}_{status}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached data for state {state}")
            return cached_data

        # Build endpoint
        endpoint = f"SEMS/STATE/{state}"
        if status:
            endpoint += f"/NPL_STATUS/{status}"
        endpoint += f"/ROWS/0:{limit}/JSON"

        # Fetch data
        self.logger.info(f"Fetching Superfund sites for state: {state}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} Superfund sites for state {state}")
        return df

    def get_site_by_id(self, site_id: str) -> pd.DataFrame:
        """
        Get detailed information for a specific Superfund site.

        Args:
            site_id: EPA Site ID

        Returns:
            pd.DataFrame: DataFrame with site details

        Example:
            >>> connector = SuperfundConnector()
            >>> site = connector.get_site_by_id("CAD009195731")
            >>> print(site['SITE_NAME'].iloc[0])
        """
        cache_key = f"site_detail_{site_id}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached data for site {site_id}")
            return cached_data

        # Fetch data
        endpoint = f"SEMS/SITE_EPA_ID/{site_id}/JSON"
        self.logger.info(f"Fetching site details for: {site_id}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        df = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved details for site {site_id}")
        return df

    def get_sites_by_city(self, city: str, state: str, limit: int = 100) -> pd.DataFrame:
        """
        Get Superfund sites by city and state.

        Args:
            city: City name
            state: Two-letter state code
            limit: Maximum number of results (default: 100)

        Returns:
            pd.DataFrame: DataFrame containing site information

        Example:
            >>> connector = SuperfundConnector()
            >>> sites = connector.get_sites_by_city("Los Angeles", "CA")
            >>> print(f"Found {len(sites)} sites")
        """
        city = city.upper().replace(" ", "%20")
        state = state.upper()
        cache_key = f"sites_city_{city}_{state}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached data for {city}, {state}")
            return cached_data

        # Fetch data
        endpoint = f"SEMS/CITY/{city}/STATE/{state}/ROWS/0:{limit}/JSON"
        self.logger.info(f"Fetching Superfund sites for: {city}, {state}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} sites for {city}, {state}")
        return df

    def get_sites_by_zip(self, zip_code: str, limit: int = 100) -> pd.DataFrame:
        """
        Get Superfund sites by ZIP code.

        Args:
            zip_code: 5-digit ZIP code
            limit: Maximum number of results (default: 100)

        Returns:
            pd.DataFrame: DataFrame containing site information

        Example:
            >>> connector = SuperfundConnector()
            >>> sites = connector.get_sites_by_zip("94102")
            >>> print(sites[['SITE_NAME', 'ADDRESS']])
        """
        cache_key = f"sites_zip_{zip_code}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached data for ZIP {zip_code}")
            return cached_data

        # Fetch data
        endpoint = f"SEMS/ZIP/{zip_code}/ROWS/0:{limit}/JSON"
        self.logger.info(f"Fetching Superfund sites for ZIP: {zip_code}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} sites for ZIP {zip_code}")
        return df

    def get_npl_sites(self, limit: int = 2000) -> pd.DataFrame:
        """
        Get all National Priorities List (NPL) sites.

        Args:
            limit: Maximum number of results (default: 2000)

        Returns:
            pd.DataFrame: DataFrame containing NPL site information

        Example:
            >>> connector = SuperfundConnector()
            >>> npl_sites = connector.get_npl_sites()
            >>> print(f"Total NPL sites: {len(npl_sites)}")
            >>> print(npl_sites['NPL_STATUS'].value_counts())
        """
        cache_key = f"npl_sites_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached NPL sites data")
            return cached_data

        # Fetch data (Final NPL sites)
        endpoint = f"SEMS/NPL_STATUS/F/ROWS/0:{limit}/JSON"
        self.logger.info("Fetching all NPL sites")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} NPL sites")
        return df

    def get_construction_complete_sites(self, state: Optional[str] = None, limit: int = 1000) -> pd.DataFrame:
        """
        Get sites with construction complete status.

        Args:
            state: Optional two-letter state code to filter by
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing construction complete sites

        Example:
            >>> connector = SuperfundConnector()
            >>> complete_sites = connector.get_construction_complete_sites("CA")
            >>> print(f"Construction complete sites in CA: {len(complete_sites)}")
        """
        cache_key = f"construction_complete_{state}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached construction complete sites")
            return cached_data

        # Build endpoint
        if state:
            endpoint = f"SEMS/STATE/{state.upper()}/CONST_COMP_IND/Y/ROWS/0:{limit}/JSON"
        else:
            endpoint = f"SEMS/CONST_COMP_IND/Y/ROWS/0:{limit}/JSON"

        # Fetch data
        self.logger.info(f"Fetching construction complete sites{f' for {state}' if state else ''}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} construction complete sites")
        return df

    def search_sites_by_name(self, site_name: str, limit: int = 100) -> pd.DataFrame:
        """
        Search for Superfund sites by name (partial match).

        Args:
            site_name: Site name to search for
            limit: Maximum number of results (default: 100)

        Returns:
            pd.DataFrame: DataFrame containing matching sites

        Example:
            >>> connector = SuperfundConnector()
            >>> sites = connector.search_sites_by_name("Chemical")
            >>> print(sites[['SITE_NAME', 'CITY', 'STATE']])
        """
        cache_key = f"search_name_{site_name}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached search results for '{site_name}'")
            return cached_data

        # Fetch data (using LIKE operator in Envirofacts)
        site_name_encoded = site_name.upper().replace(" ", "%20")
        endpoint = f"SEMS/SITE_NAME/BEGINNING/{site_name_encoded}/ROWS/0:{limit}/JSON"
        
        self.logger.info(f"Searching for sites matching: {site_name}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Found {len(df)} sites matching '{site_name}'")
        return df

    def get_site_coordinates(self, site_id: str) -> Optional[tuple]:
        """
        Get geographic coordinates for a site.

        Args:
            site_id: EPA Site ID

        Returns:
            tuple: (latitude, longitude) or None if not available

        Example:
            >>> connector = SuperfundConnector()
            >>> coords = connector.get_site_coordinates("CAD009195731")
            >>> if coords:
            ...     print(f"Location: {coords[0]}, {coords[1]}")
        """
        site_data = self.get_site_by_id(site_id)
        
        if site_data.empty:
            return None
            
        lat = site_data.get('LATITUDE', pd.Series([None])).iloc[0]
        lon = site_data.get('LONGITUDE', pd.Series([None])).iloc[0]
        
        return (float(lat), float(lon)) if (lat is not None and lon is not None) else None

    def close(self):
        """Close HTTP session."""
        if self.session:
            self.session.close()
            self.session = None
            self.logger.info("HTTP session closed")
