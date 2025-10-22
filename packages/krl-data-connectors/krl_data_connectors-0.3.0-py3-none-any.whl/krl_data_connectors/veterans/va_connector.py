"""
Department of Veterans Affairs (VA) Data Connector.

This module provides access to VA data including healthcare facilities,
benefits, disability ratings, claims processing, and veteran statistics.

API Documentation:
- VA Open Data Portal: https://www.va.gov/data/
- VA Facilities API: https://developer.va.gov/
"""

import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..base_connector import BaseConnector


# Facility types
FACILITY_TYPES = {
    'health': 'VA Health Care',
    'benefits': 'Benefits Office',
    'cemetery': 'National Cemetery',
    'vet_center': 'Vet Center',
}

# Benefit types
BENEFIT_TYPES = {
    'compensation': 'Disability Compensation',
    'pension': 'Veterans Pension',
    'education': 'Education Benefits (GI Bill)',
    'home_loan': 'Home Loan Guaranty',
    'vocational': 'Vocational Rehabilitation',
    'burial': 'Burial Benefits',
}

# Healthcare services
HEALTHCARE_SERVICES = {
    'primary_care': 'Primary Care',
    'mental_health': 'Mental Health',
    'emergency': 'Emergency Care',
    'specialty': 'Specialty Care',
    'pharmacy': 'Pharmacy',
}


class VAConnector(BaseConnector):
    """
    Connector for Department of Veterans Affairs (VA) data.
    
    Provides access to VA facilities, benefits, healthcare, disability ratings,
    and claims processing information.
    
    Attributes:
        api_url: VA Open Data API base URL
        
    Example:
        >>> connector = VAConnector()
        >>> 
        >>> # Get VA facilities
        >>> facilities = connector.get_facilities(
        ...     state='CA',
        ...     facility_type='health'
        ... )
        >>> 
        >>> # Get disability compensation data
        >>> compensation = connector.get_benefits_data(
        ...     benefit_type='compensation',
        ...     state='TX'
        ... )
        >>> 
        >>> connector.close()
    """
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, **kwargs):
        """
        Initialize VA connector.
        
        Args:
            api_key: Optional API key for VA APIs
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseConnector
        """
        self._va_api_key = api_key
        
        super().__init__(api_key=api_key, timeout=timeout, **kwargs)
        
        # VA Open Data API
        self.api_url = "https://www.va.gov/api"
    
    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for VA APIs.
        
        Returns:
            API key if available, None otherwise
        """
        return self._va_api_key
    
    def connect(self) -> None:
        """
        Establish connection to VA data sources.
        
        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return
        
        try:
            self.session = self._init_session()
            
            # Add API key to headers if available
            if self._va_api_key:
                self.session.headers['apikey'] = self._va_api_key
            
            self.logger.info("Successfully connected to VA data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to VA API: {e}")
            raise ConnectionError(f"Could not connect to VA API: {e}")
    
    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from VA APIs.
        
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
    
    def get_facilities(
        self,
        state: Optional[str] = None,
        facility_type: Optional[str] = None,
        services: Optional[str] = None,
        zip_code: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get VA facility information.
        
        Args:
            state: Two-letter state code
            facility_type: Type of facility (health, benefits, cemetery, vet_center)
            services: Services offered
            zip_code: ZIP code for proximity search
            limit: Maximum records to return
            
        Returns:
            DataFrame with facility data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if facility_type:
            params['type'] = facility_type
        
        if services:
            params['services'] = services
        
        if zip_code:
            params['zip'] = zip_code
        
        try:
            response = self.fetch(endpoint='/facilities', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching facilities data: {str(e)}")
            return pd.DataFrame()
    
    def get_benefits_data(
        self,
        benefit_type: Optional[str] = None,
        state: Optional[str] = None,
        year: Optional[int] = None,
        fiscal_quarter: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get veterans benefits data.
        
        Args:
            benefit_type: Type of benefit (compensation, pension, education, etc.)
            state: Two-letter state code
            year: Year (YYYY)
            fiscal_quarter: Fiscal quarter (1-4)
            limit: Maximum records to return
            
        Returns:
            DataFrame with benefits data
        """
        params = {
            'limit': limit,
        }
        
        if benefit_type:
            params['benefit_type'] = benefit_type
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        if fiscal_quarter:
            params['fiscal_quarter'] = str(fiscal_quarter)
        
        try:
            response = self.fetch(endpoint='/benefits', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching benefits data: {str(e)}")
            return pd.DataFrame()
    
    def get_disability_ratings(
        self,
        state: Optional[str] = None,
        rating_percentage: Optional[int] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get disability rating statistics.
        
        Args:
            state: Two-letter state code
            rating_percentage: Disability rating percentage (0-100)
            year: Year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with disability rating data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if rating_percentage is not None:
            params['rating'] = str(rating_percentage)
        
        if year:
            params['year'] = str(year)
        
        try:
            response = self.fetch(endpoint='/disability-ratings', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching disability ratings: {str(e)}")
            return pd.DataFrame()
    
    def get_claims_data(
        self,
        claim_type: Optional[str] = None,
        status: Optional[str] = None,
        state: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get veterans claims processing data.
        
        Args:
            claim_type: Type of claim (compensation, pension, burial, etc.)
            status: Claim status (pending, approved, denied)
            state: Two-letter state code
            year: Year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with claims data
        """
        params = {
            'limit': limit,
        }
        
        if claim_type:
            params['claim_type'] = claim_type
        
        if status:
            params['status'] = status
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        try:
            response = self.fetch(endpoint='/claims', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching claims data: {str(e)}")
            return pd.DataFrame()
    
    def get_healthcare_data(
        self,
        state: Optional[str] = None,
        service_type: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get VA healthcare utilization data.
        
        Args:
            state: Two-letter state code
            service_type: Type of service (primary_care, mental_health, etc.)
            year: Year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with healthcare data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if service_type:
            params['service_type'] = service_type
        
        if year:
            params['year'] = str(year)
        
        try:
            response = self.fetch(endpoint='/healthcare', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching healthcare data: {str(e)}")
            return pd.DataFrame()
    
    def get_enrollment_data(
        self,
        state: Optional[str] = None,
        priority_group: Optional[int] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get VA healthcare enrollment data.
        
        Args:
            state: Two-letter state code
            priority_group: Priority group (1-8)
            year: Year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with enrollment data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if priority_group is not None:
            params['priority_group'] = str(priority_group)
        
        if year:
            params['year'] = str(year)
        
        try:
            response = self.fetch(endpoint='/enrollment', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching enrollment data: {str(e)}")
            return pd.DataFrame()
    
    def get_veteran_population(
        self,
        state: Optional[str] = None,
        county: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get veteran population statistics.
        
        Args:
            state: Two-letter state code
            county: County name
            year: Year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with population data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if county:
            params['county'] = county
        
        if year:
            params['year'] = str(year)
        
        try:
            response = self.fetch(endpoint='/veteran-population', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching veteran population: {str(e)}")
            return pd.DataFrame()
    
    def get_suicide_prevention_data(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get veteran suicide prevention program data.
        
        Args:
            state: Two-letter state code
            year: Year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with suicide prevention data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['year'] = str(year)
        
        try:
            response = self.fetch(endpoint='/suicide-prevention', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching suicide prevention data: {str(e)}")
            return pd.DataFrame()
    
    def get_performance_metrics(
        self,
        metric_type: Optional[str] = None,
        facility_id: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get VA performance metrics and quality indicators.
        
        Args:
            metric_type: Type of metric (wait_times, satisfaction, outcomes)
            facility_id: VA facility ID
            year: Year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with performance metrics
        """
        params = {
            'limit': limit,
        }
        
        if metric_type:
            params['metric_type'] = metric_type
        
        if facility_id:
            params['facility_id'] = facility_id
        
        if year:
            params['year'] = str(year)
        
        try:
            response = self.fetch(endpoint='/performance-metrics', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching performance metrics: {str(e)}")
            return pd.DataFrame()
    
    def get_expenditures(
        self,
        state: Optional[str] = None,
        category: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get VA expenditure data.
        
        Args:
            state: Two-letter state code
            category: Expenditure category (benefits, healthcare, operations)
            year: Year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with expenditure data
        """
        params = {
            'limit': limit,
        }
        
        if state:
            params['state'] = state.upper()
        
        if category:
            params['category'] = category
        
        if year:
            params['year'] = str(year)
        
        try:
            response = self.fetch(endpoint='/expenditures', **params)
            
            if response and isinstance(response, list):
                return pd.DataFrame(response)
            elif response and isinstance(response, dict) and 'data' in response:
                return pd.DataFrame(response['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching expenditure data: {str(e)}")
            return pd.DataFrame()
    
    def close(self) -> None:
        """Close the VA API connection and cleanup resources."""
        if self.session:
            self.session.close()
            self.session = None
        self.logger.info("Connection closed")
