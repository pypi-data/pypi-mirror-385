"""Base class for REST API resources."""

import logging
import time
from typing import Any
import requests

from ..exceptions import (
    ArcherAPIException,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError
)


logger = logging.getLogger(__name__)


class BaseAPI:
    """Base class for all REST API resource classes."""
    
    def __init__(self, authenticator, config):
        self.authenticator = authenticator
        self.config = config
        self.base_url = config.base_url
    
    def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """Make an authenticated API request with retry logic."""
        if not self.authenticator.is_authenticated:
            raise AuthenticationError("Not authenticated. Call authenticate() first.")
        
        headers = self.authenticator.get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        session = self.authenticator.get_session()
        retries = 0
        
        while retries <= self.config.max_retries:
            try:
                response = session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=self.config.timeout,
                    **kwargs
                )
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    if retries < self.config.max_retries:
                        logger.warning(f"Rate limited. Retrying after {retry_after}s")
                        time.sleep(retry_after)
                        retries += 1
                        continue
                    raise RateLimitError("Rate limit exceeded")
                
                if response.status_code == 401:
                    raise AuthenticationError("Authentication failed or token expired")
                
                if response.status_code == 404:
                    raise ResourceNotFoundError(f"Resource not found: {url}")
                
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                if retries < self.config.max_retries:
                    logger.warning(f"Request failed: {e}. Retrying...")
                    retries += 1
                    time.sleep(2 ** retries)
                else:
                    raise ArcherAPIException(f"Request failed after {retries} retries: {e}")
        
        raise ArcherAPIException("Maximum retries exceeded")