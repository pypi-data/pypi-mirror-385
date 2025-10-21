"""Record operations for Archer REST API."""

import logging
from typing import Dict, List, Optional, Any

from ..exceptions import ResourceNotFoundError, ValidationError, ArcherAPIException
from .base import BaseAPI


logger = logging.getLogger(__name__)


class RecordsAPI(BaseAPI):
    """API client for Archer record operations."""
    
    def get(self, content_id: int) -> Dict[str, Any]:
        """Get a specific record by content ID."""
        url = f"{self.base_url}/api/core/content/{content_id}"
        
        try:
            response = self._make_request("GET", url)
            return response.json()
        except ArcherAPIException as e:
            if "404" in str(e):
                raise ResourceNotFoundError(f"Record {content_id} not found")
            raise
    
    def create(
        self,
        application_id: int,
        field_values: Dict[str, Any],
        sub_form_data: Optional[List[Dict]] = None
    ) -> int:
        """Create a new record in an application."""
        url = f"{self.base_url}/api/core/content"
        
        field_contents = {}
        for field_name, value in field_values.items():
            field_contents[field_name] = {
                "Type": self._infer_field_type(value),
                "Value": value
            }
        
        payload = {
            "Content": {
                "LevelId": application_id,
                "FieldContents": field_contents
            }
        }
        
        if sub_form_data:
            payload["Content"]["SubformData"] = sub_form_data
        
        try:
            response = self._make_request("POST", url, json=payload)
            data = response.json()
            return data.get("RequestedObject", {}).get("Id")
        except ArcherAPIException as e:
            if "validation" in str(e).lower():
                raise ValidationError(f"Invalid field values: {e}")
            raise
    
    def update(self, content_id: int, field_values: Dict[str, Any]) -> bool:
        """Update an existing record."""
        url = f"{self.base_url}/api/core/content/{content_id}"
        
        field_contents = {}
        for field_name, value in field_values.items():
            field_contents[field_name] = {
                "Type": self._infer_field_type(value),
                "Value": value
            }
        
        payload = {
            "Content": {
                "Id": content_id,
                "FieldContents": field_contents
            }
        }
        
        response = self._make_request("PUT", url, json=payload)
        return response.status_code == 200
    
    def delete(self, content_id: int) -> bool:
        """Delete a record."""
        url = f"{self.base_url}/api/core/content/{content_id}"
        response = self._make_request("DELETE", url)
        return response.status_code == 200
    
    def search(
        self,
        application_id: int,
        filters: Optional[Dict[str, Any]] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for records in an application."""
        url = f"{self.base_url}/api/core/content/search"
        
        payload = {
            "LevelId": application_id,
            "MaxResultCount": max_results
        }
        
        if filters:
            payload["Filters"] = filters
        
        response = self._make_request("POST", url, json=payload)
        data = response.json()
        return data.get("RequestedObject", {}).get("Records", [])
    
    @staticmethod
    def _infer_field_type(value: Any) -> int:
        """Infer Archer field type from Python value."""
        if isinstance(value, str):
            return 1  # Text
        elif isinstance(value, (int, float)):
            return 2  # Numeric
        elif isinstance(value, bool):
            return 3  # Boolean
        elif isinstance(value, list):
            return 4  # Values List
        else:
            return 1  # Default to text