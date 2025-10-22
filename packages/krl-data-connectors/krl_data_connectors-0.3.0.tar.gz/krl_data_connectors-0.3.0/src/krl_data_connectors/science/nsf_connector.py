"""
National Science Foundation (NSF) Data Connector.

This module provides access to NSF research awards, funding data,
publications, institutions, and investigator information.

API Documentation:
- NSF Awards API: https://www.research.gov/common/webapi/awardapisearch-v1.htm
- NSF Public Access Repository: https://par.nsf.gov/
"""

import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..base_connector import BaseConnector


# Award types
AWARD_TYPES = {
    'grant': 'Standard Grant',
    'continuing': 'Continuing Grant',
    'contract': 'Contract',
    'cooperative': 'Cooperative Agreement',
    'fellowship': 'Fellowship',
}

# Directorate codes
DIRECTORATES = {
    'BIO': 'Biological Sciences',
    'CSE': 'Computer and Information Science and Engineering',
    'ENG': 'Engineering',
    'GEO': 'Geosciences',
    'MPS': 'Mathematical and Physical Sciences',
    'SBE': 'Social, Behavioral and Economic Sciences',
    'EHR': 'Education and Human Resources',
    'TIP': 'Technology, Innovation and Partnerships',
}

# Funding instruments
FUNDING_INSTRUMENTS = {
    'standard_grant': 'Standard Grant',
    'continuing_grant': 'Continuing Grant',
    'contract': 'Contract',
    'cooperative_agreement': 'Cooperative Agreement',
}


class NSFConnector(BaseConnector):
    """
    Connector for National Science Foundation (NSF) data.
    
    Provides access to NSF research awards, funding information,
    institutions, investigators, and publications.
    
    Attributes:
        api_url: NSF Awards API base URL
        
    Example:
        >>> connector = NSFConnector()
        >>> 
        >>> # Get recent awards
        >>> awards = connector.get_awards(
        ...     directorate='CSE',
        ...     year=2023
        ... )
        >>> 
        >>> # Get institution awards
        >>> institution = connector.get_institution_awards(
        ...     institution_name='Stanford University'
        ... )
        >>> 
        >>> connector.close()
    """
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, **kwargs):
        """
        Initialize NSF connector.
        
        Args:
            api_key: Optional API key for NSF APIs
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseConnector
        """
        self._nsf_api_key = api_key
        
        super().__init__(api_key=api_key, timeout=timeout, **kwargs)
        
        # NSF Awards API
        self.api_url = "https://api.nsf.gov/services/v1/awards.json"
    
    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for NSF APIs.
        
        Returns:
            API key if available, None otherwise
        """
        return self._nsf_api_key
    
    def connect(self) -> None:
        """
        Establish connection to NSF data sources.
        
        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return
        
        try:
            self.session = self._init_session()
            
            # Add API key to headers if available
            if self._nsf_api_key:
                self.session.headers['Authorization'] = f'Bearer {self._nsf_api_key}'
            
            self.logger.info("Successfully connected to NSF data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to NSF API: {e}")
            raise ConnectionError(f"Could not connect to NSF API: {e}")
    
    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from NSF APIs.
        
        Args:
            endpoint: API endpoint path (optional, defaults to base URL)
            **kwargs: Additional query parameters
            
        Returns:
            API response data (list or dict)
            
        Raises:
            requests.HTTPError: If API request fails
        """
        endpoint = kwargs.pop('endpoint', '')
        
        if not self.session:
            self.connect()
        
        url = f"{self.api_url}{endpoint}" if endpoint else self.api_url
        
        try:
            response = self.session.get(url, params=kwargs, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            self.logger.error(f"Failed to fetch data from NSF API: {e}")
            return {}
    
    def get_awards(
        self,
        keyword: Optional[str] = None,
        directorate: Optional[str] = None,
        year: Optional[int] = None,
        agency: Optional[str] = None,
        award_id: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get NSF award information.
        
        Args:
            keyword: Keyword search in title or abstract
            directorate: NSF directorate code (BIO, CSE, ENG, GEO, MPS, SBE, EHR, TIP)
            year: Award year (YYYY)
            agency: Awarding agency
            award_id: Specific award ID
            limit: Maximum records to return
            
        Returns:
            DataFrame with award data
        """
        params = {
            'printFields': 'id,title,agency,startDate,expDate,fundsObligatedAmt,piFirstName,piLastName,institution',
            'offset': '1',
        }
        
        if keyword:
            params['keyword'] = keyword
        
        if directorate:
            params['directorate'] = directorate.upper()
        
        if year:
            params['dateStart'] = f'{year}-01-01'
            params['dateEnd'] = f'{year}-12-31'
        
        if agency:
            params['agency'] = agency
        
        if award_id:
            params['id'] = award_id
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'response' in response:
                awards_data = response['response'].get('award', [])
                return pd.DataFrame(awards_data)
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching awards data: {str(e)}")
            return pd.DataFrame()
    
    def get_institution_awards(
        self,
        institution_name: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get NSF awards by institution.
        
        Args:
            institution_name: Institution name (partial match)
            state: Two-letter state code
            zip_code: Institution ZIP code
            year: Award year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with institution award data
        """
        params = {
            'printFields': 'id,title,agency,startDate,fundsObligatedAmt,institution,state,zipCode',
            'offset': '1',
        }
        
        if institution_name:
            params['institution'] = institution_name
        
        if state:
            params['state'] = state.upper()
        
        if zip_code:
            params['zipCode'] = zip_code
        
        if year:
            params['dateStart'] = f'{year}-01-01'
            params['dateEnd'] = f'{year}-12-31'
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'response' in response:
                awards_data = response['response'].get('award', [])
                return pd.DataFrame(awards_data)
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching institution awards: {str(e)}")
            return pd.DataFrame()
    
    def get_investigator_awards(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        pi_name: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get NSF awards by principal investigator.
        
        Args:
            first_name: PI first name
            last_name: PI last name
            pi_name: Full PI name search
            year: Award year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with investigator award data
        """
        params = {
            'printFields': 'id,title,startDate,fundsObligatedAmt,piFirstName,piLastName,piEmail,institution',
            'offset': '1',
        }
        
        if first_name:
            params['piFirstName'] = first_name
        
        if last_name:
            params['piLastName'] = last_name
        
        if pi_name:
            params['pdPIName'] = pi_name
        
        if year:
            params['dateStart'] = f'{year}-01-01'
            params['dateEnd'] = f'{year}-12-31'
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'response' in response:
                awards_data = response['response'].get('award', [])
                return pd.DataFrame(awards_data)
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching investigator awards: {str(e)}")
            return pd.DataFrame()
    
    def get_funding_by_directorate(
        self,
        directorate: str,
        year: Optional[int] = None,
        funding_instrument: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get NSF funding data by directorate.
        
        Args:
            directorate: NSF directorate code (BIO, CSE, ENG, GEO, MPS, SBE, EHR, TIP)
            year: Award year (YYYY)
            funding_instrument: Type of funding instrument
            limit: Maximum records to return
            
        Returns:
            DataFrame with funding data
        """
        params = {
            'printFields': 'id,title,fundsObligatedAmt,estimatedTotalAmt,awardInstrument,directorate',
            'offset': '1',
            'directorate': directorate.upper(),
        }
        
        if year:
            params['dateStart'] = f'{year}-01-01'
            params['dateEnd'] = f'{year}-12-31'
        
        if funding_instrument:
            params['awardInstrument'] = funding_instrument
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'response' in response:
                awards_data = response['response'].get('award', [])
                return pd.DataFrame(awards_data)
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching funding data: {str(e)}")
            return pd.DataFrame()
    
    def get_awards_by_program(
        self,
        program_name: Optional[str] = None,
        program_element: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get NSF awards by program.
        
        Args:
            program_name: Program name (partial match)
            program_element: Program element code
            year: Award year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with program award data
        """
        params = {
            'printFields': 'id,title,fundsObligatedAmt,programElement,programManager,programReference',
            'offset': '1',
        }
        
        if program_name:
            params['program'] = program_name
        
        if program_element:
            params['programElement'] = program_element
        
        if year:
            params['dateStart'] = f'{year}-01-01'
            params['dateEnd'] = f'{year}-12-31'
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'response' in response:
                awards_data = response['response'].get('award', [])
                return pd.DataFrame(awards_data)
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching program awards: {str(e)}")
            return pd.DataFrame()
    
    def get_award_abstract(
        self,
        award_id: str
    ) -> pd.DataFrame:
        """
        Get detailed award information including abstract.
        
        Args:
            award_id: Award ID (required)
            
        Returns:
            DataFrame with detailed award data
        """
        params = {
            'printFields': 'id,title,abstractText,piFirstName,piLastName,startDate,expDate,fundsObligatedAmt',
            'offset': '1',
            'id': award_id,
        }
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'response' in response:
                awards_data = response['response'].get('award', [])
                return pd.DataFrame(awards_data)
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching award abstract: {str(e)}")
            return pd.DataFrame()
    
    def get_funding_statistics(
        self,
        state: Optional[str] = None,
        year: Optional[int] = None,
        directorate: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get NSF funding statistics.
        
        Args:
            state: Two-letter state code
            year: Award year (YYYY)
            directorate: NSF directorate code
            limit: Maximum records to return
            
        Returns:
            DataFrame with funding statistics
        """
        params = {
            'printFields': 'id,fundsObligatedAmt,estimatedTotalAmt,state,directorate',
            'offset': '1',
        }
        
        if state:
            params['state'] = state.upper()
        
        if year:
            params['dateStart'] = f'{year}-01-01'
            params['dateEnd'] = f'{year}-12-31'
        
        if directorate:
            params['directorate'] = directorate.upper()
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'response' in response:
                awards_data = response['response'].get('award', [])
                return pd.DataFrame(awards_data)
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching funding statistics: {str(e)}")
            return pd.DataFrame()
    
    def get_collaborative_awards(
        self,
        lead_institution: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get NSF collaborative research awards.
        
        Args:
            lead_institution: Lead institution name
            year: Award year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with collaborative award data
        """
        params = {
            'printFields': 'id,title,fundsObligatedAmt,institution,piFirstName,piLastName',
            'offset': '1',
            'keyword': 'collaborative',
        }
        
        if lead_institution:
            params['institution'] = lead_institution
        
        if year:
            params['dateStart'] = f'{year}-01-01'
            params['dateEnd'] = f'{year}-12-31'
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'response' in response:
                awards_data = response['response'].get('award', [])
                return pd.DataFrame(awards_data)
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching collaborative awards: {str(e)}")
            return pd.DataFrame()
    
    def get_active_awards(
        self,
        directorate: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get currently active NSF awards.
        
        Args:
            directorate: NSF directorate code
            state: Two-letter state code
            limit: Maximum records to return
            
        Returns:
            DataFrame with active award data
        """
        params = {
            'printFields': 'id,title,startDate,expDate,fundsObligatedAmt,institution,state',
            'offset': '1',
            'status': 'active',
        }
        
        if directorate:
            params['directorate'] = directorate.upper()
        
        if state:
            params['state'] = state.upper()
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'response' in response:
                awards_data = response['response'].get('award', [])
                return pd.DataFrame(awards_data)
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching active awards: {str(e)}")
            return pd.DataFrame()
    
    def get_awards_by_amount(
        self,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get NSF awards by funding amount.
        
        Args:
            min_amount: Minimum award amount
            max_amount: Maximum award amount
            year: Award year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with award data filtered by amount
        """
        params = {
            'printFields': 'id,title,fundsObligatedAmt,estimatedTotalAmt,institution,piLastName',
            'offset': '1',
        }
        
        if min_amount is not None:
            params['minAmt'] = str(int(min_amount))
        
        if max_amount is not None:
            params['maxAmt'] = str(int(max_amount))
        
        if year:
            params['dateStart'] = f'{year}-01-01'
            params['dateEnd'] = f'{year}-12-31'
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'response' in response:
                awards_data = response['response'].get('award', [])
                return pd.DataFrame(awards_data)
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching awards by amount: {str(e)}")
            return pd.DataFrame()
    
    def close(self) -> None:
        """Close the NSF API connection and cleanup resources."""
        if self.session:
            self.session.close()
            self.session = None
        self.logger.info("Connection closed")
