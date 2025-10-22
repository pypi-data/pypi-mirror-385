"""
National Institutes of Health (NIH) Data Connector.

This module provides access to NIH research projects, grants, publications,
clinical trials, and investigator information through the NIH RePORTER API.

API Documentation:
- NIH RePORTER API: https://api.reporter.nih.gov/
- RePORTER Documentation: https://api.reporter.nih.gov/documents/Data%20Elements%20for%20RePORTER%20Project%20API%20v2.pdf
"""

import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..base_connector import BaseConnector


# Activity codes (grant types)
ACTIVITY_CODES = {
    'R01': 'Research Project Grant',
    'R21': 'Exploratory/Developmental Research Grant',
    'R03': 'Small Research Grant',
    'U01': 'Research Project Cooperative Agreement',
    'P01': 'Research Program Project',
    'K01': 'Mentored Research Scientist Development Award',
    'F31': 'Predoctoral Individual National Research Service Award',
    'T32': 'Institutional Research Training Grant',
}

# NIH Institutes and Centers
NIH_INSTITUTES = {
    'NCI': 'National Cancer Institute',
    'NHLBI': 'National Heart, Lung, and Blood Institute',
    'NIAID': 'National Institute of Allergy and Infectious Diseases',
    'NIMH': 'National Institute of Mental Health',
    'NIDDK': 'National Institute of Diabetes and Digestive and Kidney Diseases',
    'NINDS': 'National Institute of Neurological Disorders and Stroke',
    'NIGMS': 'National Institute of General Medical Sciences',
    'NIA': 'National Institute on Aging',
}

# Award types
AWARD_TYPES = {
    'new': 'New Award',
    'renewal': 'Renewal',
    'supplement': 'Supplement',
    'continuation': 'Continuation',
}


class NIHConnector(BaseConnector):
    """
    Connector for National Institutes of Health (NIH) data.
    
    Provides access to NIH research projects, grants, clinical trials,
    publications, and investigator information through RePORTER API.
    
    Attributes:
        api_url: NIH RePORTER API base URL
        
    Example:
        >>> connector = NIHConnector()
        >>> 
        >>> # Get projects by keyword
        >>> projects = connector.get_projects(
        ...     keywords='cancer immunotherapy',
        ...     fiscal_year=2023
        ... )
        >>> 
        >>> # Get projects by PI
        >>> pi_projects = connector.get_pi_projects(
        ...     pi_name='Smith'
        ... )
        >>> 
        >>> connector.close()
    """
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, **kwargs):
        """
        Initialize NIH connector.
        
        Args:
            api_key: Optional API key for NIH APIs
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseConnector
        """
        self._nih_api_key = api_key
        
        super().__init__(api_key=api_key, timeout=timeout, **kwargs)
        
        # NIH RePORTER API v2
        self.api_url = "https://api.reporter.nih.gov/v2/projects/search"
    
    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for NIH APIs.
        
        Returns:
            API key if available, None otherwise
        """
        return self._nih_api_key
    
    def connect(self) -> None:
        """
        Establish connection to NIH data sources.
        
        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return
        
        try:
            self.session = self._init_session()
            
            # Add API key to headers if available
            if self._nih_api_key:
                self.session.headers['Authorization'] = f'Bearer {self._nih_api_key}'
            
            self.logger.info("Successfully connected to NIH data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to NIH API: {e}")
            raise ConnectionError(f"Could not connect to NIH API: {e}")
    
    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from NIH APIs.
        
        Args:
            endpoint: API endpoint path (optional)
            **kwargs: Request body parameters for POST request
            
        Returns:
            API response data (list or dict)
            
        Raises:
            requests.HTTPError: If API request fails
        """
        endpoint = kwargs.pop('endpoint', '')
        
        if not self.session:
            self.connect()
        
        url = f"{self.api_url}{endpoint}" if endpoint else self.api_url
        
        # NIH RePORTER API uses POST requests with JSON body
        try:
            response = self.session.post(url, json=kwargs, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            self.logger.error(f"Failed to fetch data from NIH API: {e}")
            return {}
    
    def get_projects(
        self,
        keywords: Optional[str] = None,
        fiscal_year: Optional[int] = None,
        agency: Optional[str] = None,
        project_num: Optional[str] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """
        Get NIH research projects.
        
        Args:
            keywords: Keywords to search in project title or abstract
            fiscal_year: Fiscal year (YYYY)
            agency: Funding agency (IC code)
            project_num: Specific project number
            limit: Maximum records to return
            
        Returns:
            DataFrame with project data
        """
        criteria = {}
        
        if keywords:
            criteria['advanced_text_search'] = {
                'operator': 'and',
                'search_field': 'projecttitle,terms,abstract',
                'search_text': keywords
            }
        
        if fiscal_year:
            criteria['fiscal_years'] = [fiscal_year]
        
        if agency:
            criteria['agencies'] = [agency.upper()]
        
        if project_num:
            criteria['project_nums'] = [project_num]
        
        params = {
            'criteria': criteria,
            'limit': limit,
            'offset': 0,
            'include_fields': [
                'ProjectNum', 'ProjectTitle', 'AbstractText', 'Organization',
                'FiscalYear', 'AwardAmount', 'ContactPiName', 'ProgramOfficerName'
            ]
        }
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'results' in response:
                return pd.DataFrame(response['results'])
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching projects: {str(e)}")
            return pd.DataFrame()
    
    def get_pi_projects(
        self,
        pi_name: Optional[str] = None,
        pi_id: Optional[str] = None,
        fiscal_year: Optional[int] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """
        Get NIH projects by principal investigator.
        
        Args:
            pi_name: PI name (last name or full name)
            pi_id: PI profile ID
            fiscal_year: Fiscal year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with PI project data
        """
        criteria = {}
        
        if pi_name:
            criteria['pi_names'] = [{'any_name': pi_name}]
        
        if pi_id:
            criteria['pi_profile_ids'] = [pi_id]
        
        if fiscal_year:
            criteria['fiscal_years'] = [fiscal_year]
        
        params = {
            'criteria': criteria,
            'limit': limit,
            'offset': 0,
            'include_fields': [
                'ProjectNum', 'ProjectTitle', 'ContactPiName', 'PiProfileId',
                'Organization', 'FiscalYear', 'AwardAmount'
            ]
        }
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'results' in response:
                return pd.DataFrame(response['results'])
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching PI projects: {str(e)}")
            return pd.DataFrame()
    
    def get_organization_projects(
        self,
        organization: str,
        state: Optional[str] = None,
        fiscal_year: Optional[int] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """
        Get NIH projects by organization.
        
        Args:
            organization: Organization name (required)
            state: Two-letter state code
            fiscal_year: Fiscal year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with organization project data
        """
        criteria = {
            'org_names': [organization]
        }
        
        if state:
            criteria['org_states'] = [state.upper()]
        
        if fiscal_year:
            criteria['fiscal_years'] = [fiscal_year]
        
        params = {
            'criteria': criteria,
            'limit': limit,
            'offset': 0,
            'include_fields': [
                'ProjectNum', 'ProjectTitle', 'Organization', 'OrgState',
                'FiscalYear', 'AwardAmount', 'ContactPiName'
            ]
        }
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'results' in response:
                return pd.DataFrame(response['results'])
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching organization projects: {str(e)}")
            return pd.DataFrame()
    
    def get_projects_by_activity(
        self,
        activity_code: str,
        fiscal_year: Optional[int] = None,
        agency: Optional[str] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """
        Get NIH projects by activity code (grant type).
        
        Args:
            activity_code: Activity code (e.g., R01, R21, K01)
            fiscal_year: Fiscal year (YYYY)
            agency: Funding agency (IC code)
            limit: Maximum records to return
            
        Returns:
            DataFrame with project data
        """
        criteria = {
            'activity_codes': [activity_code.upper()]
        }
        
        if fiscal_year:
            criteria['fiscal_years'] = [fiscal_year]
        
        if agency:
            criteria['agencies'] = [agency.upper()]
        
        params = {
            'criteria': criteria,
            'limit': limit,
            'offset': 0,
            'include_fields': [
                'ProjectNum', 'ProjectTitle', 'ActivityCode', 'Agency',
                'FiscalYear', 'AwardAmount', 'Organization'
            ]
        }
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'results' in response:
                return pd.DataFrame(response['results'])
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching projects by activity: {str(e)}")
            return pd.DataFrame()
    
    def get_clinical_trials(
        self,
        keywords: Optional[str] = None,
        fiscal_year: Optional[int] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """
        Get NIH-funded clinical trials.
        
        Args:
            keywords: Keywords to search
            fiscal_year: Fiscal year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with clinical trial data
        """
        criteria = {
            'is_clinical_trial': True
        }
        
        if keywords:
            criteria['advanced_text_search'] = {
                'operator': 'and',
                'search_field': 'projecttitle,terms',
                'search_text': keywords
            }
        
        if fiscal_year:
            criteria['fiscal_years'] = [fiscal_year]
        
        params = {
            'criteria': criteria,
            'limit': limit,
            'offset': 0,
            'include_fields': [
                'ProjectNum', 'ProjectTitle', 'ClinicalTrialId', 'Organization',
                'FiscalYear', 'AwardAmount', 'ContactPiName'
            ]
        }
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'results' in response:
                return pd.DataFrame(response['results'])
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching clinical trials: {str(e)}")
            return pd.DataFrame()
    
    def get_funding_by_state(
        self,
        state: str,
        fiscal_year: Optional[int] = None,
        agency: Optional[str] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """
        Get NIH funding by state.
        
        Args:
            state: Two-letter state code (required)
            fiscal_year: Fiscal year (YYYY)
            agency: Funding agency (IC code)
            limit: Maximum records to return
            
        Returns:
            DataFrame with state funding data
        """
        criteria = {
            'org_states': [state.upper()]
        }
        
        if fiscal_year:
            criteria['fiscal_years'] = [fiscal_year]
        
        if agency:
            criteria['agencies'] = [agency.upper()]
        
        params = {
            'criteria': criteria,
            'limit': limit,
            'offset': 0,
            'include_fields': [
                'ProjectNum', 'Organization', 'OrgState', 'FiscalYear',
                'AwardAmount', 'Agency', 'ActivityCode'
            ]
        }
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'results' in response:
                return pd.DataFrame(response['results'])
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching funding by state: {str(e)}")
            return pd.DataFrame()
    
    def get_publications(
        self,
        project_num: Optional[str] = None,
        pmid: Optional[str] = None,
        fiscal_year: Optional[int] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """
        Get publications associated with NIH projects.
        
        Args:
            project_num: Project number
            pmid: PubMed ID
            fiscal_year: Fiscal year (YYYY)
            limit: Maximum records to return
            
        Returns:
            DataFrame with publication data
        """
        criteria = {}
        
        if project_num:
            criteria['project_nums'] = [project_num]
        
        if pmid:
            criteria['pmids'] = [pmid]
        
        if fiscal_year:
            criteria['fiscal_years'] = [fiscal_year]
        
        params = {
            'criteria': criteria,
            'limit': limit,
            'offset': 0,
            'include_fields': [
                'ProjectNum', 'ProjectTitle', 'Publications',
                'FiscalYear', 'Organization'
            ]
        }
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'results' in response:
                return pd.DataFrame(response['results'])
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching publications: {str(e)}")
            return pd.DataFrame()
    
    def get_project_details(
        self,
        project_num: str
    ) -> pd.DataFrame:
        """
        Get detailed information for a specific project.
        
        Args:
            project_num: Project number (required)
            
        Returns:
            DataFrame with detailed project data
        """
        criteria = {
            'project_nums': [project_num]
        }
        
        params = {
            'criteria': criteria,
            'limit': 1,
            'offset': 0,
            'include_fields': [
                'ProjectNum', 'ProjectTitle', 'AbstractText', 'ContactPiName',
                'Organization', 'FiscalYear', 'AwardAmount', 'Agency',
                'ActivityCode', 'AwardType', 'BudgetStart', 'BudgetEnd',
                'ProjectStartDate', 'ProjectEndDate', 'ClinicalTrialId',
                'Publications', 'Patents'
            ]
        }
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'results' in response:
                return pd.DataFrame(response['results'])
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching project details: {str(e)}")
            return pd.DataFrame()
    
    def get_new_awards(
        self,
        fiscal_year: int,
        agency: Optional[str] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """
        Get new NIH awards for a fiscal year.
        
        Args:
            fiscal_year: Fiscal year (YYYY) (required)
            agency: Funding agency (IC code)
            limit: Maximum records to return
            
        Returns:
            DataFrame with new award data
        """
        criteria = {
            'fiscal_years': [fiscal_year],
            'award_types': ['1']  # Type 1 = New
        }
        
        if agency:
            criteria['agencies'] = [agency.upper()]
        
        params = {
            'criteria': criteria,
            'limit': limit,
            'offset': 0,
            'include_fields': [
                'ProjectNum', 'ProjectTitle', 'AwardType', 'ContactPiName',
                'Organization', 'FiscalYear', 'AwardAmount', 'Agency'
            ]
        }
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'results' in response:
                return pd.DataFrame(response['results'])
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching new awards: {str(e)}")
            return pd.DataFrame()
    
    def get_funding_trends(
        self,
        start_year: int,
        end_year: int,
        agency: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get funding trends across multiple fiscal years.
        
        Args:
            start_year: Start fiscal year (YYYY) (required)
            end_year: End fiscal year (YYYY) (required)
            agency: Funding agency (IC code)
            limit: Maximum records to return
            
        Returns:
            DataFrame with funding trend data
        """
        criteria = {
            'fiscal_years': list(range(start_year, end_year + 1))
        }
        
        if agency:
            criteria['agencies'] = [agency.upper()]
        
        params = {
            'criteria': criteria,
            'limit': limit,
            'offset': 0,
            'include_fields': [
                'ProjectNum', 'FiscalYear', 'AwardAmount', 'Agency',
                'ActivityCode', 'Organization', 'OrgState'
            ]
        }
        
        try:
            response = self.fetch(**params)
            
            if response and isinstance(response, dict) and 'results' in response:
                return pd.DataFrame(response['results'])
            elif response and isinstance(response, list):
                return pd.DataFrame(response)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching funding trends: {str(e)}")
            return pd.DataFrame()
    
    def close(self) -> None:
        """Close the NIH API connection and cleanup resources."""
        if self.session:
            self.session.close()
            self.session = None
        self.logger.info("Connection closed")
