"""
OSHA (Occupational Safety and Health Administration) Data Connector.

This connector provides access to OSHA's workplace safety and health data,
including inspections, violations, accidents, and compliance information.

Data Sources:
    - OSHA Enforcement Data: Inspection and violation records
    - Accident Investigation Data: Workplace accidents and injuries
    - Establishment Data: Employer information
    - Standards and Regulations: OSHA compliance standards

API Documentation:
    https://www.osha.gov/data

Usage:
    ```python
    from krl_data_connectors.labor import OSHAConnector
    
    # Initialize connector
    connector = OSHAConnector()
    
    # Get recent inspections in California
    inspections = connector.get_inspections(
        state='CA',
        start_date='2024-01-01',
        end_date='2024-12-31',
        limit=100
    )
    
    # Get violations by inspection number
    violations = connector.get_violations(
        inspection_number='123456789',
        severity='serious',
        limit=50
    )
    
    # Get workplace accidents
    accidents = connector.get_accidents(
        state='TX',
        start_date='2024-01-01',
        limit=100
    )
    
    # Get industry statistics by NAICS code
    stats = connector.get_industry_statistics(
        naics_code='23',
        year=2023
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

# OSHA Constants
VIOLATION_TYPES = {
    'serious': 'Serious Violation',
    'willful': 'Willful Violation',
    'repeat': 'Repeat Violation',
    'other': 'Other-than-Serious Violation',
    'failure_to_abate': 'Failure to Abate'
}

INSPECTION_TYPES = {
    'complaint': 'Complaint',
    'accident': 'Accident',
    'referral': 'Referral',
    'monitoring': 'Monitoring',
    'planned': 'Planned',
    'followup': 'Follow-up'
}

CASE_STATUS = {
    'open': 'Open',
    'closed': 'Closed',
    'appealed': 'Appealed',
    'settled': 'Settled'
}


class OSHAConnector(BaseConnector):
    """
    Connector for OSHA (Occupational Safety and Health Administration) data.
    
    Provides access to workplace safety inspections, violations, accidents,
    and compliance information through OSHA's public data APIs.
    
    Attributes:
        BASE_URL (str): Base URL for OSHA website
        API_BASE_URL (str): Base URL for OSHA data API
    """
    
    BASE_URL = "https://www.osha.gov"
    API_BASE_URL = "https://data.osha.gov/api/v1"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize the OSHA connector.
        
        Args:
            api_key: Optional API key (OSHA data is public, no key required)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            cache_dir: Optional directory for caching responses
        """
        self._osha_api_key = api_key
        super().__init__(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            cache_dir=cache_dir
        )
        logger.info("OSHAConnector initialized")
    
    def _get_api_key(self) -> Optional[str]:
        """
        Get the API key (OSHA data is public, no key required).
        
        Returns:
            None (no API key required for OSHA data)
        """
        return self._osha_api_key
    
    def connect(self) -> bool:
        """
        Establish connection to OSHA API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.API_BASE_URL}/inspections",
                params={'size': 1},
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info("Successfully connected to OSHA API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to OSHA API: {e}")
            return False
    
    def fetch(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetch data from OSHA API.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        url = f"{self.API_BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def get_inspections(
        self,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        inspection_type: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get OSHA inspection records.
        
        Args:
            state: Optional two-letter state code (e.g., 'CA', 'TX')
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            inspection_type: Optional inspection type ('complaint', 'accident', 'planned', etc.)
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing inspection records
        """
        params = {'size': limit}
        
        filters = []
        if state:
            filters.append(f"site_state:'{state}'")
        if start_date:
            filters.append(f"open_date:[{start_date} TO *]")
        if end_date:
            filters.append(f"open_date:[* TO {end_date}]")
        if inspection_type and inspection_type in INSPECTION_TYPES:
            filters.append(f"insp_type:'{inspection_type}'")
        
        if filters:
            params['search'] = ' AND '.join(filters)
        
        try:
            data = self.fetch('inspections', params)
            
            if not data or 'data' not in data:
                logger.warning("No inspection data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} inspection records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching inspections: {e}")
            return pd.DataFrame()
    
    def get_violations(
        self,
        inspection_number: Optional[str] = None,
        severity: Optional[str] = None,
        standard: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get OSHA violation records.
        
        Args:
            inspection_number: Optional inspection number
            severity: Optional violation severity ('serious', 'willful', 'repeat', etc.)
            standard: Optional OSHA standard number (e.g., '1910.147')
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing violation records
        """
        params = {'size': limit}
        
        filters = []
        if inspection_number:
            filters.append(f"inspection_nr:{inspection_number}")
        if severity and severity in VIOLATION_TYPES:
            filters.append(f"gravity:'{severity}'")
        if standard:
            filters.append(f"standard:'{standard}'")
        
        if filters:
            params['search'] = ' AND '.join(filters)
        
        try:
            data = self.fetch('violations', params)
            
            if not data or 'data' not in data:
                logger.warning("No violation data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} violation records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching violations: {e}")
            return pd.DataFrame()
    
    def get_accidents(
        self,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get OSHA accident and injury records.
        
        Args:
            state: Optional two-letter state code
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            severity: Optional severity level ('fatality', 'catastrophe', etc.)
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing accident records
        """
        params = {'size': limit}
        
        filters = []
        if state:
            filters.append(f"state:'{state}'")
        if start_date:
            filters.append(f"event_date:[{start_date} TO *]")
        if end_date:
            filters.append(f"event_date:[* TO {end_date}]")
        if severity:
            filters.append(f"degree:'{severity}'")
        
        if filters:
            params['search'] = ' AND '.join(filters)
        
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
    
    def get_establishments(
        self,
        state: Optional[str] = None,
        industry: Optional[str] = None,
        naics_code: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get OSHA establishment (employer) data.
        
        Args:
            state: Optional two-letter state code
            industry: Optional industry description
            naics_code: Optional NAICS code
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing establishment records
        """
        params = {'size': limit}
        
        filters = []
        if state:
            filters.append(f"site_state:'{state}'")
        if industry:
            filters.append(f"sic_description:*{industry}*")
        if naics_code:
            filters.append(f"naics_code:{naics_code}")
        
        if filters:
            params['search'] = ' AND '.join(filters)
        
        try:
            data = self.fetch('establishments', params)
            
            if not data or 'data' not in data:
                logger.warning("No establishment data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} establishment records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching establishments: {e}")
            return pd.DataFrame()
    
    def get_industry_statistics(
        self,
        naics_code: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get OSHA industry-level statistics.
        
        Args:
            naics_code: Optional NAICS code (2-6 digits)
            year: Optional year
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing industry statistics
        """
        params = {'size': limit}
        
        filters = []
        if naics_code:
            filters.append(f"naics_code:{naics_code}*")
        if year:
            filters.append(f"year:{year}")
        
        if filters:
            params['search'] = ' AND '.join(filters)
        
        try:
            data = self.fetch('statistics', params)
            
            if not data or 'data' not in data:
                logger.warning("No statistics data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} statistics records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching industry statistics: {e}")
            return pd.DataFrame()
    
    def get_standards(
        self,
        standard_number: Optional[str] = None,
        standard_type: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get OSHA standards and regulations.
        
        Args:
            standard_number: Optional standard number (e.g., '1910.147')
            standard_type: Optional standard type ('general', 'construction', etc.)
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing OSHA standards
        """
        params = {'size': limit}
        
        filters = []
        if standard_number:
            filters.append(f"standard:'{standard_number}'")
        if standard_type:
            filters.append(f"part:'{standard_type}'")
        
        if filters:
            params['search'] = ' AND '.join(filters)
        
        try:
            data = self.fetch('standards', params)
            
            if not data or 'data' not in data:
                logger.warning("No standards data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} standards")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching standards: {e}")
            return pd.DataFrame()
    
    def get_compliance_actions(
        self,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        action_type: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get OSHA compliance assistance actions.
        
        Args:
            state: Optional two-letter state code
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            action_type: Optional action type
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing compliance actions
        """
        params = {'size': limit}
        
        filters = []
        if state:
            filters.append(f"state:'{state}'")
        if start_date:
            filters.append(f"action_date:[{start_date} TO *]")
        if end_date:
            filters.append(f"action_date:[* TO {end_date}]")
        if action_type:
            filters.append(f"action_type:'{action_type}'")
        
        if filters:
            params['search'] = ' AND '.join(filters)
        
        try:
            data = self.fetch('compliance', params)
            
            if not data or 'data' not in data:
                logger.warning("No compliance data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} compliance actions")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching compliance actions: {e}")
            return pd.DataFrame()
    
    def get_enforcement_cases(
        self,
        case_number: Optional[str] = None,
        state: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get OSHA enforcement case data.
        
        Args:
            case_number: Optional case number
            state: Optional two-letter state code
            status: Optional case status ('open', 'closed', 'appealed', etc.)
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing enforcement cases
        """
        params = {'size': limit}
        
        filters = []
        if case_number:
            filters.append(f"case_number:'{case_number}'")
        if state:
            filters.append(f"state:'{state}'")
        if status and status in CASE_STATUS:
            filters.append(f"status:'{status}'")
        
        if filters:
            params['search'] = ' AND '.join(filters)
        
        try:
            data = self.fetch('enforcement', params)
            
            if not data or 'data' not in data:
                logger.warning("No enforcement data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} enforcement cases")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching enforcement cases: {e}")
            return pd.DataFrame()
    
    def get_fatalities(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        industry: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get workplace fatality records.
        
        Args:
            state: Optional two-letter state code
            year: Optional year
            industry: Optional industry description
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing fatality records
        """
        params = {'size': limit}
        
        filters = []
        if state:
            filters.append(f"state:'{state}'")
        if year:
            filters.append(f"event_date:[{year}-01-01 TO {year}-12-31]")
        if industry:
            filters.append(f"industry:*{industry}*")
        
        if filters:
            params['search'] = ' AND '.join(filters)
        
        try:
            data = self.fetch('fatalities', params)
            
            if not data or 'data' not in data:
                logger.warning("No fatality data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} fatality records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching fatalities: {e}")
            return pd.DataFrame()
    
    def get_inspection_history(
        self,
        establishment_name: Optional[str] = None,
        establishment_id: Optional[str] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get inspection history for a specific establishment.
        
        Args:
            establishment_name: Optional establishment name
            establishment_id: Optional establishment ID
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            DataFrame containing inspection history
        """
        params = {'size': limit}
        
        filters = []
        if establishment_name:
            filters.append(f"estab_name:*{establishment_name}*")
        if establishment_id:
            filters.append(f"establishment_id:{establishment_id}")
        
        if filters:
            params['search'] = ' AND '.join(filters)
        
        try:
            data = self.fetch('inspections', params)
            
            if not data or 'data' not in data:
                logger.warning("No inspection history found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            logger.info(f"Retrieved {len(df)} inspection history records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching inspection history: {e}")
            return pd.DataFrame()
    
    def close(self) -> None:
        """
        Close the connector and clean up resources.
        """
        if self.session:
            self.session.close()
            logger.info("OSHAConnector session closed")
