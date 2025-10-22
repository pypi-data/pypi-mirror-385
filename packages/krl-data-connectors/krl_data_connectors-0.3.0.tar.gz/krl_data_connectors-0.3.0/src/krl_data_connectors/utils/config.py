"""Configuration file utilities for KRL Data Connectors.

This module provides utilities to locate API key configuration files
in a portable, cross-platform manner.
"""

import os
from pathlib import Path
from typing import Optional


def find_config_file(filename: str = "apikeys") -> Optional[str]:
    """
    Find KRL config file in standard locations.

    Searches for configuration files in the following priority order:
    1. KRL_CONFIG_PATH environment variable (if set)
    2. ~/KR-Labs/Khipu/config/{filename} (KRL standard location)
    3. ~/.krl/{filename} (hidden config directory)
    4. ./config/{filename} (relative to current directory)

    Args:
        filename: Name of the config file to find (default: 'apikeys')

    Returns:
        Absolute path to config file if found, None otherwise

    Example:
        >>> config_path = find_config_file('apikeys')
        >>> if config_path:
        ...     with open(config_path, 'r') as f:
        ...         # Read API keys
        ...         pass
    """
    search_paths = [
        os.getenv("KRL_CONFIG_PATH"),
        Path.home() / "KR-Labs" / "Khipu" / "config" / filename,
        Path.home() / ".krl" / filename,
        Path("./config") / filename,
    ]

    for path in search_paths:
        if path and Path(path).exists():
            return str(Path(path).resolve())

    return None


def load_api_key_from_config(api_name: str, config_file: str = "apikeys") -> Optional[str]:
    """
    Load a specific API key from a configuration file.

    Args:
        api_name: Name of the API (e.g., 'BEA', 'FRED', 'BLS')
        config_file: Name of the config file (default: 'apikeys')

    Returns:
        API key string if found, None otherwise

    Example:
        >>> bea_key = load_api_key_from_config('BEA')
        >>> if bea_key:
        ...     connector = BEAConnector(api_key=bea_key)
    """
    config_path = find_config_file(config_file)
    if not config_path:
        return None

    try:
        with open(config_path, "r") as f:
            for line in f:
                # Look for patterns like "BEA API KEY: xxxxx"
                if f"{api_name.upper()} API" in line.upper():
                    if ":" in line:
                        return line.split(":", 1)[1].strip()
    except Exception:
        return None

    return None
