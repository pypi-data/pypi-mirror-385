"""Content/file operations for Archer REST API."""

import logging
from typing import BinaryIO, Optional

from .base import BaseAPI


logger = logging.getLogger(__name__)


class ContentAPI(BaseAPI):
    """API client for file/attachment operations."""
    
    def upload(
        self,
        application_id: int,
        content_id: int,
        field_id: int,
        file_data: BinaryIO,
        filename: str
    ) -> int:
        """Upload a file attachment."""
        url = f"{self.base_url}/api/core/content/attachment"
        
        files = {
            'file': (filename, file_data)
        }
        
        data = {
            'AttachmentName': filename,
            'ContentId': content_id,
            'FieldId': field_id
        }
        
        response = self._make_request("POST", url, files=files, data=data)
        result = response.json()
        return result.get("RequestedObject", {}).get("Id")
    
    def download(self, attachment_id: int) -> bytes:
        """Download a file attachment."""
        url = f"{self.base_url}/api/core/content/attachment/{attachment_id}"
        response = self._make_request("GET", url)
        return response.content
    
    def delete(self, attachment_id: int) -> bool:
        """Delete a file attachment."""
        url = f"{self.base_url}/api/core/content/attachment/{attachment_id}"
        response = self._make_request("DELETE", url)
        return response.status_code == 200