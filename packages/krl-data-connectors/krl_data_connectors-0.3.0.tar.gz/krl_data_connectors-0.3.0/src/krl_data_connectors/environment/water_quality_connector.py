# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
EPA Water Quality Connector - ECHO API Integration

This connector provides access to drinking water quality and compliance data from the
EPA's Enforcement and Compliance History Online (ECHO) database, which tracks violations
and enforcement actions for water systems under the Safe Drinking Water Act (SDWA).

Data Source: https://echo.epa.gov/tools/web-services
API Type: REST API (no authentication required)
Coverage: 150,000+ public water systems nationwide
Update Frequency: Quarterly updates

Key Features:
- Water system facility information
- SDWA violations (health-based and monitoring)
- Enforcement actions and compliance status
- Water quality contaminant data
- System demographics and population served

Violation Types:
- Health-based violations (MCL, MRDL, TT)
- Monitoring and reporting violations
- Public notification violations
- Operator certification violations

System Types:
- Community Water System (CWS)
- Non-Transient Non-Community (NTNCWS)
- Transient Non-Community (TNCWS)

Note: Data is updated quarterly. For real-time water quality data, contact state agencies.

Author: KR-Labs Development Team
License: Apache 2.0
"""

import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

from ..base_connector import BaseConnector

logger = logging.getLogger(__name__)


class WaterQualityConnector(BaseConnector):
    """
    Connector for EPA Water Quality data (ECHO API).

    Provides access to Safe Drinking Water Act (SDWA) data including:
    - Water system facility information
    - Violations and enforcement actions
    - Compliance status
    - Population served
    - Contaminant data

    No API key required for EPA ECHO.

    Attributes:
        base_url (str): Base URL for ECHO API
        session (requests.Session): HTTP session for API calls

    Example:
        >>> connector = WaterQualityConnector()
        >>> systems = connector.get_water_systems_by_state("CA")
        >>> print(f"Found {len(systems)} water systems in California")
    """

    # API Configuration
    BASE_URL = "https://data.epa.gov/efservice"
    ECHO_BASE_URL = "https://ofmpub.epa.gov/echo"

    # System type codes
    SYSTEM_TYPES = {
        "CWS": "Community Water System",
        "NTNCWS": "Non-Transient Non-Community Water System",
        "TNCWS": "Transient Non-Community Water System",
    }

    # Violation type codes
    VIOLATION_TYPES = {
        "MCL": "Maximum Contaminant Level",
        "MRDL": "Maximum Residual Disinfectant Level",
        "TT": "Treatment Technique",
        "MR": "Monitoring and Reporting",
        "PN": "Public Notification",
        "OC": "Operator Certification",
    }

    # Contaminant categories
    CONTAMINANT_GROUPS = {
        "INORGANIC": "Inorganic Chemicals",
        "ORGANIC": "Organic Chemicals",
        "MICROBIAL": "Microbial Contaminants",
        "RADIOLOGICAL": "Radionuclides",
        "DBP": "Disinfection Byproducts",
    }

    def __init__(self, **kwargs):
        """
        Initialize Water Quality connector.

        Args:
            **kwargs: Additional arguments passed to BaseConnector
        """
        # EPA ECHO doesn't require an API key
        super().__init__(api_key=None, **kwargs)
        self.base_url = self.BASE_URL
        self.echo_url = self.ECHO_BASE_URL
        self.logger.info("WaterQualityConnector initialized (no API key required)")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration.

        Returns:
            None (EPA ECHO doesn't require API key)
        """
        return None

    def connect(self) -> None:
        """
        Establish connection to EPA ECHO API.

        Raises:
            ConnectionError: If unable to connect to API
        """
        if self.session is not None:
            return

        try:
            self.session = self._init_session()
            # Test connection
            test_url = f"{self.base_url}/SDWA_PUB_WATER_SYSTEMS/ROWS/0:1/JSON"
            response = self.session.get(test_url, timeout=self.timeout)
            response.raise_for_status()
            self.logger.info("Successfully connected to EPA ECHO API")
        except Exception as e:
            self.logger.error(f"Failed to connect to EPA ECHO API: {e}")
            raise ConnectionError(f"Could not connect to EPA ECHO API: {e}")

    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from EPA ECHO API.

        Args:
            endpoint: API endpoint path (required)
            params: Query parameters (optional)

        Returns:
            dict or list: API response data

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

    def get_water_systems_by_state(
        self, state: str, system_type: Optional[str] = None, limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get water systems by state.

        Args:
            state: Two-letter state code (e.g., 'CA', 'NY')
            system_type: System type filter ('CWS', 'NTNCWS', 'TNCWS', or None for all)
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing water system information

        Example:
            >>> connector = WaterQualityConnector()
            >>> ca_systems = connector.get_water_systems_by_state("CA", system_type="CWS")
            >>> print(ca_systems[['PWS_NAME', 'CITY', 'POPULATION_SERVED_COUNT']])
        """
        state = state.upper()
        cache_key = f"systems_state_{state}_{system_type}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached data for state {state}")
            return cached_data

        # Build endpoint
        endpoint = f"SDWA_PUB_WATER_SYSTEMS/PRIMACY_AGENCY_CODE/{state}"
        if system_type:
            endpoint += f"/PWS_TYPE_CODE/{system_type}"
        endpoint += f"/ROWS/0:{limit}/JSON"

        # Fetch data
        self.logger.info(f"Fetching water systems for state: {state}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} water systems for state {state}")
        return df

    def get_system_by_id(self, pwsid: str) -> pd.DataFrame:
        """
        Get detailed information for a specific water system.

        Args:
            pwsid: Public Water System ID (e.g., 'CA1234567')

        Returns:
            pd.DataFrame: DataFrame with system details

        Example:
            >>> connector = WaterQualityConnector()
            >>> system = connector.get_system_by_id("CA1234567")
            >>> print(system['PWS_NAME'].iloc[0])
        """
        cache_key = f"system_detail_{pwsid}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached data for system {pwsid}")
            return cached_data

        # Fetch data
        endpoint = f"SDWA_PUB_WATER_SYSTEMS/PWSID/{pwsid}/JSON"
        self.logger.info(f"Fetching system details for: {pwsid}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        df = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved details for system {pwsid}")
        return df

    def get_violations_by_system(self, pwsid: str, limit: int = 500) -> pd.DataFrame:
        """
        Get SDWA violations for a specific water system.

        Args:
            pwsid: Public Water System ID
            limit: Maximum number of results (default: 500)

        Returns:
            pd.DataFrame: DataFrame containing violation information

        Example:
            >>> connector = WaterQualityConnector()
            >>> violations = connector.get_violations_by_system("CA1234567")
            >>> print(violations[['VIOLATION_CODE', 'VIOLATION_DESC', 'COMPL_STATUS']])
        """
        cache_key = f"violations_{pwsid}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached violations for {pwsid}")
            return cached_data

        # Fetch data
        endpoint = f"SDWA_VIOLATIONS/PWSID/{pwsid}/ROWS/0:{limit}/JSON"
        self.logger.info(f"Fetching violations for system: {pwsid}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} violations for system {pwsid}")
        return df

    def get_systems_by_city(self, city: str, state: str, limit: int = 100) -> pd.DataFrame:
        """
        Get water systems by city and state.

        Args:
            city: City name
            state: Two-letter state code
            limit: Maximum number of results (default: 100)

        Returns:
            pd.DataFrame: DataFrame containing water system information

        Example:
            >>> connector = WaterQualityConnector()
            >>> systems = connector.get_systems_by_city("San Francisco", "CA")
            >>> print(f"Found {len(systems)} water systems")
        """
        city = city.upper().replace(" ", "%20")
        state = state.upper()
        cache_key = f"systems_city_{city}_{state}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached data for {city}, {state}")
            return cached_data

        # Fetch data
        endpoint = f"SDWA_PUB_WATER_SYSTEMS/CITY_NAME/{city}/PRIMACY_AGENCY_CODE/{state}/ROWS/0:{limit}/JSON"
        self.logger.info(f"Fetching water systems for: {city}, {state}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} systems for {city}, {state}")
        return df

    def get_systems_by_zip(self, zip_code: str, limit: int = 100) -> pd.DataFrame:
        """
        Get water systems by ZIP code.

        Args:
            zip_code: 5-digit ZIP code
            limit: Maximum number of results (default: 100)

        Returns:
            pd.DataFrame: DataFrame containing water system information

        Example:
            >>> connector = WaterQualityConnector()
            >>> systems = connector.get_systems_by_zip("94102")
            >>> print(systems[['PWS_NAME', 'CITY_NAME']])
        """
        cache_key = f"systems_zip_{zip_code}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached data for ZIP {zip_code}")
            return cached_data

        # Fetch data
        endpoint = f"SDWA_PUB_WATER_SYSTEMS/ZIP_CODE/{zip_code}/ROWS/0:{limit}/JSON"
        self.logger.info(f"Fetching water systems for ZIP: {zip_code}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} systems for ZIP {zip_code}")
        return df

    def get_community_water_systems(self, state: Optional[str] = None, limit: int = 1000) -> pd.DataFrame:
        """
        Get Community Water Systems (CWS).

        Args:
            state: Optional two-letter state code to filter by
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing CWS information

        Example:
            >>> connector = WaterQualityConnector()
            >>> cws_systems = connector.get_community_water_systems("CA")
            >>> print(f"Community water systems in CA: {len(cws_systems)}")
        """
        cache_key = f"cws_systems_{state}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached CWS data")
            return cached_data

        # Build endpoint
        if state:
            endpoint = f"SDWA_PUB_WATER_SYSTEMS/PRIMACY_AGENCY_CODE/{state.upper()}/PWS_TYPE_CODE/CWS/ROWS/0:{limit}/JSON"
        else:
            endpoint = f"SDWA_PUB_WATER_SYSTEMS/PWS_TYPE_CODE/CWS/ROWS/0:{limit}/JSON"

        # Fetch data
        self.logger.info(f"Fetching CWS systems{f' for {state}' if state else ''}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} CWS systems")
        return df

    def get_health_based_violations(self, state: str, limit: int = 500) -> pd.DataFrame:
        """
        Get health-based violations (MCL, MRDL, TT) by state.

        Args:
            state: Two-letter state code
            limit: Maximum number of results (default: 500)

        Returns:
            pd.DataFrame: DataFrame containing health-based violations

        Example:
            >>> connector = WaterQualityConnector()
            >>> violations = connector.get_health_based_violations("CA")
            >>> print(violations['VIOLATION_CODE'].value_counts())
        """
        cache_key = f"health_violations_{state}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached health violations for {state}")
            return cached_data

        # Fetch data - query for health-based violation categories
        state = state.upper()
        endpoint = f"SDWA_VIOLATIONS/PRIMACY_AGENCY_CODE/{state}/IS_HEALTH_BASED_IND/Y/ROWS/0:{limit}/JSON"
        
        self.logger.info(f"Fetching health-based violations for: {state}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} health-based violations for {state}")
        return df

    def search_systems_by_name(self, system_name: str, state: Optional[str] = None, limit: int = 100) -> pd.DataFrame:
        """
        Search for water systems by name (partial match).

        Args:
            system_name: System name to search for
            state: Optional two-letter state code to filter
            limit: Maximum number of results (default: 100)

        Returns:
            pd.DataFrame: DataFrame containing matching systems

        Example:
            >>> connector = WaterQualityConnector()
            >>> systems = connector.search_systems_by_name("Municipal", state="CA")
            >>> print(systems[['PWS_NAME', 'CITY_NAME', 'POPULATION_SERVED_COUNT']])
        """
        cache_key = f"search_name_{system_name}_{state}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached search results for '{system_name}'")
            return cached_data

        # Fetch data (using BEGINNING operator in Envirofacts)
        system_name_encoded = system_name.upper().replace(" ", "%20")
        
        if state:
            endpoint = f"SDWA_PUB_WATER_SYSTEMS/PWS_NAME/BEGINNING/{system_name_encoded}/PRIMACY_AGENCY_CODE/{state.upper()}/ROWS/0:{limit}/JSON"
        else:
            endpoint = f"SDWA_PUB_WATER_SYSTEMS/PWS_NAME/BEGINNING/{system_name_encoded}/ROWS/0:{limit}/JSON"
        
        self.logger.info(f"Searching for systems matching: {system_name}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Found {len(df)} systems matching '{system_name}'")
        return df

    def get_enforcement_actions(self, pwsid: str, limit: int = 100) -> pd.DataFrame:
        """
        Get enforcement actions for a specific water system.

        Args:
            pwsid: Public Water System ID
            limit: Maximum number of results (default: 100)

        Returns:
            pd.DataFrame: DataFrame containing enforcement actions

        Example:
            >>> connector = WaterQualityConnector()
            >>> actions = connector.get_enforcement_actions("CA1234567")
            >>> print(actions[['ENFORCEMENT_ID', 'ENFORCEMENT_DATE', 'ENFORCEMENT_TYPE']])
        """
        cache_key = f"enforcement_{pwsid}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached enforcement actions for {pwsid}")
            return cached_data

        # Fetch data
        endpoint = f"SDWA_ENFORCEMENTS/PWSID/{pwsid}/ROWS/0:{limit}/JSON"
        self.logger.info(f"Fetching enforcement actions for: {pwsid}")
        data = self.fetch(endpoint=endpoint)

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data]) if data else pd.DataFrame()

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} enforcement actions for {pwsid}")
        return df

    def get_system_population_served(self, pwsid: str) -> Optional[int]:
        """
        Get the population served by a water system.

        Args:
            pwsid: Public Water System ID

        Returns:
            int: Population served, or None if not available

        Example:
            >>> connector = WaterQualityConnector()
            >>> population = connector.get_system_population_served("CA1234567")
            >>> if population:
            ...     print(f"Population served: {population:,}")
        """
        system_data = self.get_system_by_id(pwsid)
        
        if system_data.empty:
            return None
            
        pop = system_data.get('POPULATION_SERVED_COUNT', pd.Series([None])).iloc[0]
        
        return int(pop) if pop is not None else None

    def close(self):
        """Close HTTP session."""
        if self.session:
            self.session.close()
            self.session = None
            self.logger.info("HTTP session closed")
