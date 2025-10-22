"""
County Health Rankings & Roadmaps Data Connector

Provides access to County Health Rankings data, including:
- Health Outcomes Rankings (Length of Life, Quality of Life)
- Health Factors Rankings (Health Behaviors, Clinical Care, Social & Economic, Physical Environment)
- 30+ health measures with county-level data
- Trend data (2010-present)

**⚠️ DATA ACCESS NOTE:**

County Health Rankings does NOT provide a REST API. Data is provided as annual
CSV and SAS file releases.

**Data Downloads:**
- **National Data**:
  https://www.countyhealthrankings.org/health-data/methodology-and-sources/rankings-data-documentation
  - Available formats: CSV, SAS
  - Annual releases (2010-present)
  - Analytic Data: Rankings + raw measures
  - Trends Data: Multi-year trends

**Data Structure:**
- **Health Outcomes** (weighted 50%):
  - Length of Life (50%): Premature death
  - Quality of Life (50%): Poor physical/mental health days, low birthweight

- **Health Factors** (weighted 50%):
  - Health Behaviors (30%): Smoking, obesity, physical inactivity, alcohol use, STIs
  - Clinical Care (20%): Uninsured, primary care physicians, preventable hospital stays
  - Social & Economic Factors (40%): Education, employment, income, family structure
  - Physical Environment (10%): Air pollution, housing quality, transit

**Data Domains:**
- D05: Healthcare Access & Affordability
- D06: Public Health & Wellness
- D24: Geographic & Spatial Data

**Example Usage:**
    >>> from krl_data_connectors.health import CountyHealthRankingsConnector
    >>>
    >>> # Initialize connector
    >>> chr = CountyHealthRankingsConnector()
    >>>
    >>> # Load 2025 rankings data
    >>> data = chr.load_rankings_data('chr_2025_analytic_data.csv')
    >>>
    >>> # Filter by state
    >>> ri_data = chr.get_state_data(data, 'RI')
    >>>
    >>> # Get health outcomes rankings
    >>> outcomes = chr.get_health_outcomes(ri_data)
    >>>
    >>> # Find poorest performing counties
    >>> poor_health = chr.get_poor_performers(ri_data, percentile=75)

---

© 2025 KR-Labs. All rights reserved.

KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector


class CountyHealthRankingsConnector(BaseConnector):
    """
    Connector for County Health Rankings & Roadmaps data.

    **⚠️ IMPORTANT**: CHR does not provide a programmatic API. This connector is designed
    to work with CSV files downloaded from the County Health Rankings website.

    **Ranking Categories:**
    - **Health Outcomes Rankings**: Overall health (1 = best, higher = worse)
    - **Health Factors Rankings**: Determinants of health
    - **Length of Life**: Premature death rates
    - **Quality of Life**: Physical and mental health
    - **Health Behaviors**: Tobacco, diet, exercise, alcohol, sexual activity
    - **Clinical Care**: Access to and quality of healthcare
    - **Social & Economic Factors**: Education, employment, income, family, safety
    - **Physical Environment**: Air quality, housing, transit

    **Ranking Scale:**
    - Rank 1 = Best performing county in state
    - Higher ranks = Poorer performance
    - Some counties excluded due to insufficient data

    Attributes:
        HEALTH_OUTCOME_MEASURES: Health outcome measure names
        HEALTH_FACTOR_MEASURES: Health factor measure names
        RANKING_COLUMNS: Common ranking column names
    """

    # Core ranking columns
    RANKING_COLUMNS = {
        "health_outcomes_rank",
        "health_factors_rank",
        "length_of_life_rank",
        "quality_of_life_rank",
        "health_behaviors_rank",
        "clinical_care_rank",
        "social_economic_factors_rank",
        "physical_environment_rank",
    }

    # Health outcome measures
    HEALTH_OUTCOME_MEASURES = {
        "premature_death",
        "poor_or_fair_health",
        "poor_physical_health_days",
        "poor_mental_health_days",
        "low_birthweight",
    }

    # Health factor measures
    HEALTH_FACTOR_MEASURES = {
        "adult_smoking",
        "adult_obesity",
        "physical_inactivity",
        "excessive_drinking",
        "uninsured",
        "primary_care_physicians",
        "unemployment",
        "children_in_poverty",
        "income_inequality",
        "high_school_graduation",
        "air_pollution_particulate_matter",
        "severe_housing_problems",
    }

    def __init__(
        self, cache_dir: Optional[Union[str, Path]] = None, cache_ttl: int = 86400, **kwargs: Any
    ) -> None:
        """
        Initialize County Health Rankings connector.

        Args:
            cache_dir: Directory for caching data (default: ~/.krl/cache/chr)
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
            **kwargs: Additional arguments passed to BaseConnector
        """
        super().__init__(
            api_key=None,
            cache_dir=str(cache_dir or Path.home() / ".krl" / "cache" / "chr"),
            cache_ttl=cache_ttl,
            **kwargs,
        )
        self.logger.info("County Health Rankings connector initialized (file-based)")

    def _get_api_key(self) -> Optional[str]:
        """No API key required for file-based connector."""
        return None

    def connect(self) -> None:
        """No connection needed for file-based connector."""
        pass

    def fetch(self, **kwargs: Any) -> Any:
        """
        Not supported for file-based connector.

        Raises:
            NotImplementedError: Always raised for file-based connector
        """
        raise NotImplementedError(
            "County Health Rankings does not provide an API. Use load_rankings_data() "
            "with downloaded CSV files from "
            "https://www.countyhealthrankings.org/health-data/methodology-and-sources/rankings-data-documentation"
        )

    def load_rankings_data(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Load County Health Rankings data from CSV file.

        Expected columns include:
        - statecode, state: State information
        - countycode, county: County information
        - v001_rawvalue: Premature death rate
        - v002_rawvalue: Poor or fair health %
        - v036_rawvalue: Adult smoking %
        - v011_rawvalue: Primary care physicians ratio
        - v023_rawvalue: Unemployment %
        - Various ranking columns (*_rank, *_numerator, *_denominator)

        Args:
            file_path: Path to CHR CSV file

        Returns:
            DataFrame with CHR data

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file format is invalid

        Example:
            >>> chr = CountyHealthRankingsConnector()
            >>> data = chr.load_rankings_data('chr_2025_analytic_data.csv')
            >>> print(f"Loaded {len(data)} county records")
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"CHR data file not found: {file_path}")

        self.logger.info(f"Loading CHR data from {file_path}")

        try:
            # CHR files often have multiple header rows - skip appropriately
            data = pd.read_csv(file_path, encoding="utf-8", low_memory=False)

            # Clean column names - CHR uses various naming conventions
            data.columns = data.columns.str.lower().str.strip()

            self.logger.info(f"Loaded {len(data)} county records with {len(data.columns)} columns")
            return data
        except Exception as e:
            self.logger.error(f"Failed to load CHR data: {e}")
            raise ValueError(f"Invalid CHR CSV format: {e}")

    def load_trends_data(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Load County Health Rankings trends data (multi-year) from CSV file.

        Trends data includes historical values for key measures from 2010-present.

        Args:
            file_path: Path to CHR trends CSV file

        Returns:
            DataFrame with CHR trends data

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file format is invalid
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"CHR trends data file not found: {file_path}")

        self.logger.info(f"Loading CHR trends data from {file_path}")

        try:
            data = pd.read_csv(file_path, encoding="utf-8", low_memory=False)
            data.columns = data.columns.str.lower().str.strip()

            self.logger.info(f"Loaded {len(data)} trend records with {len(data.columns)} columns")
            return data
        except Exception as e:
            self.logger.error(f"Failed to load CHR trends data: {e}")
            raise ValueError(f"Invalid CHR trends CSV format: {e}")

    def get_state_data(
        self, data: pd.DataFrame, state: str, state_column: str = "state"
    ) -> pd.DataFrame:
        """
        Filter data by state.

        Args:
            data: CHR DataFrame
            state: Two-letter state abbreviation (e.g., 'RI', 'CA') or full state name
            state_column: Name of state column (default: 'state')

        Returns:
            DataFrame filtered to specified state

        Example:
            >>> ri_data = chr.get_state_data(data, 'RI')
            >>> ri_data = chr.get_state_data(data, 'Rhode Island')
        """
        if state_column not in data.columns:
            # Try alternative column names
            alt_columns = ["statename", "state_name", "statecode", "state_abbr"]
            for col in alt_columns:
                if col in data.columns:
                    state_column = col
                    break
            else:
                raise ValueError(f"State column not found in data. Available: {list(data.columns)}")

        # Handle both state codes and full names
        state_upper = state.upper()
        filtered = data[
            (data[state_column].str.upper() == state_upper)
            | (data[state_column].str.upper() == state_upper[:2])
        ].copy()

        self.logger.info(f"Filtered to {len(filtered)} records for state: {state}")

        return filtered

    def get_county_data(
        self,
        data: pd.DataFrame,
        county: str,
        state: Optional[str] = None,
        county_column: str = "county",
    ) -> pd.DataFrame:
        """
        Filter data by county.

        Args:
            data: CHR DataFrame
            county: County name (case-insensitive)
            state: Optional two-letter state abbreviation for disambiguation
            county_column: Name of county column (default: 'county')

        Returns:
            DataFrame filtered to specified county

        Example:
            >>> providence = chr.get_county_data(data, 'Providence', state='RI')
        """
        if county_column not in data.columns:
            # Try alternative column names
            alt_columns = ["countyname", "county_name"]
            for col in alt_columns:
                if col in data.columns:
                    county_column = col
                    break
            else:
                raise ValueError("County column not found in data")

        # Case-insensitive county match
        filtered = data[data[county_column].str.lower() == county.lower()].copy()

        # Further filter by state if provided
        if state and len(filtered) > 0:
            filtered = self.get_state_data(filtered, state)

        self.logger.info(f"Filtered to {len(filtered)} records for county: {county}")

        return filtered

    def get_health_outcomes(
        self, data: pd.DataFrame, rank_column: str = "health_outcomes_rank"
    ) -> pd.DataFrame:
        """
        Get health outcomes data sorted by rank.

        Args:
            data: CHR DataFrame
            rank_column: Name of health outcomes rank column

        Returns:
            DataFrame sorted by health outcomes rank (best to worst)

        Example:
            >>> outcomes = chr.get_health_outcomes(ri_data)
            >>> best_county = outcomes.iloc[0]
        """
        # Try alternative column names if standard not found
        if rank_column not in data.columns:
            alt_columns = ["v063_rank", "healthoutcomesrank"]
            for col in alt_columns:
                if col in data.columns:
                    rank_column = col
                    break

        if rank_column in data.columns:
            # Sort by rank (1 = best)
            sorted_data = data.sort_values(rank_column).copy()
            self.logger.info(f"Sorted {len(sorted_data)} records by health outcomes rank")
            return sorted_data
        else:
            self.logger.warning("Health outcomes rank column not found")
            return data

    def get_health_factors(
        self, data: pd.DataFrame, rank_column: str = "health_factors_rank"
    ) -> pd.DataFrame:
        """
        Get health factors data sorted by rank.

        Args:
            data: CHR DataFrame
            rank_column: Name of health factors rank column

        Returns:
            DataFrame sorted by health factors rank (best to worst)

        Example:
            >>> factors = chr.get_health_factors(ri_data)
        """
        if rank_column not in data.columns:
            alt_columns = ["v062_rank", "healthfactorsrank"]
            for col in alt_columns:
                if col in data.columns:
                    rank_column = col
                    break

        if rank_column in data.columns:
            sorted_data = data.sort_values(rank_column).copy()
            self.logger.info(f"Sorted {len(sorted_data)} records by health factors rank")
            return sorted_data
        else:
            self.logger.warning("Health factors rank column not found")
            return data

    def get_top_performers(
        self, data: pd.DataFrame, n: int = 10, rank_column: str = "health_outcomes_rank"
    ) -> pd.DataFrame:
        """
        Get top performing counties (lowest rank = best).

        Args:
            data: CHR DataFrame
            n: Number of top counties to return
            rank_column: Ranking column to use

        Returns:
            DataFrame with top n performing counties

        Example:
            >>> top_10 = chr.get_top_performers(data, n=10)
        """
        if rank_column not in data.columns:
            raise ValueError(f"Rank column '{rank_column}' not found in data")

        # Filter out missing ranks and get top n
        valid_data = data[data[rank_column].notna()].copy()
        top_n = valid_data.nsmallest(n, rank_column)

        self.logger.info(f"Retrieved top {len(top_n)} performers by {rank_column}")

        return top_n

    def get_poor_performers(
        self, data: pd.DataFrame, percentile: int = 75, rank_column: str = "health_outcomes_rank"
    ) -> pd.DataFrame:
        """
        Get poor performing counties (above percentile threshold).

        Args:
            data: CHR DataFrame
            percentile: Percentile threshold (75 = bottom 25%)
            rank_column: Ranking column to use

        Returns:
            DataFrame with poor performing counties

        Example:
            >>> poor_health = chr.get_poor_performers(data, percentile=75)
        """
        if rank_column not in data.columns:
            raise ValueError(f"Rank column '{rank_column}' not found in data")

        # Filter out missing ranks
        valid_data = data[data[rank_column].notna()].copy()

        # Calculate threshold (higher ranks = worse performance)
        threshold = valid_data[rank_column].quantile(percentile / 100)
        poor = valid_data[valid_data[rank_column] >= threshold].copy()

        self.logger.info(
            f"Retrieved {len(poor)} counties with rank >= {threshold:.0f} "
            f"({100-percentile}th percentile)"
        )

        return poor

    def filter_by_measure(
        self, data: pd.DataFrame, measure: str, threshold: float, above: bool = True
    ) -> pd.DataFrame:
        """
        Filter counties by a specific health measure threshold.

        Args:
            data: CHR DataFrame
            measure: Measure name (column name)
            threshold: Threshold value
            above: If True, filter to values >= threshold; if False, < threshold

        Returns:
            DataFrame with counties meeting threshold criteria

        Example:
            >>> high_smoking = chr.filter_by_measure(
            ...     data, 'adult_smoking', threshold=20, above=True
            ... )
        """
        if measure not in data.columns:
            raise ValueError(f"Measure column '{measure}' not found in data")

        if above:
            filtered = data[data[measure] >= threshold].copy()
        else:
            filtered = data[data[measure] < threshold].copy()

        self.logger.info(
            f"Filtered to {len(filtered)} counties with {measure} "
            f"{'≥' if above else '<'} {threshold}"
        )

        return filtered

    def compare_to_state(
        self, data: pd.DataFrame, measure: str, state_column: str = "state"
    ) -> pd.DataFrame:
        """
        Compare each county's measure to its state average.

        Args:
            data: CHR DataFrame
            measure: Measure name to compare
            state_column: Name of state column

        Returns:
            DataFrame with additional columns: {measure}_state_avg, {measure}_vs_state

        Example:
            >>> comparison = chr.compare_to_state(data, 'adult_smoking')
            >>> worse_than_state = comparison[comparison['adult_smoking_vs_state'] > 0]
        """
        if measure not in data.columns:
            raise ValueError(f"Measure column '{measure}' not found in data")

        if state_column not in data.columns:
            raise ValueError(f"State column '{state_column}' not found in data")

        result = data.copy()

        # Calculate state averages
        state_avg = data.groupby(state_column)[measure].mean()

        # Map state averages back to counties
        result[f"{measure}_state_avg"] = result[state_column].map(state_avg)

        # Calculate difference from state average
        result[f"{measure}_vs_state"] = result[measure] - result[f"{measure}_state_avg"]

        self.logger.info(f"Added state comparison columns for {measure}")

        return result

    def get_available_measures(self, data: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Get list of available health measures in the dataset.

        Args:
            data: CHR DataFrame

        Returns:
            Dictionary with measure categories and column names

        Example:
            >>> measures = chr.get_available_measures(data)
            >>> print(f"Rankings: {measures['rankings']}")
            >>> print(f"Outcomes: {measures['outcomes']}")
        """
        columns = set(data.columns)

        measures = {
            "rankings": sorted([col for col in columns if "rank" in col.lower()]),
            "raw_values": sorted([col for col in columns if "rawvalue" in col.lower()]),
            "numerators": sorted([col for col in columns if "numerator" in col.lower()]),
            "denominators": sorted([col for col in columns if "denominator" in col.lower()]),
            "z_scores": sorted([col for col in columns if "zscore" in col.lower()]),
        }

        self.logger.info(f"Found {sum(len(v) for v in measures.values())} measure columns")

        return measures

    def summarize_by_state(
        self, data: pd.DataFrame, measures: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Calculate state-level summaries of health measures.

        Args:
            data: CHR DataFrame
            measures: List of measures to summarize (default: common measures)

        Returns:
            DataFrame with state-level statistics

        Example:
            >>> summary = chr.summarize_by_state(
            ...     data,
            ...     measures=['adult_smoking', 'adult_obesity', 'uninsured']
            ... )
        """
        state_col = None
        for col in ["state", "statename", "state_name", "statecode"]:
            if col in data.columns:
                state_col = col
                break

        if state_col is None:
            raise ValueError("State column not found in data")

        if measures is None:
            # Use default common measures
            measures = []
            for measure in [
                "adult_smoking",
                "adult_obesity",
                "uninsured",
                "unemployment",
                "high_school_graduation",
            ]:
                if measure in data.columns:
                    measures.append(measure)

        # Validate measures exist
        for measure in measures:
            if measure not in data.columns:
                raise ValueError(f"Measure column '{measure}' not found in data")

        # Group by state and calculate statistics
        summary = data.groupby(state_col)[measures].agg(
            ["count", "mean", "median", "min", "max", "std"]
        )

        self.logger.info(f"Summarized data for {len(summary)} states")

        return summary
