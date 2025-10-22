"""
EPA EJScreen Connector for environmental justice screening data.

EPA EJScreen (Environmental Justice Screening and Mapping Tool) provides:
- Environmental indicators (air quality, water, hazardous waste, etc.)
- Demographic indicators (race, income, education)
- EJ indexes combining environmental and demographic factors
- Census tract, block group, and county-level data

⚠️ **DATA ACCESS NOTE**: EPA EJScreen provides annual CSV/Shapefile downloads.
   - Main site (https://www.epa.gov/ejscreen) currently unavailable (404 errors)
   - Data typically released annually via FTP: https://gaftp.epa.gov/
   - This connector supports CSV file loading and parsing
   - Requires manual download or cached data files when EPA site unavailable

**Status**: BETA - Implementation complete, data access depends on EPA availability
**Recommendation**: Download EJScreen CSV files manually from EPA when available

© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..base_connector import BaseConnector

logger = logging.getLogger(__name__)


class EJScreenConnector(BaseConnector):
    """
    Connector for EPA EJScreen environmental justice data.

    ⚠️ **DATA ACCESS**: EPA EJScreen does NOT have a real-time API.
    Data is provided as annual CSV/Shapefile downloads. This connector supports
    loading and querying downloaded CSV files.

    **Current Status**: BETA - EPA main site unavailable (404 errors as of Oct 2025)
    **Recommendation**: Download EJScreen CSV files manually when EPA restores service

    EPA EJScreen provides environmental justice indicators at census tract level:
    - **Environmental Indicators**: PM2.5, ozone, diesel PM, toxic releases, etc.
    - **Demographic Indicators**: Minority population, low income, limited English, etc.
    - **EJ Indexes**: Combined environmental + demographic scores

    **Data Domains:**
    - D11: Environmental Quality (primary)
    - D12: Environmental Justice (primary)
    - D24: Geographic & Spatial Data (related)

    **Key Features:**
    - Census tract, block group, and county-level resolution
    - 11 environmental indicators
    - 6 demographic indicators
    - Pre-calculated EJ indexes
    - State and national percentile rankings

    Example:
        >>> from krl_data_connectors.environment import EJScreenConnector
        >>> ejs = EJScreenConnector()
        >>>
        >>> # Load from local CSV file
        >>> data = ejs.load_data('path/to/ejscreen_2024.csv')
        >>>
        >>> # Get data for Rhode Island
        >>> ri_data = ejs.get_state_data(data, state='RI')
        >>>
        >>> # Get high environmental burden tracts
        >>> high_burden = ejs.filter_by_threshold(
        ...     data,
        ...     indicator='P_PM25',  # PM2.5 percentile
        ...     threshold=80  # Top 20%
        ... )
    """

    # Environmental indicators (percentiles)
    ENVIRONMENTAL_INDICATORS = {
        "P_PM25": "Particulate Matter 2.5 (PM2.5)",
        "P_OZONE": "Ozone",
        "P_DSLPM": "Diesel Particulate Matter",
        "P_PTRAF": "Traffic Proximity",
        "P_LDPNT": "Lead Paint",
        "P_PNPL": "Superfund Proximity",
        "P_PRMP": "RMP Facility Proximity",
        "P_PTSDF": "Hazardous Waste Proximity",
        "P_UST": "Underground Storage Tanks",
        "P_PWDIS": "Wastewater Discharge",
    }

    # Demographic indicators (percentiles)
    DEMOGRAPHIC_INDICATORS = {
        "P_MINORTY": "People of Color",
        "P_LWINCPCT": "Low Income",
        "P_LNGISO": "Limited English Speaking",
        "P_LTHS": "Less Than High School",
        "P_UNDER5": "Under Age 5",
        "P_OVER64": "Over Age 64",
    }

    # EJ Index indicators (environmental × demographic)
    EJ_INDEX_INDICATORS = {
        "P_D2_PM25": "PM2.5 EJ Index",
        "P_D5_PM25": "PM2.5 EJ Index (supplemental)",
        "P_D2_OZONE": "Ozone EJ Index",
        "P_D5_OZONE": "Ozone EJ Index (supplemental)",
        "P_D2_DSLPM": "Diesel PM EJ Index",
        "P_D5_DSLPM": "Diesel PM EJ Index (supplemental)",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize EJScreen connector.

        Args:
            api_key: Not required (no API available)
            cache_dir: Directory for caching downloaded files
            timeout: Request timeout in seconds
        """
        super().__init__(api_key=api_key, cache_dir=cache_dir, timeout=timeout)

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key (not required for EJScreen).

        Returns:
            None (no API key required)
        """
        return None

    def connect(self) -> None:
        """
        Connect to data source (not applicable for file-based connector).
        """
        pass

    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from endpoint (not applicable for file-based connector).

        Args:
            **kwargs: Query parameters (not used)

        Raises:
            NotImplementedError: EJScreen uses file loading, not API fetching
        """
        raise NotImplementedError(
            "EJScreen connector uses load_data() for CSV files, not API fetching. "
            "Use load_data(file_path) to load EJScreen data from downloaded CSV files."
        )

    def load_data(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Load EJScreen data from local CSV file.

        Args:
            file_path: Path to EJScreen CSV file

        Returns:
            DataFrame with EJScreen data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid

        Example:
            >>> ejs = EJScreenConnector()
            >>> data = ejs.load_data('EJSCREEN_2024_StatePct_with_AS_CNMI_GU_VI.csv')
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"EJScreen data file not found: {file_path}")

        logger.info(f"Loading EJScreen data from {file_path}")

        try:
            df = pd.read_csv(file_path, low_memory=False)
            logger.info(f"Loaded {len(df)} records from EJScreen data")
            return df
        except Exception as e:
            raise ValueError(f"Failed to load EJScreen data: {e}")

    def get_state_data(
        self, data: pd.DataFrame, state: str, state_column: str = "ST_ABBREV"
    ) -> pd.DataFrame:
        """
        Filter EJScreen data by state.

        Args:
            data: EJScreen DataFrame
            state: Two-letter state code (e.g., 'RI', 'CA')
            state_column: Column name containing state codes

        Returns:
            DataFrame filtered to specified state

        Example:
            >>> data = ejs.load_data('ejscreen.csv')
            >>> ri_data = ejs.get_state_data(data, 'RI')
        """
        if state_column not in data.columns:
            raise ValueError(f"State column '{state_column}' not found in data")

        state = state.upper()
        filtered = data[data[state_column] == state].copy()

        logger.info(f"Filtered to {len(filtered)} records for state {state}")
        return filtered

    def get_county_data(
        self, data: pd.DataFrame, county_fips: str, fips_column: str = "CNTY_FIPS"
    ) -> pd.DataFrame:
        """
        Filter EJScreen data by county FIPS code.

        Args:
            data: EJScreen DataFrame
            county_fips: 5-digit county FIPS code
            fips_column: Column name containing county FIPS codes

        Returns:
            DataFrame filtered to specified county

        Example:
            >>> data = ejs.load_data('ejscreen.csv')
            >>> # Get data for Providence County, RI (FIPS 44007)
            >>> prov_data = ejs.get_county_data(data, '44007')
        """
        if fips_column not in data.columns:
            raise ValueError(f"County FIPS column '{fips_column}' not found in data")

        filtered = data[data[fips_column].astype(str).str.zfill(5) == county_fips].copy()

        logger.info(f"Filtered to {len(filtered)} records for county {county_fips}")
        return filtered

    def filter_by_threshold(
        self,
        data: pd.DataFrame,
        indicator: str,
        threshold: float,
        above: bool = True,
    ) -> pd.DataFrame:
        """
        Filter census tracts by indicator threshold (percentile).

        Args:
            data: EJScreen DataFrame
            indicator: Indicator column name (e.g., 'P_PM25', 'P_MINORTY')
            threshold: Percentile threshold (0-100)
            above: If True, return values >= threshold; if False, return <= threshold

        Returns:
            DataFrame filtered by threshold

        Example:
            >>> data = ejs.load_data('ejscreen.csv')
            >>> # Get tracts in top 20% for PM2.5
            >>> high_pm25 = ejs.filter_by_threshold(data, 'P_PM25', 80, above=True)
        """
        if indicator not in data.columns:
            raise ValueError(f"Indicator '{indicator}' not found in data")

        if above:
            filtered = data[data[indicator] >= threshold].copy()
            logger.info(f"Found {len(filtered)} tracts with {indicator} >= {threshold}")
        else:
            filtered = data[data[indicator] <= threshold].copy()
            logger.info(f"Found {len(filtered)} tracts with {indicator} <= {threshold}")

        return filtered

    def get_high_burden_tracts(
        self,
        data: pd.DataFrame,
        environmental_threshold: float = 80,
        demographic_threshold: float = 80,
        environmental_indicator: str = "P_PM25",
        demographic_indicator: str = "P_MINORTY",
    ) -> pd.DataFrame:
        """
        Identify high environmental justice burden tracts.

        Finds census tracts with both high environmental exposure and
        high demographic vulnerability (potential EJ communities).

        Args:
            data: EJScreen DataFrame
            environmental_threshold: Percentile threshold for environmental indicator
            demographic_threshold: Percentile threshold for demographic indicator
            environmental_indicator: Environmental indicator to use
            demographic_indicator: Demographic indicator to use

        Returns:
            DataFrame with high-burden tracts

        Example:
            >>> data = ejs.load_data('ejscreen.csv')
            >>> # Find tracts with high PM2.5 AND high minority population
            >>> ej_tracts = ejs.get_high_burden_tracts(
            ...     data,
            ...     environmental_threshold=80,
            ...     demographic_threshold=80,
            ...     environmental_indicator='P_PM25',
            ...     demographic_indicator='P_MINORTY'
            ... )
        """
        env_high = data[data[environmental_indicator] >= environmental_threshold]
        both_high = env_high[env_high[demographic_indicator] >= demographic_threshold].copy()

        logger.info(
            f"Found {len(both_high)} high-burden tracts "
            f"({environmental_indicator} >= {environmental_threshold}, "
            f"{demographic_indicator} >= {demographic_threshold})"
        )

        return both_high

    def get_available_indicators(self, data: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Get available indicators in the loaded data.

        Args:
            data: EJScreen DataFrame

        Returns:
            Dictionary with indicator categories and available columns

        Example:
            >>> data = ejs.load_data('ejscreen.csv')
            >>> indicators = ejs.get_available_indicators(data)
            >>> print(indicators['environmental'])
        """
        available = {
            "environmental": [k for k in self.ENVIRONMENTAL_INDICATORS if k in data.columns],
            "demographic": [k for k in self.DEMOGRAPHIC_INDICATORS if k in data.columns],
            "ej_index": [k for k in self.EJ_INDEX_INDICATORS if k in data.columns],
        }

        return available

    def summarize_by_state(
        self, data: pd.DataFrame, indicators: List[str], state_column: str = "ST_ABBREV"
    ) -> pd.DataFrame:
        """
        Calculate summary statistics by state for specified indicators.

        Args:
            data: EJScreen DataFrame
            indicators: List of indicator column names to summarize
            state_column: Column name containing state codes

        Returns:
            DataFrame with state-level summary statistics

        Example:
            >>> data = ejs.load_data('ejscreen.csv')
            >>> summary = ejs.summarize_by_state(
            ...     data,
            ...     indicators=['P_PM25', 'P_MINORTY', 'P_D2_PM25']
            ... )
        """
        if state_column not in data.columns:
            raise ValueError(f"State column '{state_column}' not found in data")

        missing_indicators = [i for i in indicators if i not in data.columns]
        if missing_indicators:
            raise ValueError(f"Indicators not found in data: {missing_indicators}")

        summary = (
            data.groupby(state_column)[indicators]
            .agg(["mean", "median", "min", "max"])
            .reset_index()
        )

        logger.info(f"Calculated state summary for {len(indicators)} indicators")
        return summary
