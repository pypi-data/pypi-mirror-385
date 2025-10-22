"""
Validation utilities for Unified STAC Client
"""

import requests
from typing import Dict, List, Optional
from urllib.parse import urlparse


def validate_stac_endpoint(endpoint_url: str, session: requests.Session = None) -> bool:
    """
    Validate that an endpoint is a valid STAC API.
    
    Parameters
    ----------
    endpoint_url : str
        STAC API endpoint URL
    session : requests.Session, optional
        Session to use for requests
        
    Returns
    -------
    bool
        True if valid STAC endpoint
        
    Raises
    ------
    ValueError
        If endpoint is not valid
    """
    if not session:
        session = requests.Session()
    
    try:
        # Parse URL
        parsed_url = urlparse(endpoint_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Invalid URL format: {endpoint_url}")
        
        # Try to get root catalog
        response = session.get(endpoint_url, timeout=10)
        response.raise_for_status()
        
        catalog = response.json()
        
        # Check for STAC-specific fields
        required_fields = ['type', 'links']
        for field in required_fields:
            if field not in catalog:
                raise ValueError(f"Missing required STAC field: {field}")
        
        # Check type
        if catalog.get('type') not in ['Catalog', 'Collection']:
            raise ValueError(f"Invalid STAC type: {catalog.get('type')}")
        
        return True
        
    except requests.RequestException as e:
        raise ValueError(f"Failed to connect to endpoint: {e}")
    except (ValueError, KeyError) as e:
        raise ValueError(f"Invalid STAC endpoint: {e}")


def validate_search_params(params: Dict) -> bool:
    """
    Validate search parameters.
    
    Parameters
    ----------
    params : dict
        Search parameters
        
    Returns
    -------
    bool
        True if valid
        
    Raises
    ------
    ValueError
        If parameters are invalid
    """
    # Validate bbox
    if 'bbox' in params and params['bbox']:
        bbox = params['bbox']
        if not isinstance(bbox, list) or len(bbox) != 4:
            raise ValueError("bbox must be a list of 4 numbers [west, south, east, north]")
        
        west, south, east, north = bbox
        if not all(isinstance(coord, (int, float)) for coord in bbox):
            raise ValueError("bbox coordinates must be numbers")
        
        if west >= east or south >= north:
            raise ValueError("Invalid bbox: west >= east or south >= north")
    
    # Validate collections
    if 'collections' in params and params['collections']:
        if not isinstance(params['collections'], list):
            raise ValueError("collections must be a list")
        
        for collection in params['collections']:
            if not isinstance(collection, str):
                raise ValueError("collection IDs must be strings")
    
    # Validate limit
    if 'limit' in params:
        limit = params['limit']
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        
        if limit > 10000:  # Reasonable upper limit
            raise ValueError("limit too large (max 10000)")
    
    return True


def validate_datetime_format(datetime_str: str) -> bool:
    """
    Validate datetime string format.
    
    Parameters
    ----------
    datetime_str : str
        Datetime string to validate
        
    Returns
    -------
    bool
        True if valid format
    """
    import re
    
    # RFC3339 datetime patterns
    patterns = [
        r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$',  # YYYY-MM-DDTHH:MM:SSZ
        r'^\d{4}-\d{2}-\d{2}/\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD/YYYY-MM-DD
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$'  # Full range
    ]
    
    for pattern in patterns:
        if re.match(pattern, datetime_str):
            return True
    
    return False
