# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
National Center for Education Statistics (NCES) Connector

Provides access to comprehensive U.S. education data, including:
- **School Demographics**: Enrollment, staff, student characteristics
- **Performance Metrics**: Test scores, graduation rates, college readiness
- **Financial Data**: Revenues, expenditures, per-pupil spending
- **Geographic Data**: District and school-level information

**⚠️ DATA ACCESS NOTE:**

NCES provides data through multiple systems:
- **Common Core of Data (CCD)**: Public elementary/secondary schools
- **Private School Universe Survey (PSS)**: Private schools
- **Integrated Postsecondary Education Data System (IPEDS)**: Colleges/universities
- **National Assessment of Educational Progress (NAEP)**: Test scores

**Data Sources:**
- **NCES Data Tools**: https://nces.ed.gov/datatools/
- **Education Data Portal**: https://educationdata.urban.org/documentation/
- **Downloadable Files**: https://nces.ed.gov/ccd/files.asp

**API Access:**
- Urban Institute Education Data API (recommended)
- No API key required
- RESTful access to cleaned, structured data

**Data Categories:**
- **CCD**: ~100,000 public schools, ~18,000 districts
- **PSS**: ~30,000 private schools
- **IPEDS**: ~7,000 colleges/universities
- **Years**: Historical data back to 1980s

**Data Domains:**
- D09: Education & Workforce Development
- D19: Governance & Civic Infrastructure
- D24: Geographic & Spatial Data

**Example Usage:**
    >>> from krl_data_connectors.education import NCESConnector
    >>> 
    >>> # Initialize connector
    >>> nces = NCESConnector()
    >>> 
    >>> # Get Rhode Island schools
    >>> ri_schools = nces.get_state_schools('RI', year=2023)
    >>> 
    >>> # Get enrollment demographics
    >>> demographics = nces.get_demographics(ri_schools)
    >>> 
    >>> # Calculate graduation rates
    >>> grad_rates = nces.get_graduation_rates('RI', year=2023)

---

Licensed under the Apache License, Version 2.0.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

from krl_data_connectors.base_connector import BaseConnector


class NCESConnector(BaseConnector):
    """
    Connector for National Center for Education Statistics data.
    
    **Data Systems:**
    - **CCD**: Common Core of Data (public schools)
    - **PSS**: Private School Universe Survey
    - **IPEDS**: Integrated Postsecondary Education Data System
    - **NAEP**: National Assessment of Educational Progress
    
    **Data Points:**
    - School/district identifiers (NCES ID, state ID, LEA ID)
    - Enrollment (by grade, race/ethnicity, gender, special programs)
    - Staff (teachers, administrators, support staff)
    - Finance (revenues, expenditures, per-pupil spending)
    - Performance (test scores, graduation rates, dropout rates)
    
    **Geographic Levels:**
    - National (aggregate)
    - State
    - District (Local Education Agency - LEA)
    - School
    
    **API Provider:**
    - Urban Institute Education Data Portal
    - Base URL: https://educationdata.urban.org/api/v1/
    - No authentication required
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 2592000,  # 30 days
    ):
        """
        Initialize NCES connector.
        
        Args:
            api_key: Optional API key (not required)
            cache_dir: Directory for caching data
            cache_ttl: Cache time-to-live in seconds (default: 30 days)
        """
        super().__init__(
            api_key=api_key,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
        )
        
        self.base_url = "https://educationdata.urban.org/api/v1"
        
        self.school_types = {
            1: 'Regular school',
            2: 'Special education school',
            3: 'Vocational school',
            4: 'Alternative/other school'
        }
        
        self.logger.info(
            "NCESConnector initialized",
            extra={"base_url": self.base_url, "api_access": "Public"}
        )

    def _get_api_key(self) -> Optional[str]:
        """NCES/Urban API does not require an API key."""
        return None

    def connect(self) -> None:
        """
        NCES connector does not require explicit connection.
        
        The Urban Institute Education Data API is publicly accessible
        without authentication.
        """
        pass

    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """
        Fetch education data from NCES/Urban API.
        
        Args:
            state: State abbreviation (e.g., 'RI')
            year: School year
            data_type: Type of data ('schools', 'enrollment', 'finance', 'graduation')
            
        Returns:
            DataFrame with requested data
            
        Example:
            >>> data = connector.fetch(state='RI', year=2023, data_type='schools')
        """
        state = kwargs.get('state')
        year = kwargs.get('year')
        data_type = kwargs.get('data_type', 'schools')
        
        if not state or not year:
            raise ValueError("Both 'state' and 'year' are required")
        
        if data_type == 'schools':
            return self.get_state_schools(state, year)
        elif data_type == 'enrollment':
            return self.get_enrollment_data(state, year)
        elif data_type == 'finance':
            return self.get_district_finance(state, year)
        elif data_type == 'graduation':
            return self.get_graduation_rates(state, year)
        else:
            raise ValueError(f"Unknown data_type: {data_type}")

    def load_school_data(self, filepath: Union[str, Path]) -> pd.DataFrame:
        """
        Load school data from downloaded CSV file.
        
        Args:
            filepath: Path to NCES CSV file
            
        Returns:
            DataFrame with school data
            
        Example:
            >>> schools = connector.load_school_data('ccd_schools_2023.csv')
        """
        self.logger.info("Loading school data", extra={"filepath": str(filepath)})
        
        # NCES files often have various encodings
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding='latin-1')
        
        self.logger.info(
            "School data loaded",
            extra={"rows": len(df), "columns": len(df.columns)}
        )
        
        return df

    def get_state_schools(
        self,
        state: str,
        year: int,
        use_api: bool = True
    ) -> pd.DataFrame:
        """
        Get school directory for a state.
        
        Args:
            state: State abbreviation (e.g., 'RI')
            year: School year
            use_api: Use API if True, otherwise requires pre-loaded data
            
        Returns:
            DataFrame with school information
            
        Example:
            >>> ri_schools = connector.get_state_schools('RI', 2023)
        """
        if use_api:
            return self._api_get_state_schools(state, year)
        else:
            self.logger.warning("API access disabled, load data from file")
            return pd.DataFrame()

    def _api_get_state_schools(self, state: str, year: int) -> pd.DataFrame:
        """
        Get state schools via API.
        
        Args:
            state: State abbreviation
            year: School year
            
        Returns:
            DataFrame with school directory
        """
        cache_key = f"nces_schools_{state}_{year}"
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            self.logger.info("Returning cached school data", extra={"state": state, "year": year})
            return pd.DataFrame(cached)
        
        # Urban API endpoint for CCD schools
        endpoint = f"{self.base_url}/schools/ccd/directory/{year}"
        params = {'fips': self._get_state_fips(state)}
        
        self.logger.info(
            "Fetching school data via API",
            extra={"state": state, "year": year}
        )
        
        try:
            response = requests.get(endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data:
                df = pd.DataFrame(data['results'])
            else:
                df = pd.DataFrame(data)
            
            # Cache result
            self.cache.set(cache_key, df.to_dict('records'))
            
            self.logger.info(
                "School data retrieved",
                extra={"state": state, "year": year, "schools": len(df)}
            )
            
            return df
            
        except requests.exceptions.RequestException as e:
            self.logger.error(
                f"API request failed: {e}",
                extra={"state": state, "year": year}
            )
            return pd.DataFrame()

    def _get_state_fips(self, state: str) -> int:
        """
        Convert state abbreviation to FIPS code.
        
        Args:
            state: State abbreviation
            
        Returns:
            FIPS code
        """
        # Simplified mapping - full implementation would have all 50 states
        fips_map = {
            'RI': 44, 'MA': 25, 'CT': 9, 'NY': 36, 'CA': 6,
            'TX': 48, 'FL': 12, 'IL': 17, 'PA': 42, 'OH': 39
        }
        return fips_map.get(state.upper(), 0)

    def get_enrollment_data(
        self,
        state: str,
        year: int,
        use_api: bool = True
    ) -> pd.DataFrame:
        """
        Get enrollment statistics for a state.
        
        Args:
            state: State abbreviation
            year: School year
            use_api: Use API if True
            
        Returns:
            DataFrame with enrollment data
            
        Example:
            >>> enrollment = connector.get_enrollment_data('RI', 2023)
        """
        if not use_api:
            self.logger.warning("API access disabled, load data from file")
            return pd.DataFrame()
        
        cache_key = f"nces_enrollment_{state}_{year}"
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            return pd.DataFrame(cached)
        
        # Use directory endpoint instead - enrollment is already included
        endpoint = f"{self.base_url}/schools/ccd/directory/{year}"
        params = {'fips': self._get_state_fips(state)}
        
        self.logger.info("Fetching enrollment data from directory", extra={"state": state, "year": year})
        
        try:
            response = requests.get(endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            df = pd.DataFrame(results)
            
            # Extract enrollment columns
            enrollment_cols = ['ncessch', 'school_name', 'leaid', 'lea_name']
            enrollment_cols += [col for col in df.columns if 'enrollment' in col.lower()]
            
            if enrollment_cols and all(col in df.columns or col in ['ncessch', 'school_name', 'leaid', 'lea_name'] for col in enrollment_cols):
                df = df[[col for col in enrollment_cols if col in df.columns]]
            
            self.cache.set(cache_key, df.to_dict('records'))
            
            self.logger.info(
                "Enrollment data retrieved",
                extra={"state": state, "year": year, "records": len(df)}
            )
            
            return df
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Enrollment API request failed: {e}")
            return pd.DataFrame()

    def get_demographics(self, schools_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract demographic information from school data.
        
        Args:
            schools_df: DataFrame with school information
            
        Returns:
            DataFrame with demographic columns
            
        Example:
            >>> demographics = connector.get_demographics(ri_schools)
        """
        demo_cols = [col for col in schools_df.columns if any(
            keyword in col.lower() for keyword in [
                'race', 'ethnicity', 'gender', 'asian', 'black', 'white',
                'hispanic', 'native', 'pacific', 'male', 'female'
            ]
        )]
        
        if demo_cols:
            result = schools_df[['ncessch', 'school_name'] + demo_cols] if 'ncessch' in schools_df.columns else schools_df[demo_cols]
        else:
            result = pd.DataFrame()
        
        self.logger.info(
            "Extracted demographics",
            extra={"columns": len(demo_cols)}
        )
        
        return result

    def get_graduation_rates(
        self,
        state: str,
        year: int,
        use_api: bool = True
    ) -> pd.DataFrame:
        """
        Get graduation rate statistics.
        
        Args:
            state: State abbreviation
            year: School year
            use_api: Use API if True
            
        Returns:
            DataFrame with graduation rates
            
        Example:
            >>> grad_rates = connector.get_graduation_rates('RI', 2023)
        """
        if not use_api:
            self.logger.warning("API access disabled, load data from file")
            return pd.DataFrame()
        
        cache_key = f"nces_grad_rates_{state}_{year}"
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            return pd.DataFrame(cached)
        
        # Note: Graduation rates from EDFacts have limited recent years
        # Try EDFacts school-level graduation rates
        endpoint = f"{self.base_url}/schools/edfacts/grad-rates/{year}"
        params = {'fips': self._get_state_fips(state)}
        
        self.logger.info("Fetching graduation rates", extra={"state": state, "year": year})
        
        try:
            response = requests.get(endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data.get('results', []))
            
            self.cache.set(cache_key, df.to_dict('records'))
            
            self.logger.info(
                "Graduation rates retrieved",
                extra={"state": state, "year": year, "records": len(df)}
            )
            
            return df
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Graduation rates API request failed: {e}")
            return pd.DataFrame()

    def get_district_finance(
        self,
        state: str,
        year: int,
        use_api: bool = True
    ) -> pd.DataFrame:
        """
        Get school district financial data.
        
        Args:
            state: State abbreviation
            year: School year
            use_api: Use API if True
            
        Returns:
            DataFrame with district finances
            
        Example:
            >>> finances = connector.get_district_finance('RI', 2023)
        """
        if not use_api:
            self.logger.warning("API access disabled, load data from file")
            return pd.DataFrame()
        
        cache_key = f"nces_finance_{state}_{year}"
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            return pd.DataFrame(cached)
        
        endpoint = f"{self.base_url}/school-districts/ccd/finance/{year}"
        params = {'fips': self._get_state_fips(state)}
        
        self.logger.info("Fetching district finances", extra={"state": state, "year": year})
        
        try:
            response = requests.get(endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data.get('results', data))
            
            self.cache.set(cache_key, df.to_dict('records'))
            
            self.logger.info(
                "District finances retrieved",
                extra={"state": state, "year": year, "districts": len(df)}
            )
            
            return df
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Finance API request failed: {e}")
            return pd.DataFrame()

    def calculate_per_pupil_spending(
        self,
        finance_df: pd.DataFrame,
        enrollment_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate per-pupil spending by district.
        
        Args:
            finance_df: District financial data
            enrollment_df: District enrollment data
            
        Returns:
            DataFrame with per-pupil spending
            
        Example:
            >>> per_pupil = connector.calculate_per_pupil_spending(
            ...     finances, enrollment
            ... )
        """
        # Merge finance and enrollment data
        merge_col = 'leaid' if 'leaid' in finance_df.columns else 'district_id'
        
        if merge_col not in finance_df.columns or merge_col not in enrollment_df.columns:
            self.logger.warning(f"Required column '{merge_col}' not found")
            return pd.DataFrame()
        
        merged = finance_df.merge(
            enrollment_df[[merge_col, 'enrollment']],
            on=merge_col,
            how='left'
        )
        
        # Calculate per-pupil spending
        if 'total_expenditures' in merged.columns and 'enrollment' in merged.columns:
            merged['per_pupil_spending'] = merged['total_expenditures'] / merged['enrollment']
        
        self.logger.info(
            "Calculated per-pupil spending",
            extra={"districts": len(merged)}
        )
        
        return merged

    def compare_districts(
        self,
        state: str,
        year: int,
        metric: str = 'enrollment'
    ) -> pd.DataFrame:
        """
        Compare metrics across districts in a state.
        
        Args:
            state: State abbreviation
            year: School year
            metric: Metric to compare ('enrollment', 'spending', 'graduation')
            
        Returns:
            DataFrame with district comparisons
            
        Example:
            >>> comparison = connector.compare_districts('RI', 2023, 'spending')
        """
        if metric == 'enrollment':
            data = self.get_enrollment_data(state, year)
        elif metric == 'spending':
            data = self.get_district_finance(state, year)
        elif metric == 'graduation':
            data = self.get_graduation_rates(state, year)
        else:
            self.logger.warning(f"Unknown metric: {metric}")
            return pd.DataFrame()
        
        self.logger.info(
            "Compared districts",
            extra={"state": state, "year": year, "metric": metric}
        )
        
        return data

    def get_school_performance(
        self,
        schools_df: pd.DataFrame,
        performance_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Extract performance metrics from school data.
        
        Args:
            schools_df: DataFrame with school data
            performance_cols: Optional list of performance columns
            
        Returns:
            DataFrame with performance metrics
        """
        if performance_cols is None:
            performance_cols = [col for col in schools_df.columns if any(
                keyword in col.lower() for keyword in [
                    'test', 'score', 'proficient', 'achievement',
                    'graduation', 'dropout', 'attendance'
                ]
            )]
        
        if performance_cols:
            result = schools_df[['ncessch', 'school_name'] + performance_cols] if 'ncessch' in schools_df.columns else schools_df[performance_cols]
        else:
            result = pd.DataFrame()
        
        self.logger.info(
            "Extracted performance metrics",
            extra={"columns": len(performance_cols)}
        )
        
        return result

    def export_to_csv(self, df: pd.DataFrame, filepath: Union[str, Path]) -> None:
        """
        Export DataFrame to CSV file.
        
        Args:
            df: DataFrame to export
            filepath: Output file path
        """
        df.to_csv(filepath, index=False)
        self.logger.info(
            "Exported to CSV",
            extra={"filepath": str(filepath), "rows": len(df)}
        )
