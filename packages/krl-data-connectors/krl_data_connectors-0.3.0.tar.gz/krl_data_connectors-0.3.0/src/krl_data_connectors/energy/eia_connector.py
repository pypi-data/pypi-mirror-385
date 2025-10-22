"""
Energy Information Administration (EIA) Data Connector.

This module provides access to the U.S. Energy Information Administration's
comprehensive energy data, including electricity generation, consumption,
natural gas, petroleum, coal, renewable energy, and more.

API Documentation: https://www.eia.gov/opendata/
"""

import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..base_connector import BaseConnector


# Energy source types
ENERGY_SOURCES = {
    'coal': 'COL',
    'natural_gas': 'NG',
    'nuclear': 'NUC',
    'petroleum': 'PET',
    'renewable': 'REN',
    'solar': 'SUN',
    'wind': 'WND',
    'hydroelectric': 'HYD',
    'geothermal': 'GEO',
    'biomass': 'BIO',
    'other': 'OTH'
}

# Electricity sectors
ELECTRICITY_SECTORS = {
    'residential': 'RES',
    'commercial': 'COM',
    'industrial': 'IND',
    'transportation': 'TRA',
    'total': 'TOT'
}

# Data series types
SERIES_TYPES = {
    'generation': 'GEN',
    'consumption': 'CON',
    'production': 'PRO',
    'imports': 'IMP',
    'exports': 'EXP',
    'stocks': 'STK',
    'prices': 'PRI'
}


class EIAConnector(BaseConnector):
    """
    Connector for U.S. Energy Information Administration (EIA) data.
    
    Provides access to comprehensive energy statistics including electricity,
    natural gas, petroleum, coal, renewable energy, and nuclear data.
    
    Attributes:
        base_url: EIA Open Data API base URL
        
    Example:
        >>> connector = EIAConnector(api_key="your_eia_api_key")
        >>> 
        >>> # Get electricity generation data
        >>> generation = connector.get_electricity_generation(
        ...     state='CA',
        ...     energy_source='solar',
        ...     start_date='2024-01-01',
        ...     limit=100
        ... )
        >>> 
        >>> # Get natural gas data
        >>> gas_data = connector.get_natural_gas_data(
        ...     state='TX',
        ...     series_type='production',
        ...     limit=100
        ... )
        >>> 
        >>> connector.close()
    """
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, **kwargs):
        """
        Initialize EIA connector.
        
        Args:
            api_key: EIA Open Data API key (required for API access)
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseConnector
        """
        # Store EIA-specific API key before parent initialization
        self._eia_api_key = api_key
        
        super().__init__(api_key=api_key, timeout=timeout, **kwargs)
        self.api_url = "https://api.eia.gov/v2"
    
    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for EIA API.
        
        Returns:
            API key if available, None otherwise
        """
        return self._eia_api_key
    
    def connect(self) -> None:
        """
        Establish connection to EIA data sources.
        
        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return
        
        try:
            self.session = self._init_session()
            self.logger.info("Successfully connected to EIA data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to EIA API: {e}")
            raise ConnectionError(f"Could not connect to EIA API: {e}")
    
    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from EIA API.
        
        Args:
            endpoint: API endpoint path (required)
            **kwargs: Additional query parameters
            
        Returns:
            API response data
            
        Raises:
            requests.HTTPError: If API request fails
        """
        endpoint = kwargs.pop('endpoint', None)
        
        if not endpoint:
            raise ValueError("endpoint parameter is required")
        
        if not self.session:
            self.connect()
        
        url = f"{self.api_url}{endpoint}"
        
        # Add API key if available
        if self.api_key:
            kwargs['api_key'] = self.api_key
        
        try:
            response = self.session.get(url, params=kwargs, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse JSON response
            try:
                return response.json()
            except ValueError:
                return {}
        
        except Exception as e:
            self.logger.error(f"Failed to fetch data from {endpoint}: {e}")
            return {}
    
    def get_electricity_generation(
        self,
        state: Optional[str] = None,
        energy_source: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = 'monthly',
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get electricity generation data by state and energy source.
        
        Args:
            state: Two-letter state code (e.g., 'CA', 'TX')
            energy_source: Energy source type (coal, natural_gas, nuclear, etc.)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency (monthly, quarterly, annual)
            limit: Maximum records to return
            
        Returns:
            DataFrame with electricity generation data
        """
        params = {
            'frequency': frequency,
            'data[0]': 'generation',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': limit
        }
        
        if state:
            params['facets[stateid][]'] = state.upper()
        
        if energy_source:
            source_code = ENERGY_SOURCES.get(energy_source.lower(), energy_source)
            params['facets[fueltypeid][]'] = source_code
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        try:
            response = self.fetch(endpoint='/electricity/electric-power-operational-data/data/', **params)
            
            if response and 'response' in response and 'data' in response['response']:
                return pd.DataFrame(response['response']['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching electricity generation data: {str(e)}")
            return pd.DataFrame()
    
    def get_electricity_consumption(
        self,
        state: Optional[str] = None,
        sector: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = 'monthly',
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get electricity consumption (sales) data by state and sector.
        
        Args:
            state: Two-letter state code
            sector: Consumption sector (residential, commercial, industrial, transportation)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency
            limit: Maximum records to return
            
        Returns:
            DataFrame with electricity consumption data
        """
        params = {
            'frequency': frequency,
            'data[0]': 'sales',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': limit
        }
        
        if state:
            params['facets[stateid][]'] = state.upper()
        
        if sector:
            sector_code = ELECTRICITY_SECTORS.get(sector.lower(), sector)
            params['facets[sectorid][]'] = sector_code
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        try:
            response = self.fetch(endpoint='/electricity/retail-sales/data/', **params)
            
            if response and 'response' in response and 'data' in response['response']:
                return pd.DataFrame(response['response']['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching electricity consumption data: {str(e)}")
            return pd.DataFrame()
    
    def get_natural_gas_data(
        self,
        state: Optional[str] = None,
        series_type: str = 'production',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = 'monthly',
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get natural gas production, consumption, or price data.
        
        Args:
            state: Two-letter state code
            series_type: Type of data (production, consumption, prices)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency
            limit: Maximum records to return
            
        Returns:
            DataFrame with natural gas data
        """
        # Map series type to endpoint
        endpoint_map = {
            'production': '/natural-gas/prod/sum/data/',
            'consumption': '/natural-gas/cons/sum/data/',
            'prices': '/natural-gas/pri/sum/data/',
            'stocks': '/natural-gas/stor/sum/data/'
        }
        
        endpoint = endpoint_map.get(series_type.lower(), endpoint_map['production'])
        
        params = {
            'frequency': frequency,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': limit
        }
        
        if state:
            params['facets[stateid][]'] = state.upper()
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        try:
            response = self.fetch(endpoint=endpoint, **params)
            
            if response and 'response' in response and 'data' in response['response']:
                return pd.DataFrame(response['response']['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching natural gas data: {str(e)}")
            return pd.DataFrame()
    
    def get_petroleum_data(
        self,
        product: Optional[str] = None,
        series_type: str = 'production',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = 'weekly',
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get petroleum and crude oil data.
        
        Args:
            product: Product type (crude_oil, gasoline, diesel, etc.)
            series_type: Type of data (production, consumption, imports, exports, stocks, prices)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency
            limit: Maximum records to return
            
        Returns:
            DataFrame with petroleum data
        """
        params = {
            'frequency': frequency,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': limit
        }
        
        if product:
            params['facets[product][]'] = product.upper()
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        try:
            response = self.fetch(endpoint='/petroleum/sum/data/', **params)
            
            if response and 'response' in response and 'data' in response['response']:
                return pd.DataFrame(response['response']['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching petroleum data: {str(e)}")
            return pd.DataFrame()
    
    def get_coal_data(
        self,
        state: Optional[str] = None,
        series_type: str = 'production',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = 'monthly',
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get coal production, consumption, and price data.
        
        Args:
            state: Two-letter state code
            series_type: Type of data (production, consumption, prices)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency
            limit: Maximum records to return
            
        Returns:
            DataFrame with coal data
        """
        params = {
            'frequency': frequency,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': limit
        }
        
        if state:
            params['facets[stateid][]'] = state.upper()
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        try:
            response = self.fetch(endpoint='/coal/data/', **params)
            
            if response and 'response' in response and 'data' in response['response']:
                return pd.DataFrame(response['response']['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching coal data: {str(e)}")
            return pd.DataFrame()
    
    def get_renewable_energy(
        self,
        energy_source: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = 'monthly',
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get renewable energy generation data (solar, wind, hydro, etc.).
        
        Args:
            energy_source: Renewable source (solar, wind, hydroelectric, geothermal, biomass)
            state: Two-letter state code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency
            limit: Maximum records to return
            
        Returns:
            DataFrame with renewable energy data
        """
        params = {
            'frequency': frequency,
            'data[0]': 'generation',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': limit
        }
        
        if energy_source:
            source_code = ENERGY_SOURCES.get(energy_source.lower(), energy_source)
            params['facets[fueltypeid][]'] = source_code
        
        if state:
            params['facets[stateid][]'] = state.upper()
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        try:
            response = self.fetch(endpoint='/electricity/electric-power-operational-data/data/', **params)
            
            if response and 'response' in response and 'data' in response['response']:
                return pd.DataFrame(response['response']['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching renewable energy data: {str(e)}")
            return pd.DataFrame()
    
    def get_nuclear_energy(
        self,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = 'monthly',
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get nuclear power generation data.
        
        Args:
            state: Two-letter state code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency
            limit: Maximum records to return
            
        Returns:
            DataFrame with nuclear energy data
        """
        params = {
            'frequency': frequency,
            'data[0]': 'generation',
            'facets[fueltypeid][]': 'NUC',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': limit
        }
        
        if state:
            params['facets[stateid][]'] = state.upper()
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        try:
            response = self.fetch(endpoint='/electricity/electric-power-operational-data/data/', **params)
            
            if response and 'response' in response and 'data' in response['response']:
                return pd.DataFrame(response['response']['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching nuclear energy data: {str(e)}")
            return pd.DataFrame()
    
    def get_energy_prices(
        self,
        energy_type: str = 'electricity',
        state: Optional[str] = None,
        sector: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = 'monthly',
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get energy price data for electricity, natural gas, or petroleum.
        
        Args:
            energy_type: Type of energy (electricity, natural_gas, petroleum)
            state: Two-letter state code
            sector: Consumer sector (residential, commercial, industrial)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency
            limit: Maximum records to return
            
        Returns:
            DataFrame with energy price data
        """
        # Map energy type to endpoint
        endpoint_map = {
            'electricity': '/electricity/retail-sales/data/',
            'natural_gas': '/natural-gas/pri/sum/data/',
            'petroleum': '/petroleum/pri/spt/data/'
        }
        
        endpoint = endpoint_map.get(energy_type.lower(), endpoint_map['electricity'])
        
        params = {
            'frequency': frequency,
            'data[0]': 'price',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': limit
        }
        
        if state:
            params['facets[stateid][]'] = state.upper()
        
        if sector:
            sector_code = ELECTRICITY_SECTORS.get(sector.lower(), sector)
            params['facets[sectorid][]'] = sector_code
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        try:
            response = self.fetch(endpoint=endpoint, **params)
            
            if response and 'response' in response and 'data' in response['response']:
                return pd.DataFrame(response['response']['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching energy price data: {str(e)}")
            return pd.DataFrame()
    
    def get_state_energy_data(
        self,
        state: str,
        data_type: str = 'all',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = 'annual',
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get comprehensive energy data for a specific state.
        
        Args:
            state: Two-letter state code (required)
            data_type: Type of data (production, consumption, prices, all)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency
            limit: Maximum records to return
            
        Returns:
            DataFrame with state energy data
        """
        params = {
            'frequency': frequency,
            'facets[stateid][]': state.upper(),
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': limit
        }
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        try:
            response = self.fetch(endpoint='/seds/data/', **params)
            
            if response and 'response' in response and 'data' in response['response']:
                return pd.DataFrame(response['response']['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching state energy data: {str(e)}")
            return pd.DataFrame()
    
    def get_international_energy(
        self,
        country: Optional[str] = None,
        energy_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = 'annual',
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get international energy statistics.
        
        Args:
            country: Country name or code
            energy_type: Type of energy (petroleum, natural_gas, coal, electricity)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency
            limit: Maximum records to return
            
        Returns:
            DataFrame with international energy data
        """
        params = {
            'frequency': frequency,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': limit
        }
        
        if country:
            params['facets[countryRegionId][]'] = country.upper()
        
        if energy_type:
            params['facets[productId][]'] = energy_type.upper()
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        try:
            response = self.fetch(endpoint='/international/data/', **params)
            
            if response and 'response' in response and 'data' in response['response']:
                return pd.DataFrame(response['response']['data'])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching international energy data: {str(e)}")
            return pd.DataFrame()
    
    def close(self) -> None:
        """Close the EIA API connection and cleanup resources."""
        if self.session:
            self.session.close()
            self.session = None
        self.logger.info("Connection closed")
