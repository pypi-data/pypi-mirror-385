# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
HUD Fair Market Rents (FMR) Connector

Provides access to HUD's Fair Market Rent data, including:
- Fair Market Rents by bedroom count (0BR - 4BR+)
- Income limits by household size
- Small Area FMRs (ZIP code level)
- 40th and 50th percentile rent estimates

**⚠️ DATA ACCESS NOTE:**

HUD provides FMR data through their website as downloadable datasets.
An API exists but is limited in functionality.

**Data Downloads:**
- **FMR Data**: https://www.huduser.gov/portal/datasets/fmr.html
  - Available formats: Excel, CSV
  - Geographic levels: Metro (CBSA), County, ZIP (Small Area FMRs)
  - Annual releases (typically October for following fiscal year)

**API Access (Limited):**
- **HUD USER APIs**: https://www.huduser.gov/portal/dataset/fmr-api.html
  - Requires API key registration
  - Rate limits apply

**Data Components:**
- **FMR**: Fair Market Rent by bedroom count
- **Income Limits**: Very Low, Low, and Median Income by household size
- **SAFMRs**: Small Area FMRs at ZIP code level
- **Metro vs Non-Metro**: Different calculation methodologies

**Data Domains:**
- D04: Housing Market & Affordability
- D03: Income & Poverty
- D11: Community Development

**Example Usage:**
    >>> from krl_data_connectors.housing import HUDFMRConnector
    >>> 
    >>> # Initialize connector
    >>> hud = HUDFMRConnector(api_key='your_api_key')
    >>> 
    >>> # Get FMRs for Rhode Island
    >>> ri_fmr = hud.get_state_fmrs('RI', year=2025)
    >>> 
    >>> # Get FMRs for specific metro area
    >>> providence_fmr = hud.get_metro_fmrs('Providence', year=2025)
    >>> 
    >>> # Calculate affordability (30% of income rule)
    >>> affordable = hud.calculate_affordability(income=50000, bedrooms=2)

---

Licensed under the Apache License, Version 2.0.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

from krl_data_connectors.base_connector import BaseConnector


class HUDFMRConnector(BaseConnector):
    """
    Connector for HUD Fair Market Rent data.
    
    **Data Sources:**
    - Fair Market Rents (FMRs) - Annual rent estimates by metro/county
    - Small Area FMRs (SAFMRs) - ZIP code level rent estimates
    - Income Limits - Low, very low, and median income thresholds
    
    **Bedroom Categories:**
    - 0BR (Studio/Efficiency)
    - 1BR (One Bedroom)
    - 2BR (Two Bedroom)
    - 3BR (Three Bedroom)
    - 4BR (Four+ Bedroom)
    
    **API Requirements:**
    - API key required for programmatic access
    - Register at: https://www.huduser.gov/portal/dataset/fmr-api.html
    - Rate limits: 1,200 requests/day
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,  # 24 hours
    ):
        """
        Initialize HUD FMR connector.
        
        Args:
            api_key: HUD USER API key
            cache_dir: Directory for caching data
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
        """
        super().__init__(
            api_key=api_key,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
        )
        
        self.base_url = "https://www.huduser.gov/hudapi/public"
        
        self.logger.info(
            "HUDFMRConnector initialized",
            extra={
                "has_api_key": bool(self.api_key),
                "base_url": self.base_url
            }
        )

    def _get_api_key(self) -> Optional[str]:
        """Get HUD API key from configuration."""
        return self.config.get("HUD_API_KEY")

    def connect(self) -> None:
        """
        HUD connector does not require explicit connection.
        
        The HUD API is stateless and does not require session setup.
        """
        pass

    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """
        Fetch HUD Fair Market Rent data.
        
        Args:
            state: State abbreviation (e.g., 'RI')
            year: Fiscal year
            data_type: Type of data ('fmr' only for now)
            
        Returns:
            DataFrame with requested data
            
        Example:
            >>> data = connector.fetch(state='RI', year=2025, data_type='fmr')
        """
        state = kwargs.get('state')
        year = kwargs.get('year')
        data_type = kwargs.get('data_type', 'fmr')
        
        if not state or not year:
            raise ValueError("Both 'state' and 'year' are required")
        
        if data_type == 'fmr':
            return self.get_state_fmrs(state, year)
        else:
            raise ValueError(f"Unknown data_type: {data_type}. Use 'fmr'.")

    def load_fmr_data(self, filepath: Union[str, Path]) -> pd.DataFrame:
        """
        Load FMR data from downloaded CSV/Excel file.
        
        Args:
            filepath: Path to FMR data file
            
        Returns:
            DataFrame with FMR data
            
        Example:
            >>> fmr = connector.load_fmr_data('FY2025_FMRs.csv')
        """
        self.logger.info("Loading FMR data", extra={"filepath": str(filepath)})
        
        filepath = Path(filepath)
        if filepath.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath)
        else:
            df = pd.read_csv(filepath, encoding='utf-8')
        
        self.logger.info(
            "FMR data loaded",
            extra={"rows": len(df), "columns": len(df.columns)}
        )
        
        return df

    def get_state_fmrs(
        self,
        state: str,
        year: Optional[int] = None,
        use_api: bool = True
    ) -> pd.DataFrame:
        """
        Get Fair Market Rents for a state.
        
        Args:
            state: State abbreviation (e.g., 'RI')
            year: Fiscal year (default: current year)
            use_api: Use API if available (default: True)
            
        Returns:
            DataFrame with FMR data for state
            
        Example:
            >>> ri_fmr = connector.get_state_fmrs('RI', year=2025)
        """
        if use_api and self.api_key:
            return self._api_get_state_fmrs(state, year)
        else:
            self.logger.warning("API access not available, please load from file")
            return pd.DataFrame()

    def _api_get_state_fmrs(self, state: str, year: Optional[int] = None) -> pd.DataFrame:
        """
        Get FMRs via API.
        
        Args:
            state: State abbreviation
            year: Fiscal year
            
        Returns:
            DataFrame with FMR data
        """
        if not self.api_key:
            raise ValueError("API key required for API access")
        
        # Construct API endpoint
        endpoint = f"{self.base_url}/fmr/statedata/{state}"
        
        params = {}
        if year:
            params['year'] = year
        
        # Make request
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        cache_key = f"fmr_state_{state}_{year or 'current'}"
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            self.logger.info("Returning cached FMR data", extra={"state": state})
            return pd.DataFrame(cached)
        
        self.logger.info(
            "Fetching FMR data via API",
            extra={"state": state, "year": year}
        )
        
        response = requests.get(endpoint, headers=headers, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle nested structure from state endpoint
        if 'data' in data and isinstance(data['data'], dict):
            # Combine metroareas and counties into single DataFrame
            records = []
            if 'metroareas' in data['data']:
                records.extend(data['data']['metroareas'])
            if 'counties' in data['data']:
                records.extend(data['data']['counties'])
            df = pd.DataFrame(records)
        elif 'data' in data:
            df = pd.DataFrame(data['data'])
        else:
            df = pd.DataFrame(data)
        
        # Standardize column names for FMR values
        column_mapping = {
            'Efficiency': 'fmr_0br',
            'One-Bedroom': 'fmr_1br',
            'Two-Bedroom': 'fmr_2br',
            'Three-Bedroom': 'fmr_3br',
            'Four-Bedroom': 'fmr_4br'
        }
        df = df.rename(columns=column_mapping)
        
        # Cache result
        self.cache.set(cache_key, df.to_dict('records'))
        
        self.logger.info(
            "FMR data retrieved",
            extra={"state": state, "rows": len(df)}
        )
        
        return df

    def get_metro_fmrs(
        self,
        metro_name: str,
        year: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get FMRs for a specific metro area.
        
        Args:
            metro_name: Metro area name
            year: Fiscal year
            
        Returns:
            DataFrame with metro FMR data
            
        Example:
            >>> providence = connector.get_metro_fmrs('Providence', year=2025)
        """
        self.logger.info(
            "Fetching metro FMRs",
            extra={"metro": metro_name, "year": year}
        )
        
        # Note: This would use API or require pre-loaded data
        self.logger.warning("Metro FMR lookup requires pre-loaded data file")
        return pd.DataFrame()

    def get_county_fmrs(
        self,
        state: str,
        county: str,
        year: Optional[int] = None,
        data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Get FMRs for a specific county.
        
        Args:
            state: State abbreviation
            county: County name
            year: Fiscal year
            data: Pre-loaded FMR DataFrame (optional)
            
        Returns:
            DataFrame with county FMR data
            
        Example:
            >>> providence = connector.get_county_fmrs('RI', 'Providence', data=fmr_data)
        """
        if data is None:
            self.logger.warning("No data provided, load FMR data first")
            return pd.DataFrame()
        
        # Filter by state and county
        filtered = data[
            (data['state_alpha'].str.upper() == state.upper()) &
            (data['county_name'].str.contains(county, case=False, na=False))
        ]
        
        self.logger.info(
            "Filtered county FMRs",
            extra={"state": state, "county": county, "rows": len(filtered)}
        )
        
        return filtered

    def get_fmr_by_bedrooms(
        self,
        data: pd.DataFrame,
        bedrooms: Union[int, str]
    ) -> pd.DataFrame:
        """
        Extract FMR values for specific bedroom count.
        
        Args:
            data: DataFrame with FMR data
            bedrooms: Bedroom count (0, 1, 2, 3, 4) or 'all'
            
        Returns:
            DataFrame with FMR column for specified bedrooms
            
        Example:
            >>> fmr_2br = connector.get_fmr_by_bedrooms(fmr_data, bedrooms=2)
        """
        if bedrooms == 'all':
            return data
        
        # Column naming varies: 'fmr_0', 'fmr0', 'FMR_0BR', etc.
        br_col = f'fmr_{bedrooms}'
        alt_br_cols = [
            f'fmr{bedrooms}',
            f'FMR_{bedrooms}BR',
            f'{bedrooms}BR',
            f'Rent_{bedrooms}BR'
        ]
        
        for col in [br_col] + alt_br_cols:
            if col in data.columns:
                return data[['county_name', col] if 'county_name' in data.columns else [col]]
        
        self.logger.warning(
            f"No FMR column found for {bedrooms} bedrooms",
            extra={"columns": list(data.columns)}
        )
        return pd.DataFrame()

    def calculate_affordability(
        self,
        income: float,
        bedrooms: int,
        fmr_value: Optional[float] = None,
        income_threshold: float = 0.30
    ) -> Dict[str, Any]:
        """
        Calculate housing affordability based on 30% income rule.
        
        Args:
            income: Annual household income
            bedrooms: Bedroom count
            fmr_value: Fair Market Rent (monthly)
            income_threshold: Percent of income for rent (default: 0.30)
            
        Returns:
            Dictionary with affordability metrics
            
        Example:
            >>> afford = connector.calculate_affordability(
            ...     income=50000,
            ...     bedrooms=2,
            ...     fmr_value=1200
            ... )
            >>> print(f"Affordable: {afford['is_affordable']}")
        """
        monthly_income = income / 12
        max_affordable_rent = monthly_income * income_threshold
        
        result = {
            'annual_income': income,
            'monthly_income': monthly_income,
            'max_affordable_rent': max_affordable_rent,
            'income_threshold_pct': income_threshold * 100,
            'bedrooms': bedrooms
        }
        
        if fmr_value:
            result['fmr'] = fmr_value
            result['is_affordable'] = fmr_value <= max_affordable_rent
            result['rent_to_income_ratio'] = (fmr_value / monthly_income) * 100
            result['monthly_surplus_deficit'] = max_affordable_rent - fmr_value
        
        self.logger.info(
            "Calculated affordability",
            extra=result
        )
        
        return result

    def get_income_limits(
        self,
        state: str,
        county: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get HUD income limits for area.
        
        Args:
            state: State abbreviation
            county: County name
            year: Fiscal year
            
        Returns:
            Dictionary with income limits by category
            
        Example:
            >>> limits = connector.get_income_limits('RI', 'Providence')
        """
        if not self.api_key:
            self.logger.warning("API key required for income limits")
            return {}
        
        # This would use HUD Income Limits API
        endpoint = f"{self.base_url}/il/statedata/{state}"
        
        self.logger.info(
            "Fetching income limits",
            extra={"state": state, "county": county, "year": year}
        )
        
        # Placeholder - actual API implementation would go here
        return {
            'very_low_income': None,
            'low_income': None,
            'median_income': None,
            'state': state,
            'county': county
        }

    def compare_fmrs(
        self,
        data: pd.DataFrame,
        regions: List[str],
        bedrooms: int = 2
    ) -> pd.DataFrame:
        """
        Compare FMRs across multiple regions.
        
        Args:
            data: DataFrame with FMR data
            regions: List of county/metro names
            bedrooms: Bedroom count to compare
            
        Returns:
            DataFrame with comparison
            
        Example:
            >>> comparison = connector.compare_fmrs(
            ...     fmr_data,
            ...     ['Providence', 'Kent', 'Washington'],
            ...     bedrooms=2
            ... )
        """
        comparison = []
        
        for region in regions:
            region_data = data[data['county_name'].str.contains(region, case=False, na=False)]
            if not region_data.empty:
                fmr_col = f'fmr_{bedrooms}'
                if fmr_col in region_data.columns:
                    comparison.append({
                        'region': region,
                        'fmr': region_data[fmr_col].iloc[0],
                        'bedrooms': bedrooms
                    })
        
        result_df = pd.DataFrame(comparison)
        
        self.logger.info(
            "Compared FMRs",
            extra={"regions": len(regions), "bedrooms": bedrooms}
        )
        
        return result_df

    def calculate_yoy_change(
        self,
        current_year_data: pd.DataFrame,
        previous_year_data: pd.DataFrame,
        bedrooms: int = 2
    ) -> pd.DataFrame:
        """
        Calculate year-over-year FMR changes.
        
        Args:
            current_year_data: Current year FMR data
            previous_year_data: Previous year FMR data
            bedrooms: Bedroom count to analyze (0-4)
            
        Returns:
            DataFrame with YoY change metrics
        """
        fmr_col = f'fmr_{bedrooms}br'
        
        if fmr_col not in current_year_data.columns or fmr_col not in previous_year_data.columns:
            self.logger.warning(f"FMR column '{fmr_col}' not found")
            return pd.DataFrame()
        
        # Merge on county_name (for counties) or metro_name (for metros)
        # Create a merge key that works for both
        current = current_year_data.copy()
        previous = previous_year_data.copy()
        
        # Use county_name if available, otherwise use metro_name
        current['merge_key'] = current.apply(
            lambda x: x['county_name'] if pd.notna(x.get('county_name')) else x.get('metro_name', ''),
            axis=1
        )
        previous['merge_key'] = previous.apply(
            lambda x: x['county_name'] if pd.notna(x.get('county_name')) else x.get('metro_name', ''),
            axis=1
        )
        
        # Merge on the key
        merged = current.merge(
            previous[['merge_key', fmr_col]],
            on='merge_key',
            suffixes=('_current', '_previous'),
            how='inner'
        )
        
        # Calculate change
        merged['fmr_change'] = merged[f'{fmr_col}_current'] - merged[f'{fmr_col}_previous']
        merged['fmr_change_pct'] = (merged['fmr_change'] / merged[f'{fmr_col}_previous']) * 100
        
        self.logger.info(
            "Calculated YoY change",
            extra={"rows": len(merged), "bedrooms": bedrooms}
        )
        
        return merged

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
