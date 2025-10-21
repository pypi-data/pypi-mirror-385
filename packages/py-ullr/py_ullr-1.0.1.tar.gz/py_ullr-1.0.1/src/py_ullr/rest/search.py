"""Advanced search operations for Archer REST API."""

import logging
from typing import List, Dict, Any, Optional

from .base import BaseAPI


logger = logging.getLogger(__name__)


class SearchAPI(BaseAPI):
    """API client for advanced search operations."""
    
    def advanced_search(
        self,
        application_id: int,
        filters: Optional[List[Dict[str, Any]]] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Perform advanced search."""
        url = f"{self.base_url}/api/core/content/search"
        
        payload = {
            "LevelId": application_id,
            "MaxResultCount": max_results
        }
        
        if filters:
            payload["Criteria"] = filters
        
        response = self._make_request("POST", url, json=payload)
        data = response.json()
        return data.get("RequestedObject", {}).get("Records", [])