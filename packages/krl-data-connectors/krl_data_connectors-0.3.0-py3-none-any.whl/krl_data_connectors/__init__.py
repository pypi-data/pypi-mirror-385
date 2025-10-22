# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""
KRL Data Connectors - Production-ready data connectors for 40 major data sources.

This package provides unified interfaces for accessing data from major government,
research, and public data providers including FRED, Census Bureau, BLS, World Bank,
OECD, NIH, NSF, and 33 other authoritative sources.

Complete coverage across domains:
- Economic & Financial Data (8 connectors)
- Demographic & Labor Data (3 connectors)
- Health & Wellbeing Data (5 connectors)
- Environmental & Climate Data (5 connectors)
- Education Data (3 connectors)
- Housing & Urban Data (2 connectors)
- Agricultural Data (2 connectors)
- Crime & Justice Data (3 connectors)
- Energy Data (1 connector)
- Science & Research Data (2 connectors)
- Transportation Data (1 connector)
- Labor Safety Data (1 connector)
- Social Services Data (2 connectors)
- Veterans Services Data (1 connector)
- Financial Regulation Data (3 connectors)
"""

from .__version__ import __author__, __license__, __version__
from .agricultural import USDAFoodAtlasConnector, USDANASSConnector
from .base_connector import BaseConnector
from .bea_connector import BEAConnector
from .bls_connector import BLSConnector
from .cbp_connector import CountyBusinessPatternsConnector
from .census_connector import CensusConnector
from .crime import BureauOfJusticeConnector, FBIUCRConnector, VictimsOfCrimeConnector
from .economic import OECDConnector, WorldBankConnector
from .education import CollegeScorecardConnector, IPEDSConnector, NCESConnector
from .energy import EIAConnector
from .environment import (
    EJScreenConnector,
    EPAAirQualityConnector,
    NOAAClimateConnector,
    SuperfundConnector,
    WaterQualityConnector,
)
from .financial import FDICConnector, SECConnector, TreasuryConnector
from .fred_connector import FREDConnector
from .health import (
    CDCWonderConnector,
    CountyHealthRankingsConnector,
    FDAConnector,
    HRSAConnector,
    NIHConnector,
)
from .housing import HUDFMRConnector, ZillowConnector
from .labor import OSHAConnector
from .lehd_connector import LEHDConnector
from .science import NSFConnector, USGSConnector
from .social import ACFConnector, SSAConnector
from .transportation import FAAConnector
from .utils.config import find_config_file, load_api_key_from_config
from .veterans import VAConnector

__all__ = [
    # Base
    "BaseConnector",
    # Economic & Financial (8)
    "FREDConnector",
    "BLSConnector",
    "BEAConnector",
    "OECDConnector",
    "WorldBankConnector",
    "SECConnector",
    "TreasuryConnector",
    "FDICConnector",
    # Demographic & Labor (3)
    "CensusConnector",
    "CountyBusinessPatternsConnector",
    "LEHDConnector",
    # Health (5)
    "HRSAConnector",
    "CDCWonderConnector",
    "CountyHealthRankingsConnector",
    "FDAConnector",
    "NIHConnector",
    # Environmental (5)
    "EJScreenConnector",
    "EPAAirQualityConnector",
    "SuperfundConnector",
    "WaterQualityConnector",
    "NOAAClimateConnector",
    # Education (3)
    "NCESConnector",
    "CollegeScorecardConnector",
    "IPEDSConnector",
    # Housing (2)
    "HUDFMRConnector",
    "ZillowConnector",
    # Agricultural (2)
    "USDAFoodAtlasConnector",
    "USDANASSConnector",
    # Crime & Justice (3)
    "FBIUCRConnector",
    "BureauOfJusticeConnector",
    "VictimsOfCrimeConnector",
    # Energy (1)
    "EIAConnector",
    # Science (2)
    "USGSConnector",
    "NSFConnector",
    # Transportation (1)
    "FAAConnector",
    # Labor Safety (1)
    "OSHAConnector",
    # Social Services (2)
    "SSAConnector",
    "ACFConnector",
    # Veterans (1)
    "VAConnector",
    # Utilities
    "find_config_file",
    "load_api_key_from_config",
]
