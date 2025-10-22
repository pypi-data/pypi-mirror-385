# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
U.S. Department of Treasury Connector for KRL Data Connectors.

This connector provides access to fiscal data, treasury rates, and federal
financial statistics from the U.S. Department of Treasury.

Data Sources:
    - Treasury interest rates (daily, monthly, annual)
    - Federal debt statistics
    - Federal revenue and spending
    - International capital flows
    - Exchange rate data
    - Treasury securities auctions

API Documentation:
    https://fiscaldata.treasury.gov/api-documentation/

Connector Type:
    REST API connector with caching

Authentication:
    No API key required (public data access)

Example Usage:
    ```python
    from krl_data_connectors.financial.treasury_connector import TreasuryConnector

    # Initialize connector
    connector = TreasuryConnector()

    # Get daily treasury rates
    rates = connector.get_daily_treasury_rates(start_date="2023-01-01")

    # Get federal debt data
    debt = connector.get_federal_debt(fiscal_year=2023)

    # Get revenue and spending
    revenue = connector.get_federal_revenue(fiscal_year=2023)

    # Get exchange rates
    exchange = connector.get_exchange_rates(country="China", start_date="2023-01-01")

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
RATE_TYPES = {
    "DAILY": "Daily Treasury Yield Curve Rates",
    "MONTHLY": "Monthly Average Treasury Rates",
    "LONG_TERM": "Treasury Long-Term Rates",
    "REAL_YIELD": "Treasury Real Yield Curve Rates",
}

DEBT_CATEGORIES = {
    "PUBLIC": "Debt Held by the Public",
    "INTRAGOVERNMENTAL": "Intragovernmental Holdings",
    "TOTAL": "Total Public Debt",
}


class TreasuryConnector(BaseConnector):
    """
    Connector for U.S. Department of Treasury fiscal data.

    This connector retrieves treasury rates, federal debt, revenue, spending,
    and other financial statistics from the Treasury's Fiscal Data API.

    Attributes:
        BASE_URL: Base URL for Treasury Fiscal Data website
        API_BASE_URL: Base URL for Fiscal Data API
    """

    BASE_URL = "https://fiscaldata.treasury.gov"
    API_BASE_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"

    def __init__(self, timeout: int = 30, **kwargs):
        """
        Initialize the TreasuryConnector.

        Args:
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseConnector

        Example:
            >>> connector = TreasuryConnector(timeout=60)
        """
        super().__init__(timeout=timeout, **kwargs)
        self.api_url = self.API_BASE_URL
        logger.info("TreasuryConnector initialized (no API key required)")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for Treasury API.

        Treasury Fiscal Data API does not require authentication.

        Returns:
            None (no API key required)
        """
        return None

    def connect(self) -> None:
        """
        Establish connection to Treasury Fiscal Data sources.

        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return

        try:
            self.session = self._init_session()
            self.logger.info("Successfully connected to Treasury Fiscal Data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to Treasury API: {e}")
            raise ConnectionError(f"Could not connect to Treasury API: {e}")

    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from Treasury Fiscal Data API.

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
                else:
                    return pd.DataFrame([data])
            else:
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Failed to fetch data from {endpoint}: {e}")
            # Return empty DataFrame on error
            return pd.DataFrame()

    def get_daily_treasury_rates(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get daily treasury yield curve rates.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of records

        Returns:
            DataFrame with daily treasury rates

        Example:
            >>> connector = TreasuryConnector()
            >>> rates = connector.get_daily_treasury_rates(start_date="2023-01-01")
        """
        params: Dict[str, Any] = {
            "page[size]": limit,
            "sort": "-record_date",
        }
        
        filters = []
        if start_date:
            filters.append(f"record_date:gte:{start_date}")
        if end_date:
            filters.append(f"record_date:lte:{end_date}")
        
        if filters:
            params["filter"] = ",".join(filters)

        logger.info(f"Fetching daily treasury rates: {params}")
        return self.fetch(endpoint="v2/accounting/od/avg_interest_rates", **params)

    def get_monthly_treasury_rates(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get monthly average treasury rates.

        Args:
            start_date: Start date (YYYY-MM)
            end_date: End date (YYYY-MM)
            limit: Maximum number of records

        Returns:
            DataFrame with monthly treasury rates

        Example:
            >>> connector = TreasuryConnector()
            >>> rates = connector.get_monthly_treasury_rates(start_date="2023-01")
        """
        params: Dict[str, Any] = {
            "page[size]": limit,
            "sort": "-record_date",
        }
        
        filters = []
        if start_date:
            filters.append(f"record_date:gte:{start_date}")
        if end_date:
            filters.append(f"record_date:lte:{end_date}")
        
        if filters:
            params["filter"] = ",".join(filters)

        logger.info(f"Fetching monthly treasury rates: {params}")
        return self.fetch(endpoint="v2/accounting/od/avg_interest_rates", **params)

    def get_federal_debt(
        self,
        fiscal_year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get federal debt statistics.

        Args:
            fiscal_year: Fiscal year (YYYY)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of records

        Returns:
            DataFrame with federal debt data

        Example:
            >>> connector = TreasuryConnector()
            >>> debt = connector.get_federal_debt(fiscal_year=2023)
        """
        params: Dict[str, Any] = {
            "page[size]": limit,
            "sort": "-record_date",
        }
        
        filters = []
        if fiscal_year:
            filters.append(f"record_fiscal_year:eq:{fiscal_year}")
        if start_date:
            filters.append(f"record_date:gte:{start_date}")
        if end_date:
            filters.append(f"record_date:lte:{end_date}")
        
        if filters:
            params["filter"] = ",".join(filters)

        logger.info(f"Fetching federal debt: {params}")
        return self.fetch(endpoint="v2/accounting/od/debt_to_penny", **params)

    def get_federal_revenue(
        self,
        fiscal_year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get federal revenue data.

        Args:
            fiscal_year: Fiscal year (YYYY)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of records

        Returns:
            DataFrame with federal revenue data

        Example:
            >>> connector = TreasuryConnector()
            >>> revenue = connector.get_federal_revenue(fiscal_year=2023)
        """
        params: Dict[str, Any] = {
            "page[size]": limit,
            "sort": "-record_date",
        }
        
        filters = []
        if fiscal_year:
            filters.append(f"record_fiscal_year:eq:{fiscal_year}")
        if start_date:
            filters.append(f"record_date:gte:{start_date}")
        if end_date:
            filters.append(f"record_date:lte:{end_date}")
        
        if filters:
            params["filter"] = ",".join(filters)

        logger.info(f"Fetching federal revenue: {params}")
        return self.fetch(endpoint="v2/accounting/mts/mts_table_5", **params)

    def get_federal_spending(
        self,
        fiscal_year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get federal spending data.

        Args:
            fiscal_year: Fiscal year (YYYY)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of records

        Returns:
            DataFrame with federal spending data

        Example:
            >>> connector = TreasuryConnector()
            >>> spending = connector.get_federal_spending(fiscal_year=2023)
        """
        params: Dict[str, Any] = {
            "page[size]": limit,
            "sort": "-record_date",
        }
        
        filters = []
        if fiscal_year:
            filters.append(f"record_fiscal_year:eq:{fiscal_year}")
        if start_date:
            filters.append(f"record_date:gte:{start_date}")
        if end_date:
            filters.append(f"record_date:lte:{end_date}")
        
        if filters:
            params["filter"] = ",".join(filters)

        logger.info(f"Fetching federal spending: {params}")
        return self.fetch(endpoint="v2/accounting/mts/mts_table_6", **params)

    def get_exchange_rates(
        self,
        country: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get foreign exchange rates.

        Args:
            country: Country name (e.g., "China", "United Kingdom")
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of records

        Returns:
            DataFrame with exchange rate data

        Example:
            >>> connector = TreasuryConnector()
            >>> rates = connector.get_exchange_rates(country="China")
        """
        params: Dict[str, Any] = {
            "page[size]": limit,
            "sort": "-record_date",
        }
        
        filters = []
        if country:
            filters.append(f"country:eq:{country}")
        if start_date:
            filters.append(f"record_date:gte:{start_date}")
        if end_date:
            filters.append(f"record_date:lte:{end_date}")
        
        if filters:
            params["filter"] = ",".join(filters)

        logger.info(f"Fetching exchange rates: {params}")
        return self.fetch(endpoint="v2/accounting/od/rates_of_exchange", **params)

    def get_treasury_auctions(
        self,
        security_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get treasury securities auction results.

        Args:
            security_type: Security type (e.g., "Bill", "Note", "Bond")
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of records

        Returns:
            DataFrame with auction data

        Example:
            >>> connector = TreasuryConnector()
            >>> auctions = connector.get_treasury_auctions(security_type="Bill")
        """
        params: Dict[str, Any] = {
            "page[size]": limit,
            "sort": "-auction_date",
        }
        
        filters = []
        if security_type:
            filters.append(f"security_type:eq:{security_type}")
        if start_date:
            filters.append(f"auction_date:gte:{start_date}")
        if end_date:
            filters.append(f"auction_date:lte:{end_date}")
        
        if filters:
            params["filter"] = ",".join(filters)

        logger.info(f"Fetching treasury auctions: {params}")
        return self.fetch(endpoint="v2/accounting/od/auctions_query", **params)

    def get_interest_expense(
        self,
        fiscal_year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get federal interest expense data.

        Args:
            fiscal_year: Fiscal year (YYYY)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of records

        Returns:
            DataFrame with interest expense data

        Example:
            >>> connector = TreasuryConnector()
            >>> expense = connector.get_interest_expense(fiscal_year=2023)
        """
        params: Dict[str, Any] = {
            "page[size]": limit,
            "sort": "-record_date",
        }
        
        filters = []
        if fiscal_year:
            filters.append(f"record_fiscal_year:eq:{fiscal_year}")
        if start_date:
            filters.append(f"record_date:gte:{start_date}")
        if end_date:
            filters.append(f"record_date:lte:{end_date}")
        
        if filters:
            params["filter"] = ",".join(filters)

        logger.info(f"Fetching interest expense: {params}")
        return self.fetch(endpoint="v2/accounting/od/interest_expense", **params)

    def get_gift_contributions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Get gift contributions to reduce public debt.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of records

        Returns:
            DataFrame with gift contribution data

        Example:
            >>> connector = TreasuryConnector()
            >>> gifts = connector.get_gift_contributions(start_date="2023-01-01")
        """
        params: Dict[str, Any] = {
            "page[size]": limit,
            "sort": "-record_date",
        }
        
        filters = []
        if start_date:
            filters.append(f"record_date:gte:{start_date}")
        if end_date:
            filters.append(f"record_date:lte:{end_date}")
        
        if filters:
            params["filter"] = ",".join(filters)

        logger.info(f"Fetching gift contributions: {params}")
        return self.fetch(endpoint="v2/accounting/od/gift_contributions", **params)

    def get_budget_outlook(
        self,
        fiscal_year: Optional[int] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get federal budget outlook and projections.

        Args:
            fiscal_year: Fiscal year (YYYY)
            limit: Maximum number of records

        Returns:
            DataFrame with budget outlook data

        Example:
            >>> connector = TreasuryConnector()
            >>> outlook = connector.get_budget_outlook(fiscal_year=2024)
        """
        params: Dict[str, Any] = {
            "page[size]": limit,
            "sort": "-record_fiscal_year",
        }
        
        if fiscal_year:
            params["filter"] = f"record_fiscal_year:eq:{fiscal_year}"

        logger.info(f"Fetching budget outlook: {params}")
        return self.fetch(endpoint="v2/accounting/mts/mts_table_1", **params)

    def close(self) -> None:
        """
        Close the HTTP session.

        Example:
            >>> connector = TreasuryConnector()
            >>> connector.close()
        """
        if self.session:
            self.session.close()
            self.session = None
            logger.info("HTTP session closed")
