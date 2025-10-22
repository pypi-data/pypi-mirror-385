"""
College Scorecard API Connector.

Provides access to the U.S. Department of Education's College Scorecard API
for postsecondary education institutional data.
"""

from typing import Any, Dict, List, Optional

import requests

from krl_data_connectors.base_connector import BaseConnector


class CollegeScorecardConnector(BaseConnector):
    """
    Connector for the U.S. Department of Education College Scorecard API.

    The College Scorecard provides data on postsecondary institutions including:
    - School characteristics (name, location, size)
    - Student demographics
    - Costs (tuition, fees, net price)
    - Financial aid
    - Completion rates
    - Earnings after graduation
    - Debt levels

    API Documentation: https://github.com/RTICWDT/open-data-maker/blob/master/API.md
    Data Dictionary: https://collegescorecard.ed.gov/assets/CollegeScorecardDataDictionary.xlsx
    API Key Registration: https://api.data.gov/signup

    Example:
        ```python
        connector = CollegeScorecardConnector(api_key="your_api_key")
        connector.connect()

        # Get schools in California with over 5000 students
        schools = connector.get_schools(
            state="CA",
            student_size_range="5000..",
            fields="id,school.name,latest.student.size,latest.cost.tuition.in_state"
        )
        ```
    """

    base_url: str = "https://api.data.gov/ed/collegescorecard/v1"
    connector_name: str = "CollegeScorecard"

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        """
        Initialize College Scorecard connector.

        Args:
            api_key: API key for data.gov (required, free registration)
            **kwargs: Additional arguments passed to BaseConnector
        """
        super().__init__(api_key=api_key, **kwargs)

    def _get_api_key(self) -> Optional[str]:
        """
        Get College Scorecard API key from instance or configuration.

        Returns:
            API key string or None
        """
        # First check if API key was set during initialization
        if hasattr(self, "api_key") and self.api_key:
            return self.api_key

        # Try to get from config
        try:
            return self.config.get("api_keys", {}).get("college_scorecard")
        except (AttributeError, KeyError):
            return None

    def connect(self) -> None:
        """
        Establish connection to College Scorecard API.

        Validates API key with a simple test request.

        Raises:
            ValueError: If API key is missing
            ConnectionError: If unable to connect to College Scorecard API
        """
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError(
                "College Scorecard API key is required. " "Get one at https://api.data.gov/signup"
            )

        self._init_session()
        assert self.session is not None

        try:
            # Test connection with minimal query
            response = self.session.get(
                f"{self.base_url}/schools.json",
                params={"api_key": api_key, "per_page": 1},
                timeout=30,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to College Scorecard API: {str(e)}") from e

    def fetch(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic fetch method for College Scorecard API queries.

        Args:
            **kwargs: Query parameters

        Returns:
            API response with metadata and results

        Raises:
            ValueError: If API key is missing or parameters invalid
            ConnectionError: If API request fails
        """
        query_params = kwargs.pop("query_params", kwargs)
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("API key is required")

        assert self.session is not None

        params = {"api_key": api_key, **query_params}

        try:
            response = self.session.get(f"{self.base_url}/schools.json", params=params, timeout=60)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if isinstance(data, dict) and "errors" in data:
                error_messages = [err.get("message", str(err)) for err in data["errors"]]
                raise ValueError(f"API error: {', '.join(error_messages)}")

            return data

        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Failed to fetch data from College Scorecard API: {str(e)}"
            ) from e

    def get_schools(
        self,
        school_name: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        distance: Optional[str] = None,
        student_size_range: Optional[str] = None,
        predominant_degree: Optional[int] = None,
        region_id: Optional[int] = None,
        fields: Optional[str] = None,
        page: int = 0,
        per_page: int = 20,
        sort: Optional[str] = None,
        **additional_params: Any,
    ) -> List[Dict[str, Any]]:
        """
        Search for postsecondary schools with various filters.

        Args:
            school_name: School name (partial match supported)
            state: Two-letter state code (e.g., "CA", "NY")
            zip_code: ZIP code for geographic filtering
            distance: Distance from ZIP code (e.g., "10mi", "50km")
            student_size_range: Student size range (e.g., "1000..5000", "5000..")
            predominant_degree: Predominant degree awarded (0=Not classified, 1=Certificate,
                                2=Associate, 3=Bachelor's, 4=Graduate)
            region_id: Census region (0-9)
            fields: Comma-separated list of fields to return (improves performance)
            page: Page number (starts at 0)
            per_page: Results per page (max 100)
            sort: Sort field with optional :asc or :desc (e.g., "latest.student.size:desc")
            **additional_params: Additional query parameters

        Returns:
            List of school records matching the query

        Raises:
            ValueError: If no filters provided or invalid parameters
            ConnectionError: If API request fails

        Example:
            ```python
            # Find large universities in California
            schools = connector.get_schools(
                state="CA",
                student_size_range="10000..",
                predominant_degree=3,  # Bachelor's
                fields="id,school.name,latest.student.size,latest.admissions.admission_rate.overall",
                sort="latest.student.size:desc"
            )
            ```
        """
        params: Dict[str, Any] = {}

        # Add filters
        if school_name is not None:
            params["school.name"] = school_name
        if state is not None:
            params["school.state"] = state
        if zip_code is not None:
            params["zip"] = zip_code
        if distance is not None:
            params["distance"] = distance
        if student_size_range is not None:
            params["latest.student.size__range"] = student_size_range
        if predominant_degree is not None:
            params["school.degrees_awarded.predominant"] = predominant_degree
        if region_id is not None:
            params["school.region_id"] = region_id

        # Add options
        params["page"] = page
        params["per_page"] = min(per_page, 100)  # Max 100 per API

        if fields is not None:
            params["_fields"] = fields
        if sort is not None:
            params["_sort"] = sort

        # Add any additional parameters
        params.update(additional_params)

        response = self.fetch(query_params=params)

        return response.get("results", [])

    def get_school_by_id(
        self, school_id: int, fields: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific school by its IPEDS ID.

        Args:
            school_id: IPEDS institution ID
            fields: Comma-separated list of fields to return

        Returns:
            School record or None if not found

        Example:
            ```python
            # Get MIT (IPEDS ID: 166683)
            mit = connector.get_school_by_id(
                school_id=166683,
                fields="id,school.name,latest.cost.tuition,latest.admissions.sat_scores"
            )
            ```
        """
        params: Dict[str, Any] = {"id": school_id}

        if fields is not None:
            params["_fields"] = fields

        response = self.fetch(query_params=params)
        results = response.get("results", [])

        return results[0] if results else None

    def get_metadata(self, **query_params: Any) -> Dict[str, Any]:
        """
        Get metadata about query results (total count, pagination info).

        Args:
            **query_params: Same parameters as get_schools()

        Returns:
            Metadata dictionary with 'total', 'page', 'per_page' fields

        Example:
            ```python
            # Check how many schools match criteria
            meta = connector.get_metadata(
                state="CA",
                student_size_range="5000.."
            )
            print(f"Found {meta['total']} schools")
            ```
        """
        response = self.fetch(query_params=query_params)
        return response.get("metadata", {})
