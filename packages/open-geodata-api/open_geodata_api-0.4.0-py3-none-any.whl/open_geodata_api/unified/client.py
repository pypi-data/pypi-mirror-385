"""
Unified STAC API Client

A generic client that can connect to any STAC-compliant API endpoint
and provide consistent interface similar to earthsearch and planetary clients.
"""

from typing import Optional, Dict, List, Union
from urllib.parse import urljoin, urlparse
import requests
import json
from datetime import datetime, date
import pandas as pd
from shapely.geometry import box

from ..core.base_client import BaseAPIClient
from ..core.search import STACSearch
from ..core.items import STACItem, STACItemCollection
from .validation import validate_stac_endpoint, validate_search_params
from .utils import create_band_mapping, map_band_names


class UnifiedSTACClient(BaseAPIClient):
    """
    A unified client for connecting to any STAC API endpoint.
    
    This client provides a consistent interface for accessing various
    STAC-compliant APIs while handling endpoint-specific differences.
    
    Parameters
    ----------
    api_url : str
        Base URL of the STAC API endpoint
        Examples: 
        - "https://geoservice.dlr.de/eoc/ogc/stac/v1/"
        - "https://earthengine.openeo.org/v1.0/"
        - "https://your-custom-stac-api.com/stac/"
    auth_token : str, optional
        Authentication token if required by the API
    headers : dict, optional
        Additional headers to include in requests
    timeout : int, default 30
        Request timeout in seconds
    verify_ssl : bool, default True
        Whether to verify SSL certificates
    """
    
    def __init__(
        self, 
        api_url: str,
        auth_token: Optional[str] = None,
        headers: Optional[Dict] = None,
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        self.api_url = api_url.rstrip('/')
        self.auth_token = auth_token
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # Setup session with headers
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
            
        # Validate endpoint and get capabilities
        self._validate_and_setup()
        
    def _validate_and_setup(self):
        """Validate STAC endpoint and setup client capabilities."""
        try:
            # Get root catalog
            response = self.session.get(
                self.api_url, 
                timeout=self.timeout, 
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            self.root_catalog = response.json()
            self.stac_version = self.root_catalog.get('stac_version', 'unknown')
            
            # Check for search endpoint
            self.search_endpoint = None
            for link in self.root_catalog.get('links', []):
                if link.get('rel') == 'search':
                    self.search_endpoint = urljoin(self.api_url, link['href'])
                    break
            
            if not self.search_endpoint:
                self.search_endpoint = f"{self.api_url}/search"
                
            # Validate search endpoint
            validate_stac_endpoint(self.search_endpoint, self.session)
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to STAC API at {self.api_url}: {e}")
    
    def search(
        self,
        collections: Optional[List[str]] = None,
        bbox: Optional[List[float]] = None,
        datetime: Optional[str] = None,
        query: Optional[Dict] = None,
        limit: int = 100,
        **kwargs
    ) -> STACSearch:
        """
        Search for STAC items.
        
        Parameters
        ----------
        collections : list of str, optional
            Collection IDs to search
        bbox : list of float, optional
            Bounding box [west, south, east, north]
        datetime : str, optional
            Datetime range in RFC3339 format
        query : dict, optional
            Additional query parameters
        limit : int, default 100
            Maximum number of items to return
        **kwargs
            Additional search parameters
            
        Returns
        -------
        STACSearch
            Search results object
        """
        # Build search parameters
        search_params = {
            'limit': limit
        }
        
        if collections:
            search_params['collections'] = collections
        if bbox:
            search_params['bbox'] = bbox
        if datetime:
            search_params['datetime'] = datetime
        if query:
            search_params['query'] = query
            
        # Add any additional parameters
        search_params.update(kwargs)
        
        # Validate parameters
        validate_search_params(search_params)
        
        try:
            # Execute search
            response = self.session.post(
                self.search_endpoint,
                json=search_params,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            search_results = response.json()
            
            # Convert to STACSearch object
            return self._create_search_object(search_results, search_params)
            
        except Exception as e:
            raise RuntimeError(f"Search failed: {e}")
    
    def get_collections(self) -> List[Dict]:
        """
        Get list of available collections.
        
        Returns
        -------
        list of dict
            Collection metadata
        """
        try:
            collections_url = f"{self.api_url}/collections"
            response = self.session.get(
                collections_url,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            collections_data = response.json()
            return collections_data.get('collections', [])
            
        except Exception as e:
            raise RuntimeError(f"Failed to get collections: {e}")
    
    def list_collections(self) -> List[str]:
        """
        Get list of collection IDs.
        
        Returns
        -------
        list of str
            Collection ID strings
        """
        collections = self.get_collections()
        return [col.get('id') for col in collections if col.get('id')]
    
    def get_collection_info(self, collection_id: str) -> Dict:
        """
        Get detailed information about a specific collection.
        
        Parameters
        ----------
        collection_id : str
            Collection ID
            
        Returns
        -------
        dict
            Collection metadata
        """
        try:
            collection_url = f"{self.api_url}/collections/{collection_id}"
            response = self.session.get(
                collection_url,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            raise RuntimeError(f"Failed to get collection info for {collection_id}: {e}")
    
    def _create_search_object(self, search_results: Dict, search_params: Dict) -> STACSearch:
        """Create STACSearch object from API response."""
        items = []
        for feature in search_results.get('features', []):
            # Create STACItem with unified client context
            stac_item = STACItem(feature)
            stac_item._client = self  # Attach client for asset URL handling
            items.append(stac_item)
        
        return STACSearch(
            items=items,
            search_params=search_params,
            total_results=search_results.get('numberMatched', len(items))
        )
    
    def get_asset_url(self, item: STACItem, asset_key: str, prefer_jp2: bool = True) -> Optional[str]:
        """
        Get asset URL for a specific asset key, with band name mapping.
        
        Parameters
        ----------
        item : STACItem
            STAC item object
        asset_key : str
            Asset key (e.g., 'B02', 'blue', 'red')
        prefer_jp2 : bool, default True
            Prefer JP2 format assets if available
            
        Returns
        -------
        str or None
            Asset URL if found
        """
        # Map band names to common formats
        mapped_key = map_band_names(asset_key, prefer_jp2)
        
        # Try original key first
        if asset_key in item.assets:
            return item.assets[asset_key]['href']
        
        # Try mapped key
        if mapped_key and mapped_key in item.assets:
            return item.assets[mapped_key]['href']
        
        # Try variations
        variations = [
            asset_key.lower(),
            asset_key.upper(),
            f"{asset_key}-jp2" if prefer_jp2 else asset_key,
        ]
        
        for var in variations:
            if var in item.assets:
                return item.assets[var]['href']
        
        return None
    
    def get_info(self) -> Dict:
        """
        Get client and endpoint information.
        
        Returns
        -------
        dict
            Client information
        """
        return {
            'client_type': 'UnifiedSTAC',
            'api_url': self.api_url,
            'stac_version': self.stac_version,
            'search_endpoint': self.search_endpoint,
            'collections_count': len(self.list_collections()),
            'auth_enabled': bool(self.auth_token)
        }


# Compatibility function for factory pattern
def create_unified_client(api_url: str, **kwargs) -> UnifiedSTACClient:
    """
    Factory function to create a UnifiedSTACClient.
    
    Parameters
    ----------
    api_url : str
        STAC API endpoint URL
    **kwargs
        Additional client parameters
        
    Returns
    -------
    UnifiedSTACClient
        Configured client instance
    """
    return UnifiedSTACClient(api_url, **kwargs)
