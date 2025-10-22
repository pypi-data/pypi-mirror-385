# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Office for Victims of Crime (OVC) Connector for KRL Data Connectors.

This connector provides access to victim services and compensation data from the
U.S. Department of Justice Office for Victims of Crime.

Data Sources:
    - Victim compensation program statistics
    - Victim assistance program data
    - Crime victim demographics
    - Service utilization statistics
    - Grant funding information
    - State program performance
    - Victim rights implementation

API Documentation:
    https://ovc.ojp.gov/data

Connector Type:
    REST API connector with caching

Authentication:
    No API key required (public data access)

Example Usage:
    ```python
    from krl_data_connectors.crime.victims_of_crime_connector import VictimsOfCrimeConnector

    # Initialize connector
    connector = VictimsOfCrimeConnector()

    # Get compensation data
    compensation = connector.get_compensation_data(year=2023, state="CA")

    # Get victim assistance programs
    programs = connector.get_assistance_programs(state="NY")

    # Get victim demographics
    demographics = connector.get_victim_demographics(year=2023)

    # Close connection
    connector.close()
    ```

Dependencies:
    - pandas: For data manipulation
    - requests: For HTTP requests
    - BaseConnector: For connection management and caching

Author: KR-Labs
License: Apache-2.0
"""

import logging
from typing import Any, Dict, Optional

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)


# Data type constants
CRIME_TYPES = {
    "VIOLENT": "Violent Crime",
    "PROPERTY": "Property Crime",
    "ASSAULT": "Assault",
    "ROBBERY": "Robbery",
    "SEXUAL_ASSAULT": "Sexual Assault",
    "DOMESTIC_VIOLENCE": "Domestic Violence",
    "CHILD_ABUSE": "Child Abuse",
    "ELDER_ABUSE": "Elder Abuse",
    "HUMAN_TRAFFICKING": "Human Trafficking",
    "HOMICIDE": "Homicide",
    "DUI": "DUI/DWI",
    "OTHER": "Other Crime",
}

SERVICE_TYPES = {
    "COUNSELING": "Mental Health Counseling",
    "LEGAL": "Legal Assistance",
    "MEDICAL": "Medical Services",
    "SHELTER": "Emergency Shelter",
    "ADVOCACY": "Victim Advocacy",
    "TRANSPORTATION": "Transportation",
    "FINANCIAL": "Financial Assistance",
    "CASE_MANAGEMENT": "Case Management",
    "INTERPRETATION": "Interpretation Services",
    "OTHER": "Other Services",
}

COMPENSATION_TYPES = {
    "MEDICAL": "Medical Expenses",
    "COUNSELING": "Counseling Expenses",
    "LOST_WAGES": "Lost Wages",
    "FUNERAL": "Funeral Expenses",
    "REHABILITATION": "Rehabilitation",
    "REPLACEMENT_SERVICES": "Replacement Services",
    "CRIME_SCENE_CLEANUP": "Crime Scene Cleanup",
    "OTHER": "Other Compensation",
}


class VictimsOfCrimeConnector(BaseConnector):
    """
    Connector for Office for Victims of Crime data.

    This connector retrieves victim services, compensation programs, and
    victimization statistics from the OVC public data API.

    Attributes:
        BASE_URL: Base URL for OVC website
        API_BASE_URL: Base URL for OVC data API
    """

    BASE_URL = "https://ovc.ojp.gov"
    API_BASE_URL = "https://ovc.ojp.gov/api/data"

    def __init__(self, timeout: int = 30, **kwargs):
        """
        Initialize the VictimsOfCrimeConnector.

        Args:
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseConnector

        Example:
            >>> connector = VictimsOfCrimeConnector(timeout=60)
        """
        super().__init__(timeout=timeout, **kwargs)
        self.api_url = self.API_BASE_URL
        logger.info("VictimsOfCrimeConnector initialized (no API key required)")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for OVC API.

        OVC data is publicly accessible and does not require authentication.

        Returns:
            None (no API key required)
        """
        return None

    def connect(self) -> None:
        """
        Establish connection to OVC data sources.

        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return

        try:
            self.session = self._init_session()
            self.logger.info("Successfully connected to OVC data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to OVC: {e}")
            raise ConnectionError(f"Could not connect to OVC: {e}")

    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from OVC API.

        Args:
            endpoint: API endpoint path (required)
            **kwargs: Additional query parameters

        Returns:
            DataFrame: Query results

        Raises:
            requests.HTTPError: If API request fails
        """
        endpoint = kwargs.pop('endpoint', None)
        
        if not endpoint:
            raise ValueError("endpoint parameter is required")
        
        if not self.session:
            self.connect()

        url = f"{self.api_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=kwargs, timeout=self.timeout)
            response.raise_for_status()
            
            # Try JSON first
            try:
                data = response.json()
            except ValueError:
                # Return empty dataframe if no JSON
                return pd.DataFrame()

            # Convert to DataFrame
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                # Handle different response structures
                if 'data' in data:
                    return pd.DataFrame(data['data'])
                elif 'results' in data:
                    return pd.DataFrame(data['results'])
                else:
                    return pd.DataFrame([data])
            else:
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Failed to fetch data from {endpoint}: {e}")
            # Return empty DataFrame on error
            return pd.DataFrame()

    def get_compensation_data(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None,
        crime_type: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get victim compensation program data.

        Args:
            year: Year for data (e.g., 2023)
            state: State code (e.g., "CA")
            crime_type: Type of crime (use CRIME_TYPES constants)
            limit: Maximum number of records

        Returns:
            DataFrame with compensation data

        Example:
            >>> connector = VictimsOfCrimeConnector()
            >>> data = connector.get_compensation_data(year=2023, state="CA")
        """
        params: Dict[str, Any] = {"limit": limit}
        if year:
            params["year"] = year
        if state:
            params["state"] = state.upper()
        if crime_type:
            params["crime_type"] = crime_type

        logger.info(f"Fetching compensation data: {params}")
        return self.fetch(endpoint="compensation", **params)

    def get_assistance_programs(
        self,
        state: Optional[str] = None,
        service_type: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get victim assistance program information.

        Args:
            state: State code (e.g., "NY")
            service_type: Type of service (use SERVICE_TYPES constants)
            limit: Maximum number of records

        Returns:
            DataFrame with assistance program data

        Example:
            >>> connector = VictimsOfCrimeConnector()
            >>> programs = connector.get_assistance_programs(state="NY")
        """
        params: Dict[str, Any] = {"limit": limit}
        if state:
            params["state"] = state.upper()
        if service_type:
            params["service_type"] = service_type

        logger.info(f"Fetching assistance programs: {params}")
        return self.fetch(endpoint="assistance", **params)

    def get_victim_demographics(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None,
        age_group: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get victim demographic information.

        Args:
            year: Year for data
            state: State code
            age_group: Age group filter
            limit: Maximum number of records

        Returns:
            DataFrame with demographic data

        Example:
            >>> connector = VictimsOfCrimeConnector()
            >>> demographics = connector.get_victim_demographics(year=2023)
        """
        params: Dict[str, Any] = {"limit": limit}
        if year:
            params["year"] = year
        if state:
            params["state"] = state.upper()
        if age_group:
            params["age_group"] = age_group

        logger.info(f"Fetching victim demographics: {params}")
        return self.fetch(endpoint="demographics", **params)

    def get_service_utilization(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None,
        service_type: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get service utilization statistics.

        Args:
            year: Year for data
            state: State code
            service_type: Type of service (use SERVICE_TYPES constants)
            limit: Maximum number of records

        Returns:
            DataFrame with service utilization data

        Example:
            >>> connector = VictimsOfCrimeConnector()
            >>> utilization = connector.get_service_utilization(year=2023)
        """
        params: Dict[str, Any] = {"limit": limit}
        if year:
            params["year"] = year
        if state:
            params["state"] = state.upper()
        if service_type:
            params["service_type"] = service_type

        logger.info(f"Fetching service utilization: {params}")
        return self.fetch(endpoint="services/utilization", **params)

    def get_grant_funding(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None,
        program_type: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get OVC grant funding information.

        Args:
            year: Year for funding data
            state: State code
            program_type: Type of program
            limit: Maximum number of records

        Returns:
            DataFrame with grant funding data

        Example:
            >>> connector = VictimsOfCrimeConnector()
            >>> grants = connector.get_grant_funding(year=2023, state="TX")
        """
        params: Dict[str, Any] = {"limit": limit}
        if year:
            params["year"] = year
        if state:
            params["state"] = state.upper()
        if program_type:
            params["program_type"] = program_type

        logger.info(f"Fetching grant funding: {params}")
        return self.fetch(endpoint="grants", **params)

    def get_state_performance(
        self,
        state: str,
        year: Optional[int] = None,
        metric: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get state program performance metrics.

        Args:
            state: State code (required)
            year: Year for data
            metric: Specific metric to retrieve

        Returns:
            DataFrame with state performance data

        Example:
            >>> connector = VictimsOfCrimeConnector()
            >>> performance = connector.get_state_performance("CA", year=2023)
        """
        params: Dict[str, Any] = {"state": state.upper()}
        if year:
            params["year"] = year
        if metric:
            params["metric"] = metric

        logger.info(f"Fetching state performance: {params}")
        return self.fetch(endpoint="performance/state", **params)

    def get_compensation_by_type(
        self,
        compensation_type: str,
        year: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get compensation data by specific type.

        Args:
            compensation_type: Type of compensation (use COMPENSATION_TYPES constants)
            year: Year for data
            state: State code
            limit: Maximum number of records

        Returns:
            DataFrame with compensation type data

        Example:
            >>> connector = VictimsOfCrimeConnector()
            >>> medical = connector.get_compensation_by_type("MEDICAL", year=2023)
        """
        params: Dict[str, Any] = {
            "compensation_type": compensation_type,
            "limit": limit,
        }
        if year:
            params["year"] = year
        if state:
            params["state"] = state.upper()

        logger.info(f"Fetching compensation by type: {params}")
        return self.fetch(endpoint="compensation/type", **params)

    def get_victim_rights_data(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None,
        right_type: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get victim rights implementation data.

        Args:
            year: Year for data
            state: State code
            right_type: Type of victim right
            limit: Maximum number of records

        Returns:
            DataFrame with victim rights data

        Example:
            >>> connector = VictimsOfCrimeConnector()
            >>> rights = connector.get_victim_rights_data(year=2023)
        """
        params: Dict[str, Any] = {"limit": limit}
        if year:
            params["year"] = year
        if state:
            params["state"] = state.upper()
        if right_type:
            params["right_type"] = right_type

        logger.info(f"Fetching victim rights data: {params}")
        return self.fetch(endpoint="rights", **params)

    def get_compensation_trends(
        self,
        start_year: int,
        end_year: int,
        state: Optional[str] = None,
        crime_type: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get compensation trends over multiple years.

        Args:
            start_year: Starting year (required)
            end_year: Ending year (required)
            state: State code
            crime_type: Type of crime

        Returns:
            DataFrame with compensation trend data

        Example:
            >>> connector = VictimsOfCrimeConnector()
            >>> trends = connector.get_compensation_trends(2015, 2023, state="CA")
        """
        params: Dict[str, Any] = {
            "start_year": start_year,
            "end_year": end_year,
        }
        if state:
            params["state"] = state.upper()
        if crime_type:
            params["crime_type"] = crime_type

        logger.info(f"Fetching compensation trends: {params}")
        return self.fetch(endpoint="trends/compensation", **params)

    def get_services_by_state(
        self,
        state: str,
        year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get all victim services for a specific state.

        Args:
            state: State code (required)
            year: Year for data

        Returns:
            DataFrame with state services data

        Example:
            >>> connector = VictimsOfCrimeConnector()
            >>> services = connector.get_services_by_state("TX", year=2023)
        """
        params: Dict[str, Any] = {"state": state.upper()}
        if year:
            params["year"] = year

        logger.info(f"Fetching services by state: {params}")
        return self.fetch(endpoint="services/state", **params)

    def close(self) -> None:
        """
        Close the HTTP session.

        Example:
            >>> connector = VictimsOfCrimeConnector()
            >>> connector.close()
        """
        if self.session:
            self.session.close()
            self.session = None
            logger.info("HTTP session closed")
