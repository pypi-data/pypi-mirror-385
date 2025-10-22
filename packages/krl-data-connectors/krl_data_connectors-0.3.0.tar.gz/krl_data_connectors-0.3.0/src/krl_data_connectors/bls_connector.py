# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0
#
# Khipu Research Analytics Suite - KR-Labs™
# Licensed under the Apache License, Version 2.0

"""
Bureau of Labor Statistics (BLS) Data Connector.

This connector provides access to BLS public data API, including:
- Employment and unemployment data
- Consumer Price Index (CPI)
- Producer Price Index (PPI)
- Average hourly earnings
- And many other economic indicators

Data Source: https://www.bls.gov/data/
API Documentation: https://www.bls.gov/developers/api_signature_v2.htm
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from .base_connector import BaseConnector


class BLSConnector(BaseConnector):
    """
    Connector for Bureau of Labor Statistics (BLS) Public Data API.

    The BLS API provides access to economic time series data including:
    - Current Employment Statistics (CES)
    - Local Area Unemployment Statistics (LAUS)
    - Consumer Price Index (CPI)
    - Producer Price Index (PPI)
    - Employment Cost Index (ECI)
    - And many more series

    Rate Limits:
    - Without API key: 25 queries per day, 10 years per query
    - With API key v1.0: 500 queries per day, 10 years per query
    - With API key v2.0: 500 queries per day, 20 years per query

    Example:
        >>> bls = BLSConnector(api_key='your_key')
        >>> # Get national unemployment rate
        >>> data = bls.get_series('LNS14000000', start_year=2020, end_year=2023)
        >>> # Get CPI for all urban consumers
        >>> cpi = bls.get_series('CUUR0000SA0', start_year=2020, end_year=2023)
    """

    BASE_URL_V2 = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    BASE_URL_V1 = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

    # Common series IDs
    COMMON_SERIES = {
        "unemployment_rate": "LNS14000000",  # National unemployment rate
        "employment_level": "LNS12000000",  # Employment level
        "labor_force": "LNS11000000",  # Civilian labor force
        "cpi_all": "CUUR0000SA0",  # CPI-U All items
        "cpi_food": "CUUR0000SAF",  # CPI-U Food
        "cpi_energy": "CUUR0000SA0E",  # CPI-U Energy
        "ppi_all": "WPUFD49207",  # PPI All commodities
    }

    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[str] = None):
        """
        Initialize BLS connector.

        Args:
            api_key: BLS API key (register at https://data.bls.gov/registrationEngine/)
            cache_dir: Optional directory for caching responses
        """
        super().__init__(api_key=api_key, cache_dir=cache_dir)
        self.base_url = self.BASE_URL_V2 if api_key else self.BASE_URL_V1
        self.logger.info(f"Initialized BLS connector (API version: {'v2' if api_key else 'v1'})")

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or config."""
        return self.config.get("bls_api_key")

    def connect(self) -> None:
        """Establish connection to BLS API (no-op, API is public)."""
        self.logger.debug(f"BLS connector ready (API version: {'v2' if self.api_key else 'v1'})")

    def _bls_post_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make POST request to BLS API.

        This is a separate method to allow for easier mocking in tests.

        Args:
            payload: JSON payload for the request

        Returns:
            Response data as dictionary
        """
        session = self._init_session()
        response = session.post(self.base_url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """
        Fetch BLS data (generic method).

        This is a wrapper for get_series().

        Args:
            series_id: BLS series ID
            **kwargs: Parameters for get_series()

        Returns:
            DataFrame with requested data
        """
        series_id = kwargs.pop("series_id", None)
        if not series_id:
            raise ValueError("series_id is required")

        return self.get_series(series_id, **kwargs)

    def get_series(
        self,
        series_id: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        calculations: bool = False,
        annual_average: bool = False,
    ) -> pd.DataFrame:
        """
        Get time series data for a BLS series.

        Args:
            series_id: BLS series ID (e.g., 'LNS14000000' for unemployment rate)
            start_year: Start year (default: current year - 9)
            end_year: End year (default: current year)
            calculations: Include calculations (percent change, etc.)
            annual_average: Include annual averages

        Returns:
            DataFrame with columns: year, period, periodName, value, date

        Example:
            >>> bls = BLSConnector(api_key='your_key')
            >>> # Get unemployment rate for last 3 years
            >>> data = bls.get_series('LNS14000000', start_year=2021, end_year=2023)
        """
        # Default to last 10 years
        if end_year is None:
            end_year = datetime.now().year
        if start_year is None:
            start_year = end_year - 9

        # Validate year range
        max_years = 20 if self.api_key else 10
        if end_year - start_year + 1 > max_years:
            raise ValueError(
                f"Year range too large. Maximum is {max_years} years for this API key type."
            )

        payload = {
            "seriesid": [series_id],
            "startyear": str(start_year),
            "endyear": str(end_year),
            "calculations": calculations,
            "annualaverage": annual_average,
        }

        if self.api_key:
            payload["registrationkey"] = self.api_key

        self.logger.info(f"Fetching BLS series: {series_id}, years {start_year}-{end_year}")

        try:
            data = self._bls_post_request(payload)

            # Check status
            if data.get("status") != "REQUEST_SUCCEEDED":
                error_msg = data.get("message", ["Unknown error"])[0]
                raise ValueError(f"BLS API error: {error_msg}")

            # Extract data
            series_data = data.get("Results", {}).get("series", [])
            if not series_data:
                self.logger.warning(f"No data returned for series {series_id}")
                return pd.DataFrame()

            # Parse data
            observations = series_data[0].get("data", [])

            df = pd.DataFrame(observations)

            # Convert value to numeric
            if "value" in df.columns:
                df["value"] = pd.to_numeric(df["value"], errors="coerce")

            # Create date column
            if "year" in df.columns and "period" in df.columns:
                df["date"] = pd.to_datetime(
                    df["year"]
                    + "-"
                    + df["period"]
                    .str.replace("M", "")
                    .str.replace("Q0", "Q")
                    .str.replace("A01", "01"),
                    errors="coerce",
                )

            # Sort by date
            if "date" in df.columns:
                df = df.sort_values("date").reset_index(drop=True)

            self.logger.info(f"Retrieved {len(df):,} observations for series {series_id}")
            return df

        except Exception as e:
            self.logger.error(f"Failed to fetch BLS series {series_id}: {e}")
            raise

    def get_multiple_series(
        self,
        series_ids: List[str],
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        calculations: bool = False,
        annual_average: bool = False,
    ) -> Dict[str, pd.DataFrame]:
        """
        Get data for multiple series in a single request.

        Args:
            series_ids: List of BLS series IDs (max 50 for v2, max 25 for v1)
            start_year: Start year
            end_year: End year
            calculations: Include calculations
            annual_average: Include annual averages

        Returns:
            Dictionary mapping series_id to DataFrame

        Example:
            >>> bls = BLSConnector(api_key='your_key')
            >>> series = ['LNS14000000', 'LNS12000000']  # Unemployment and employment
            >>> data = bls.get_multiple_series(series, start_year=2020, end_year=2023)
        """
        max_series = 50 if self.api_key else 25
        if len(series_ids) > max_series:
            raise ValueError(
                f"Too many series requested. Maximum is {max_series} for this API key type."
            )

        # Default to last 10 years
        if end_year is None:
            end_year = datetime.now().year
        if start_year is None:
            start_year = end_year - 9

        payload = {
            "seriesid": series_ids,
            "startyear": str(start_year),
            "endyear": str(end_year),
            "calculations": calculations,
            "annualaverage": annual_average,
        }

        if self.api_key:
            payload["registrationkey"] = self.api_key

        self.logger.info(f"Fetching {len(series_ids)} BLS series")

        try:
            data = self._bls_post_request(payload)

            if data.get("status") != "REQUEST_SUCCEEDED":
                error_msg = data.get("message", ["Unknown error"])[0]
                raise ValueError(f"BLS API error: {error_msg}")

            # Parse each series
            result = {}
            series_data = data.get("Results", {}).get("series", [])

            for series in series_data:
                series_id = series.get("seriesID")
                observations = series.get("data", [])

                df = pd.DataFrame(observations)

                if "value" in df.columns:
                    df["value"] = pd.to_numeric(df["value"], errors="coerce")

                if "year" in df.columns and "period" in df.columns:
                    df["date"] = pd.to_datetime(
                        df["year"]
                        + "-"
                        + df["period"]
                        .str.replace("M", "")
                        .str.replace("Q0", "Q")
                        .str.replace("A01", "01"),
                        errors="coerce",
                    )

                if "date" in df.columns:
                    df = df.sort_values("date").reset_index(drop=True)

                result[series_id] = df

            self.logger.info(f"Retrieved data for {len(result)} series")
            return result

        except Exception as e:
            self.logger.error(f"Failed to fetch multiple BLS series: {e}")
            raise

    def get_unemployment_rate(
        self,
        area_code: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get unemployment rate data.

        Args:
            area_code: Optional area code (default: national)
                - National: None or 'LNS14000000'
                - State: use state FIPS code
                - Metro: use metro area code
            start_year: Start year
            end_year: End year

        Returns:
            DataFrame with unemployment rate data

        Example:
            >>> bls = BLSConnector(api_key='your_key')
            >>> # National unemployment rate
            >>> national = bls.get_unemployment_rate()
            >>> # California unemployment rate
            >>> ca = bls.get_unemployment_rate(area_code='06')
        """
        if area_code is None:
            series_id = "LNS14000000"  # National
        else:
            # State unemployment: LASST + 2-digit state FIPS + 0000000003
            series_id = f"LASST{area_code}0000000003"

        return self.get_series(series_id, start_year, end_year)

    def get_cpi(
        self,
        item: str = "SA0",  # All items
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get Consumer Price Index data.

        Args:
            item: Item code (default: 'SA0' for all items)
                Common codes:
                - SA0: All items
                - SAF: Food
                - SA0E: Energy
                - SAH: Housing
                - SAM: Medical care
            start_year: Start year
            end_year: End year

        Returns:
            DataFrame with CPI data

        Example:
            >>> bls = BLSConnector(api_key='your_key')
            >>> # All items CPI
            >>> cpi_all = bls.get_cpi()
            >>> # Food CPI
            >>> cpi_food = bls.get_cpi(item='SAF')
        """
        # CPI-U for all urban consumers, US city average
        series_id = f"CUUR0000{item}"
        return self.get_series(series_id, start_year, end_year)

    @staticmethod
    def get_common_series_id(name: str) -> Optional[str]:
        """
        Get series ID for common series by name.

        Args:
            name: Common series name

        Returns:
            Series ID or None if not found
        """
        return BLSConnector.COMMON_SERIES.get(name)
