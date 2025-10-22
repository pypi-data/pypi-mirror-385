# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0
#
# Khipu Research Analytics Suite - KR-Labs™
# Licensed under the Apache License, Version 2.0

"""
Bureau of Economic Analysis (BEA) Data Connector.

This connector provides access to BEA economic data, including:
- National Income and Product Accounts (NIPA) - GDP data
- Regional economic accounts
- International transactions accounts
- Fixed assets accounts
- Input-Output accounts

Data Source: https://www.bea.gov/
API Documentation: https://apps.bea.gov/api/signup/
"""

from typing import Any, Optional

import pandas as pd

from .base_connector import BaseConnector


class BEAConnector(BaseConnector):
    """
    Connector for Bureau of Economic Analysis (BEA) Data API.

    Provides access to:
    - NIPA: National Income and Product Accounts (GDP, personal income, etc.)
    - NIUnderlyingDetail: Underlying NIPA details
    - FixedAssets: Fixed assets accounts
    - MNE: Multinational Enterprises
    - GDPbyIndustry: GDP by industry
    - Regional: Regional economic accounts (state/metro GDP, personal income)
    - IntlServTrade: International services trade
    - ITA: International transactions accounts
    - IIP: International investment position
    - InputOutput: Input-Output tables

    API Key Required: Register at https://apps.bea.gov/api/signup/

    Example:
        >>> bea = BEAConnector(api_key='your_key')
        >>> # Get GDP data
        >>> gdp = bea.get_nipa_data(table_name='T10101', frequency='Q', year='2020,2021,2022,2023')
        >>> # Get state personal income
        >>> income = bea.get_regional_data(dataset='RegionalIncome', geo_fips='STATE', year='2020,2021,2022')
    """

    BASE_URL = "https://apps.bea.gov/api/data"

    # Common NIPA tables
    NIPA_TABLES = {
        "gdp": "T10101",  # GDP
        "gdp_components": "T10102",  # GDP components
        "personal_income": "T20100",  # Personal income
        "disposable_income": "T20600",  # Disposable personal income
        "pce": "T20804",  # Personal consumption expenditures
    }

    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[str] = None):
        """
        Initialize BEA connector.

        Args:
            api_key: BEA API key (register at https://apps.bea.gov/api/signup/)
            cache_dir: Optional directory for caching responses
        """
        super().__init__(api_key=api_key, cache_dir=cache_dir)

        if not self.api_key:
            raise ValueError(
                "BEA API key is required. Register at https://apps.bea.gov/api/signup/"
            )

        self.logger.info("Initialized BEA connector")

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or config."""
        return self.config.get("bea_api_key")

    def connect(self) -> None:
        """Establish connection to BEA API."""
        if not self.api_key:
            raise ValueError("BEA API key required for data access")
        self.logger.debug("BEA connector ready")

    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """
        Fetch BEA data (generic method).

        This is a wrapper that dispatches to specific dataset methods.
        Prefer using get_nipa_data(), get_regional_data(), etc. directly.

        Args:
            dataset: Dataset name ('nipa', 'regional', 'gdpindustry', 'fixedassets')
            **kwargs: Parameters for the specific dataset method

        Returns:
            DataFrame with requested data
        """
        dataset = kwargs.pop("dataset", "nipa")

        if dataset == "nipa":
            return self.get_nipa_data(**kwargs)
        elif dataset == "regional":
            return self.get_regional_data(**kwargs)
        elif dataset == "gdpindustry":
            return self.get_gdp_by_industry(**kwargs)
        elif dataset == "fixedassets":
            return self.get_fixed_assets(**kwargs)
        else:
            raise ValueError(
                f"Invalid dataset: {dataset}. Must be 'nipa', 'regional', 'gdpindustry', or 'fixedassets'"
            )

    def get_dataset_list(self) -> pd.DataFrame:
        """
        Get list of available BEA datasets.

        Returns:
            DataFrame with dataset names and descriptions
        """
        params = {"UserID": self.api_key, "method": "GETDATASETLIST", "ResultFormat": "JSON"}

        data = self._make_request(self.BASE_URL, params=params)
        datasets = data.get("BEAAPI", {}).get("Results", {}).get("Dataset", [])

        return pd.DataFrame(datasets)

    def get_parameter_list(self, dataset_name: str) -> pd.DataFrame:
        """
        Get list of parameters for a dataset.

        Args:
            dataset_name: Name of the dataset (e.g., 'NIPA', 'Regional')

        Returns:
            DataFrame with parameter names and descriptions
        """
        params = {
            "UserID": self.api_key,
            "method": "GETPARAMETERLIST",
            "DataSetName": dataset_name,
            "ResultFormat": "JSON",
        }

        response = self._make_request(self.BASE_URL, params=params)
        parameters = response.get("BEAAPI", {}).get("Results", {}).get("Parameter", [])

        return pd.DataFrame(parameters)

    def get_parameter_values(self, dataset_name: str, parameter_name: str) -> pd.DataFrame:
        """
        Get valid values for a parameter.

        Args:
            dataset_name: Name of the dataset
            parameter_name: Name of the parameter

        Returns:
            DataFrame with parameter values
        """
        params = {
            "UserID": self.api_key,
            "method": "GETPARAMETERVALUES",
            "DataSetName": dataset_name,
            "ParameterName": parameter_name,
            "ResultFormat": "JSON",
        }

        response = self._make_request(self.BASE_URL, params=params)

        # Different datasets return values in different formats
        results = response.get("BEAAPI", {}).get("Results", {})

        # Try different possible keys
        for key in ["ParamValue", "Statistic", "Line"]:
            if key in results:
                return pd.DataFrame(results[key])

        return pd.DataFrame()

    def get_nipa_data(
        self,
        table_name: str,
        frequency: str = "A",
        year: Optional[str] = None,
        show_millionths: str = "N",
    ) -> pd.DataFrame:
        """
        Get National Income and Product Accounts (NIPA) data.

        Args:
            table_name: NIPA table name (e.g., 'T10101' for GDP)
            frequency: Data frequency ('A' for annual, 'Q' for quarterly, 'M' for monthly)
            year: Year(s) as comma-separated string (e.g., '2020,2021,2022' or 'X' for all)
            show_millionths: Show data in millionths ('Y' or 'N')

        Returns:
            DataFrame with NIPA data

        Example:
            >>> bea = BEAConnector(api_key='your_key')
            >>> # Get quarterly GDP for 2020-2023
            >>> gdp = bea.get_nipa_data(table_name='T10101', frequency='Q', year='2020,2021,2022,2023')
        """
        if year is None:
            year = "X"  # All years

        params = {
            "UserID": self.api_key,
            "method": "GETDATA",
            "DataSetName": "NIPA",
            "TableName": table_name,
            "Frequency": frequency,
            "Year": year,
            "ShowMillionths": show_millionths,
            "ResultFormat": "JSON",
        }

        self.logger.info(f"Fetching NIPA table {table_name}, frequency={frequency}, year={year}")

        response = self._make_request(self.BASE_URL, params=params)
        data = response.get("BEAAPI", {}).get("Results", {}).get("Data", [])

        df = pd.DataFrame(data)

        # Convert data values to numeric
        if "DataValue" in df.columns:
            df["DataValue"] = pd.to_numeric(df["DataValue"].str.replace(",", ""), errors="coerce")

        self.logger.info(f"Retrieved {len(df):,} observations")
        return df

    def get_regional_data(
        self,
        table_name: str = "SAINC1",
        line_code: str = "1",
        geo_fips: str = "STATE",
        year: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get regional economic data (state, MSA, county).

        Args:
            table_name: Regional table name
                Common tables:
                - SAINC1: Personal income summary
                - SAINC4: Personal income by major component
                - SAGDP2: GDP by state and industry
                - CAINC1: County income summary
            line_code: Line code for the metric (use get_parameter_values to find valid codes)
            geo_fips: Geography level
                - STATE: All states
                - COUNTY: All counties
                - MSA: Metropolitan Statistical Areas
                Or specific FIPS codes (e.g., '06' for California)
            year: Year(s) as comma-separated string or 'LAST5' for last 5 years

        Returns:
            DataFrame with regional data

        Example:
            >>> bea = BEAConnector(api_key='your_key')
            >>> # Get state personal income for last 5 years
            >>> income = bea.get_regional_data(table_name='SAINC1', line_code='1', geo_fips='STATE', year='LAST5')
        """
        if year is None:
            year = "LAST5"

        params = {
            "UserID": self.api_key,
            "method": "GETDATA",
            "DataSetName": "Regional",
            "TableName": table_name,
            "LineCode": line_code,
            "GeoFips": geo_fips,
            "Year": year,
            "ResultFormat": "JSON",
        }

        self.logger.info(f"Fetching regional data: table={table_name}, geo={geo_fips}, year={year}")

        response = self._make_request(self.BASE_URL, params=params)
        data = response.get("BEAAPI", {}).get("Results", {}).get("Data", [])

        df = pd.DataFrame(data)

        # Convert data values to numeric
        if "DataValue" in df.columns:
            df["DataValue"] = pd.to_numeric(df["DataValue"].str.replace(",", ""), errors="coerce")

        self.logger.info(f"Retrieved {len(df):,} observations")
        return df

    def get_gdp_by_industry(
        self,
        industry: str = "ALL",
        year: Optional[str] = None,
        table_id: str = "1",
        frequency: str = "A",
    ) -> pd.DataFrame:
        """
        Get GDP by industry data.

        Args:
            industry: Industry code ('ALL' for all industries, or specific NAICS code)
            year: Year(s) as comma-separated string or 'ALL'
            table_id: Table ID (1-11, see BEA documentation)
            frequency: 'A' for annual, 'Q' for quarterly

        Returns:
            DataFrame with GDP by industry data

        Example:
            >>> bea = BEAConnector(api_key='your_key')
            >>> # Get all industries for 2020-2022
            >>> gdp_ind = bea.get_gdp_by_industry(industry='ALL', year='2020,2021,2022')
        """
        if year is None:
            year = "ALL"

        params = {
            "UserID": self.api_key,
            "method": "GETDATA",
            "DataSetName": "GDPbyIndustry",
            "Industry": industry,
            "Year": year,
            "TableID": table_id,
            "Frequency": frequency,
            "ResultFormat": "JSON",
        }

        self.logger.info(f"Fetching GDP by industry: industry={industry}, year={year}")

        response = self._make_request(self.BASE_URL, params=params)
        data = response.get("BEAAPI", {}).get("Results", {}).get("Data", [])

        df = pd.DataFrame(data)

        # Convert data values to numeric
        if "DataValue" in df.columns:
            df["DataValue"] = pd.to_numeric(df["DataValue"].str.replace(",", ""), errors="coerce")

        self.logger.info(f"Retrieved {len(df):,} observations")
        return df

    def get_fixed_assets(
        self,
        table_name: str = "FAAt101",
        year: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get Fixed Assets data.

        Args:
            table_name: Fixed Assets table name (see BEA documentation)
            year: Year(s) as comma-separated string or 'X' for all

        Returns:
            DataFrame with Fixed Assets data
        """
        if year is None:
            year = "X"

        params = {
            "UserID": self.api_key,
            "method": "GETDATA",
            "DataSetName": "FixedAssets",
            "TableName": table_name,
            "Year": year,
            "ResultFormat": "JSON",
        }

        response = self._make_request(self.BASE_URL, params=params)
        data = response.get("BEAAPI", {}).get("Results", {}).get("Data", [])

        df = pd.DataFrame(data)

        if "DataValue" in df.columns:
            df["DataValue"] = pd.to_numeric(df["DataValue"].str.replace(",", ""), errors="coerce")

        return df

    @staticmethod
    def get_common_table(name: str) -> Optional[str]:
        """
        Get table ID for common NIPA tables.

        Args:
            name: Common table name

        Returns:
            Table ID or None if not found
        """
        return BEAConnector.NIPA_TABLES.get(name)
