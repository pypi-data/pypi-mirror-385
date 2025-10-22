"""
U.S. Geological Survey (USGS) Data Connector.

This module provides access to USGS data including water resources,
earthquakes, geological surveys, and environmental monitoring.

API Documentation:
- Water Services: https://waterservices.usgs.gov/
- Earthquake API: https://earthquake.usgs.gov/fdsnws/event/1/
"""

import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..base_connector import BaseConnector


# Water parameter codes (common measurements)
WATER_PARAMETERS = {
    'discharge': '00060',  # Streamflow/discharge (cubic feet per second)
    'gage_height': '00065',  # Gage height (feet)
    'temperature': '00010',  # Water temperature (Celsius)
    'ph': '00400',  # pH
    'dissolved_oxygen': '00300',  # Dissolved oxygen (mg/L)
    'conductivity': '00095',  # Specific conductance (microsiemens/cm)
    'turbidity': '63680',  # Turbidity (NTU)
    'nitrate': '00618',  # Nitrate (mg/L as N)
    'phosphorus': '00665',  # Phosphorus (mg/L as P)
}

# Earthquake magnitude types
MAGNITUDE_TYPES = {
    'all': 'all',
    'significant': 'significant',
    '4.5+': '4.5',
    '2.5+': '2.5',
    '1.0+': '1.0',
}

# Site types
SITE_TYPES = {
    'stream': 'ST',
    'lake': 'LK',
    'estuary': 'ES',
    'well': 'GW',
    'spring': 'SP',
    'atmosphere': 'AT',
}


class USGSConnector(BaseConnector):
    """
    Connector for U.S. Geological Survey (USGS) data.
    
    Provides access to water resources, earthquake data, geological surveys,
    and environmental monitoring information.
    
    Attributes:
        water_url: USGS Water Services API base URL
        earthquake_url: USGS Earthquake API base URL
        
    Example:
        >>> connector = USGSConnector()
        >>> 
        >>> # Get streamflow data
        >>> streamflow = connector.get_streamflow_data(
        ...     site_no='01646500',  # Potomac River
        ...     start_date='2024-01-01',
        ...     end_date='2024-12-31'
        ... )
        >>> 
        >>> # Get earthquake data
        >>> earthquakes = connector.get_earthquakes(
        ...     min_magnitude=4.5,
        ...     start_time='2024-01-01',
        ...     limit=100
        ... )
        >>> 
        >>> connector.close()
    """
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, **kwargs):
        """
        Initialize USGS connector.
        
        Args:
            api_key: Optional API key (not required for USGS APIs)
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseConnector
        """
        self._usgs_api_key = api_key
        
        super().__init__(api_key=api_key, timeout=timeout, **kwargs)
        
        # USGS has multiple API endpoints
        self.water_url = "https://waterservices.usgs.gov/nwis"
        self.earthquake_url = "https://earthquake.usgs.gov/fdsnws/event/1"
    
    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for USGS APIs.
        
        Returns:
            API key if available, None otherwise (USGS APIs are public)
        """
        return self._usgs_api_key
    
    def connect(self) -> None:
        """
        Establish connection to USGS data sources.
        
        Raises:
            ConnectionError: If unable to connect
        """
        if self.session is not None:
            return
        
        try:
            self.session = self._init_session()
            self.logger.info("Successfully connected to USGS data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect to USGS API: {e}")
            raise ConnectionError(f"Could not connect to USGS API: {e}")
    
    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from USGS APIs.
        
        Args:
            endpoint: API endpoint path (required)
            base_url: Base URL to use (water_url or earthquake_url)
            **kwargs: Additional query parameters
            
        Returns:
            API response data
            
        Raises:
            requests.HTTPError: If API request fails
        """
        endpoint = kwargs.pop('endpoint', None)
        base_url = kwargs.pop('base_url', self.water_url)
        
        if not endpoint:
            raise ValueError("endpoint parameter is required")
        
        if not self.session:
            self.connect()
        
        url = f"{base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=kwargs, timeout=self.timeout)
            response.raise_for_status()
            
            # Try JSON first
            try:
                return response.json()
            except ValueError:
                # Some USGS endpoints return text/csv
                return {'text': response.text}
        
        except Exception as e:
            self.logger.error(f"Failed to fetch data from {endpoint}: {e}")
            return {}
    
    def get_streamflow_data(
        self,
        site_no: Optional[str] = None,
        state_cd: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        parameter_cd: str = '00060',
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get streamflow/discharge data from USGS monitoring sites.
        
        Args:
            site_no: USGS site number (8-15 digit number)
            state_cd: Two-letter state code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            parameter_cd: Parameter code (default: 00060 for discharge)
            limit: Maximum records to return
            
        Returns:
            DataFrame with streamflow data
        """
        params = {
            'format': 'json',
            'parameterCd': parameter_cd,
        }
        
        if site_no:
            params['sites'] = site_no
        
        if state_cd:
            params['stateCd'] = state_cd.upper()
        
        if start_date:
            params['startDT'] = start_date
        if end_date:
            params['endDT'] = end_date
        
        try:
            response = self.fetch(endpoint='/iv/', base_url=self.water_url, **params)
            
            if response and 'value' in response and 'timeSeries' in response['value']:
                time_series = response['value']['timeSeries']
                
                data_list = []
                for series in time_series:
                    if 'values' in series and len(series['values']) > 0:
                        values = series['values'][0].get('value', [])
                        site_info = series.get('sourceInfo', {})
                        
                        for value_data in values[:limit]:
                            data_list.append({
                                'site_no': site_info.get('siteCode', [{}])[0].get('value'),
                                'site_name': site_info.get('siteName'),
                                'datetime': value_data.get('dateTime'),
                                'value': value_data.get('value'),
                                'qualifiers': value_data.get('qualifiers'),
                            })
                
                return pd.DataFrame(data_list)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching streamflow data: {str(e)}")
            return pd.DataFrame()
    
    def get_water_quality_data(
        self,
        site_no: Optional[str] = None,
        state_cd: Optional[str] = None,
        parameter: str = 'temperature',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get water quality data from USGS monitoring sites.
        
        Args:
            site_no: USGS site number
            state_cd: Two-letter state code
            parameter: Water quality parameter (temperature, ph, dissolved_oxygen, etc.)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum records to return
            
        Returns:
            DataFrame with water quality data
        """
        # Get parameter code
        parameter_cd = WATER_PARAMETERS.get(parameter.lower(), parameter)
        
        params = {
            'format': 'json',
            'parameterCd': parameter_cd,
        }
        
        if site_no:
            params['sites'] = site_no
        
        if state_cd:
            params['stateCd'] = state_cd.upper()
        
        if start_date:
            params['startDT'] = start_date
        if end_date:
            params['endDT'] = end_date
        
        try:
            response = self.fetch(endpoint='/iv/', base_url=self.water_url, **params)
            
            if response and 'value' in response and 'timeSeries' in response['value']:
                time_series = response['value']['timeSeries']
                
                data_list = []
                for series in time_series:
                    if 'values' in series and len(series['values']) > 0:
                        values = series['values'][0].get('value', [])
                        site_info = series.get('sourceInfo', {})
                        variable = series.get('variable', {})
                        
                        for value_data in values[:limit]:
                            data_list.append({
                                'site_no': site_info.get('siteCode', [{}])[0].get('value'),
                                'site_name': site_info.get('siteName'),
                                'parameter': variable.get('variableName'),
                                'datetime': value_data.get('dateTime'),
                                'value': value_data.get('value'),
                                'unit': variable.get('unit', {}).get('unitCode'),
                            })
                
                return pd.DataFrame(data_list)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching water quality data: {str(e)}")
            return pd.DataFrame()
    
    def get_groundwater_levels(
        self,
        site_no: Optional[str] = None,
        state_cd: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get groundwater level data from USGS monitoring wells.
        
        Args:
            site_no: USGS site number
            state_cd: Two-letter state code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum records to return
            
        Returns:
            DataFrame with groundwater level data
        """
        params = {
            'format': 'json',
            'parameterCd': '72019',  # Groundwater level parameter code
            'siteType': 'GW',
        }
        
        if site_no:
            params['sites'] = site_no
        
        if state_cd:
            params['stateCd'] = state_cd.upper()
        
        if start_date:
            params['startDT'] = start_date
        if end_date:
            params['endDT'] = end_date
        
        try:
            response = self.fetch(endpoint='/iv/', base_url=self.water_url, **params)
            
            if response and 'value' in response and 'timeSeries' in response['value']:
                time_series = response['value']['timeSeries']
                
                data_list = []
                for series in time_series:
                    if 'values' in series and len(series['values']) > 0:
                        values = series['values'][0].get('value', [])
                        site_info = series.get('sourceInfo', {})
                        
                        for value_data in values[:limit]:
                            data_list.append({
                                'site_no': site_info.get('siteCode', [{}])[0].get('value'),
                                'site_name': site_info.get('siteName'),
                                'datetime': value_data.get('dateTime'),
                                'depth_to_water': value_data.get('value'),
                                'qualifiers': value_data.get('qualifiers'),
                            })
                
                return pd.DataFrame(data_list)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching groundwater data: {str(e)}")
            return pd.DataFrame()
    
    def get_site_information(
        self,
        site_no: Optional[str] = None,
        state_cd: Optional[str] = None,
        county_cd: Optional[str] = None,
        site_type: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get information about USGS monitoring sites.
        
        Args:
            site_no: USGS site number
            state_cd: Two-letter state code
            county_cd: County code
            site_type: Site type (stream, lake, well, etc.)
            limit: Maximum records to return
            
        Returns:
            DataFrame with site information
        """
        params = {
            'format': 'json',
        }
        
        if site_no:
            params['sites'] = site_no
        
        if state_cd:
            params['stateCd'] = state_cd.upper()
        
        if county_cd:
            params['countyCd'] = county_cd
        
        if site_type:
            site_type_cd = SITE_TYPES.get(site_type.lower(), site_type)
            params['siteType'] = site_type_cd
        
        try:
            response = self.fetch(endpoint='/site/', base_url=self.water_url, **params)
            
            if response and 'value' in response and 'timeSeries' in response['value']:
                sites = response['value']['timeSeries']
                
                data_list = []
                for site_data in sites[:limit]:
                    site_info = site_data.get('sourceInfo', {})
                    geo_location = site_info.get('geoLocation', {}).get('geogLocation', {})
                    
                    data_list.append({
                        'site_no': site_info.get('siteCode', [{}])[0].get('value'),
                        'site_name': site_info.get('siteName'),
                        'site_type': site_info.get('siteType', [{}])[0].get('value'),
                        'latitude': geo_location.get('latitude'),
                        'longitude': geo_location.get('longitude'),
                        'county': site_info.get('siteProperty', [{}])[0].get('value'),
                    })
                
                return pd.DataFrame(data_list)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching site information: {str(e)}")
            return pd.DataFrame()
    
    def get_earthquakes(
        self,
        min_magnitude: Optional[float] = None,
        max_magnitude: Optional[float] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        max_radius_km: Optional[float] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get earthquake data from USGS Earthquake Hazards Program.
        
        Args:
            min_magnitude: Minimum earthquake magnitude
            max_magnitude: Maximum earthquake magnitude
            start_time: Start time (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
            end_time: End time (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
            latitude: Center latitude for radius search
            longitude: Center longitude for radius search
            max_radius_km: Maximum radius from lat/lon point (km)
            limit: Maximum records to return
            
        Returns:
            DataFrame with earthquake data
        """
        params = {
            'format': 'geojson',
            'limit': limit,
            'orderby': 'time',
        }
        
        if min_magnitude is not None:
            params['minmagnitude'] = min_magnitude
        
        if max_magnitude is not None:
            params['maxmagnitude'] = max_magnitude
        
        if start_time:
            params['starttime'] = start_time
        
        if end_time:
            params['endtime'] = end_time
        
        if latitude is not None and longitude is not None:
            params['latitude'] = latitude
            params['longitude'] = longitude
            
            if max_radius_km is not None:
                params['maxradiuskm'] = max_radius_km
        
        try:
            response = self.fetch(endpoint='/query', base_url=self.earthquake_url, **params)
            
            if response and 'features' in response:
                features = response['features']
                
                data_list = []
                for feature in features:
                    props = feature.get('properties', {})
                    geom = feature.get('geometry', {})
                    coords = geom.get('coordinates', [None, None, None])
                    
                    data_list.append({
                        'id': feature.get('id'),
                        'magnitude': props.get('mag'),
                        'place': props.get('place'),
                        'time': props.get('time'),
                        'updated': props.get('updated'),
                        'url': props.get('url'),
                        'detail': props.get('detail'),
                        'felt': props.get('felt'),
                        'tsunami': props.get('tsunami'),
                        'alert': props.get('alert'),
                        'status': props.get('status'),
                        'type': props.get('type'),
                        'longitude': coords[0],
                        'latitude': coords[1],
                        'depth': coords[2],
                    })
                
                return pd.DataFrame(data_list)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching earthquake data: {str(e)}")
            return pd.DataFrame()
    
    def get_daily_streamflow(
        self,
        site_no: Optional[str] = None,
        state_cd: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get daily mean streamflow data (statistical summaries).
        
        Args:
            site_no: USGS site number
            state_cd: Two-letter state code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum records to return
            
        Returns:
            DataFrame with daily streamflow statistics
        """
        params = {
            'format': 'json',
            'parameterCd': '00060',
        }
        
        if site_no:
            params['sites'] = site_no
        
        if state_cd:
            params['stateCd'] = state_cd.upper()
        
        if start_date:
            params['startDT'] = start_date
        if end_date:
            params['endDT'] = end_date
        
        try:
            response = self.fetch(endpoint='/dv/', base_url=self.water_url, **params)
            
            if response and 'value' in response and 'timeSeries' in response['value']:
                time_series = response['value']['timeSeries']
                
                data_list = []
                for series in time_series:
                    if 'values' in series and len(series['values']) > 0:
                        values = series['values'][0].get('value', [])
                        site_info = series.get('sourceInfo', {})
                        
                        for value_data in values[:limit]:
                            data_list.append({
                                'site_no': site_info.get('siteCode', [{}])[0].get('value'),
                                'site_name': site_info.get('siteName'),
                                'date': value_data.get('dateTime'),
                                'mean_discharge': value_data.get('value'),
                                'qualifiers': value_data.get('qualifiers'),
                            })
                
                return pd.DataFrame(data_list)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching daily streamflow data: {str(e)}")
            return pd.DataFrame()
    
    def get_peak_streamflow(
        self,
        site_no: Optional[str] = None,
        state_cd: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get peak streamflow data (annual maximum flows).
        
        Args:
            site_no: USGS site number
            state_cd: Two-letter state code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum records to return
            
        Returns:
            DataFrame with peak streamflow data
        """
        params = {
            'format': 'json',
        }
        
        if site_no:
            params['site_no'] = site_no
        
        if state_cd:
            params['state_cd'] = state_cd.upper()
        
        if start_date:
            params['begin_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        try:
            response = self.fetch(endpoint='/peak/', base_url=self.water_url, **params)
            
            # Peak data often returns as text, need to parse
            if response and 'text' in response:
                # Return raw text for now - would need custom parser
                return pd.DataFrame({'raw_data': [response['text']]})
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching peak streamflow data: {str(e)}")
            return pd.DataFrame()
    
    def get_water_use_data(
        self,
        state_cd: Optional[str] = None,
        county_cd: Optional[str] = None,
        year: Optional[int] = None,
        category: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get water use data (estimates of water withdrawals and use).
        
        Args:
            state_cd: Two-letter state code
            county_cd: County code
            year: Year (available every 5 years: 1985, 1990, 1995, 2000, 2005, 2010, 2015)
            category: Water use category (public, domestic, irrigation, etc.)
            limit: Maximum records to return
            
        Returns:
            DataFrame with water use data
        """
        params = {
            'format': 'json',
        }
        
        if state_cd:
            params['stateCd'] = state_cd.upper()
        
        if county_cd:
            params['countyCd'] = county_cd
        
        if year:
            params['year'] = year
        
        if category:
            params['category'] = category
        
        try:
            # Note: Water use API endpoint may vary
            response = self.fetch(endpoint='/wateruse/', base_url=self.water_url, **params)
            
            if response:
                # Water use data structure varies - basic parsing
                return pd.DataFrame([response])
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching water use data: {str(e)}")
            return pd.DataFrame()
    
    def get_statistical_data(
        self,
        site_no: str,
        stat_type: str = 'mean',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get statistical summaries for site data.
        
        Args:
            site_no: USGS site number (required)
            stat_type: Type of statistic (mean, median, max, min)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum records to return
            
        Returns:
            DataFrame with statistical data
        """
        params = {
            'format': 'json',
            'sites': site_no,
            'statType': stat_type,
        }
        
        if start_date:
            params['startDT'] = start_date
        if end_date:
            params['endDT'] = end_date
        
        try:
            response = self.fetch(endpoint='/stat/', base_url=self.water_url, **params)
            
            if response and 'value' in response and 'timeSeries' in response['value']:
                time_series = response['value']['timeSeries']
                
                data_list = []
                for series in time_series:
                    if 'values' in series and len(series['values']) > 0:
                        values = series['values'][0].get('value', [])
                        site_info = series.get('sourceInfo', {})
                        
                        for value_data in values[:limit]:
                            data_list.append({
                                'site_no': site_info.get('siteCode', [{}])[0].get('value'),
                                'statistic': stat_type,
                                'period': value_data.get('dateTime'),
                                'value': value_data.get('value'),
                            })
                
                return pd.DataFrame(data_list)
            
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error fetching statistical data: {str(e)}")
            return pd.DataFrame()
    
    def close(self) -> None:
        """Close the USGS API connection and cleanup resources."""
        if self.session:
            self.session.close()
            self.session = None
        self.logger.info("Connection closed")
