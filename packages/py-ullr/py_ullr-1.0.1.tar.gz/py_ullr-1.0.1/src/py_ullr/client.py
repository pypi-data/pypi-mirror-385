"""Main Archer API client."""

import logging
from typing import Optional
from dataclasses import dataclass

from .auth.authenticator import Authenticator
from .rest.applications import ApplicationsAPI
from .rest.records import RecordsAPI
from .rest.content import ContentAPI
from .rest.users import UsersAPI
from .rest.value_lists import ValueListsAPI
from .rest.reports import ReportsAPI
from .rest.search import SearchAPI
from .webservices.client import WebServicesClient
from .exceptions import ArcherAPIException


logger = logging.getLogger(__name__)


@dataclass
class ArcherConfig:
    """Configuration for Archer API client."""
    
    base_url: str
    instance_name: str
    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True
    proxy: Optional[dict] = None
    log_level: str = "INFO"


class RESTAPIClient:
    """Container for REST API resources."""
    
    def __init__(self, authenticator: Authenticator, config: ArcherConfig):
        self.applications = ApplicationsAPI(authenticator, config)
        self.records = RecordsAPI(authenticator, config)
        self.content = ContentAPI(authenticator, config)
        self.users = UsersAPI(authenticator, config)
        self.value_lists = ValueListsAPI(authenticator, config)
        self.reports = ReportsAPI(authenticator, config)
        self.search = SearchAPI(authenticator, config)


class ArcherClient:
    """
    Main client for interacting with Archer APIs.
    
    Args:
        base_url: Base URL of the Archer instance
        instance_name: Name of the Archer instance
        username: Optional username for automatic authentication
        password: Optional password for automatic authentication
        config: Optional ArcherConfig object
    """
    
    def __init__(
        self,
        base_url: str = None,
        instance_name: str = None,
        username: str = None,
        password: str = None,
        config: Optional[ArcherConfig] = None
    ):
        if config:
            self.config = config
        elif base_url and instance_name:
            self.config = ArcherConfig(
                base_url=base_url,
                instance_name=instance_name
            )
        else:
            raise ValueError("Either config or base_url and instance_name must be provided")
        
        logging.basicConfig(level=self.config.log_level)
        
        self._authenticator = Authenticator(self.config)
        self.rest = RESTAPIClient(self._authenticator, self.config)
        self.webservices = WebServicesClient(self._authenticator, self.config)
        
        if username and password:
            self.authenticate(username, password)
    
    def authenticate(self, username: str, password: str, user_domain: str = "") -> str:
        """Authenticate with Archer."""
        logger.info(f"Authenticating user: {username}")
        token = self._authenticator.authenticate(username, password, user_domain)
        logger.info("Authentication successful")
        return token
    
    def logout(self) -> None:
        """Logout and clear the session token."""
        logger.info("Logging out")
        self._authenticator.logout()
    
    @property
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        return self._authenticator.is_authenticated
    
    @property
    def session_token(self) -> Optional[str]:
        """Get the current session token."""
        return self._authenticator.session_token