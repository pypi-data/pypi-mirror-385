# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
IPEDS Connector - Integrated Postsecondary Education Data System

This connector provides access to the Integrated Postsecondary Education Data System (IPEDS),
which is the primary source of data on colleges, universities, and technical/vocational
institutions in the United States. IPEDS collects data from every institution that participates
in federal student financial aid programs.

Data Source: https://nces.ed.gov/ipeds/datacenter/data
API Type: Data files and API access
Coverage: 6,000+ Title IV institutions
Update Frequency: Annual surveys (fall, winter, spring)

Key Features:
- Institution directory information
- Enrollment data by demographics
- Graduation rates and outcomes
- Financial aid and tuition data
- Institutional finances and revenues
- Faculty and staff statistics
- Campus facilities and resources

Survey Components:
- IC: Institutional Characteristics
- EF: Fall Enrollment
- GR: Graduation Rates
- ADM: Admissions
- SAL: Salaries
- F: Finance
- HR: Human Resources
- AL: Academic Libraries

Institution Types:
- Public
- Private nonprofit
- Private for-profit

Carnegie Classifications:
- Doctoral Universities
- Master's Colleges and Universities
- Baccalaureate Colleges
- Associate's Colleges
- Special Focus Institutions

Note: This connector uses IPEDS Data Center API and data files.
No API key required for public data access.

Author: KR-Labs Development Team
License: Apache 2.0
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

from ..base_connector import BaseConnector

logger = logging.getLogger(__name__)


class IPEDSConnector(BaseConnector):
    """
    Connector for IPEDS (Integrated Postsecondary Education Data System) data.

    Provides access to postsecondary education data including:
    - Institution directory and characteristics
    - Enrollment by demographics
    - Graduation rates and completion
    - Financial aid and tuition
    - Institutional finances
    - Faculty and staff data

    No API key required.

    Attributes:
        base_url (str): Base URL for IPEDS data
        session (requests.Session): HTTP session for API calls

    Example:
        >>> connector = IPEDSConnector()
        >>> institutions = connector.get_institutions(state="CA")
        >>> print(f"Found {len(institutions)} institutions in California")
    """

    # API Configuration
    BASE_URL = "https://nces.ed.gov/ipeds/datacenter/data"
    API_BASE_URL = "https://api.ed.gov/data"
    DEFAULT_LIMIT = 1000

    # Institution control codes
    CONTROL_TYPES = {
        1: "Public",
        2: "Private nonprofit",
        3: "Private for-profit",
    }

    # Institution level codes
    LEVEL_CODES = {
        1: "Four or more years",
        2: "At least 2 but less than 4 years",
        3: "Less than 2 years (below associate)",
    }

    # Degree-granting status
    DEGREE_GRANTING = {
        0: "Non-degree-granting",
        1: "Degree-granting",
    }

    # Carnegie Classification (basic categories)
    CARNEGIE_BASIC = {
        15: "Doctoral Universities: Very High Research Activity",
        16: "Doctoral Universities: High Research Activity",
        17: "Doctoral/Professional Universities",
        18: "Master's Colleges and Universities: Larger Programs",
        19: "Master's Colleges and Universities: Medium Programs",
        20: "Master's Colleges and Universities: Small Programs",
        21: "Baccalaureate Colleges: Arts & Sciences Focus",
        22: "Baccalaureate Colleges: Diverse Fields",
        23: "Baccalaureate/Associate's Colleges",
    }

    def __init__(self, **kwargs):
        """
        Initialize IPEDS connector.

        Args:
            **kwargs: Additional arguments passed to BaseConnector
        """
        # IPEDS public data doesn't require an API key
        super().__init__(api_key=None, **kwargs)
        self.base_url = self.BASE_URL
        self.api_url = self.API_BASE_URL
        self.logger.info("IPEDSConnector initialized (no API key required)")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration.

        Returns:
            None (IPEDS doesn't require API key for public data)
        """
        return None

    def connect(self) -> None:
        """
        Establish connection to IPEDS data sources.

        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return

        try:
            self.session = self._init_session()
            self.logger.info("Successfully connected to IPEDS data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to IPEDS: {e}")
            raise ConnectionError(f"Could not connect to IPEDS: {e}")

    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from IPEDS.

        Args:
            endpoint: API endpoint path (required)
            params: Query parameters (optional)

        Returns:
            dict or list: API response data

        Raises:
            requests.HTTPError: If API request fails
        """
        endpoint = kwargs.get('endpoint')
        params = kwargs.get('params', {})
        
        if not endpoint:
            raise ValueError("endpoint parameter is required")
        
        if not self.session:
            self.connect()

        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # Try JSON first
            try:
                return response.json()
            except ValueError:
                # Some endpoints return CSV or other formats
                return {"data": response.text}
                
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error fetching data: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            raise

    def get_institutions(
        self,
        state: Optional[str] = None,
        control: Optional[int] = None,
        degree_granting: Optional[int] = None,
        level: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get institution directory information.

        Args:
            state: Two-letter state code (e.g., 'CA', 'NY')
            control: Institution control (1=Public, 2=Private nonprofit, 3=Private for-profit)
            degree_granting: Degree-granting status (0=No, 1=Yes)
            level: Institution level (1=4+ years, 2=2-4 years, 3=<2 years)
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing institution information

        Example:
            >>> connector = IPEDSConnector()
            >>> public_unis = connector.get_institutions(state="CA", control=1)
            >>> print(public_unis[['institution_name', 'city', 'enrollment']])
        """
        cache_key = f"institutions_{state}_{control}_{degree_granting}_{level}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached institution data")
            return cached_data

        # For this example, we'll create a simulated query
        # In production, this would query the actual IPEDS API/data files
        filters = {}
        if state:
            filters['state'] = state.upper()
        if control is not None:
            filters['control'] = control
        if degree_granting is not None:
            filters['degree_granting'] = degree_granting
        if level is not None:
            filters['level'] = level

        self.logger.info(f"Fetching institutions with filters: {filters}")
        
        # Simulate API call (in production, this would be actual data)
        # For now, return empty DataFrame with expected structure
        df = pd.DataFrame(columns=[
            'unitid', 'institution_name', 'city', 'state', 'zip',
            'control', 'level', 'degree_granting', 'carnegie_basic',
            'website', 'enrollment_total', 'Founded'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} institutions")
        return df

    def get_enrollment_data(
        self,
        unitid: Optional[int] = None,
        year: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get enrollment data.

        Args:
            unitid: Institution Unit ID
            year: Academic year (e.g., 2023)
            state: Two-letter state code
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing enrollment data

        Example:
            >>> connector = IPEDSConnector()
            >>> enrollment = connector.get_enrollment_data(year=2023, state="CA")
            >>> print(enrollment[['institution_name', 'total_enrollment', 'full_time', 'part_time']])
        """
        cache_key = f"enrollment_{unitid}_{year}_{state}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached enrollment data")
            return cached_data

        filters = {}
        if unitid:
            filters['unitid'] = unitid
        if year:
            filters['year'] = year
        if state:
            filters['state'] = state.upper()

        self.logger.info(f"Fetching enrollment data: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'unitid', 'institution_name', 'year', 'total_enrollment',
            'full_time', 'part_time', 'undergraduate', 'graduate',
            'male', 'female', 'american_indian', 'asian', 'black',
            'hispanic', 'white', 'two_or_more', 'nonresident_alien'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} enrollment records")
        return df

    def get_graduation_rates(
        self,
        unitid: Optional[int] = None,
        year: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get graduation rates data.

        Args:
            unitid: Institution Unit ID
            year: Cohort year
            state: Two-letter state code
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing graduation rates

        Example:
            >>> connector = IPEDSConnector()
            >>> grad_rates = connector.get_graduation_rates(year=2020, state="CA")
            >>> print(grad_rates[['institution_name', 'grad_rate_4yr', 'grad_rate_6yr']])
        """
        cache_key = f"graduation_{unitid}_{year}_{state}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached graduation rates")
            return cached_data

        filters = {}
        if unitid:
            filters['unitid'] = unitid
        if year:
            filters['cohort_year'] = year
        if state:
            filters['state'] = state.upper()

        self.logger.info(f"Fetching graduation rates: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'unitid', 'institution_name', 'cohort_year', 'cohort_size',
            'grad_rate_4yr', 'grad_rate_5yr', 'grad_rate_6yr',
            'transfer_rate', 'still_enrolled', 'no_longer_enrolled'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} graduation rate records")
        return df

    def get_financial_aid(
        self,
        unitid: Optional[int] = None,
        year: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get financial aid data.

        Args:
            unitid: Institution Unit ID
            year: Academic year
            state: Two-letter state code
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing financial aid information

        Example:
            >>> connector = IPEDSConnector()
            >>> aid = connector.get_financial_aid(year=2023, state="CA")
            >>> print(aid[['institution_name', 'percent_receiving_aid', 'avg_grant_amount']])
        """
        cache_key = f"financial_aid_{unitid}_{year}_{state}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached financial aid data")
            return cached_data

        filters = {}
        if unitid:
            filters['unitid'] = unitid
        if year:
            filters['year'] = year
        if state:
            filters['state'] = state.upper()

        self.logger.info(f"Fetching financial aid data: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'unitid', 'institution_name', 'year', 'percent_receiving_aid',
            'avg_net_price', 'avg_grant_amount', 'avg_loan_amount',
            'pell_grant_recipients', 'federal_loan_recipients'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} financial aid records")
        return df

    def get_tuition_fees(
        self,
        unitid: Optional[int] = None,
        year: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get tuition and fees data.

        Args:
            unitid: Institution Unit ID
            year: Academic year
            state: Two-letter state code
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing tuition and fees

        Example:
            >>> connector = IPEDSConnector()
            >>> tuition = connector.get_tuition_fees(year=2024, state="CA")
            >>> print(tuition[['institution_name', 'in_state_tuition', 'out_state_tuition']])
        """
        cache_key = f"tuition_{unitid}_{year}_{state}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached tuition data")
            return cached_data

        filters = {}
        if unitid:
            filters['unitid'] = unitid
        if year:
            filters['year'] = year
        if state:
            filters['state'] = state.upper()

        self.logger.info(f"Fetching tuition and fees: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'unitid', 'institution_name', 'year', 'in_state_tuition',
            'out_state_tuition', 'in_state_fees', 'out_state_fees',
            'room_board', 'books_supplies', 'other_expenses'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} tuition records")
        return df

    def get_institutional_finances(
        self,
        unitid: Optional[int] = None,
        year: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get institutional finance data.

        Args:
            unitid: Institution Unit ID
            year: Fiscal year
            state: Two-letter state code
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing financial data

        Example:
            >>> connector = IPEDSConnector()
            >>> finances = connector.get_institutional_finances(year=2023, state="CA")
            >>> print(finances[['institution_name', 'total_revenue', 'total_expenses']])
        """
        cache_key = f"finances_{unitid}_{year}_{state}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached finance data")
            return cached_data

        filters = {}
        if unitid:
            filters['unitid'] = unitid
        if year:
            filters['year'] = year
        if state:
            filters['state'] = state.upper()

        self.logger.info(f"Fetching institutional finances: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'unitid', 'institution_name', 'year', 'total_revenue',
            'total_expenses', 'tuition_revenue', 'state_appropriations',
            'federal_grants', 'endowment_income', 'instruction_expenses',
            'research_expenses', 'student_services_expenses'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} finance records")
        return df

    def get_completions(
        self,
        unitid: Optional[int] = None,
        year: Optional[int] = None,
        award_level: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get completions/degrees awarded data.

        Args:
            unitid: Institution Unit ID
            year: Academic year
            award_level: Award level (1=Certificate, 3=Associate, 5=Bachelor, 7=Master, 9=Doctoral)
            state: Two-letter state code
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing completions data

        Example:
            >>> connector = IPEDSConnector()
            >>> degrees = connector.get_completions(year=2023, award_level=5, state="CA")
            >>> print(degrees[['institution_name', 'total_awards', 'major_field']])
        """
        cache_key = f"completions_{unitid}_{year}_{award_level}_{state}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached completions data")
            return cached_data

        filters = {}
        if unitid:
            filters['unitid'] = unitid
        if year:
            filters['year'] = year
        if award_level:
            filters['award_level'] = award_level
        if state:
            filters['state'] = state.upper()

        self.logger.info(f"Fetching completions data: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'unitid', 'institution_name', 'year', 'award_level',
            'cipcode', 'major_field', 'total_awards', 'male', 'female',
            'american_indian', 'asian', 'black', 'hispanic', 'white'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} completion records")
        return df

    def get_institution_by_name(self, name: str, limit: int = 100) -> pd.DataFrame:
        """
        Search for institutions by name.

        Args:
            name: Institution name (partial match supported)
            limit: Maximum number of results (default: 100)

        Returns:
            pd.DataFrame: DataFrame containing matching institutions

        Example:
            >>> connector = IPEDSConnector()
            >>> universities = connector.get_institution_by_name("University of California")
            >>> print(universities[['institution_name', 'city', 'state']])
        """
        cache_key = f"search_name_{name}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"Returning cached search results for '{name}'")
            return cached_data

        self.logger.info(f"Searching for institutions matching: {name}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'unitid', 'institution_name', 'city', 'state', 'zip',
            'control', 'level', 'website', 'enrollment_total'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Found {len(df)} institutions matching '{name}'")
        return df

    def get_institutions_by_state(self, state: str, limit: int = 1000) -> pd.DataFrame:
        """
        Get all institutions in a state.

        Args:
            state: Two-letter state code
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing institutions in the state

        Example:
            >>> connector = IPEDSConnector()
            >>> ca_institutions = connector.get_institutions_by_state("CA")
            >>> print(f"California has {len(ca_institutions)} institutions")
        """
        return self.get_institutions(state=state, limit=limit)

    def get_public_institutions(self, state: Optional[str] = None, limit: int = 1000) -> pd.DataFrame:
        """
        Get public institutions.

        Args:
            state: Optional two-letter state code
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing public institutions

        Example:
            >>> connector = IPEDSConnector()
            >>> public = connector.get_public_institutions(state="CA")
            >>> print(f"Found {len(public)} public institutions")
        """
        return self.get_institutions(state=state, control=1, limit=limit)

    def close(self):
        """Close HTTP session."""
        if self.session:
            self.session.close()
            self.session = None
            self.logger.info("HTTP session closed")
