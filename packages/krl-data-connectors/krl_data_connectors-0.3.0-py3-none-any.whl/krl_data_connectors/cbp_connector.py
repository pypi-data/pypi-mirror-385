# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0
#
# Khipu Research Analytics Suite - KR-Labs™
# Licensed under the Apache License, Version 2.0

"""
County Business Patterns (CBP) Data Connector.

This connector provides access to the Census Bureau's County Business Patterns,
which includes annual data on establishments, employment, and payroll by industry
and geography.

Data Source: https://www.census.gov/programs-surveys/cbp.html
API Documentation: https://www.census.gov/data/developers/data-sets/cbp-nonemp-zbp/cbp-api.html
"""

from typing import Any, List, Optional

import pandas as pd

from .base_connector import BaseConnector


class CountyBusinessPatternsConnector(BaseConnector):
    """
    Connector for County Business Patterns (CBP) data.

    CBP provides subnational economic data by industry, including:
    - Number of establishments
    - Employment during pay period including March 12
    - First quarter payroll
    - Annual payroll

    Data is available by:
    - Industry (NAICS codes)
    - Geography (national, state, county, metro, ZIP code)
    - Size class (employment size of establishment)

    Example:
        >>> cbp = CountyBusinessPatternsConnector(api_key='your_key')
        >>> # Get 2021 data for all counties
        >>> data = cbp.get_county_data(year=2021)
        >>> # Get specific NAICS sector (e.g., retail trade)
        >>> retail = cbp.get_county_data(year=2021, naics='44-45')
    """

    BASE_URL = "https://api.census.gov/data"

    # NAICS 2-digit sectors
    NAICS_SECTORS = {
        "11": "Agriculture, Forestry, Fishing and Hunting",
        "21": "Mining, Quarrying, and Oil and Gas Extraction",
        "22": "Utilities",
        "23": "Construction",
        "31-33": "Manufacturing",
        "42": "Wholesale Trade",
        "44-45": "Retail Trade",
        "48-49": "Transportation and Warehousing",
        "51": "Information",
        "52": "Finance and Insurance",
        "53": "Real Estate and Rental and Leasing",
        "54": "Professional, Scientific, and Technical Services",
        "55": "Management of Companies and Enterprises",
        "56": "Administrative and Support and Waste Management",
        "61": "Educational Services",
        "62": "Health Care and Social Assistance",
        "71": "Arts, Entertainment, and Recreation",
        "72": "Accommodation and Food Services",
        "81": "Other Services (except Public Administration)",
        "92": "Public Administration",
    }

    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[str] = None):
        """
        Initialize CBP connector.

        Args:
            api_key: Census API key (get from https://api.census.gov/data/key_signup.html)
            cache_dir: Optional directory for caching responses
        """
        super().__init__(api_key=api_key, cache_dir=cache_dir)
        self.logger.info("Initialized County Business Patterns connector")

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or config."""
        return self.config.get("CENSUS_API_KEY") or self.config.get("census_api_key")

    def connect(self) -> None:
        """Establish connection to CBP API."""
        if not self.api_key:
            raise ValueError("Census API key required for CBP data access")
        self.logger.debug("CBP connector ready")

    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """
        Fetch CBP data (generic method).

        This is a wrapper that dispatches to specific geography methods.
        Prefer using get_county_data(), get_state_data(), or get_metro_data() directly.

        Args:
            geography: Geography level ('county', 'state', 'metro')
            **kwargs: Parameters for the specific geography method

        Returns:
            DataFrame with requested data
        """
        geography = kwargs.pop("geography", "county")

        if geography == "county":
            return self.get_county_data(**kwargs)
        elif geography == "state":
            return self.get_state_data(**kwargs)
        elif geography == "metro":
            return self.get_metro_data(**kwargs)
        else:
            raise ValueError(
                f"Invalid geography: {geography}. Must be 'county', 'state', or 'metro'"
            )

    def _build_cbp_url(self, year: int) -> str:
        """
        Build CBP API URL for a specific year.

        Args:
            year: Year of data (2017+)

        Returns:
            API base URL
        """
        return f"{self.BASE_URL}/{year}/cbp"

    def get_county_data(
        self,
        year: int,
        variables: Optional[List[str]] = None,
        state: Optional[str] = None,
        county: Optional[str] = None,
        naics: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get County Business Patterns data at the county level.

        Args:
            year: Year of data (2017-2021)
            variables: List of variable names to retrieve (default: common variables)
            state: Optional state FIPS code to filter (e.g., '06' for California)
            county: Optional county FIPS code (3 digits, requires state)
            naics: Optional NAICS code or sector (e.g., '44-45' for retail)

        Returns:
            DataFrame with requested data

        Common variables:
            - ESTAB: Number of establishments
            - EMP: Employment
            - PAYANN: Annual payroll ($1,000)
            - EMPSZES: Employment size of establishment code

        Example:
            >>> cbp = CountyBusinessPatternsConnector(api_key='your_key')
            >>> # Get all California counties
            >>> ca_data = cbp.get_county_data(year=2021, state='06')
            >>> # Get retail trade in Los Angeles County
            >>> la_retail = cbp.get_county_data(
            ...     year=2021, state='06', county='037', naics='44-45'
            ... )
        """
        if variables is None:
            variables = [
                "ESTAB",  # Number of establishments
                "EMP",  # Employment
                "PAYANN",  # Annual payroll
                "EMPSZES",  # Employment size code
                "NAICS2017",  # NAICS code
                "NAME",  # Geographic name
            ]

        params = {
            "get": ",".join(variables),
            "for": "county:*" if county is None else f"county:{county}",
        }

        if state:
            params["in"] = f"state:{state}"

        # Note: Census API doesn't accept NAICS2017 as a query parameter
        # We filter the results after retrieving them instead

        if self.api_key:
            params["key"] = self.api_key

        url = self._build_cbp_url(year)

        self.logger.info(
            f"Fetching CBP county data: year={year}, state={state}, "
            f"county={county}, naics={naics}"
        )

        try:
            data = self._make_request(url, params=params)

            # Convert to DataFrame (first row is headers)
            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])

                # Convert numeric columns
                numeric_cols = ["ESTAB", "EMP", "PAYANN"]
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")

                # Filter by NAICS code if specified
                if naics and "NAICS2017" in df.columns:
                    df = df[df["NAICS2017"].str.startswith(naics)]

                self.logger.info(f"Retrieved {len(df):,} CBP county records")
                return df
            else:
                self.logger.warning("No data returned from CBP API")
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Failed to fetch CBP county data: {e}")
            raise

    def get_state_data(
        self,
        year: int,
        variables: Optional[List[str]] = None,
        state: Optional[str] = None,
        naics: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get County Business Patterns data at the state level.

        Args:
            year: Year of data (2017-2021)
            variables: List of variable names to retrieve
            state: Optional state FIPS code to filter
            naics: Optional NAICS code or sector

        Returns:
            DataFrame with requested data

        Example:
            >>> cbp = CountyBusinessPatternsConnector(api_key='your_key')
            >>> # Get all states
            >>> states = cbp.get_state_data(year=2021)
            >>> # Get manufacturing in all states
            >>> mfg = cbp.get_state_data(year=2021, naics='31-33')
        """
        if variables is None:
            variables = ["ESTAB", "EMP", "PAYANN", "NAICS2017", "NAME"]

        params = {
            "get": ",".join(variables),
            "for": f"state:{state}" if state else "state:*",
        }

        # Note: Census API doesn't accept NAICS2017 as a query parameter
        # We filter the results after retrieving them instead

        if self.api_key:
            params["key"] = self.api_key

        url = self._build_cbp_url(year)

        self.logger.info(f"Fetching CBP state data: year={year}, state={state}, naics={naics}")

        try:
            data = self._make_request(url, params=params)

            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])

                # Convert numeric columns
                numeric_cols = ["ESTAB", "EMP", "PAYANN"]
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")

                # Filter by NAICS code if specified
                if naics and "NAICS2017" in df.columns:
                    df = df[df["NAICS2017"].str.startswith(naics)]

                self.logger.info(f"Retrieved {len(df):,} CBP state records")
                return df
            else:
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Failed to fetch CBP state data: {e}")
            raise

    def get_metro_data(
        self,
        year: int,
        variables: Optional[List[str]] = None,
        metro: Optional[str] = None,
        naics: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get County Business Patterns data at the metropolitan area level.

        Args:
            year: Year of data (2017-2021)
            variables: List of variable names to retrieve
            metro: Optional metro area code (CBSA code)
            naics: Optional NAICS code or sector

        Returns:
            DataFrame with requested data

        Example:
            >>> cbp = CountyBusinessPatternsConnector(api_key='your_key')
            >>> # Get all metro areas
            >>> metros = cbp.get_metro_data(year=2021)
        """
        if variables is None:
            variables = ["ESTAB", "EMP", "PAYANN", "NAICS2017", "NAME"]

        params = {
            "get": ",".join(variables),
            "for": (
                f"metropolitan statistical area/micropolitan statistical area:{metro}"
                if metro
                else "metropolitan statistical area/micropolitan statistical area:*"
            ),
        }

        if naics:
            params["NAICS2017"] = naics

        if self.api_key:
            params["key"] = self.api_key

        url = self._build_cbp_url(year)

        self.logger.info(f"Fetching CBP metro data: year={year}, metro={metro}, naics={naics}")

        try:
            data = self._make_request(url, params=params)

            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])

                # Convert numeric columns
                numeric_cols = ["ESTAB", "EMP", "PAYANN"]
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")

                self.logger.info(f"Retrieved {len(df):,} CBP metro records")
                return df
            else:
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Failed to fetch CBP metro data: {e}")
            raise

    def get_naics_totals(
        self,
        df: pd.DataFrame,
        level: int = 2,
    ) -> pd.DataFrame:
        """
        Aggregate data to specific NAICS level (2, 3, 4, 5, or 6 digits).

        Args:
            df: DataFrame with NAICS codes and numeric data
            level: Number of NAICS digits (2=sector, 3=subsector, etc.)

        Returns:
            DataFrame aggregated to specified NAICS level

        Example:
            >>> data = cbp.get_county_data(year=2021, state='06')
            >>> # Aggregate to 2-digit sectors
            >>> sectors = cbp.get_naics_totals(data, level=2)
        """
        # Handle empty DataFrame
        if df.empty:
            return df

        # Validate level
        if level < 2 or level > 6:
            raise ValueError(f"Level must be between 2 and 6, got {level}")

        df = df.copy()

        # Extract NAICS at specified level
        naics_col = "NAICS2017" if "NAICS2017" in df.columns else "NAICS"
        df["naics_level"] = df[naics_col].str[:level]

        # Aggregate numeric columns
        numeric_cols = df.select_dtypes(include=["number"]).columns
        agg_df = df.groupby("naics_level")[numeric_cols].sum().reset_index()
        agg_df.rename(columns={"naics_level": "naics"}, inplace=True)

        return agg_df

    @staticmethod
    def get_naics_sector_name(naics_code: str) -> str:
        """
        Get human-readable name for 2-digit NAICS sector.

        Args:
            naics_code: 2-digit NAICS code

        Returns:
            Sector name
        """
        sectors = {
            "11": "Agriculture, Forestry, Fishing and Hunting",
            "21": "Mining, Quarrying, and Oil and Gas Extraction",
            "22": "Utilities",
            "23": "Construction",
            "31-33": "Manufacturing",
            "42": "Wholesale Trade",
            "44-45": "Retail Trade",
            "48-49": "Transportation and Warehousing",
            "51": "Information",
            "52": "Finance and Insurance",
            "53": "Real Estate and Rental and Leasing",
            "54": "Professional, Scientific, and Technical Services",
            "55": "Management of Companies and Enterprises",
            "56": "Administrative and Support and Waste Management",
            "61": "Educational Services",
            "62": "Health Care and Social Assistance",
            "71": "Arts, Entertainment, and Recreation",
            "72": "Accommodation and Food Services",
            "81": "Other Services (except Public Administration)",
            "92": "Public Administration",
        }
        return sectors.get(naics_code[:2], f"Unknown sector: {naics_code}")
