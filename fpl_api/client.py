"""
Base FPL API Client with error handling, retries, and caching.
"""
import requests
import logging
from typing import Dict, Any, Optional
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings


logger = logging.getLogger(__name__)


class FPLClient:
    """Base client for FPL API with robust error handling and caching."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize FPL Client.
        
        Args:
            base_url: Base URL for FPL API. Defaults to settings value.
        """
        self.base_url = base_url or settings.fpl_base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FPL-Agent/1.0'
        })
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request to FPL API with retry logic.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.HTTPError: If request fails after retries
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making request to: {url}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            raise
    
    def get(self, endpoint: str, params: Optional[Dict] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        GET request with optional caching.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            use_cache: Whether to use caching
            
        Returns:
            API response data
        """
        if use_cache and settings.enable_cache:
            return self._cached_get(endpoint, str(params))
        return self._make_request(endpoint, params)
    
    @lru_cache(maxsize=128)
    def _cached_get(self, endpoint: str, params_str: str) -> Dict[str, Any]:
        """Cached version of GET request."""
        params = eval(params_str) if params_str != "None" else None
        return self._make_request(endpoint, params)
    
    def clear_cache(self):
        """Clear the request cache."""
        self._cached_get.cache_clear()
        logger.info("Cache cleared")
