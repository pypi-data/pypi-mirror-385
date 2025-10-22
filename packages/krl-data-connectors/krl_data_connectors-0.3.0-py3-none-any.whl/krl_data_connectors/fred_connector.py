# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""FRED (Federal Reserve Economic Data) connector implementation."""

from typing import Any, Dict, List, Optional

import pandas as pd

from .base_connector import BaseConnector


class FREDConnector(BaseConnector):
    """
    Connector for Federal Reserve Economic Data (FRED) API.

    Provides access to 800,000+ economic time series from the St. Louis Fed.

    API Documentation: https://fred.stlouisfed.org/docs/api/fred/

    Args:
        api_key: FRED API key (or set FRED_API_KEY environment variable)
        base_url: FRED API base URL (default: official API endpoint)
        cache_dir: Cache directory (default: ~/.krl_cache)
        cache_ttl: Cache TTL in seconds (default: 3600)

    Example:
        >>> from krl_data_connectors import FREDConnector
        >>> fred = FREDConnector(api_key="your_key")
        >>> unemployment = fred.get_series("UNRATE", start_date="2020-01-01")
        >>> print(unemployment.head())
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.stlouisfed.org/fred",
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        **kwargs: Any,
    ):
        self.base_url = base_url
        super().__init__(api_key=api_key, cache_dir=cache_dir, cache_ttl=cache_ttl, **kwargs)

    def _get_api_key(self) -> Optional[str]:
        """Get FRED API key from configuration."""
        return self.config.get("FRED_API_KEY")

    def connect(self) -> None:
        """
        Connect to FRED API (verify API key).

        Makes a simple API call to verify the API key is valid.
        """
        try:
            # Make a simple request to verify API key
            url = f"{self.base_url}/series"
            params = {"series_id": "GNPCA", "api_key": self.api_key, "file_type": "json"}

            self._make_request(url, params, use_cache=False)

            self.logger.info("Successfully connected to FRED API")

        except Exception as e:
            self.logger.error(f"Failed to connect to FRED API: {e}", exc_info=True)
            raise

    def fetch(self, series_id: str, **kwargs: Any) -> pd.DataFrame:
        """
        Fetch data for a FRED series.

        Alias for get_series() to implement abstract method.

        Args:
            series_id: FRED series ID (e.g., "UNRATE" for unemployment)
            **kwargs: Additional parameters passed to get_series()

        Returns:
            DataFrame with series data
        """
        return self.get_series(series_id, **kwargs)

    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        units: str = "lin",
        frequency: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get observations for a FRED series.

        Args:
            series_id: FRED series ID (e.g., "UNRATE" for unemployment rate)
            start_date: Start date in YYYY-MM-DD format (default: earliest available)
            end_date: End date in YYYY-MM-DD format (default: latest available)
            units: Data transformation units (default: "lin" for linear/no transformation)
                Options: lin, chg, ch1, pch, pc1, pca, cch, cca, log
            frequency: Aggregation frequency (default: series native frequency)
                Options: d (daily), w (weekly), m (monthly), q (quarterly), a (annual)

        Returns:
            DataFrame with columns: date, value

        Example:
            >>> fred = FREDConnector(api_key="your_key")
            >>> gdp = fred.get_series("GDP", start_date="2020-01-01")
        """
        url = f"{self.base_url}/series/observations"

        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "units": units,
        }

        if start_date:
            params["observation_start"] = start_date
        if end_date:
            params["observation_end"] = end_date
        if frequency:
            params["frequency"] = frequency

        self.logger.info(
            "Fetching FRED series",
            extra={"series_id": series_id, "start_date": start_date, "end_date": end_date},
        )

        response = self._make_request(url, params)

        # Parse response
        observations = response.get("observations", [])

        if not observations:
            self.logger.warning(f"No data found for series {series_id}")
            return pd.DataFrame(columns=["date", "value"])

        # Convert to DataFrame
        df = pd.DataFrame(observations)
        df = df[["date", "value"]]

        # Convert types
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

        self.logger.info("FRED series fetched", extra={"series_id": series_id, "rows": len(df)})

        return df

    def search_series(self, search_text: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for FRED series by text.

        Args:
            search_text: Search query text
            limit: Maximum number of results (default: 100)

        Returns:
            List of series metadata dictionaries

        Example:
            >>> fred = FREDConnector(api_key="your_key")
            >>> results = fred.search_series("unemployment rate")
            >>> for series in results:
            ...     print(f"{series['id']}: {series['title']}")
        """
        url = f"{self.base_url}/series/search"

        params = {
            "search_text": search_text,
            "api_key": self.api_key,
            "file_type": "json",
            "limit": limit,
        }

        self.logger.info("Searching FRED series", extra={"search_text": search_text})

        response = self._make_request(url, params)
        series_list = response.get("seriess", [])

        self.logger.info(
            "Search complete", extra={"search_text": search_text, "results": len(series_list)}
        )

        return series_list

    def get_series_info(self, series_id: str) -> Dict[str, Any]:
        """
        Get metadata for a FRED series.

        Args:
            series_id: FRED series ID

        Returns:
            Dictionary with series metadata (title, units, frequency, etc.)

        Example:
            >>> fred = FREDConnector(api_key="your_key")
            >>> info = fred.get_series_info("UNRATE")
            >>> print(info["title"])
        """
        url = f"{self.base_url}/series"

        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
        }

        response = self._make_request(url, params)
        series_info = response.get("seriess", [{}])[0]

        return series_info
