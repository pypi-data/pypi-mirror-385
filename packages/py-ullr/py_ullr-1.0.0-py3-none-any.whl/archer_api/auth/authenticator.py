"""Authentication management for Archer APIs."""

import requests
import logging
from typing import Optional
from datetime import datetime, timedelta

from ..exceptions import AuthenticationError


logger = logging.getLogger(__name__)


class Authenticator:
    """Handles authentication and session management."""
    
    def __init__(self, config):
        self.config = config
        self._session_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._session = requests.Session()
        
        if config.proxy:
            self._session.proxies.update(config.proxy)
        
        self._session.verify = config.verify_ssl
    
    def authenticate(
        self,
        username: str,
        password: str,
        user_domain: str = ""
    ) -> str:
        """Authenticate with Archer and obtain a session token."""
        url = f"{self.config.base_url}/api/core/security/login"
        
        payload = {
            "InstanceName": self.config.instance_name,
            "Username": username,
            "UserDomain": user_domain,
            "Password": password
        }
        
        try:
            response = self._session.post(
                url,
                json=payload,
                timeout=self.config.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self._session_token = data.get("RequestedObject", {}).get("SessionToken")
                
                if not self._session_token:
                    raise AuthenticationError("No session token in response")
                
                self._token_expiry = datetime.now() + timedelta(minutes=30)
                
                logger.info("Authentication successful")
                return self._session_token
            else:
                error_msg = f"Authentication failed: {response.status_code}"
                logger.error(error_msg)
                raise AuthenticationError(error_msg)
                
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise AuthenticationError(f"Authentication request failed: {e}")
    
    def logout(self) -> None:
        """Logout and clear the session token."""
        if not self._session_token:
            return
        
        url = f"{self.config.base_url}/api/core/security/logout"
        
        try:
            self._session.post(
                url,
                headers=self._get_headers(),
                timeout=self.config.timeout
            )
        except requests.RequestException as e:
            logger.warning(f"Logout request failed: {e}")
        finally:
            self._session_token = None
            self._token_expiry = None
    
    def _get_headers(self) -> dict:
        """Get request headers with session token."""
        if not self._session_token:
            raise AuthenticationError("Not authenticated")
        
        return {
            "Authorization": f"Archer session-id={self._session_token}",
            "Content-Type": "application/json"
        }
    
    @property
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with a valid token."""
        if not self._session_token:
            return False
        
        if self._token_expiry and datetime.now() >= self._token_expiry:
            logger.warning("Session token expired")
            return False
        
        return True
    
    @property
    def session_token(self) -> Optional[str]:
        """Get the current session token."""
        return self._session_token
    
    def get_session(self) -> requests.Session:
        """Get the configured requests session."""
        return self._session
    
    def get_headers(self) -> dict:
        """Get authenticated request headers."""
        return self._get_headers()