"""
Social Security Administration (SSA) Data Connector.

This module provides access to SSA data including OASDI (Old-Age, Survivors,
and Disability Insurance) statistics, beneficiary information, and program data.

API Documentation:
- SSA Open Data: https://www.ssa.gov/data/
"""

import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..base_connector import BaseConnector


# Benefit program types
PROGRAM_TYPES = {
    'oasi': 'Old-Age and Survivors Insurance',
    'di': 'Disability Insurance',
    'ssi': 'Supplemental Security Income',
    'all': 'All Programs',
}

# Beneficiary types
BENEFICIARY_TYPES = {
    'retired_workers': 'Retired Workers',
    'disabled_workers': 'Disabled Workers',
    'widows': 'Widows and Widowers',
    'spouses': 'Spouses',
    'children': 'Children',
    'survivors': 'Survivors',
    'all': 'All Beneficiaries',
}

# Payment categories
PAYMENT_CATEGORIES = {
    'monthly': 'Monthly Benefits',
    'lump_sum': 'Lump Sum Payments',
    'retirement': 'Retirement Benefits',
    'disability': 'Disability Benefits',
    'survivors': 'Survivors Benefits',
}


class SSAConnector(BaseConnector):
    """
    Connector for Social Security Administration (SSA) data.
    
    Provides access to OASDI statistics, beneficiary information,
    payment data, and program statistics.
    
    Attributes:
        api_url: SSA Open Data API base URL
        
    Example:
        >>> connector = SSAConnector()
        >>> 
        >>> # Get beneficiary statistics
        >>> beneficiaries = connector.get_beneficiary_data(
        ...     program='oasi',
        ...     year=2024,
        ...     state='CA'
        ... )
        >>> 
        >>> # Get payment information
        >>> payments = connector.get_payment_data(
        ...     category='retirement',
        ...     year=2024
        ... )
        >>> 
        >>> connector.close()
    """
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, **kwargs):
        """
        Initialize SSA connector.
        
        Args:
            api_key: Optional API key (not required for SSA APIs)
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseConnector
        """
        self._ssa_api_key = api_key
        
        super().__init__(api_key=api_key, timeout=timeout, **kwargs)
        
        # SSA Open Data API
        self.api_url = "https://www.ssa.gov/open/data"
    
    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for SSA APIs.
        
        Returns:
            API key if available, None otherwise (SSA APIs are public)
        """
        return self._ssa_api_key
    
    def connect(self) -> None:
        """
        Establish connection to SSA data sources.
        
        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return
        
        try:
            self.session = self._init_session()
            self.logger.info("Successfully connected to SSA data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to SSA API: {e}")
            raise ConnectionError(f"Could not connect to SSA API: {e}")
    
    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from SSA APIs.
        
        Args:
            endpoint: API endpoint path (required)
            **kwargs: Additional query parameters
            
        Returns:
            API response data (list or dict)
            
        Raises:
            requests.HTTPError: If API request fails
        """
        endpoint = kwargs.pop('endpoint', None)
        
        if not endpoint:
            raise ValueError("endpoint parameter is required")
        
        if not self.session:
            self.connect()
        
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=kwargs, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            self.logger.error(f"Failed to fetch data from {endpoint}: {e}")
            return {}
    
    def get_beneficiary_data(
        self,
        program: Optional[str] = None,
        beneficiary_type: Optional[str] = None,
        state: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get beneficiary statistics by program, type, and location.
        
        Args:
            program: Program type (oasi, di, ssi, or all)
            beneficiary_type: Type of beneficiary (retired_workers, disabled_workers, etc.)
            state: Two-letter state code
            year: Year (YYYY)
            month: Month (1-12)
            limit: Maximum records to return
            
        Returns:
            DataFrame with beneficiary data
        """
        params = {
            'limit': limit,
        }
        
        if program:
            params['program'] = program.lower()
        
        if beneficiary_type:
            params['beneficiary_type'] = beneficiary_type
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if month:
            params['month'] = str(month)
        
        try:
            response = self.fetch(endpoint='/beneficiaries', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching beneficiary data: {str(e)}")
            return pd.DataFrame()
    
    def get_payment_data(
        self,
        category: Optional[str] = None,
        state: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get payment statistics by category and location.
        
        Args:
            category: Payment category (monthly, retirement, disability, survivors)
            state: Two-letter state code
            year: Year (YYYY)
            month: Month (1-12)
            limit: Maximum records to return
            
        Returns:
            DataFrame with payment data
        """
        params = {
            'limit': limit,
        }
        
        if category:
            params['category'] = category
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if month:
            params['month'] = str(month)
        
        try:
            response = self.fetch(endpoint='/payments', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching payment data: {str(e)}")
            return pd.DataFrame()
    
    def get_disability_data(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        age_group: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get disability insurance statistics.
        
        Args:
            state: Two-letter state code
            year: Year (YYYY)
            age_group: Age group filter
            limit: Maximum records to return
            
        Returns:
            DataFrame with disability data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if age_group:
            params['age_group'] = age_group
        
        try:
            response = self.fetch(endpoint='/disability', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching disability data: {str(e)}")
            return pd.DataFrame()
    
    def get_retirement_data(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        age_group: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get retirement insurance statistics.
        
        Args:
            state: Two-letter state code
            year: Year (YYYY)
            age_group: Age group filter
            limit: Maximum records to return
            
        Returns:
            DataFrame with retirement data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if age_group:
            params['age_group'] = age_group
        
        try:
            response = self.fetch(endpoint='/retirement', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching retirement data: {str(e)}")
            return pd.DataFrame()
    
    def get_survivors_data(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        relationship: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get survivors benefits statistics.
        
        Args:
            state: Two-letter state code
            year: Year (YYYY)
            relationship: Relationship to deceased (widow, child, parent)
            limit: Maximum records to return
            
        Returns:
            DataFrame with survivors data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if relationship:
            params['relationship'] = relationship
        
        try:
            response = self.fetch(endpoint='/survivors', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching survivors data: {str(e)}")
            return pd.DataFrame()
    
    def get_ssi_data(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        recipient_type: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get Supplemental Security Income (SSI) statistics.
        
        Args:
            state: Two-letter state code
            year: Year (YYYY)
            recipient_type: Type of recipient (aged, blind, disabled)
            limit: Maximum records to return
            
        Returns:
            DataFrame with SSI data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if recipient_type:
            params['recipient_type'] = recipient_type
        
        try:
            response = self.fetch(endpoint='/ssi', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching SSI data: {str(e)}")
            return pd.DataFrame()
    
    def get_state_summary(
        self,
        state: str,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get comprehensive state-level summary statistics.
        
        Args:
            state: Two-letter state code (required)
            year: Year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with state summary data
        """
        params = {
            'state': state.upper(),
            'limit': limit,
        }
        
        if year:
            params['year'] = str(year)
        
        try:
            response = self.fetch(endpoint='/state-summary', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching state summary: {str(e)}")
            return pd.DataFrame()
    
    def get_national_summary(
        self,
        year: Optional[int] = None,
        program: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get national-level summary statistics.
        
        Args:
            year: Year (YYYY)
            program: Program type (oasi, di, ssi, or all)
            limit: Maximum records to return
            
        Returns:
            DataFrame with national summary data
        """
        params = {
            'limit': limit,
        }
        
        if year:
            params['year'] = str(year)
        
        if program:
            params['program'] = program.lower()
        
        try:
            response = self.fetch(endpoint='/national-summary', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching national summary: {str(e)}")
            return pd.DataFrame()
    
    def get_monthly_statistics(
        self,
        year: int,
        month: int,
        program: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get monthly program statistics.
        
        Args:
            year: Year (YYYY) - required
            month: Month (1-12) - required
            program: Program type (oasi, di, ssi, or all)
            state: Two-letter state code
            limit: Maximum records to return
            
        Returns:
            DataFrame with monthly statistics
        """
        params = {
            'year': str(year),
            'month': str(month),
            'limit': limit,
        }
        
        if program:
            params['program'] = program.lower()
        
        if state:
            params['state'] = state.upper()
        
        try:
            response = self.fetch(endpoint='/monthly-statistics', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching monthly statistics: {str(e)}")
            return pd.DataFrame()
    
    def get_demographic_data(
        self,
        program: Optional[str] = None,
        age_group: Optional[str] = None,
        gender: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get demographic breakdowns of beneficiaries.
        
        Args:
            program: Program type (oasi, di, ssi, or all)
            age_group: Age group filter
            gender: Gender filter (M, F)
            year: Year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with demographic data
        """
        params = {
            'limit': limit,
        }
        
        if program:
            params['program'] = program.lower()
        
        if age_group:
            params['age_group'] = age_group
        
        if gender:
            params['gender'] = gender.upper()
        
        if year:
            params['year'] = str(year)
        
        try:
            response = self.fetch(endpoint='/demographics', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching demographic data: {str(e)}")
            return pd.DataFrame()
    
    def close(self) -> None:
        """Close the SSA API connection and cleanup resources."""
        if self.session:
            self.session.close()
            self.session = None
        self.logger.info("Connection closed")
