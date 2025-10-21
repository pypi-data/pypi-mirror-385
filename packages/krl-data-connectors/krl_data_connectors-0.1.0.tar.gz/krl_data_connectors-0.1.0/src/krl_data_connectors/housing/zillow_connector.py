# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Zillow Open Data Connector

Provides access to Zillow housing market data, including:
- Home values (ZHVI - Zillow Home Value Index)
- Rental prices (ZRI - Zillow Rent Index)
- Inventory metrics (homes for sale, new listings)
- Market forecasts
- Market temperature indicators

**⚠️ DATA ACCESS NOTE:**

Zillow provides data through their Research Data portal as downloadable CSV files.
There is no official REST API for programmatic access.

**Data Downloads:**
- **Zillow Research Data**: https://www.zillow.com/research/data/
  - Available formats: CSV
  - Geographic levels: National, State, Metro, County, City, ZIP, Neighborhood
  - Time series: Monthly data (varies by dataset)

**Data Categories:**
- **Home Values (ZHVI)**: Smoothed, seasonally adjusted measure of typical home value
- **Rentals (ZRI)**: Smoothed measure of typical market rate rent
- **Sales**: List prices, sale prices, price cuts
- **Inventory**: For-sale homes, new listings, days on market
- **Forecasts**: Expected value changes over 1-year horizon

**Data Domains:**
- D04: Housing Market & Affordability
- D11: Community Development & Neighborhood Vitality
- D24: Geographic & Spatial Data

**Example Usage:**
    >>> from krl_data_connectors.housing import ZillowConnector
    >>> 
    >>> # Initialize connector
    >>> zillow = ZillowConnector()
    >>> 
    >>> # Load ZHVI data from downloaded CSV
    >>> zhvi_data = zillow.load_zhvi_data('ZHVI_SingleFamilyResidence.csv')
    >>> 
    >>> # Get data for specific state
    >>> ri_values = zillow.get_state_data(zhvi_data, 'RI')
    >>> 
    >>> # Get metro area data
    >>> providence_data = zillow.get_metro_data(zhvi_data, 'Providence, RI')
    >>> 
    >>> # Calculate year-over-year growth
    >>> growth = zillow.calculate_yoy_growth(ri_values)

---

Licensed under the Apache License, Version 2.0.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import numpy as np

from krl_data_connectors.base_connector import BaseConnector


class ZillowConnector(BaseConnector):
    """
    Connector for Zillow Research Data.
    
    **⚠️ IMPORTANT**: Zillow does not provide a programmatic API. This connector is designed
    to work with CSV files downloaded from Zillow Research Data portal.
    
    **Supported Data Types:**
    - **ZHVI** (Zillow Home Value Index): Typical home values
    - **ZRI** (Zillow Rent Index): Typical market rent
    - **Sales**: List prices, sale prices, sold homes
    - **Inventory**: For-sale inventory, new listings
    - **Forecasts**: Expected value changes
    
    **Geographic Levels:**
    - National
    - State
    - Metro (CBSA)
    - County
    - City
    - ZIP Code
    - Neighborhood
    
    **Time Frequency:**
    - Monthly time series data
    - Historical data varies by dataset (typically 1996-present)
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,  # 24 hours
    ):
        """
        Initialize Zillow connector.
        
        Args:
            cache_dir: Directory for caching data
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
        """
        super().__init__(
            api_key=None,  # No API key needed
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
        )
        
        self.logger.info(
            "ZillowConnector initialized",
            extra={"data_source": "Zillow Research Data (file-based)"}
        )

    def _get_api_key(self) -> Optional[str]:
        """Zillow Research Data does not require an API key."""
        return None

    def connect(self) -> None:
        """
        Zillow connector does not require explicit connection.
        
        Zillow Research Data is accessed via downloadable CSV files,
        not a live API connection.
        """
        pass

    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """
        Fetch Zillow housing data.
        
        Args:
            filepath: Path to Zillow CSV file
            data_type: Type of data ('zhvi', 'zri', 'inventory', 'sales')
            state: Optional state filter
            
        Returns:
            DataFrame with requested data
            
        Example:
            >>> data = connector.fetch(filepath='ZHVI.csv', data_type='zhvi', state='RI')
        """
        filepath = kwargs.get('filepath')
        data_type = kwargs.get('data_type', 'zhvi')
        state = kwargs.get('state')
        
        if not filepath:
            raise ValueError("'filepath' is required")
        
        if data_type == 'zhvi':
            df = self.load_zhvi_data(filepath)
        elif data_type == 'zri':
            df = self.load_zri_data(filepath)
        elif data_type == 'inventory':
            df = self.load_inventory_data(filepath)
        elif data_type == 'sales':
            df = self.load_sales_data(filepath)
        else:
            raise ValueError(f"Unknown data_type: {data_type}")
        
        if state:
            df = self.get_state_data(df, state)
        
        return df

    def load_zhvi_data(self, filepath: Union[str, Path]) -> pd.DataFrame:
        """
        Load ZHVI (Zillow Home Value Index) data from CSV file.
        
        Args:
            filepath: Path to ZHVI CSV file
            
        Returns:
            DataFrame with ZHVI time series data
            
        Example:
            >>> zhvi = connector.load_zhvi_data('ZHVI_SingleFamily.csv')
            >>> print(zhvi.head())
        """
        self.logger.info("Loading ZHVI data", extra={"filepath": str(filepath)})
        
        df = pd.read_csv(filepath, encoding='utf-8')
        
        # Convert date columns to datetime
        date_cols = [col for col in df.columns if col.startswith('20') or col.startswith('19')]
        
        self.logger.info(
            "ZHVI data loaded",
            extra={
                "rows": len(df),
                "date_columns": len(date_cols),
                "geographic_levels": df.columns[0] if len(df.columns) > 0 else None
            }
        )
        
        return df

    def load_zri_data(self, filepath: Union[str, Path]) -> pd.DataFrame:
        """
        Load ZRI (Zillow Rent Index) data from CSV file.
        
        Args:
            filepath: Path to ZRI CSV file
            
        Returns:
            DataFrame with ZRI time series data
            
        Example:
            >>> zri = connector.load_zri_data('ZRI_AllHomes.csv')
            >>> print(zri.head())
        """
        self.logger.info("Loading ZRI data", extra={"filepath": str(filepath)})
        
        df = pd.read_csv(filepath, encoding='utf-8')
        
        self.logger.info(
            "ZRI data loaded",
            extra={"rows": len(df)}
        )
        
        return df

    def load_inventory_data(self, filepath: Union[str, Path]) -> pd.DataFrame:
        """
        Load inventory data (homes for sale, new listings) from CSV file.
        
        Args:
            filepath: Path to inventory CSV file
            
        Returns:
            DataFrame with inventory time series data
        """
        self.logger.info("Loading inventory data", extra={"filepath": str(filepath)})
        
        df = pd.read_csv(filepath, encoding='utf-8')
        
        self.logger.info(
            "Inventory data loaded",
            extra={"rows": len(df)}
        )
        
        return df

    def load_sales_data(self, filepath: Union[str, Path]) -> pd.DataFrame:
        """
        Load sales data (list prices, sale prices) from CSV file.
        
        Args:
            filepath: Path to sales CSV file
            
        Returns:
            DataFrame with sales time series data
        """
        self.logger.info("Loading sales data", extra={"filepath": str(filepath)})
        
        df = pd.read_csv(filepath, encoding='utf-8')
        
        self.logger.info(
            "Sales data loaded",
            extra={"rows": len(df)}
        )
        
        return df

    def get_state_data(self, df: pd.DataFrame, state: Union[str, List[str]]) -> pd.DataFrame:
        """
        Filter data by state.
        
        Args:
            df: DataFrame with Zillow data
            state: State abbreviation (e.g., 'RI') or list of states
            
        Returns:
            Filtered DataFrame
            
        Example:
            >>> ri_data = connector.get_state_data(zhvi, 'RI')
            >>> northeast = connector.get_state_data(zhvi, ['RI', 'MA', 'CT'])
        """
        if isinstance(state, str):
            state = [state]
        
        # Handle case-insensitive matching
        state = [s.upper() for s in state]
        
        if 'State' in df.columns:
            filtered = df[df['State'].str.upper().isin(state)]
        elif 'StateCodeFIPS' in df.columns:
            # Some datasets use FIPS codes
            filtered = df[df['StateCodeFIPS'].isin(state)]
        else:
            self.logger.warning("No state column found", extra={"columns": list(df.columns)})
            return pd.DataFrame()
        
        self.logger.info(
            "Filtered by state",
            extra={"states": state, "rows_returned": len(filtered)}
        )
        
        return filtered

    def get_metro_data(self, df: pd.DataFrame, metro: str) -> pd.DataFrame:
        """
        Filter data by metro area.
        
        Args:
            df: DataFrame with Zillow data
            metro: Metro area name (e.g., 'Providence, RI')
            
        Returns:
            Filtered DataFrame
            
        Example:
            >>> providence = connector.get_metro_data(zhvi, 'Providence, RI')
        """
        if 'Metro' in df.columns:
            filtered = df[df['Metro'].str.contains(metro, case=False, na=False)]
        elif 'RegionName' in df.columns and 'RegionType' in df.columns:
            # Some datasets use RegionName + RegionType
            metro_df = df[df['RegionType'] == 'msa']
            filtered = metro_df[metro_df['RegionName'].str.contains(metro, case=False, na=False)]
        else:
            self.logger.warning("No metro column found")
            return pd.DataFrame()
        
        self.logger.info(
            "Filtered by metro",
            extra={"metro": metro, "rows_returned": len(filtered)}
        )
        
        return filtered

    def get_county_data(self, df: pd.DataFrame, county: str, state: Optional[str] = None) -> pd.DataFrame:
        """
        Filter data by county.
        
        Args:
            df: DataFrame with Zillow data
            county: County name
            state: Optional state filter for disambiguation
            
        Returns:
            Filtered DataFrame
            
        Example:
            >>> providence_county = connector.get_county_data(zhvi, 'Providence', 'RI')
        """
        if 'CountyName' in df.columns:
            filtered = df[df['CountyName'].str.contains(county, case=False, na=False)]
            if state:
                filtered = filtered[filtered['State'].str.upper() == state.upper()]
        else:
            self.logger.warning("No county column found")
            return pd.DataFrame()
        
        self.logger.info(
            "Filtered by county",
            extra={"county": county, "state": state, "rows_returned": len(filtered)}
        )
        
        return filtered

    def get_zip_data(self, df: pd.DataFrame, zip_code: Union[str, int, List]) -> pd.DataFrame:
        """
        Filter data by ZIP code.
        
        Args:
            df: DataFrame with Zillow data
            zip_code: ZIP code(s) as string, int, or list
            
        Returns:
            Filtered DataFrame
            
        Example:
            >>> ri_zips = connector.get_zip_data(zhvi, ['02906', '02907', '02908'])
        """
        if isinstance(zip_code, (str, int)):
            zip_code = [str(zip_code)]
        else:
            zip_code = [str(z) for z in zip_code]
        
        if 'RegionName' in df.columns:
            # ZIP codes are typically in RegionName column
            filtered = df[df['RegionName'].astype(str).isin(zip_code)]
        else:
            self.logger.warning("No ZIP code column found")
            return pd.DataFrame()
        
        self.logger.info(
            "Filtered by ZIP",
            extra={"zip_codes": zip_code, "rows_returned": len(filtered)}
        )
        
        return filtered

    def get_time_series(self, df: pd.DataFrame, region_id: Optional[str] = None) -> pd.DataFrame:
        """
        Extract time series data from wide-format DataFrame.
        
        Args:
            df: DataFrame with Zillow data (wide format)
            region_id: Optional region identifier to filter
            
        Returns:
            DataFrame in long format with Date and Value columns
            
        Example:
            >>> ts = connector.get_time_series(ri_data)
        """
        # Identify date columns (typically '2015-01', '2015-02', etc.)
        date_cols = [col for col in df.columns if isinstance(col, str) and ('-' in col or col.isdigit())]
        
        if not date_cols:
            self.logger.warning("No date columns found")
            return pd.DataFrame()
        
        # Melt to long format
        id_vars = [col for col in df.columns if col not in date_cols]
        
        melted = df.melt(
            id_vars=id_vars,
            value_vars=date_cols,
            var_name='Date',
            value_name='Value'
        )
        
        # Convert date column to datetime
        melted['Date'] = pd.to_datetime(melted['Date'], errors='coerce')
        
        # Remove rows with null values
        melted = melted.dropna(subset=['Value'])
        
        self.logger.info(
            "Converted to time series",
            extra={"rows": len(melted), "date_range": f"{melted['Date'].min()} to {melted['Date'].max()}"}
        )
        
        return melted

    def calculate_yoy_growth(self, df: pd.DataFrame, value_col: str = 'Value') -> pd.DataFrame:
        """
        Calculate year-over-year growth rates.
        
        Args:
            df: DataFrame with time series data
            value_col: Name of value column
            
        Returns:
            DataFrame with YoY growth rate column added
            
        Example:
            >>> growth = connector.calculate_yoy_growth(ts_data)
        """
        df = df.copy()
        df = df.sort_values('Date')
        
        # Calculate YoY growth (12 months prior)
        df['YoY_Growth'] = df[value_col].pct_change(periods=12) * 100
        
        self.logger.info(
            "Calculated YoY growth",
            extra={"rows_with_growth": df['YoY_Growth'].notna().sum()}
        )
        
        return df

    def calculate_mom_growth(self, df: pd.DataFrame, value_col: str = 'Value') -> pd.DataFrame:
        """
        Calculate month-over-month growth rates.
        
        Args:
            df: DataFrame with time series data
            value_col: Name of value column
            
        Returns:
            DataFrame with MoM growth rate column added
        """
        df = df.copy()
        df = df.sort_values('Date')
        
        # Calculate MoM growth
        df['MoM_Growth'] = df[value_col].pct_change(periods=1) * 100
        
        self.logger.info(
            "Calculated MoM growth",
            extra={"rows_with_growth": df['MoM_Growth'].notna().sum()}
        )
        
        return df

    def get_latest_values(self, df: pd.DataFrame, n: int = 1) -> pd.DataFrame:
        """
        Get the most recent values for each region.
        
        Args:
            df: DataFrame with time series data
            n: Number of recent periods to return
            
        Returns:
            DataFrame with latest n periods
            
        Example:
            >>> latest = connector.get_latest_values(zhvi, n=3)  # Last 3 months
        """
        if 'Date' not in df.columns:
            self.logger.warning("No Date column found")
            return df
        
        df = df.sort_values('Date', ascending=False)
        
        if 'RegionName' in df.columns:
            # Group by region and take top n
            latest = df.groupby('RegionName').head(n)
        else:
            latest = df.head(n)
        
        self.logger.info(
            "Retrieved latest values",
            extra={"n_periods": n, "rows_returned": len(latest)}
        )
        
        return latest

    def calculate_summary_statistics(self, df: pd.DataFrame, value_col: str = 'Value') -> Dict[str, float]:
        """
        Calculate summary statistics for a time series.
        
        Args:
            df: DataFrame with time series data
            value_col: Name of value column
            
        Returns:
            Dictionary with summary statistics
            
        Example:
            >>> stats = connector.calculate_summary_statistics(ts_data)
            >>> print(f"Mean: ${stats['mean']:,.0f}")
        """
        stats = {
            'mean': df[value_col].mean(),
            'median': df[value_col].median(),
            'std': df[value_col].std(),
            'min': df[value_col].min(),
            'max': df[value_col].max(),
            'count': len(df[value_col].dropna())
        }
        
        self.logger.info(
            "Calculated summary statistics",
            extra=stats
        )
        
        return stats

    def export_to_csv(self, df: pd.DataFrame, filepath: Union[str, Path]) -> None:
        """
        Export DataFrame to CSV file.
        
        Args:
            filepath: Output file path
            df: DataFrame to export
        """
        df.to_csv(filepath, index=False)
        self.logger.info(
            "Exported to CSV",
            extra={"filepath": str(filepath), "rows": len(df)}
        )
