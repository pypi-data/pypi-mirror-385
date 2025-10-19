"""Value list operations for Archer REST API."""

import logging
from typing import List, Dict, Any

from .base import BaseAPI


logger = logging.getLogger(__name__)


class ValueListsAPI(BaseAPI):
    """API client for value list operations."""
    
    def get(self, value_list_id: int) -> Dict[str, Any]:
        """Get a value list."""
        url = f"{self.base_url}/api/core/system/valueslistvalue/valueslist/{value_list_id}"
        response = self._make_request("GET", url)
        return response.json()
    
    def get_values(self, value_list_id: int) -> List[Dict[str, Any]]:
        """Get all values in a value list."""
        url = f"{self.base_url}/api/core/system/valueslistvalue/valueslist/{value_list_id}"
        response = self._make_request("GET", url)
        data = response.json()
        return data.get("RequestedObject", [])