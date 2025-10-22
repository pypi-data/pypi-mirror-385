# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Food and Drug Administration (FDA) Connector for KRL Data Connectors.

This connector provides access to drug approvals, recalls, adverse events,
device classifications, food facility registrations, and other FDA data.

Data Sources:
    - Drug product labels and approvals
    - Drug recalls and enforcement reports
    - Adverse event reports (FAERS)
    - Medical device classifications
    - Food facility registrations
    - Clinical trials
    - Import alerts

API Documentation:
    https://open.fda.gov/apis/

Connector Type:
    REST API connector with caching

Authentication:
    API key optional (higher rate limits with key)

Example Usage:
    ```python
    from krl_data_connectors.health.fda_connector import FDAConnector

    # Initialize connector
    connector = FDAConnector(api_key="your_api_key")

    # Get drug recalls
    recalls = connector.get_drug_recalls(start_date="2023-01-01")

    # Get drug adverse events
    events = connector.get_drug_adverse_events(brand_name="Aspirin")

    # Get device classifications
    devices = connector.get_device_classifications(device_class="III")

    # Get drug approvals
    approvals = connector.get_drug_approvals(year=2023)

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
DEVICE_CLASSES = {
    "I": "Class I - Low Risk",
    "II": "Class II - Moderate Risk",
    "III": "Class III - High Risk",
}

RECALL_STATUS = {
    "ONGOING": "Ongoing",
    "COMPLETED": "Completed",
    "TERMINATED": "Terminated",
}


class FDAConnector(BaseConnector):
    """
    Connector for Food and Drug Administration (FDA) openFDA API.

    This connector retrieves drug data, medical device information,
    adverse events, recalls, and other FDA regulatory data.

    Attributes:
        BASE_URL: Base URL for openFDA website
        API_BASE_URL: Base URL for openFDA API
    """

    BASE_URL = "https://open.fda.gov"
    API_BASE_URL = "https://api.fda.gov"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, **kwargs):
        """
        Initialize the FDAConnector.

        Args:
            api_key: Optional FDA API key (higher rate limits with key)
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseConnector

        Example:
            >>> connector = FDAConnector(api_key="your_api_key", timeout=60)
        """
        self._fda_api_key = api_key
        super().__init__(api_key=api_key, timeout=timeout, **kwargs)
        self.api_url = self.API_BASE_URL
        logger.info("FDAConnector initialized")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for FDA API.

        Returns:
            API key if available, None otherwise
        """
        return self._fda_api_key

    def connect(self) -> None:
        """
        Establish connection to FDA data sources.

        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return

        try:
            self.session = self._init_session()
            self.logger.info("Successfully connected to FDA data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to FDA API: {e}")
            raise ConnectionError(f"Could not connect to FDA API: {e}")

    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from openFDA API.

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
        
        # Add API key if available
        if self.api_key:
            kwargs['api_key'] = self.api_key
        
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
            if isinstance(data, dict):
                if 'results' in data:
                    return pd.DataFrame(data['results'])
                elif 'data' in data:
                    return pd.DataFrame(data['data'])
                else:
                    return pd.DataFrame([data])
            elif isinstance(data, list):
                return pd.DataFrame(data)
            else:
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Failed to fetch data from {endpoint}: {e}")
            # Return empty DataFrame on error
            return pd.DataFrame()

    def get_drug_recalls(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        classification: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get drug recall information.

        Args:
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            classification: Recall classification (e.g., "Class I", "Class II")
            limit: Maximum number of records

        Returns:
            DataFrame with drug recall data

        Example:
            >>> connector = FDAConnector()
            >>> recalls = connector.get_drug_recalls(start_date="20230101")
        """
        params: Dict[str, Any] = {
            "limit": limit,
        }
        
        search_terms = []
        if start_date:
            search_terms.append(f"report_date:[{start_date} TO *]")
        if end_date:
            search_terms.append(f"report_date:[* TO {end_date}]")
        if classification:
            search_terms.append(f'classification:"{classification}"')
        
        if search_terms:
            params["search"] = " AND ".join(search_terms)

        logger.info(f"Fetching drug recalls: {params}")
        return self.fetch(endpoint="drug/enforcement.json", **params)

    def get_drug_adverse_events(
        self,
        brand_name: Optional[str] = None,
        generic_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get drug adverse event reports (FAERS).

        Args:
            brand_name: Brand name of drug
            generic_name: Generic name of drug
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            limit: Maximum number of records

        Returns:
            DataFrame with adverse event data

        Example:
            >>> connector = FDAConnector()
            >>> events = connector.get_drug_adverse_events(brand_name="Aspirin")
        """
        params: Dict[str, Any] = {
            "limit": limit,
        }
        
        search_terms = []
        if brand_name:
            search_terms.append(f'patient.drug.openfda.brand_name:"{brand_name}"')
        if generic_name:
            search_terms.append(f'patient.drug.openfda.generic_name:"{generic_name}"')
        if start_date:
            search_terms.append(f"receivedate:[{start_date} TO *]")
        if end_date:
            search_terms.append(f"receivedate:[* TO {end_date}]")
        
        if search_terms:
            params["search"] = " AND ".join(search_terms)

        logger.info(f"Fetching drug adverse events: {params}")
        return self.fetch(endpoint="drug/event.json", **params)

    def get_device_recalls(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        classification: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get medical device recall information.

        Args:
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            classification: Recall classification
            limit: Maximum number of records

        Returns:
            DataFrame with device recall data

        Example:
            >>> connector = FDAConnector()
            >>> recalls = connector.get_device_recalls(start_date="20230101")
        """
        params: Dict[str, Any] = {
            "limit": limit,
        }
        
        search_terms = []
        if start_date:
            search_terms.append(f"report_date:[{start_date} TO *]")
        if end_date:
            search_terms.append(f"report_date:[* TO {end_date}]")
        if classification:
            search_terms.append(f'classification:"{classification}"')
        
        if search_terms:
            params["search"] = " AND ".join(search_terms)

        logger.info(f"Fetching device recalls: {params}")
        return self.fetch(endpoint="device/enforcement.json", **params)

    def get_device_classifications(
        self,
        device_class: Optional[str] = None,
        medical_specialty: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get medical device classification information.

        Args:
            device_class: Device class (I, II, or III)
            medical_specialty: Medical specialty (e.g., "Cardiovascular")
            limit: Maximum number of records

        Returns:
            DataFrame with device classification data

        Example:
            >>> connector = FDAConnector()
            >>> devices = connector.get_device_classifications(device_class="III")
        """
        params: Dict[str, Any] = {
            "limit": limit,
        }
        
        search_terms = []
        if device_class:
            search_terms.append(f'device_class:"{device_class}"')
        if medical_specialty:
            search_terms.append(f'medical_specialty:"{medical_specialty}"')
        
        if search_terms:
            params["search"] = " AND ".join(search_terms)

        logger.info(f"Fetching device classifications: {params}")
        return self.fetch(endpoint="device/classification.json", **params)

    def get_device_adverse_events(
        self,
        device_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get medical device adverse event reports.

        Args:
            device_name: Device brand or generic name
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            limit: Maximum number of records

        Returns:
            DataFrame with device adverse event data

        Example:
            >>> connector = FDAConnector()
            >>> events = connector.get_device_adverse_events(device_name="Pacemaker")
        """
        params: Dict[str, Any] = {
            "limit": limit,
        }
        
        search_terms = []
        if device_name:
            search_terms.append(f'device.brand_name:"{device_name}"')
        if start_date:
            search_terms.append(f"date_received:[{start_date} TO *]")
        if end_date:
            search_terms.append(f"date_received:[* TO {end_date}]")
        
        if search_terms:
            params["search"] = " AND ".join(search_terms)

        logger.info(f"Fetching device adverse events: {params}")
        return self.fetch(endpoint="device/event.json", **params)

    def get_food_recalls(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        classification: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get food recall information.

        Args:
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            classification: Recall classification
            limit: Maximum number of records

        Returns:
            DataFrame with food recall data

        Example:
            >>> connector = FDAConnector()
            >>> recalls = connector.get_food_recalls(start_date="20230101")
        """
        params: Dict[str, Any] = {
            "limit": limit,
        }
        
        search_terms = []
        if start_date:
            search_terms.append(f"report_date:[{start_date} TO *]")
        if end_date:
            search_terms.append(f"report_date:[* TO {end_date}]")
        if classification:
            search_terms.append(f'classification:"{classification}"')
        
        if search_terms:
            params["search"] = " AND ".join(search_terms)

        logger.info(f"Fetching food recalls: {params}")
        return self.fetch(endpoint="food/enforcement.json", **params)

    def get_drug_approvals(
        self,
        year: Optional[int] = None,
        sponsor_name: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get drug approval information (NDAs and ANDAs).

        Args:
            year: Approval year
            sponsor_name: Sponsor/manufacturer name
            limit: Maximum number of records

        Returns:
            DataFrame with drug approval data

        Example:
            >>> connector = FDAConnector()
            >>> approvals = connector.get_drug_approvals(year=2023)
        """
        params: Dict[str, Any] = {
            "limit": limit,
        }
        
        search_terms = []
        if year:
            search_terms.append(f"submissions.submission_status_date:[{year}0101 TO {year}1231]")
        if sponsor_name:
            search_terms.append(f'sponsor_name:"{sponsor_name}"')
        
        if search_terms:
            params["search"] = " AND ".join(search_terms)

        logger.info(f"Fetching drug approvals: {params}")
        return self.fetch(endpoint="drug/nda.json", **params)

    def get_drug_labels(
        self,
        brand_name: Optional[str] = None,
        generic_name: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get drug label information (SPL).

        Args:
            brand_name: Brand name of drug
            generic_name: Generic name of drug
            limit: Maximum number of records

        Returns:
            DataFrame with drug label data

        Example:
            >>> connector = FDAConnector()
            >>> labels = connector.get_drug_labels(brand_name="Tylenol")
        """
        params: Dict[str, Any] = {
            "limit": limit,
        }
        
        search_terms = []
        if brand_name:
            search_terms.append(f'openfda.brand_name:"{brand_name}"')
        if generic_name:
            search_terms.append(f'openfda.generic_name:"{generic_name}"')
        
        if search_terms:
            params["search"] = " AND ".join(search_terms)

        logger.info(f"Fetching drug labels: {params}")
        return self.fetch(endpoint="drug/label.json", **params)

    def get_device_registrations(
        self,
        registration_number: Optional[str] = None,
        proprietary_name: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get medical device registration and listing information.

        Args:
            registration_number: Device registration number
            proprietary_name: Device proprietary/brand name
            limit: Maximum number of records

        Returns:
            DataFrame with device registration data

        Example:
            >>> connector = FDAConnector()
            >>> devices = connector.get_device_registrations()
        """
        params: Dict[str, Any] = {
            "limit": limit,
        }
        
        search_terms = []
        if registration_number:
            search_terms.append(f'registration_number:"{registration_number}"')
        if proprietary_name:
            search_terms.append(f'proprietary_name:"{proprietary_name}"')
        
        if search_terms:
            params["search"] = " AND ".join(search_terms)

        logger.info(f"Fetching device registrations: {params}")
        return self.fetch(endpoint="device/reglist.json", **params)

    def get_tobacco_problem_reports(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get tobacco product problem reports.

        Args:
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            limit: Maximum number of records

        Returns:
            DataFrame with tobacco problem report data

        Example:
            >>> connector = FDAConnector()
            >>> reports = connector.get_tobacco_problem_reports(start_date="20230101")
        """
        params: Dict[str, Any] = {
            "limit": limit,
        }
        
        search_terms = []
        if start_date:
            search_terms.append(f"date_submitted:[{start_date} TO *]")
        if end_date:
            search_terms.append(f"date_submitted:[* TO {end_date}]")
        
        if search_terms:
            params["search"] = " AND ".join(search_terms)

        logger.info(f"Fetching tobacco problem reports: {params}")
        return self.fetch(endpoint="tobacco/problem.json", **params)

    def close(self) -> None:
        """
        Close the HTTP session.

        Example:
            >>> connector = FDAConnector()
            >>> connector.close()
        """
        if self.session:
            self.session.close()
            self.session = None
            logger.info("HTTP session closed")
