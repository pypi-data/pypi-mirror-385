"""Application operations for Archer REST API."""

import logging
from typing import List, Dict, Any

from .base import BaseAPI


logger = logging.getLogger(__name__)


class ApplicationsAPI(BaseAPI):
    """API client for Archer application operations."""
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all applications."""
        url = f"{self.base_url}/api/core/system/application"
        response = self._make_request("GET", url)
        return response.json()
    
    def get(self, application_id: int) -> Dict[str, Any]:
        """Get a specific application."""
        url = f"{self.base_url}/api/core/system/application/{application_id}"
        response = self._make_request("GET", url)
        return response.json()
    
    def get_fields(self, application_id: int) -> List[Dict[str, Any]]:
        """Get fields for an application."""
        url = f"{self.base_url}/api/core/system/fielddefinition/application/{application_id}"
        response = self._make_request("GET", url)
        return response.json()