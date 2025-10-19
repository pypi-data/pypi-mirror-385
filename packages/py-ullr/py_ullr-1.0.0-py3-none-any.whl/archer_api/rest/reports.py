"""Report operations for Archer REST API."""

import logging
from typing import Dict, Any

from .base import BaseAPI


logger = logging.getLogger(__name__)


class ReportsAPI(BaseAPI):
    """API client for report operations."""
    
    def execute(self, report_id: int) -> Dict[str, Any]:
        """Execute a report and get results."""
        url = f"{self.base_url}/api/core/system/report/{report_id}/execute"
        response = self._make_request("GET", url)
        return response.json()
    
    def get(self, report_id: int) -> Dict[str, Any]:
        """Get report metadata."""
        url = f"{self.base_url}/api/core/system/report/{report_id}"
        response = self._make_request("GET", url)
        return response.json()