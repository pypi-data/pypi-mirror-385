# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""Abstract base class for data connectors."""

import hashlib
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from krl_core import ConfigManager, FileCache, get_logger


class BaseConnector(ABC):
    """
    Abstract base class for data connectors.

    Provides common functionality for all data connectors including:
    - Structured logging
    - Configuration management
    - Intelligent caching
    - HTTP session management
    - Error handling and retries
    - Rate limiting

    Subclasses must implement:
    - _get_api_key(): Return API key from config
    - connect(): Establish connection to data source
    - fetch(): Fetch data from source

    Args:
        api_key: API key for the data source (optional if in config)
        cache_dir: Directory for cache files (default: from config or ~/.krl_cache)
        cache_ttl: Cache time-to-live in seconds (default: 3600)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts (default: 3)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        # Initialize logger
        self.logger = get_logger(self.__class__.__name__)

        # Initialize configuration manager
        self.config = ConfigManager()

        # Initialize cache
        cache_dir = cache_dir or self.config.get("CACHE_DIR", default="~/.krl_cache")
        self.cache = FileCache(
            cache_dir=cache_dir,
            default_ttl=cache_ttl,
            namespace=self.__class__.__name__.lower(),
        )

        # Get API key
        self.api_key = api_key or self._get_api_key()
        if not self.api_key:
            self.logger.warning("No API key provided", extra={"connector": self.__class__.__name__})

        # HTTP session settings
        self.timeout = timeout
        self.max_retries = max_retries
        self.session: Optional[requests.Session] = None

        self.logger.info(
            "Connector initialized",
            extra={
                "connector": self.__class__.__name__,
                "cache_dir": str(self.cache.cache_dir),
                "cache_ttl": cache_ttl,
                "has_api_key": bool(self.api_key),
            },
        )

    @abstractmethod
    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration.

        Should be implemented by subclasses to retrieve the appropriate
        API key from environment variables or config files.

        Returns:
            API key or None if not found
        """

    def _init_session(self) -> requests.Session:
        """
        Initialize HTTP session with retry logic.

        Returns:
            Configured requests.Session object
        """
        if self.session is None:
            self.session = requests.Session()

            # Configure retries
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry

            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],
            )

            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

            self.logger.debug("HTTP session initialized")

        return self.session

    def _make_cache_key(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a cache key from URL and parameters.

        Args:
            url: Request URL
            params: Request parameters

        Returns:
            Cache key (SHA256 hash of URL + params)
        """
        # Create a deterministic string representation
        param_str = urlencode(sorted((params or {}).items()))
        cache_str = f"{url}?{param_str}"

        # Hash to create shorter key
        return hashlib.sha256(cache_str.encode()).hexdigest()

    def _make_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with caching and error handling.

        Args:
            url: Request URL
            params: Query parameters
            use_cache: Whether to use cache (default: True)

        Returns:
            Response data as dictionary

        Raises:
            requests.RequestException: If request fails after retries
        """
        # Check cache first
        if use_cache:
            cache_key = self._make_cache_key(url, params)
            cached_response = self.cache.get(cache_key)

            if cached_response is not None:
                self.logger.info("Cache hit", extra={"url": url, "cache_key": cache_key[:16]})
                return cached_response

        # Make request
        session = self._init_session()

        self.logger.info("Making API request", extra={"url": url, "params": params})

        try:
            response = session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Cache successful response
            if use_cache:
                cache_key = self._make_cache_key(url, params)
                self.cache.set(cache_key, data)

                self.logger.debug("Response cached", extra={"cache_key": cache_key[:16]})

            return data

        except requests.exceptions.HTTPError as e:
            extra_info = {"url": url}
            if e.response is not None:
                extra_info["status_code"] = e.response.status_code
            self.logger.error("HTTP error", extra=extra_info, exc_info=True)
            raise

        except requests.exceptions.Timeout:
            self.logger.error(
                "Request timeout", extra={"url": url, "timeout": self.timeout}, exc_info=True
            )
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error("Request failed", extra={"url": url, "error": str(e)}, exc_info=True)
            raise

    @abstractmethod
    def connect(self) -> None:
        """
        Establish connection to the data source.

        Should be implemented by subclasses to perform any necessary
        connection setup or authentication.
        """

    @abstractmethod
    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from the source.

        Should be implemented by subclasses to retrieve data.

        Args:
            **kwargs: Connector-specific parameters

        Returns:
            Fetched data (format depends on connector)
        """

    def disconnect(self) -> None:
        """
        Close connection and cleanup resources.

        Closes HTTP session and cleans up any resources.
        Can be overridden by subclasses for additional cleanup.
        """
        if self.session:
            self.session.close()
            self.session = None
            self.logger.debug("HTTP session closed")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics (hits, misses, size, etc.)
        """
        return self.cache.get_stats()

    def clear_cache(self) -> None:
        """Clear all cached responses for this connector."""
        self.cache.clear()
        self.logger.info("Cache cleared")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"has_api_key={bool(self.api_key)}, "
            f"cache_dir='{self.cache.cache_dir}'"
            ")"
        )
