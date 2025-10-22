"""
Administration for Children and Families (ACF) Data Connector.

This module provides access to ACF data including child welfare,
TANF (Temporary Assistance for Needy Families), Head Start,
child support enforcement, and foster care statistics.

API Documentation:
- ACF Data Portal: https://www.acf.hhs.gov/olab/data
"""

import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..base_connector import BaseConnector


# Program types
PROGRAM_TYPES = {
    'tanf': 'Temporary Assistance for Needy Families',
    'head_start': 'Head Start',
    'ccdf': 'Child Care and Development Fund',
    'child_support': 'Child Support Enforcement',
    'foster_care': 'Foster Care',
    'adoption': 'Adoption Assistance',
    'child_welfare': 'Child Welfare Services',
}

# Data categories
DATA_CATEGORIES = {
    'caseload': 'Program Caseload',
    'expenditures': 'Program Expenditures',
    'recipients': 'Program Recipients',
    'outcomes': 'Program Outcomes',
    'demographics': 'Demographic Data',
}

# Child welfare indicators
WELFARE_INDICATORS = {
    'maltreatment': 'Child Maltreatment',
    'investigations': 'CPS Investigations',
    'removals': 'Foster Care Removals',
    'reunifications': 'Family Reunifications',
    'adoptions': 'Adoptions Finalized',
}


class ACFConnector(BaseConnector):
    """
    Connector for Administration for Children and Families (ACF) data.
    
    Provides access to child welfare, TANF, Head Start, child support,
    and foster care statistics.
    
    Attributes:
        api_url: ACF Data Portal API base URL
        
    Example:
        >>> connector = ACFConnector()
        >>> 
        >>> # Get TANF caseload data
        >>> tanf_data = connector.get_tanf_data(
        ...     state='CA',
        ...     year=2024,
        ...     category='caseload'
        ... )
        >>> 
        >>> # Get child welfare statistics
        >>> welfare_data = connector.get_child_welfare_data(
        ...     state='TX',
        ...     indicator='maltreatment'
        ... )
        >>> 
        >>> connector.close()
    """
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, **kwargs):
        """
        Initialize ACF connector.
        
        Args:
            api_key: Optional API key (not required for ACF APIs)
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseConnector
        """
        self._acf_api_key = api_key
        
        super().__init__(api_key=api_key, timeout=timeout, **kwargs)
        
        # ACF Data Portal API
        self.api_url = "https://www.acf.hhs.gov/api"
    
    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for ACF APIs.
        
        Returns:
            API key if available, None otherwise (ACF APIs are public)
        """
        return self._acf_api_key
    
    def connect(self) -> None:
        """
        Establish connection to ACF data sources.
        
        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return
        
        try:
            self.session = self._init_session()
            self.logger.info("Successfully connected to ACF data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to ACF API: {e}")
            raise ConnectionError(f"Could not connect to ACF API: {e}")
    
    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from ACF APIs.
        
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
    
    def get_tanf_data(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        category: Optional[str] = None,
        fiscal_quarter: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get TANF (Temporary Assistance for Needy Families) program data.
        
        Args:
            state: Two-letter state code
            year: Year (YYYY)
            category: Data category (caseload, expenditures, recipients, outcomes)
            fiscal_quarter: Fiscal quarter (1-4)
            limit: Maximum records to return
            
        Returns:
            DataFrame with TANF data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if category:
            params['category'] = category
        
        if fiscal_quarter:
            params['fiscal_quarter'] = str(fiscal_quarter)
        
        try:
            response = self.fetch(endpoint='/tanf', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching TANF data: {str(e)}")
            return pd.DataFrame()
    
    def get_head_start_data(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        program_type: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get Head Start program data.
        
        Args:
            state: Two-letter state code
            year: Year (YYYY)
            program_type: Program type (early_head_start, head_start, both)
            limit: Maximum records to return
            
        Returns:
            DataFrame with Head Start data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if program_type:
            params['program_type'] = program_type
        
        try:
            response = self.fetch(endpoint='/head-start', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching Head Start data: {str(e)}")
            return pd.DataFrame()
    
    def get_child_support_data(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        metric: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get child support enforcement data.
        
        Args:
            state: Two-letter state code
            year: Year (YYYY)
            metric: Metric type (collections, cases, paternity, etc.)
            limit: Maximum records to return
            
        Returns:
            DataFrame with child support data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if metric:
            params['metric'] = metric
        
        try:
            response = self.fetch(endpoint='/child-support', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching child support data: {str(e)}")
            return pd.DataFrame()
    
    def get_foster_care_data(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        data_type: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get foster care statistics.
        
        Args:
            state: Two-letter state code
            year: Year (YYYY)
            data_type: Data type (entries, exits, in_care, demographics)
            limit: Maximum records to return
            
        Returns:
            DataFrame with foster care data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if data_type:
            params['data_type'] = data_type
        
        try:
            response = self.fetch(endpoint='/foster-care', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching foster care data: {str(e)}")
            return pd.DataFrame()
    
    def get_child_welfare_data(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        indicator: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get child welfare services data.
        
        Args:
            state: Two-letter state code
            year: Year (YYYY)
            indicator: Welfare indicator (maltreatment, investigations, removals, etc.)
            limit: Maximum records to return
            
        Returns:
            DataFrame with child welfare data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if indicator:
            params['indicator'] = indicator
        
        try:
            response = self.fetch(endpoint='/child-welfare', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching child welfare data: {str(e)}")
            return pd.DataFrame()
    
    def get_adoption_data(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        adoption_type: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get adoption assistance data.
        
        Args:
            state: Two-letter state code
            year: Year (YYYY)
            adoption_type: Type of adoption (foster, private, international)
            limit: Maximum records to return
            
        Returns:
            DataFrame with adoption data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if adoption_type:
            params['adoption_type'] = adoption_type
        
        try:
            response = self.fetch(endpoint='/adoption', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching adoption data: {str(e)}")
            return pd.DataFrame()
    
    def get_ccdf_data(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        data_category: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get Child Care and Development Fund (CCDF) data.
        
        Args:
            state: Two-letter state code
            year: Year (YYYY)
            data_category: Data category (enrollment, expenditures, providers)
            limit: Maximum records to return
            
        Returns:
            DataFrame with CCDF data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if data_category:
            params['data_category'] = data_category
        
        try:
            response = self.fetch(endpoint='/ccdf', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching CCDF data: {str(e)}")
            return pd.DataFrame()
    
    def get_state_summary(
        self,
        state: str,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get comprehensive state-level summary across all ACF programs.
        
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
    
    def get_national_statistics(
        self,
        year: Optional[int] = None,
        program: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get national-level statistics across ACF programs.
        
        Args:
            year: Year (YYYY)
            program: Program type (tanf, head_start, foster_care, etc.)
            limit: Maximum records to return
            
        Returns:
            DataFrame with national statistics
        """
        params = {
            'limit': limit,
        }
        
        if year:
            params['year'] = str(year)
        
        if program:
            params['program'] = program
        
        try:
            response = self.fetch(endpoint='/national-statistics', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching national statistics: {str(e)}")
            return pd.DataFrame()
    
    def get_program_outcomes(
        self,
        program: str,
        state: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get program outcome measures and performance indicators.
        
        Args:
            program: Program name (required - tanf, head_start, foster_care, etc.)
            state: Two-letter state code
            year: Year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with program outcomes
        """
        params = {
            'program': program,
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        try:
            response = self.fetch(endpoint='/program-outcomes', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching program outcomes: {str(e)}")
            return pd.DataFrame()
    
    def close(self) -> None:
        """Close the ACF API connection and cleanup resources."""
        if self.session:
            self.session.close()
            self.session = None
        self.logger.info("Connection closed")
