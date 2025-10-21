"""
HRSA (Health Resources and Services Administration) Data Connector

Provides access to HRSA health facility data, including:
- Health Professional Shortage Areas (HPSA) - Primary Care, Dental, Mental Health
- Medically Underserved Areas/Populations (MUA/P)
- Health Centers (FQHC - Federally Qualified Health Centers)
- UDS (Uniform Data System) metrics

**⚠️ DATA ACCESS NOTE:**

HRSA does NOT provide a REST API for programmatic access. Data is provided as
downloadable files from the HRSA Data Warehouse.

**Data Downloads:**
- **Shortage Areas**: https://data.hrsa.gov/data/download?data=SHORT
  - Available formats: CSV, XLSX, KML, SHP (Shapefile)
  - Includes HPSA (Primary Care, Dental, Mental Health) and MUA/P data
  
- **Health Centers**: https://data.hrsa.gov/data/download
  - Health Center service delivery sites
  - Grant information
  - UDS (Uniform Data System) data

**Interactive Tools:**
- HPSA Find: https://data.hrsa.gov/topics/health-workforce/shortage-areas/hpsa-find
- MUA Find: https://data.hrsa.gov/topics/health-workforce/shortage-areas/mua-find
- Health Center Locator: https://findahealthcenter.hrsa.gov/

For actual data access, download CSV files from HRSA Data Warehouse and use this connector
to load and analyze the data.

**Data Domains:**
- D05: Healthcare Access & Affordability
- D06: Public Health & Wellness
- D24: Geographic & Spatial Data

**Example Usage:**
    >>> from krl_data_connectors.health import HRSAConnector
    >>> 
    >>> # Initialize connector
    >>> hrsa = HRSAConnector()
    >>> 
    >>> # Load HPSA data from downloaded CSV
    >>> hpsa_data = hrsa.load_hpsa_data('HPSA_data.csv')
    >>> 
    >>> # Filter by state
    >>> ri_shortages = hrsa.get_state_data(hpsa_data, 'RI')
    >>> 
    >>> # Get primary care shortages
    >>> primary_care = hrsa.filter_by_discipline(hpsa_data, 'Primary Care')
    >>> 
    >>> # Find high-need areas (score >= 15)
    >>> high_need = hrsa.get_high_need_areas(hpsa_data, score_threshold=15)

---

© 2025 KR-Labs. All rights reserved.

KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector


class HRSAConnector(BaseConnector):
    """
    Connector for HRSA (Health Resources and Services Administration) data.
    
    **⚠️ IMPORTANT**: HRSA does not provide a programmatic API. This connector is designed
    to work with CSV files downloaded from the HRSA Data Warehouse.
    
    **Supported Data Types:**
    - **HPSA** (Health Professional Shortage Areas): Primary Care, Dental Health, Mental Health
    - **MUA/P** (Medically Underserved Areas/Populations)
    - **Health Centers**: FQHC service delivery sites
    - **UDS**: Uniform Data System health center metrics
    
    **HPSA Disciplines:**
    - Primary Care
    - Dental Health
    - Mental Health
    
    **HPSA Types:**
    - Geographic (geographic area)
    - Population (specific population group)
    - Facility (specific healthcare facility)
    
    **Shortage Score:**
    - Range: 0-26 (higher = greater shortage)
    - Score >= 15: High need
    - Score >= 20: Critical need
    
    Attributes:
        HPSA_DISCIPLINES: Set of valid HPSA discipline types
        HPSA_TYPES: Set of valid HPSA designation types
        MUA_TYPES: Set of valid MUA/P designation types
    """
    
    # HPSA discipline categories
    HPSA_DISCIPLINES = {
        'Primary Care',
        'Dental Health',
        'Mental Health'
    }
    
    # HPSA designation types
    HPSA_TYPES = {
        'Geographic',
        'Population',
        'Facility'
    }
    
    # MUA/P designation types
    MUA_TYPES = {
        'Geographic MUA',
        'Population MUP',
        'Geographic MUA and Population MUP'
    }
    
    def __init__(
        self,
        cache_dir: Optional[Union[str, Path]] = None,
        cache_ttl: int = 86400,
        **kwargs: Any
    ) -> None:
        """
        Initialize HRSA connector.
        
        Args:
            cache_dir: Directory for caching data (default: ~/.krl/cache/hrsa)
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
            **kwargs: Additional arguments passed to BaseConnector
        """
        super().__init__(
            api_key=None,
            cache_dir=str(cache_dir or Path.home() / ".krl" / "cache" / "hrsa"),
            cache_ttl=cache_ttl,
            **kwargs
        )
        self.logger.info("HRSA connector initialized (file-based)")
    
    def _get_api_key(self) -> Optional[str]:
        """No API key required for file-based connector."""
        return None
    
    def connect(self) -> None:
        """No connection needed for file-based connector."""
        pass
    
    def fetch(self, **kwargs: Any) -> Any:
        """
        Not supported for file-based connector.
        
        Raises:
            NotImplementedError: Always raised for file-based connector
        """
        raise NotImplementedError(
            "HRSA does not provide an API. Use load_hpsa_data() or load_health_center_data() "
            "with downloaded CSV files from https://data.hrsa.gov/data/download"
        )
    
    def load_hpsa_data(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Load HPSA (Health Professional Shortage Area) data from CSV file.
        
        Expected columns include:
        - State_Abbr, State_Name: State information
        - County_Name, County_Equivalent: County information
        - HPSA_Name, Common_Name: Shortage area name
        - Designation_Type: Geographic, Population, or Facility
        - HPSA_Discipline: Primary Care, Dental Health, or Mental Health
        - HPSA_Score: Shortage score (0-26)
        - HPSA_Status: Designated or Proposed
        - Rural_Status: Rural or Not Rural
        - HPSA_FTE: Full-time equivalent practitioners needed
        
        Args:
            file_path: Path to HRSA HPSA CSV file
            
        Returns:
            DataFrame with HPSA data
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file format is invalid
            
        Example:
            >>> hrsa = HRSAConnector()
            >>> data = hrsa.load_hpsa_data('BCD_HPSA_FCT_DET_PC.csv')
            >>> print(f"Loaded {len(data)} HPSA records")
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"HPSA data file not found: {file_path}")
        
        self.logger.info(f"Loading HPSA data from {file_path}")
        
        try:
            data = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
            self.logger.info(f"Loaded {len(data)} HPSA records with {len(data.columns)} columns")
            return data
        except Exception as e:
            self.logger.error(f"Failed to load HPSA data: {e}")
            raise ValueError(f"Invalid HPSA CSV format: {e}")
    
    def load_mua_data(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Load MUA/P (Medically Underserved Area/Population) data from CSV file.
        
        Expected columns include:
        - State_Abbr, State_Name: State information
        - County_Name: County information
        - MUA_Name, Common_Name: MUA/P name
        - Designation_Type: Geographic MUA, Population MUP, or both
        - MUA_Status: Designated or Proposed
        - Rural_Status: Rural or Not Rural
        - IMU_Score: Index of Medical Underservice (0-100, lower = more underserved)
        
        Args:
            file_path: Path to HRSA MUA/P CSV file
            
        Returns:
            DataFrame with MUA/P data
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file format is invalid
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"MUA/P data file not found: {file_path}")
        
        self.logger.info(f"Loading MUA/P data from {file_path}")
        
        try:
            data = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
            self.logger.info(f"Loaded {len(data)} MUA/P records with {len(data.columns)} columns")
            return data
        except Exception as e:
            self.logger.error(f"Failed to load MUA/P data: {e}")
            raise ValueError(f"Invalid MUA/P CSV format: {e}")
    
    def load_health_center_data(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Load Health Center data from CSV file.
        
        Expected columns include:
        - Health_Center_Name: Facility name
        - State_Abbr, State_Name: State information
        - City, Address, Zip_Code: Location information
        - Health_Center_Type: FQHC, Look-Alike, etc.
        - Patients_Served: Number of patients
        - Services: Types of services offered
        
        Args:
            file_path: Path to HRSA Health Center CSV file
            
        Returns:
            DataFrame with health center data
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file format is invalid
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Health Center data file not found: {file_path}")
        
        self.logger.info(f"Loading Health Center data from {file_path}")
        
        try:
            data = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
            self.logger.info(f"Loaded {len(data)} health center records with {len(data.columns)} columns")
            return data
        except Exception as e:
            self.logger.error(f"Failed to load Health Center data: {e}")
            raise ValueError(f"Invalid Health Center CSV format: {e}")
    
    def get_state_data(
        self,
        data: pd.DataFrame,
        state: str,
        state_column: str = 'State_Abbr'
    ) -> pd.DataFrame:
        """
        Filter data by state.
        
        Args:
            data: HPSA, MUA/P, or Health Center DataFrame
            state: Two-letter state abbreviation (e.g., 'RI', 'CA')
            state_column: Name of state column (default: 'State_Abbr')
            
        Returns:
            DataFrame filtered to specified state
            
        Example:
            >>> ri_hpsas = hrsa.get_state_data(hpsa_data, 'RI')
        """
        state = state.upper()
        
        if state_column not in data.columns:
            raise ValueError(f"State column '{state_column}' not found in data")
        
        filtered = data[data[state_column].str.upper() == state].copy()
        self.logger.info(f"Filtered to {len(filtered)} records for state: {state}")
        
        return filtered
    
    def get_county_data(
        self,
        data: pd.DataFrame,
        county: str,
        state: Optional[str] = None,
        county_column: str = 'County_Name'
    ) -> pd.DataFrame:
        """
        Filter data by county.
        
        Args:
            data: HPSA, MUA/P, or Health Center DataFrame
            county: County name (case-insensitive)
            state: Optional two-letter state abbreviation for disambiguation
            county_column: Name of county column (default: 'County_Name')
            
        Returns:
            DataFrame filtered to specified county
            
        Example:
            >>> providence = hrsa.get_county_data(hpsa_data, 'Providence', state='RI')
        """
        if county_column not in data.columns:
            raise ValueError(f"County column '{county_column}' not found in data")
        
        # Case-insensitive county match
        filtered = data[data[county_column].str.lower() == county.lower()].copy()
        
        # Further filter by state if provided
        if state:
            state = state.upper()
            if 'State_Abbr' in filtered.columns:
                filtered = filtered[filtered['State_Abbr'].str.upper() == state]
        
        self.logger.info(f"Filtered to {len(filtered)} records for county: {county}")
        
        return filtered
    
    def filter_by_discipline(
        self,
        data: pd.DataFrame,
        discipline: str,
        discipline_column: str = 'HPSA_Discipline'
    ) -> pd.DataFrame:
        """
        Filter HPSA data by discipline (Primary Care, Dental Health, Mental Health).
        
        Args:
            data: HPSA DataFrame
            discipline: HPSA discipline ('Primary Care', 'Dental Health', 'Mental Health')
            discipline_column: Name of discipline column (default: 'HPSA_Discipline')
            
        Returns:
            DataFrame filtered to specified discipline
            
        Raises:
            ValueError: If discipline is not valid
            
        Example:
            >>> primary_care = hrsa.filter_by_discipline(hpsa_data, 'Primary Care')
        """
        if discipline not in self.HPSA_DISCIPLINES:
            raise ValueError(
                f"Invalid discipline: {discipline}. Must be one of {self.HPSA_DISCIPLINES}"
            )
        
        if discipline_column not in data.columns:
            raise ValueError(f"Discipline column '{discipline_column}' not found in data")
        
        filtered = data[data[discipline_column] == discipline].copy()
        self.logger.info(f"Filtered to {len(filtered)} {discipline} HPSAs")
        
        return filtered
    
    def filter_by_type(
        self,
        data: pd.DataFrame,
        designation_type: str,
        type_column: str = 'Designation_Type'
    ) -> pd.DataFrame:
        """
        Filter data by designation type.
        
        For HPSA: 'Geographic', 'Population', 'Facility'
        For MUA/P: 'Geographic MUA', 'Population MUP', 'Geographic MUA and Population MUP'
        
        Args:
            data: HPSA or MUA/P DataFrame
            designation_type: Designation type
            type_column: Name of type column (default: 'Designation_Type')
            
        Returns:
            DataFrame filtered to specified type
            
        Example:
            >>> geographic = hrsa.filter_by_type(hpsa_data, 'Geographic')
        """
        if type_column not in data.columns:
            raise ValueError(f"Type column '{type_column}' not found in data")
        
        filtered = data[data[type_column] == designation_type].copy()
        self.logger.info(f"Filtered to {len(filtered)} {designation_type} designations")
        
        return filtered
    
    def get_high_need_areas(
        self,
        data: pd.DataFrame,
        score_threshold: int = 15,
        score_column: str = 'HPSA_Score'
    ) -> pd.DataFrame:
        """
        Filter HPSA data to high-need areas (score >= threshold).
        
        HPSA Score ranges from 0-26:
        - 0-14: Moderate shortage
        - 15-19: High shortage
        - 20-26: Critical shortage
        
        Args:
            data: HPSA DataFrame
            score_threshold: Minimum HPSA score (default: 15 for high need)
            score_column: Name of score column (default: 'HPSA_Score')
            
        Returns:
            DataFrame with high-need areas
            
        Example:
            >>> critical = hrsa.get_high_need_areas(hpsa_data, score_threshold=20)
        """
        if score_column not in data.columns:
            raise ValueError(f"Score column '{score_column}' not found in data")
        
        filtered = data[data[score_column] >= score_threshold].copy()
        self.logger.info(
            f"Filtered to {len(filtered)} areas with score >= {score_threshold}"
        )
        
        return filtered
    
    def get_rural_areas(
        self,
        data: pd.DataFrame,
        rural_column: str = 'Rural_Status'
    ) -> pd.DataFrame:
        """
        Filter data to rural areas only.
        
        Args:
            data: HPSA or MUA/P DataFrame
            rural_column: Name of rural status column (default: 'Rural_Status')
            
        Returns:
            DataFrame with rural areas only
            
        Example:
            >>> rural = hrsa.get_rural_areas(hpsa_data)
        """
        if rural_column not in data.columns:
            raise ValueError(f"Rural column '{rural_column}' not found in data")
        
        filtered = data[data[rural_column] == 'Rural'].copy()
        self.logger.info(f"Filtered to {len(filtered)} rural areas")
        
        return filtered
    
    def summarize_by_state(
        self,
        data: pd.DataFrame,
        metrics: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Calculate state-level summaries of shortage data.
        
        Args:
            data: HPSA or MUA/P DataFrame
            metrics: List of numeric columns to summarize (default: score columns)
            
        Returns:
            DataFrame with state-level statistics
            
        Example:
            >>> summary = hrsa.summarize_by_state(hpsa_data, metrics=['HPSA_Score', 'HPSA_FTE'])
        """
        if 'State_Abbr' not in data.columns:
            raise ValueError("State_Abbr column not found in data")
        
        if metrics is None:
            # Default metrics
            metrics = []
            if 'HPSA_Score' in data.columns:
                metrics.append('HPSA_Score')
            if 'HPSA_FTE' in data.columns:
                metrics.append('HPSA_FTE')
            if 'IMU_Score' in data.columns:
                metrics.append('IMU_Score')
        
        # Validate metrics exist
        for metric in metrics:
            if metric not in data.columns:
                raise ValueError(f"Metric column '{metric}' not found in data")
        
        # Group by state and calculate statistics
        summary = data.groupby('State_Abbr')[metrics].agg(['count', 'mean', 'median', 'min', 'max'])
        
        self.logger.info(f"Summarized data for {len(summary)} states")
        
        return summary
    
    def get_available_disciplines(self, data: pd.DataFrame) -> Dict[str, int]:
        """
        Get count of records by HPSA discipline.
        
        Args:
            data: HPSA DataFrame
            
        Returns:
            Dictionary mapping discipline to count
            
        Example:
            >>> disciplines = hrsa.get_available_disciplines(hpsa_data)
            >>> print(f"Primary Care: {disciplines['Primary Care']}")
        """
        if 'HPSA_Discipline' not in data.columns:
            return {}
        
        counts = data['HPSA_Discipline'].value_counts().to_dict()
        self.logger.info(f"Found {len(counts)} disciplines in data")
        
        return counts
