"""
Base FPL API Client with error handling, retries, and caching.
"""
import requests
import logging
import time
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
        self.last_request_time = 0
        self.min_request_interval = 0.5  # Minimum 500ms between requests
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=30)
    )
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request to FPL API with retry logic and rate limiting.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.HTTPError: If request fails after retries
        """
        # Rate limiting: wait if we made a request too recently
        time_since_last_request = time.time() - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making request to: {url}")
            response = self.session.get(url, params=params, timeout=15)
            self.last_request_time = time.time()  # Update last request time
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Handle rate limiting specifically
            if response.status_code == 429:
                logger.warning(f"Rate limited by FPL API. Waiting before retry...")
                time.sleep(5)  # Wait 5 seconds before retry
                raise  # Will trigger retry with exponential backoff
            logger.error(f"HTTP error for {url}: {str(e)}")
            raise
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
