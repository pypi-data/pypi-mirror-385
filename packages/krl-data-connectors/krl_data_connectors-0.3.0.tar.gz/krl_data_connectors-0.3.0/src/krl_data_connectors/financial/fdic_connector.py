# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Federal Deposit Insurance Corporation (FDIC) Connector for KRL Data Connectors.

This connector provides access to banking data, institution information,
failed banks, financial statistics, and regulatory data from the FDIC.

Data Sources:
    - Bank financial data and performance metrics
    - Failed bank lists
    - Institution details and branch locations
    - Summary of deposits (SOD)
    - Financial institution letters (FILs)
    - Structure change data

API Documentation:
    https://banks.data.fdic.gov/docs/

Connector Type:
    REST API connector with caching

Authentication:
    No API key required (public data access)

Example Usage:
    ```python
    from krl_data_connectors.financial.fdic_connector import FDICConnector

    # Initialize connector
    connector = FDICConnector()

    # Get list of failed banks
    failed = connector.get_failed_banks(start_date="2020-01-01")

    # Get institution details
    institutions = connector.get_institutions(state="NY")

    # Get financial data
    financials = connector.get_financials(cert="3511")

    # Get summary of deposits
    deposits = connector.get_summary_of_deposits(year=2023)

    # Close connection
    connector.close()
    ```

Dependencies:
    - pandas: For data manipulation
    - requests: For HTTP requests
    - BaseConnector: For connection management and caching

Author: KR-Labs
License: Apache-2.0
"""

import logging
from typing import Any, Dict, Optional

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)


# Data constants
INSTITUTION_TYPES = {
    "COMMERCIAL_BANK": "N",
    "SAVINGS_BANK": "SB",
    "SAVINGS_ASSOCIATION": "SA",
    "COOPERATIVE_BANK": "CB",
}

FINANCIAL_REPORT_TYPES = {
    "CALL_REPORT": "Call Report",
    "TFR": "Thrift Financial Report",
    "UBPR": "Uniform Bank Performance Report",
}


class FDICConnector(BaseConnector):
    """
    Connector for Federal Deposit Insurance Corporation (FDIC) data.

    This connector retrieves banking institution data, failed banks,
    financial statistics, and regulatory information from the FDIC API.

    Attributes:
        BASE_URL: Base URL for FDIC BankFind Suite website
        API_BASE_URL: Base URL for FDIC BankFind Suite API
    """

    BASE_URL = "https://banks.data.fdic.gov"
    API_BASE_URL = "https://banks.data.fdic.gov/api"

    def __init__(self, timeout: int = 30, **kwargs):
        """
        Initialize the FDICConnector.

        Args:
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseConnector

        Example:
            >>> connector = FDICConnector(timeout=60)
        """
        super().__init__(timeout=timeout, **kwargs)
        self.api_url = self.API_BASE_URL
        logger.info("FDICConnector initialized (no API key required)")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for FDIC API.

        FDIC BankFind Suite API does not require authentication.

        Returns:
            None (no API key required)
        """
        return None

    def connect(self) -> None:
        """
        Establish connection to FDIC data sources.

        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return

        try:
            self.session = self._init_session()
            self.logger.info("Successfully connected to FDIC data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to FDIC API: {e}")
            raise ConnectionError(f"Could not connect to FDIC API: {e}")

    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from FDIC BankFind Suite API.

        Args:
            endpoint: API endpoint path (required)
            **kwargs: Additional query parameters

        Returns:
            DataFrame: Query results

        Raises:
            requests.HTTPError: If API request fails
        """
        endpoint = kwargs.pop('endpoint', None)
        
        if not endpoint:
            raise ValueError("endpoint parameter is required")
        
        if not self.session:
            self.connect()

        url = f"{self.api_url}/{endpoint}"
        
        # Add format parameter if not specified
        if 'format' not in kwargs:
            kwargs['format'] = 'json'
        
        try:
            response = self.session.get(url, params=kwargs, timeout=self.timeout)
            response.raise_for_status()
            
            # Try JSON first
            try:
                data = response.json()
            except ValueError:
                # Return empty dataframe if no JSON
                return pd.DataFrame()

            # Convert to DataFrame
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                # Handle different response structures
                if 'data' in data:
                    return pd.DataFrame(data['data'])
                elif 'results' in data:
                    return pd.DataFrame(data['results'])
                elif 'institutions' in data:
                    return pd.DataFrame(data['institutions'])
                else:
                    return pd.DataFrame([data])
            else:
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Failed to fetch data from {endpoint}: {e}")
            # Return empty DataFrame on error
            return pd.DataFrame()

    def get_failed_banks(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get list of failed banks.

        Args:
            start_date: Start date for failures (YYYY-MM-DD)
            end_date: End date for failures (YYYY-MM-DD)
            state: State abbreviation (e.g., "NY", "CA")
            limit: Maximum number of records

        Returns:
            DataFrame with failed bank information

        Example:
            >>> connector = FDICConnector()
            >>> failed = connector.get_failed_banks(start_date="2020-01-01")
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "sort_by": "FAILDATE",
            "sort_order": "DESC",
        }
        
        filters = []
        if start_date:
            filters.append(f"FAILDATE:[{start_date} TO *]")
        if end_date:
            filters.append(f"FAILDATE:[* TO {end_date}]")
        if state:
            filters.append(f"STALP:{state}")
        
        if filters:
            params["filters"] = " AND ".join(filters)

        logger.info(f"Fetching failed banks: {params}")
        return self.fetch(endpoint="failures", **params)

    def get_institutions(
        self,
        state: Optional[str] = None,
        city: Optional[str] = None,
        institution_type: Optional[str] = None,
        active: bool = True,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get list of FDIC-insured institutions.

        Args:
            state: State abbreviation (e.g., "NY", "CA")
            city: City name
            institution_type: Institution type (use INSTITUTION_TYPES constants)
            active: Include only active institutions (default: True)
            limit: Maximum number of records

        Returns:
            DataFrame with institution information

        Example:
            >>> connector = FDICConnector()
            >>> banks = connector.get_institutions(state="NY", city="New York")
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "sort_by": "NAME",
            "sort_order": "ASC",
        }
        
        filters = []
        if state:
            filters.append(f"STALP:{state}")
        if city:
            filters.append(f"CITY:{city}")
        if institution_type:
            filters.append(f"INSTCLASS:{institution_type}")
        if active:
            filters.append("ACTIVE:1")
        
        if filters:
            params["filters"] = " AND ".join(filters)

        logger.info(f"Fetching institutions: {params}")
        return self.fetch(endpoint="institutions", **params)

    def get_financials(
        self,
        cert: Optional[str] = None,
        report_date: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get financial data for institutions.

        Args:
            cert: FDIC certificate number
            report_date: Report date (YYYY-MM-DD or YYYYMMDD)
            limit: Maximum number of records

        Returns:
            DataFrame with financial data

        Example:
            >>> connector = FDICConnector()
            >>> financials = connector.get_financials(cert="3511")
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "sort_by": "REPDTE",
            "sort_order": "DESC",
        }
        
        filters = []
        if cert:
            filters.append(f"CERT:{cert}")
        if report_date:
            # Convert date format if needed
            clean_date = report_date.replace("-", "")
            filters.append(f"REPDTE:{clean_date}")
        
        if filters:
            params["filters"] = " AND ".join(filters)

        logger.info(f"Fetching financials: {params}")
        return self.fetch(endpoint="financials", **params)

    def get_summary_of_deposits(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None,
        county: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get Summary of Deposits (SOD) data.

        Args:
            year: Data year (YYYY)
            state: State abbreviation
            county: County name
            limit: Maximum number of records

        Returns:
            DataFrame with deposit summary data

        Example:
            >>> connector = FDICConnector()
            >>> deposits = connector.get_summary_of_deposits(year=2023, state="NY")
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "sort_by": "YEAR",
            "sort_order": "DESC",
        }
        
        filters = []
        if year:
            filters.append(f"YEAR:{year}")
        if state:
            filters.append(f"STNAME:{state}")
        if county:
            filters.append(f"COUNTY:{county}")
        
        if filters:
            params["filters"] = " AND ".join(filters)

        logger.info(f"Fetching summary of deposits: {params}")
        return self.fetch(endpoint="sod", **params)

    def get_institution_branches(
        self,
        cert: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get branch locations for institutions.

        Args:
            cert: FDIC certificate number
            state: State abbreviation
            limit: Maximum number of records

        Returns:
            DataFrame with branch location data

        Example:
            >>> connector = FDICConnector()
            >>> branches = connector.get_institution_branches(cert="3511")
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "sort_by": "BKCLASS",
            "sort_order": "ASC",
        }
        
        filters = []
        if cert:
            filters.append(f"CERT:{cert}")
        if state:
            filters.append(f"STALP:{state}")
        
        if filters:
            params["filters"] = " AND ".join(filters)

        logger.info(f"Fetching institution branches: {params}")
        return self.fetch(endpoint="locations", **params)

    def get_structure_changes(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        change_type: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get bank structure change data (mergers, acquisitions, etc.).

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            change_type: Type of change (e.g., "MERGER", "ACQUISITION")
            limit: Maximum number of records

        Returns:
            DataFrame with structure change data

        Example:
            >>> connector = FDICConnector()
            >>> changes = connector.get_structure_changes(start_date="2023-01-01")
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "sort_by": "EFFDATE",
            "sort_order": "DESC",
        }
        
        filters = []
        if start_date:
            clean_date = start_date.replace("-", "")
            filters.append(f"EFFDATE:[{clean_date} TO *]")
        if end_date:
            clean_date = end_date.replace("-", "")
            filters.append(f"EFFDATE:[* TO {clean_date}]")
        if change_type:
            filters.append(f"CHANGETYPE:{change_type}")
        
        if filters:
            params["filters"] = " AND ".join(filters)

        logger.info(f"Fetching structure changes: {params}")
        return self.fetch(endpoint="history", **params)

    def get_institution_by_cert(
        self,
        cert: str,
    ) -> pd.DataFrame:
        """
        Get detailed information for a specific institution by CERT number.

        Args:
            cert: FDIC certificate number

        Returns:
            DataFrame with institution details

        Example:
            >>> connector = FDICConnector()
            >>> bank = connector.get_institution_by_cert("3511")
        """
        params: Dict[str, Any] = {
            "filters": f"CERT:{cert}",
            "limit": 1,
        }

        logger.info(f"Fetching institution by cert: {cert}")
        return self.fetch(endpoint="institutions", **params)

    def get_institution_by_name(
        self,
        name: str,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Search for institutions by name.

        Args:
            name: Institution name (partial match supported)
            limit: Maximum number of records

        Returns:
            DataFrame with matching institutions

        Example:
            >>> connector = FDICConnector()
            >>> banks = connector.get_institution_by_name("Chase")
        """
        params: Dict[str, Any] = {
            "search": name,
            "limit": limit,
            "sort_by": "NAME",
            "sort_order": "ASC",
        }

        logger.info(f"Searching institutions by name: {name}")
        return self.fetch(endpoint="institutions", **params)

    def get_financial_ratios(
        self,
        cert: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get financial ratios and performance metrics for an institution.

        Args:
            cert: FDIC certificate number
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of records

        Returns:
            DataFrame with financial ratios

        Example:
            >>> connector = FDICConnector()
            >>> ratios = connector.get_financial_ratios(cert="3511")
        """
        params: Dict[str, Any] = {
            "filters": f"CERT:{cert}",
            "limit": limit,
            "sort_by": "REPDTE",
            "sort_order": "DESC",
        }
        
        # Add date filters if provided
        if start_date or end_date:
            date_filters = [f"CERT:{cert}"]
            if start_date:
                clean_date = start_date.replace("-", "")
                date_filters.append(f"REPDTE:[{clean_date} TO *]")
            if end_date:
                clean_date = end_date.replace("-", "")
                date_filters.append(f"REPDTE:[* TO {clean_date}]")
            params["filters"] = " AND ".join(date_filters)

        logger.info(f"Fetching financial ratios: {params}")
        return self.fetch(endpoint="financials", **params)

    def get_bank_holding_companies(
        self,
        state: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get bank holding company information.

        Args:
            state: State abbreviation
            limit: Maximum number of records

        Returns:
            DataFrame with bank holding company data

        Example:
            >>> connector = FDICConnector()
            >>> bhcs = connector.get_bank_holding_companies(state="NY")
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "sort_by": "NAME",
            "sort_order": "ASC",
        }
        
        filters = []
        if state:
            filters.append(f"STALP:{state}")
        # Filter for bank holding companies
        filters.append("SUBCHAPS:1")
        
        if filters:
            params["filters"] = " AND ".join(filters)

        logger.info(f"Fetching bank holding companies: {params}")
        return self.fetch(endpoint="institutions", **params)

    def close(self) -> None:
        """
        Close the HTTP session.

        Example:
            >>> connector = FDICConnector()
            >>> connector.close()
        """
        if self.session:
            self.session.close()
            self.session = None
            logger.info("HTTP session closed")
