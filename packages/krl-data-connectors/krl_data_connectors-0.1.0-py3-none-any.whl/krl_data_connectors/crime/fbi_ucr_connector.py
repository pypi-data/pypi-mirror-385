# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
FBI Uniform Crime Reporting (UCR) Connector

Provides access to FBI UCR crime statistics, including:
- Violent Crime: Murder, rape, robbery, aggravated assault
- Property Crime: Burglary, larceny-theft, motor vehicle theft, arson
- Arrest Data: Arrests by offense type, age, sex, race
- Law Enforcement: Agency participation, officer assaults, officers killed

**⚠️ DATA ACCESS NOTE:**

The FBI UCR Program provides data through downloadable files and the Crime Data Explorer (CDE) API.

**Data Sources:**
- **Crime Data Explorer API**: https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/docApi
  - RESTful API for programmatic access
  - No API key required
  - Rate limits apply
  
- **Downloadable Data**: https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/downloads
  - CSV files with historical data
  - National, state, and agency-level data

**Data Categories:**
- **Offenses Known**: Reported crimes by type
- **Arrests**: Arrest counts by offense, demographics
- **Law Enforcement Officers**: Officers killed/assaulted
- **Hate Crime**: Bias-motivated incidents

**Data Domains:**
- D10: Public Safety & Crime
- D19: Governance & Civic Infrastructure
- D24: Geographic & Spatial Data

**Example Usage:**
    >>> from krl_data_connectors.crime import FBIUCRConnector
    >>> 
    >>> # Initialize connector
    >>> fbi = FBIUCRConnector()
    >>> 
    >>> # Get state crime data
    >>> ri_crime = fbi.get_state_crime_data('RI', year=2023)
    >>> 
    >>> # Get violent crime trends
    >>> violent = fbi.get_violent_crime(ri_crime)
    >>> 
    >>> # Compare crime rates across states
    >>> comparison = fbi.compare_states(['RI', 'MA', 'CT'], year=2023)

---

Licensed under the Apache License, Version 2.0.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

from krl_data_connectors.base_connector import BaseConnector


class FBIUCRConnector(BaseConnector):
    """
    Connector for FBI Uniform Crime Reporting (UCR) data.
    
    **Crime Categories:**
    - **Violent Crime**: Murder, rape, robbery, aggravated assault
    - **Property Crime**: Burglary, larceny, motor vehicle theft, arson
    - **Other**: Fraud, embezzlement, vandalism, weapons violations
    
    **Geographic Levels:**
    - National (aggregate)
    - State
    - Agency (individual police departments)
    
    **Data Availability:**
    - Historical data: 1960-present
    - Updated: Annually
    - Coverage: ~18,000 law enforcement agencies
    
    **API Access:**
    - No API key required
    - Rate limits: Reasonable use
    - Base URL: https://api.usa.gov/crime/fbi/cde
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 604800,  # 7 days
    ):
        """
        Initialize FBI UCR connector.
        
        Args:
            api_key: Optional API key (not required)
            cache_dir: Directory for caching data
            cache_ttl: Cache time-to-live in seconds (default: 7 days)
        """
        super().__init__(
            api_key=api_key,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
        )
        
        self.base_url = "https://api.usa.gov/crime/fbi/cde"
        
        self.violent_crimes = ['murder', 'rape', 'robbery', 'aggravated-assault']
        self.property_crimes = ['burglary', 'larceny', 'motor-vehicle-theft', 'arson']
        
        self.logger.info(
            "FBIUCRConnector initialized",
            extra={"base_url": self.base_url, "api_access": "Public"}
        )

    def _get_api_key(self) -> Optional[str]:
        """FBI UCR API does not require an API key."""
        return None

    def connect(self) -> None:
        """
        FBI UCR connector does not require explicit connection.
        
        The Crime Data Explorer API is publicly accessible without
        authentication or session management.
        """
        pass

    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """
        Fetch FBI UCR crime data.
        
        Args:
            state: State abbreviation (e.g., 'RI')
            year: Year of data
            data_type: Type of data ('state', 'violent', 'property')
            
        Returns:
            DataFrame with requested crime data
            
        Example:
            >>> data = connector.fetch(state='RI', year=2023, data_type='state')
        """
        state = kwargs.get('state')
        year = kwargs.get('year')
        data_type = kwargs.get('data_type', 'state')
        
        if not state or not year:
            raise ValueError("Both 'state' and 'year' are required")
        
        if data_type == 'state':
            return self.get_state_crime_data(state, year)
        elif data_type == 'violent':
            state_data = self.get_state_crime_data(state, year)
            return self.get_violent_crime(state_data)
        elif data_type == 'property':
            state_data = self.get_state_crime_data(state, year)
            return self.get_property_crime(state_data)
        else:
            raise ValueError(f"Unknown data_type: {data_type}. Use 'state', 'violent', or 'property'.")

    def load_crime_data(self, filepath: Union[str, Path]) -> pd.DataFrame:
        """
        Load crime data from downloaded CSV file.
        
        Args:
            filepath: Path to UCR CSV file
            
        Returns:
            DataFrame with crime data
            
        Example:
            >>> crime_data = connector.load_crime_data('ucr_2023.csv')
        """
        self.logger.info("Loading crime data", extra={"filepath": str(filepath)})
        
        df = pd.read_csv(filepath, encoding='utf-8')
        
        self.logger.info(
            "Crime data loaded",
            extra={"rows": len(df), "columns": len(df.columns)}
        )
        
        return df

    def get_state_crime_data(
        self,
        state: str,
        year: int,
        use_api: bool = True
    ) -> pd.DataFrame:
        """
        Get crime statistics for a state.
        
        Args:
            state: State abbreviation (e.g., 'RI')
            year: Year of data
            use_api: Use API if True, otherwise requires pre-loaded data
            
        Returns:
            DataFrame with state crime data
            
        Example:
            >>> ri_crime = connector.get_state_crime_data('RI', 2023)
        """
        if use_api:
            return self._api_get_state_crime(state, year)
        else:
            self.logger.warning("API access disabled, load data from file")
            return pd.DataFrame()

    def _api_get_state_crime(self, state: str, year: int) -> pd.DataFrame:
        """
        Get state crime data via API.
        
        Args:
            state: State abbreviation
            year: Year of data
            
        Returns:
            DataFrame with crime statistics
        """
        cache_key = f"ucr_state_{state}_{year}"
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            self.logger.info("Returning cached crime data", extra={"state": state, "year": year})
            return pd.DataFrame(cached)
        
        # Construct API endpoint
        endpoint = f"{self.base_url}/crime/state/{state}"
        params: Dict[str, Union[int, str]] = {'year': year}
        
        # Add API key if available (required by FBI CDE API)
        if self.api_key:
            params['api_key'] = self.api_key
        
        self.logger.info(
            "Fetching crime data via API",
            extra={"state": state, "year": year, "has_api_key": bool(self.api_key)}
        )
        
        try:
            response = requests.get(endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data:
                df = pd.DataFrame(data['data'])
            else:
                df = pd.DataFrame([data])
            
            # Cache result
            self.cache.set(cache_key, df.to_dict('records'))
            
            self.logger.info(
                "Crime data retrieved",
                extra={"state": state, "year": year, "rows": len(df)}
            )
            
            return df
            
        except requests.exceptions.RequestException as e:
            self.logger.error(
                f"API request failed: {e}",
                extra={"state": state, "year": year}
            )
            return pd.DataFrame()

    def get_violent_crime(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract violent crime statistics from dataset.
        
        Args:
            data: DataFrame with crime data
            
        Returns:
            DataFrame with violent crime columns
            
        Example:
            >>> violent = connector.get_violent_crime(crime_data)
        """
        violent_cols = [col for col in data.columns if any(
            crime in col.lower() for crime in ['murder', 'rape', 'robbery', 'assault', 'violent']
        )]
        
        if violent_cols:
            result = data[['year', 'state'] + violent_cols] if 'year' in data.columns else data[violent_cols]
        else:
            result = pd.DataFrame()
        
        self.logger.info(
            "Extracted violent crime",
            extra={"columns": len(violent_cols)}
        )
        
        return result

    def get_property_crime(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract property crime statistics from dataset.
        
        Args:
            data: DataFrame with crime data
            
        Returns:
            DataFrame with property crime columns
        """
        property_cols = [col for col in data.columns if any(
            crime in col.lower() for crime in ['burglary', 'larceny', 'theft', 'arson', 'property']
        )]
        
        if property_cols:
            result = data[['year', 'state'] + property_cols] if 'year' in data.columns else data[property_cols]
        else:
            result = pd.DataFrame()
        
        self.logger.info(
            "Extracted property crime",
            extra={"columns": len(property_cols)}
        )
        
        return result

    def calculate_crime_rate(
        self,
        data: pd.DataFrame,
        crime_col: str,
        population_col: str = 'population',
        per_capita: int = 100000
    ) -> pd.DataFrame:
        """
        Calculate crime rate per capita.
        
        Args:
            data: DataFrame with crime counts and population
            crime_col: Column with crime counts
            population_col: Column with population
            per_capita: Rate denominator (default: 100,000)
            
        Returns:
            DataFrame with rate column added
            
        Example:
            >>> with_rates = connector.calculate_crime_rate(
            ...     crime_data,
            ...     crime_col='violent_crime',
            ...     per_capita=100000
            ... )
        """
        if crime_col not in data.columns or population_col not in data.columns:
            self.logger.warning(
                f"Required columns not found",
                extra={"crime_col": crime_col, "population_col": population_col}
            )
            return data
        
        data = data.copy()
        rate_col = f'{crime_col}_rate'
        data[rate_col] = (data[crime_col] / data[population_col]) * per_capita
        
        self.logger.info(
            "Calculated crime rate",
            extra={"crime_col": crime_col, "per_capita": per_capita}
        )
        
        return data

    def compare_states(
        self,
        states: List[str],
        year: int,
        crime_type: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Compare crime statistics across multiple states.
        
        Args:
            states: List of state abbreviations
            year: Year of data
            crime_type: Optional crime type filter ('violent', 'property', or None for all)
            
        Returns:
            DataFrame with comparison
            
        Example:
            >>> comparison = connector.compare_states(
            ...     ['RI', 'MA', 'CT'],
            ...     year=2023,
            ...     crime_type='violent'
            ... )
        """
        all_data = []
        
        for state in states:
            state_data = self.get_state_crime_data(state, year)
            if not state_data.empty:
                all_data.append(state_data)
        
        if not all_data:
            return pd.DataFrame()
        
        comparison = pd.concat(all_data, ignore_index=True)
        
        if crime_type == 'violent':
            comparison = self.get_violent_crime(comparison)
        elif crime_type == 'property':
            comparison = self.get_property_crime(comparison)
        
        self.logger.info(
            "Compared states",
            extra={"states": len(states), "year": year, "crime_type": crime_type}
        )
        
        return comparison

    def calculate_yoy_change(
        self,
        current_year: pd.DataFrame,
        previous_year: pd.DataFrame,
        crime_col: str
    ) -> pd.DataFrame:
        """
        Calculate year-over-year change in crime.
        
        Args:
            current_year: Current year crime data
            previous_year: Previous year crime data
            crime_col: Crime column to analyze
            
        Returns:
            DataFrame with YoY change metrics
        """
        if crime_col not in current_year.columns or crime_col not in previous_year.columns:
            self.logger.warning(f"Crime column '{crime_col}' not found")
            return pd.DataFrame()
        
        # Merge on state/agency
        merge_col = 'state' if 'state' in current_year.columns else 'agency'
        
        merged = current_year.merge(
            previous_year[[merge_col, crime_col]],
            on=merge_col,
            suffixes=('_current', '_previous')
        )
        
        merged['yoy_change'] = merged[f'{crime_col}_current'] - merged[f'{crime_col}_previous']
        merged['yoy_change_pct'] = (merged['yoy_change'] / merged[f'{crime_col}_previous']) * 100
        
        self.logger.info(
            "Calculated YoY change",
            extra={"crime_type": crime_col, "regions": len(merged)}
        )
        
        return merged

    def get_trend_data(
        self,
        state: str,
        start_year: int,
        end_year: int
    ) -> pd.DataFrame:
        """
        Get multi-year trend data for a state.
        
        Args:
            state: State abbreviation
            start_year: Start year
            end_year: End year
            
        Returns:
            DataFrame with trend data
            
        Example:
            >>> trends = connector.get_trend_data('RI', 2018, 2023)
        """
        years = range(start_year, end_year + 1)
        all_data = []
        
        for year in years:
            year_data = self.get_state_crime_data(state, year)
            if not year_data.empty:
                year_data['year'] = year
                all_data.append(year_data)
        
        if not all_data:
            return pd.DataFrame()
        
        trends = pd.concat(all_data, ignore_index=True)
        
        self.logger.info(
            "Retrieved trend data",
            extra={"state": state, "years": len(years), "rows": len(trends)}
        )
        
        return trends

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
