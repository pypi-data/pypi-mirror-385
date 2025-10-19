"""User operations for Archer REST API."""

import logging
from typing import List, Dict, Any

from .base import BaseAPI


logger = logging.getLogger(__name__)


class UsersAPI(BaseAPI):
    """API client for user operations."""
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all users."""
        url = f"{self.base_url}/api/core/system/user"
        response = self._make_request("GET", url)
        return response.json()
    
    def get(self, user_id: int) -> Dict[str, Any]:
        """Get a specific user."""
        url = f"{self.base_url}/api/core/system/user/{user_id}"
        response = self._make_request("GET", url)
        return response.json()
    
    def search(self, username: str) -> List[Dict[str, Any]]:
        """Search for users by username."""
        url = f"{self.base_url}/api/core/system/user/search"
        payload = {"Username": username}
        response = self._make_request("POST", url, json=payload)
        return response.json()