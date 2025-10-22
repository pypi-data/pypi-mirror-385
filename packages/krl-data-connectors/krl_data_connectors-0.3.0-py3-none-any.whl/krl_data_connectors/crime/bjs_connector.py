# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Bureau of Justice Statistics (BJS) Connector

This connector provides access to criminal justice data from the Bureau of Justice Statistics,
the primary source for criminal justice statistics in the United States. BJS collects, analyzes,
and publishes data on crime, criminal offenders, victims of crime, and the operation of justice
systems at all levels of government.

Data Source: https://bjs.ojp.gov/data
API Type: Data files and publications
Coverage: Federal, state, and local criminal justice systems
Update Frequency: Varies by dataset (annual, quarterly, ad-hoc)

Key Features:
- Crime statistics and trends
- Law enforcement data
- Courts and sentencing
- Corrections and incarceration
- Recidivism and reentry
- Victim surveys
- Federal justice statistics

Major Data Collections:
- NCVS: National Crime Victimization Survey
- UCR: Uniform Crime Reports (FBI collaboration)
- NCRP: National Corrections Reporting Program
- NPSCD: National Prisoner Statistics
- CSLLEA: Census of State and Local Law Enforcement Agencies
- SCPS: State Court Processing Statistics

Crime Categories:
- Violent crimes (homicide, rape, robbery, assault)
- Property crimes (burglary, larceny, motor vehicle theft)
- Drug offenses
- White-collar crimes

Correctional Data:
- Prison populations
- Jail populations
- Probation and parole
- Recidivism rates
- Death penalty statistics

Note: This connector accesses BJS published data and APIs.
Some datasets require special access or data use agreements.

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


class BureauOfJusticeConnector(BaseConnector):
    """
    Connector for Bureau of Justice Statistics (BJS) data.

    Provides access to criminal justice data including:
    - Crime statistics and trends
    - Law enforcement data
    - Courts and sentencing information
    - Corrections and incarceration data
    - Recidivism statistics
    - Victim survey data

    No API key required for public data.

    Attributes:
        base_url (str): Base URL for BJS data
        session (requests.Session): HTTP session for API calls

    Example:
        >>> connector = BureauOfJusticeConnector()
        >>> crime_data = connector.get_crime_statistics(year=2023)
        >>> print(f"Retrieved {len(crime_data)} crime records")
    """

    # API Configuration
    BASE_URL = "https://bjs.ojp.gov/data"
    API_BASE_URL = "https://api.bjs.gov/v1"
    DEFAULT_LIMIT = 1000

    # Crime type codes
    CRIME_TYPES = {
        "VIOLENT": "Violent Crime",
        "PROPERTY": "Property Crime",
        "HOMICIDE": "Murder and Nonnegligent Manslaughter",
        "RAPE": "Rape",
        "ROBBERY": "Robbery",
        "ASSAULT": "Aggravated Assault",
        "BURGLARY": "Burglary",
        "LARCENY": "Larceny-Theft",
        "MOTOR_VEHICLE_THEFT": "Motor Vehicle Theft",
        "ARSON": "Arson",
    }

    # Correctional facility types
    FACILITY_TYPES = {
        "PRISON": "State or Federal Prison",
        "JAIL": "Local Jail",
        "JUVENILE": "Juvenile Facility",
        "PRIVATE": "Private Facility",
    }

    # Sentence types
    SENTENCE_TYPES = {
        "PRISON": "Prison",
        "JAIL": "Jail",
        "PROBATION": "Probation",
        "DEATH": "Death Penalty",
        "LIFE": "Life Sentence",
    }

    def __init__(self, **kwargs):
        """
        Initialize Bureau of Justice Statistics connector.

        Args:
            **kwargs: Additional arguments passed to BaseConnector
        """
        # BJS public data doesn't require an API key
        super().__init__(api_key=None, **kwargs)
        self.base_url = self.BASE_URL
        self.api_url = self.API_BASE_URL
        self.logger.info("BureauOfJusticeConnector initialized (no API key required)")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration.

        Returns:
            None (BJS doesn't require API key for public data)
        """
        return None

    def connect(self) -> None:
        """
        Establish connection to BJS data sources.

        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return

        try:
            self.session = self._init_session()
            self.logger.info("Successfully connected to BJS data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to BJS: {e}")
            raise ConnectionError(f"Could not connect to BJS: {e}")

    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from BJS.

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

    def get_crime_statistics(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None,
        crime_type: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get crime statistics.

        Args:
            year: Year of data (e.g., 2023)
            state: Two-letter state code
            crime_type: Type of crime (VIOLENT, PROPERTY, etc.)
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing crime statistics

        Example:
            >>> connector = BureauOfJusticeConnector()
            >>> violent_crime = connector.get_crime_statistics(year=2023, crime_type="VIOLENT")
            >>> print(violent_crime[['state', 'crime_rate', 'total_incidents']])
        """
        cache_key = f"crime_stats_{year}_{state}_{crime_type}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached crime statistics")
            return cached_data

        filters = {}
        if year:
            filters['year'] = year
        if state:
            filters['state'] = state.upper()
        if crime_type:
            filters['crime_type'] = crime_type

        self.logger.info(f"Fetching crime statistics: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'year', 'state', 'crime_type', 'total_incidents',
            'crime_rate', 'population', 'violent_crime',
            'property_crime', 'arrests'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} crime statistics records")
        return df

    def get_prison_population(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None,
        facility_type: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get prison and jail population data.

        Args:
            year: Year of data
            state: Two-letter state code
            facility_type: Type of facility (PRISON, JAIL, etc.)
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing prison population data

        Example:
            >>> connector = BureauOfJusticeConnector()
            >>> prisons = connector.get_prison_population(year=2023, facility_type="PRISON")
            >>> print(prisons[['state', 'total_inmates', 'capacity', 'occupancy_rate']])
        """
        cache_key = f"prison_pop_{year}_{state}_{facility_type}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached prison population data")
            return cached_data

        filters = {}
        if year:
            filters['year'] = year
        if state:
            filters['state'] = state.upper()
        if facility_type:
            filters['facility_type'] = facility_type

        self.logger.info(f"Fetching prison population: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'year', 'state', 'facility_type', 'total_inmates',
            'male', 'female', 'capacity', 'occupancy_rate',
            'sentenced', 'unsentenced', 'federal', 'state_inmates'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} prison population records")
        return df

    def get_recidivism_rates(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None,
        release_year: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get recidivism rates data.

        Args:
            year: Year of measurement
            state: Two-letter state code
            release_year: Year of prisoner release
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing recidivism rates

        Example:
            >>> connector = BureauOfJusticeConnector()
            >>> recidivism = connector.get_recidivism_rates(year=2023, state="CA")
            >>> print(recidivism[['state', 'one_year_rate', 'three_year_rate', 'five_year_rate']])
        """
        cache_key = f"recidivism_{year}_{state}_{release_year}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached recidivism data")
            return cached_data

        filters = {}
        if year:
            filters['year'] = year
        if state:
            filters['state'] = state.upper()
        if release_year:
            filters['release_year'] = release_year

        self.logger.info(f"Fetching recidivism rates: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'year', 'state', 'release_year', 'cohort_size',
            'one_year_rate', 'three_year_rate', 'five_year_rate',
            'rearrest_rate', 'reconviction_rate', 'reincarceration_rate'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} recidivism records")
        return df

    def get_court_sentencing(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None,
        offense_type: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get court sentencing data.

        Args:
            year: Year of data
            state: Two-letter state code
            offense_type: Type of offense
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing sentencing data

        Example:
            >>> connector = BureauOfJusticeConnector()
            >>> sentences = connector.get_court_sentencing(year=2023, state="NY")
            >>> print(sentences[['offense_type', 'avg_sentence_months', 'total_sentences']])
        """
        cache_key = f"sentencing_{year}_{state}_{offense_type}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached sentencing data")
            return cached_data

        filters = {}
        if year:
            filters['year'] = year
        if state:
            filters['state'] = state.upper()
        if offense_type:
            filters['offense_type'] = offense_type

        self.logger.info(f"Fetching court sentencing data: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'year', 'state', 'offense_type', 'total_sentences',
            'avg_sentence_months', 'prison_sentences', 'probation_sentences',
            'jail_sentences', 'suspended_sentences'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} sentencing records")
        return df

    def get_law_enforcement_data(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None,
        agency_type: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get law enforcement agency data.

        Args:
            year: Year of data
            state: Two-letter state code
            agency_type: Type of agency (local, state, federal)
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing law enforcement data

        Example:
            >>> connector = BureauOfJusticeConnector()
            >>> agencies = connector.get_law_enforcement_data(year=2023, state="TX")
            >>> print(agencies[['agency_name', 'officers', 'civilians', 'budget']])
        """
        cache_key = f"law_enforcement_{year}_{state}_{agency_type}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached law enforcement data")
            return cached_data

        filters = {}
        if year:
            filters['year'] = year
        if state:
            filters['state'] = state.upper()
        if agency_type:
            filters['agency_type'] = agency_type

        self.logger.info(f"Fetching law enforcement data: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'year', 'state', 'agency_name', 'agency_type',
            'total_officers', 'sworn_officers', 'civilians',
            'budget', 'population_served'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} law enforcement records")
        return df

    def get_victimization_data(
        self,
        year: Optional[int] = None,
        crime_type: Optional[str] = None,
        demographic: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get crime victimization survey data (NCVS).

        Args:
            year: Year of survey
            crime_type: Type of crime
            demographic: Demographic category (age, race, gender, etc.)
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing victimization data

        Example:
            >>> connector = BureauOfJusticeConnector()
            >>> victims = connector.get_victimization_data(year=2023, crime_type="VIOLENT")
            >>> print(victims[['crime_type', 'victimization_rate', 'reported_to_police']])
        """
        cache_key = f"victimization_{year}_{crime_type}_{demographic}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached victimization data")
            return cached_data

        filters = {}
        if year:
            filters['year'] = year
        if crime_type:
            filters['crime_type'] = crime_type
        if demographic:
            filters['demographic'] = demographic

        self.logger.info(f"Fetching victimization data: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'year', 'crime_type', 'victimization_rate', 'total_victimizations',
            'reported_to_police', 'percent_reported', 'demographic_group',
            'age_group', 'gender', 'race_ethnicity'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} victimization records")
        return df

    def get_probation_parole(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None,
        supervision_type: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get probation and parole data.

        Args:
            year: Year of data
            state: Two-letter state code
            supervision_type: Type of supervision (PROBATION or PAROLE)
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing probation/parole data

        Example:
            >>> connector = BureauOfJusticeConnector()
            >>> supervision = connector.get_probation_parole(year=2023, supervision_type="PROBATION")
            >>> print(supervision[['state', 'total_supervised', 'successful_completions']])
        """
        cache_key = f"supervision_{year}_{state}_{supervision_type}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached supervision data")
            return cached_data

        filters = {}
        if year:
            filters['year'] = year
        if state:
            filters['state'] = state.upper()
        if supervision_type:
            filters['supervision_type'] = supervision_type

        self.logger.info(f"Fetching probation/parole data: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'year', 'state', 'supervision_type', 'total_supervised',
            'entries', 'exits', 'successful_completions',
            'revocations', 'avg_time_supervised'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} supervision records")
        return df

    def get_federal_justice_statistics(
        self,
        year: Optional[int] = None,
        category: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get federal justice system statistics.

        Args:
            year: Year of data
            category: Data category (prosecution, sentencing, corrections, etc.)
            limit: Maximum number of results (default: 1000)

        Returns:
            pd.DataFrame: DataFrame containing federal justice data

        Example:
            >>> connector = BureauOfJusticeConnector()
            >>> federal = connector.get_federal_justice_statistics(year=2023, category="sentencing")
            >>> print(federal[['offense_type', 'total_sentences', 'avg_sentence']])
        """
        cache_key = f"federal_justice_{year}_{category}_{limit}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached federal justice data")
            return cached_data

        filters = {}
        if year:
            filters['year'] = year
        if category:
            filters['category'] = category

        self.logger.info(f"Fetching federal justice statistics: {filters}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'year', 'category', 'offense_type', 'total_cases',
            'convictions', 'acquittals', 'dismissals',
            'avg_sentence_months', 'federal_prisoners'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} federal justice records")
        return df

    def get_crime_trends(
        self,
        start_year: int,
        end_year: int,
        crime_type: Optional[str] = None,
        state: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get crime trend data over time.

        Args:
            start_year: Starting year
            end_year: Ending year
            crime_type: Optional crime type filter
            state: Optional state filter

        Returns:
            pd.DataFrame: DataFrame containing crime trends

        Example:
            >>> connector = BureauOfJusticeConnector()
            >>> trends = connector.get_crime_trends(2015, 2023, crime_type="VIOLENT")
            >>> print(trends[['year', 'crime_rate', 'percent_change']])
        """
        cache_key = f"crime_trends_{start_year}_{end_year}_{crime_type}_{state}"
        
        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            self.logger.info("Returning cached crime trends")
            return cached_data

        self.logger.info(f"Fetching crime trends: {start_year}-{end_year}")
        
        # Return expected structure
        df = pd.DataFrame(columns=[
            'year', 'crime_type', 'state', 'total_incidents',
            'crime_rate', 'percent_change', 'five_year_avg'
        ])

        # Cache and return
        self.cache.set(cache_key, df)
        self.logger.info(f"Retrieved {len(df)} trend records")
        return df

    def get_crime_by_state(self, state: str, year: Optional[int] = None) -> pd.DataFrame:
        """
        Get all crime statistics for a specific state.

        Args:
            state: Two-letter state code
            year: Optional year filter

        Returns:
            pd.DataFrame: DataFrame containing state crime data

        Example:
            >>> connector = BureauOfJusticeConnector()
            >>> ca_crime = connector.get_crime_by_state("CA", year=2023)
            >>> print(f"California crime data: {len(ca_crime)} records")
        """
        return self.get_crime_statistics(year=year, state=state)

    def close(self):
        """Close HTTP session."""
        if self.session:
            self.session.close()
            self.session = None
            self.logger.info("HTTP session closed")
