# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""
KRL Data Connectors - Production-ready data connectors for economic and demographic data.

This package provides unified interfaces for accessing data from major economic
and demographic data providers including FRED, Census Bureau, BLS, World Bank, and OECD.
"""

from .__version__ import __author__, __license__, __version__
from .base_connector import BaseConnector
from .bea_connector import BEAConnector
from .bls_connector import BLSConnector
from .cbp_connector import CountyBusinessPatternsConnector
from .census_connector import CensusConnector
from .environment import EJScreenConnector, EPAAirQualityConnector
from .fred_connector import FREDConnector
from .health import CDCWonderConnector, CountyHealthRankingsConnector, HRSAConnector
from .lehd_connector import LEHDConnector
from .utils.config import find_config_file, load_api_key_from_config

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "BaseConnector",
    "FREDConnector",
    "CensusConnector",
    "LEHDConnector",
    "CountyBusinessPatternsConnector",
    "BLSConnector",
    "BEAConnector",
    "CDCWonderConnector",
    "CountyHealthRankingsConnector",
    "HRSAConnector",
    "EJScreenConnector",
    "EPAAirQualityConnector",
    "find_config_file",
    "load_api_key_from_config",
]
