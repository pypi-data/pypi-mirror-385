# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Securities and Exchange Commission (SEC) Connector for KRL Data Connectors.

This connector provides access to company filings, financial data, and regulatory
information from the SEC EDGAR database.

Data Sources:
    - Company filings (10-K, 10-Q, 8-K, etc.)
    - Insider trading transactions (Form 4)
    - Mutual fund holdings (Form N-PORT)
    - Company facts and financial statements
    - Submissions metadata

API Documentation:
    https://www.sec.gov/edgar/sec-api-documentation

Connector Type:
    REST API connector with caching

Authentication:
    No API key required (rate limited by User-Agent)

Example Usage:
    ```python
    from krl_data_connectors.financial.sec_connector import SECConnector

    # Initialize connector
    connector = SECConnector(user_agent="MyCompany contact@example.com")

    # Get company filings
    filings = connector.get_company_filings(cik="0000320193")  # Apple Inc.

    # Get company facts
    facts = connector.get_company_facts(cik="0000320193")

    # Get recent 10-K filings
    ten_k = connector.get_filings_by_form(form_type="10-K", limit=100)

    # Get insider trading
    insider = connector.get_insider_trading(cik="0000320193")

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


# Form type constants
FORM_TYPES = {
    "10-K": "Annual Report",
    "10-Q": "Quarterly Report",
    "8-K": "Current Report",
    "S-1": "Registration Statement",
    "S-3": "Registration Statement (Simplified)",
    "S-4": "Registration Statement (Business Combination)",
    "S-8": "Registration Statement (Employee Benefit Plan)",
    "DEF 14A": "Proxy Statement",
    "DEFM14A": "Merger Proxy Statement",
    "SC 13D": "Beneficial Ownership Report",
    "SC 13G": "Beneficial Ownership Report (Passive)",
    "4": "Insider Trading (Form 4)",
    "3": "Initial Statement of Beneficial Ownership",
    "5": "Annual Statement of Changes in Beneficial Ownership",
    "NPORT-P": "Monthly Portfolio Investments Report",
}


class SECConnector(BaseConnector):
    """
    Connector for SEC EDGAR database.

    This connector retrieves company filings, financial statements, and
    regulatory information from the SEC's public API.

    Attributes:
        BASE_URL: Base URL for SEC EDGAR website
        API_BASE_URL: Base URL for SEC EDGAR API
        user_agent: Required User-Agent string for SEC API compliance
    """

    BASE_URL = "https://www.sec.gov"
    API_BASE_URL = "https://data.sec.gov"

    def __init__(self, user_agent: str = "KRL-Data-Connectors info@krlabs.dev", timeout: int = 30, **kwargs):
        """
        Initialize the SECConnector.

        Args:
            user_agent: User-Agent string (required by SEC, should include company name and contact)
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseConnector

        Example:
            >>> connector = SECConnector(user_agent="MyCompany contact@example.com")
        """
        super().__init__(timeout=timeout, **kwargs)
        self.api_url = self.API_BASE_URL
        self.user_agent = user_agent
        logger.info(f"SECConnector initialized with User-Agent: {user_agent}")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for SEC EDGAR API.

        SEC EDGAR API does not require an API key, but requires a proper User-Agent header.

        Returns:
            None (no API key required)
        """
        return None

    def connect(self) -> None:
        """
        Establish connection to SEC EDGAR data sources.

        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return

        try:
            self.session = self._init_session()
            # Set required User-Agent header for SEC compliance
            self.session.headers.update({"User-Agent": self.user_agent})
            self.logger.info("Successfully connected to SEC EDGAR data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to SEC EDGAR: {e}")
            raise ConnectionError(f"Could not connect to SEC EDGAR: {e}")

    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from SEC EDGAR API.

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
                if 'filings' in data and 'recent' in data['filings']:
                    return pd.DataFrame(data['filings']['recent'])
                elif 'data' in data:
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

    def get_company_filings(
        self,
        cik: str,
        form_type: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get company filings by CIK number.

        Args:
            cik: Central Index Key (CIK) number (10-digit, zero-padded)
            form_type: Filter by form type (e.g., "10-K", "10-Q")
            limit: Maximum number of records

        Returns:
            DataFrame with company filings

        Example:
            >>> connector = SECConnector(user_agent="MyCompany contact@example.com")
            >>> filings = connector.get_company_filings(cik="0000320193")  # Apple
        """
        # Ensure CIK is 10 digits with leading zeros
        cik = cik.zfill(10)
        
        params: Dict[str, Any] = {"count": limit}
        if form_type:
            params["type"] = form_type

        logger.info(f"Fetching filings for CIK {cik}: {params}")
        endpoint = f"submissions/CIK{cik}.json"
        return self.fetch(endpoint=endpoint, **params)

    def get_company_facts(
        self,
        cik: str,
        taxonomy: str = "us-gaap",
    ) -> pd.DataFrame:
        """
        Get company facts (XBRL financial data).

        Args:
            cik: Central Index Key (CIK) number
            taxonomy: XBRL taxonomy (default: "us-gaap")

        Returns:
            DataFrame with company financial facts

        Example:
            >>> connector = SECConnector(user_agent="MyCompany contact@example.com")
            >>> facts = connector.get_company_facts(cik="0000320193")
        """
        cik = cik.zfill(10)
        
        logger.info(f"Fetching facts for CIK {cik}, taxonomy: {taxonomy}")
        endpoint = f"api/xbrl/companyfacts/CIK{cik}.json"
        return self.fetch(endpoint=endpoint)

    def get_filings_by_form(
        self,
        form_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get filings by form type across all companies.

        Args:
            form_type: Form type (e.g., "10-K", "10-Q", "8-K")
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of records

        Returns:
            DataFrame with filings

        Example:
            >>> connector = SECConnector(user_agent="MyCompany contact@example.com")
            >>> ten_k = connector.get_filings_by_form("10-K", limit=50)
        """
        params: Dict[str, Any] = {
            "form": form_type,
            "count": limit,
        }
        if start_date:
            params["startdt"] = start_date
        if end_date:
            params["enddt"] = end_date

        logger.info(f"Fetching {form_type} filings: {params}")
        return self.fetch(endpoint="submissions", **params)

    def get_insider_trading(
        self,
        cik: str,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get insider trading transactions (Form 4 filings).

        Args:
            cik: Central Index Key (CIK) number
            limit: Maximum number of records

        Returns:
            DataFrame with insider trading data

        Example:
            >>> connector = SECConnector(user_agent="MyCompany contact@example.com")
            >>> insider = connector.get_insider_trading(cik="0000320193")
        """
        cik = cik.zfill(10)
        
        logger.info(f"Fetching insider trading for CIK {cik}")
        return self.get_company_filings(cik=cik, form_type="4", limit=limit)

    def get_mutual_fund_holdings(
        self,
        cik: str,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get mutual fund portfolio holdings (Form N-PORT).

        Args:
            cik: Central Index Key (CIK) number
            limit: Maximum number of records

        Returns:
            DataFrame with mutual fund holdings

        Example:
            >>> connector = SECConnector(user_agent="MyCompany contact@example.com")
            >>> holdings = connector.get_mutual_fund_holdings(cik="0001166559")  # Vanguard
        """
        cik = cik.zfill(10)
        
        logger.info(f"Fetching mutual fund holdings for CIK {cik}")
        return self.get_company_filings(cik=cik, form_type="NPORT-P", limit=limit)

    def get_company_tickers(self) -> pd.DataFrame:
        """
        Get mapping of company tickers to CIK numbers.

        Returns:
            DataFrame with ticker to CIK mappings

        Example:
            >>> connector = SECConnector(user_agent="MyCompany contact@example.com")
            >>> tickers = connector.get_company_tickers()
        """
        logger.info("Fetching company ticker mappings")
        return self.fetch(endpoint="files/company_tickers.json")

    def get_sic_codes(self) -> pd.DataFrame:
        """
        Get Standard Industrial Classification (SIC) codes.

        Returns:
            DataFrame with SIC codes and descriptions

        Example:
            >>> connector = SECConnector(user_agent="MyCompany contact@example.com")
            >>> sic = connector.get_sic_codes()
        """
        logger.info("Fetching SIC codes")
        return self.fetch(endpoint="files/sic_codes.json")

    def get_recent_filings(
        self,
        form_type: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get most recent filings across all companies.

        Args:
            form_type: Filter by form type (optional)
            limit: Maximum number of records

        Returns:
            DataFrame with recent filings

        Example:
            >>> connector = SECConnector(user_agent="MyCompany contact@example.com")
            >>> recent = connector.get_recent_filings(form_type="8-K", limit=50)
        """
        params: Dict[str, Any] = {"count": limit}
        if form_type:
            params["form"] = form_type

        logger.info(f"Fetching recent filings: {params}")
        return self.fetch(endpoint="submissions/filings-recent.json", **params)

    def search_companies(
        self,
        query: str,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Search for companies by name or ticker.

        Args:
            query: Search query (company name or ticker)
            limit: Maximum number of results

        Returns:
            DataFrame with matching companies

        Example:
            >>> connector = SECConnector(user_agent="MyCompany contact@example.com")
            >>> results = connector.search_companies("Apple")
        """
        params: Dict[str, Any] = {
            "query": query,
            "limit": limit,
        }

        logger.info(f"Searching companies: {query}")
        return self.fetch(endpoint="cgi-bin/browse-edgar", **params)

    def get_company_by_ticker(
        self,
        ticker: str,
    ) -> pd.DataFrame:
        """
        Get company information by ticker symbol.

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")

        Returns:
            DataFrame with company information

        Example:
            >>> connector = SECConnector(user_agent="MyCompany contact@example.com")
            >>> company = connector.get_company_by_ticker("AAPL")
        """
        logger.info(f"Fetching company info for ticker: {ticker}")
        
        # Get all tickers first
        tickers_df = self.get_company_tickers()
        
        # Filter by ticker
        if not tickers_df.empty:
            result = tickers_df[tickers_df['ticker'].str.upper() == ticker.upper()]
            return result
        
        return pd.DataFrame()

    def close(self) -> None:
        """
        Close the HTTP session.

        Example:
            >>> connector = SECConnector(user_agent="MyCompany contact@example.com")
            >>> connector.close()
        """
        if self.session:
            self.session.close()
            self.session = None
            logger.info("HTTP session closed")
