"""
FAA (Federal Aviation Administration) Data Connector.

This connector provides access to FAA aviation safety and regulatory data,
including aircraft registration, accidents, incidents, and airworthiness information.

Data Sources:
    - Aircraft Registry: Aircraft registration database
    - Accident/Incident Data: NTSB aviation safety data
    - Airport Data: Airport facilities and operations
    - Airmen Certification: Pilot and crew certification data
    - Airworthiness Directives: Safety directives and compliance

API Documentation:
    https://www.faa.gov/data_research/

Usage:
    ```python
    from krl_data_connectors.transportation import FAAConnector
    
    # Initialize connector
    connector = FAAConnector()
    
    # Get aircraft by N-number
    aircraft = connector.get_aircraft_registry(
        n_number='N12345',
        limit=100
    )
    
    # Get recent accidents
    accidents = connector.get_accidents(
        start_date='2024-01-01',
        end_date='2024-12-31',
        state='CA',
        limit=50
    )
    
    # Get airports in a state
    airports = connector.get_airports(
        state='TX',
        type='public',
        limit=100
    )
    
    # Get airworthiness directives
    ads = connector.get_airworthiness_directives(
        aircraft_type='Boeing 737',
        start_date='2024-01-01',
        limit=50
    )
    
    # Clean up
    connector.close()
    ```

Author: KR Analytics Suite
Date: 2024-10-21
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from ..base_connector import BaseConnector

# Configure logging
logger = logging.getLogger(__name__)

# FAA Constants
AIRCRAFT_CATEGORIES = {
    '1': 'Land',
    '2': 'Sea',
    '3': 'Amphibian'
}

AIRPORT_TYPES = {
    'public': 'Publicly-owned',
    'private': 'Privately-owned',
    'military': 'Military',
    'heliport': 'Heliport'
}

CERTIFICATION_TYPES = {
    'student': 'Student Pilot',
    'private': 'Private Pilot',
    'commercial': 'Commercial Pilot',
    'atp': 'Airline Transport Pilot',
    'cfi': 'Certified Flight Instructor',
    'mechanic': 'Mechanic',
    'repairman': 'Repairman'
}


class FAAConnector(BaseConnector):
    """
    Connector for FAA (Federal Aviation Administration) data.
    
    Provides access to aviation safety data including aircraft registry,
    accidents, incidents, airports, and airworthiness information.
    
    Attributes:
        BASE_URL (str): Base URL for FAA website
        API_BASE_URL (str): Base URL for FAA data API
    """
    
    BASE_URL = "https://www.faa.gov"
    API_BASE_URL = "https://api.faa.gov/v1"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize the FAA connector.
        
        Args:
            api_key: Optional API key (some FAA data requires authentication)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            cache_dir: Optional directory for caching responses
        """
        self._faa_api_key = api_key
        super().__init__(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            cache_dir=cache_dir
        )
        logger.info("FAAConnector initialized")
    
    def _get_api_key(self) -> Optional[str]:
        """
        Get the API key for FAA data access.
        
        Returns:
            API key if available, None otherwise
        """
        return self._faa_api_key
    
    def connect(self) -> bool:
        """
        Establish connection to FAA API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.API_BASE_URL}/aircraft",
                params={'limit': 1},
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info("Successfully connected to FAA API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to FAA API: {e}")
            return False
    
    def fetch(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetch data from FAA API.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        url = f"{self.API_BASE_URL}/{endpoint}"
        if self._faa_api_key:
            if params is None:
                params = {}
            params['api_key'] = self._faa_api_key
        
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def get_aircraft_registry(
        self,
        n_number: Optional[str] = None,
        state: Optional[str] = None,
        aircraft_type: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get FAA aircraft registration records.
        
        Args:
            n_number: Optional N-number (aircraft registration number)
            state: Optional two-letter state code
            aircraft_type: Optional aircraft type/model
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing aircraft registration records
        """
        params = {'limit': limit}
        
        if n_number:
            params['n_number'] = n_number
        if state:
            params['state'] = state
        if aircraft_type:
            params['aircraft_type'] = aircraft_type
        
        try:
            data = self.fetch('aircraft', params)
            
            if not data or 'data' not in data:
                logger.warning("No aircraft registry data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} aircraft records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching aircraft registry: {e}")
            return pd.DataFrame()
    
    def get_accidents(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        state: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get FAA/NTSB accident records.
        
        Args:
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            state: Optional two-letter state code
            severity: Optional severity level ('fatal', 'serious', 'minor')
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing accident records
        """
        params = {'limit': limit}
        
        if start_date:
            params['event_date_gte'] = start_date
        if end_date:
            params['event_date_lte'] = end_date
        if state:
            params['state'] = state
        if severity:
            params['severity'] = severity
        
        try:
            data = self.fetch('accidents', params)
            
            if not data or 'data' not in data:
                logger.warning("No accident data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} accident records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching accidents: {e}")
            return pd.DataFrame()
    
    def get_incidents(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        severity: Optional[str] = None,
        incident_type: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get FAA incident reports.
        
        Args:
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            severity: Optional severity level
            incident_type: Optional incident type
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing incident records
        """
        params = {'limit': limit}
        
        if start_date:
            params['event_date_gte'] = start_date
        if end_date:
            params['event_date_lte'] = end_date
        if severity:
            params['severity'] = severity
        if incident_type:
            params['type'] = incident_type
        
        try:
            data = self.fetch('incidents', params)
            
            if not data or 'data' not in data:
                logger.warning("No incident data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} incident records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching incidents: {e}")
            return pd.DataFrame()
    
    def get_airports(
        self,
        state: Optional[str] = None,
        airport_type: Optional[str] = None,
        facility_name: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get FAA airport information.
        
        Args:
            state: Optional two-letter state code
            airport_type: Optional airport type ('public', 'private', 'military', 'heliport')
            facility_name: Optional facility name search
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing airport records
        """
        params = {'limit': limit}
        
        if state:
            params['state'] = state
        if airport_type and airport_type in AIRPORT_TYPES:
            params['type'] = airport_type
        if facility_name:
            params['facility_name'] = facility_name
        
        try:
            data = self.fetch('airports', params)
            
            if not data or 'data' not in data:
                logger.warning("No airport data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} airport records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching airports: {e}")
            return pd.DataFrame()
    
    def get_airmen_certifications(
        self,
        certification_type: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get FAA airmen certification records.
        
        Args:
            certification_type: Optional certification type ('student', 'private', 'commercial', etc.)
            state: Optional two-letter state code
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing airmen certification records
        """
        params = {'limit': limit}
        
        if certification_type and certification_type in CERTIFICATION_TYPES:
            params['cert_type'] = certification_type
        if state:
            params['state'] = state
        
        try:
            data = self.fetch('airmen', params)
            
            if not data or 'data' not in data:
                logger.warning("No airmen certification data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} airmen records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching airmen certifications: {e}")
            return pd.DataFrame()
    
    def get_airworthiness_directives(
        self,
        aircraft_type: Optional[str] = None,
        start_date: Optional[str] = None,
        ad_number: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get FAA Airworthiness Directives (ADs).
        
        Args:
            aircraft_type: Optional aircraft type/model
            start_date: Optional start date (YYYY-MM-DD)
            ad_number: Optional AD number
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing airworthiness directives
        """
        params = {'limit': limit}
        
        if aircraft_type:
            params['aircraft_type'] = aircraft_type
        if start_date:
            params['effective_date_gte'] = start_date
        if ad_number:
            params['ad_number'] = ad_number
        
        try:
            data = self.fetch('airworthiness', params)
            
            if not data or 'data' not in data:
                logger.warning("No airworthiness directive data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} airworthiness directives")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching airworthiness directives: {e}")
            return pd.DataFrame()
    
    def get_enforcement_actions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        action_type: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get FAA enforcement action records.
        
        Args:
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            action_type: Optional action type
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing enforcement actions
        """
        params = {'limit': limit}
        
        if start_date:
            params['action_date_gte'] = start_date
        if end_date:
            params['action_date_lte'] = end_date
        if action_type:
            params['action_type'] = action_type
        
        try:
            data = self.fetch('enforcement', params)
            
            if not data or 'data' not in data:
                logger.warning("No enforcement action data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} enforcement actions")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching enforcement actions: {e}")
            return pd.DataFrame()
    
    def get_service_difficulty_reports(
        self,
        aircraft_type: Optional[str] = None,
        part_name: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get Service Difficulty Reports (SDRs).
        
        Args:
            aircraft_type: Optional aircraft type/model
            part_name: Optional part name
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing service difficulty reports
        """
        params = {'limit': limit}
        
        if aircraft_type:
            params['aircraft_type'] = aircraft_type
        if part_name:
            params['part_name'] = part_name
        
        try:
            data = self.fetch('sdr', params)
            
            if not data or 'data' not in data:
                logger.warning("No SDR data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} service difficulty reports")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching service difficulty reports: {e}")
            return pd.DataFrame()
    
    def get_maintenance_records(
        self,
        aircraft_id: Optional[str] = None,
        n_number: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get aircraft maintenance records.
        
        Args:
            aircraft_id: Optional aircraft ID
            n_number: Optional N-number
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing maintenance records
        """
        params = {'limit': limit}
        
        if aircraft_id:
            params['aircraft_id'] = aircraft_id
        if n_number:
            params['n_number'] = n_number
        
        try:
            data = self.fetch('maintenance', params)
            
            if not data or 'data' not in data:
                logger.warning("No maintenance records found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} maintenance records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching maintenance records: {e}")
            return pd.DataFrame()
    
    def get_flight_standards_data(
        self,
        district: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get FAA Flight Standards District Office (FSDO) data.
        
        Args:
            district: Optional district office code
            category: Optional data category
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing flight standards data
        """
        params = {'limit': limit}
        
        if district:
            params['district'] = district
        if category:
            params['category'] = category
        
        try:
            data = self.fetch('flight_standards', params)
            
            if not data or 'data' not in data:
                logger.warning("No flight standards data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} flight standards records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching flight standards data: {e}")
            return pd.DataFrame()
    
    def close(self) -> None:
        """
        Close the connector and clean up resources.
        """
        if self.session:
            self.session.close()
            logger.info("FAAConnector session closed")
