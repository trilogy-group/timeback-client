"""API module for organization management.

This module provides the OrgsAPI class for managing organizations
in the OneRoster system.
"""

from typing import Dict, Any, Optional
from ..core.client import TimeBackService
from ..models.org import Org

class OrgsAPI(TimeBackService):
    """API client for organization management.
    
    This class provides methods for creating, reading, updating, and deleting
    organizations in the OneRoster system.
    """
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the OrgsAPI.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "rostering", client_id, client_secret)
    
    def create_org(self, org: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new organization.
        
        Args:
            org: Organization data following the OneRoster schema
            
        Returns:
            The created organization data
            
        Example:
            >>> api = OrgsAPI("https://alpha-1edtech.com")
            >>> org = {
            ...     "sourcedId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            ...     "status": "active",
            ...     "dateLastModified": "2025-03-26T15:00:00Z",
            ...     "name": "Alpha Anywhere",
            ...     "type": "school",
            ...     "identifier": "AA-001"
            ... }
            >>> response = api.create_org({"org": org})
        """
        return self._make_request("/orgs", method="POST", data={"org": org})
    
    def get_org(self, sourcedId: str) -> Dict[str, Any]:
        """Get an organization by ID.
        
        Args:
            sourcedId: The OneRoster ID of the organization
            
        Returns:
            The organization data
        """
        return self._make_request(f"/orgs/{sourcedId}")
    
    def list_orgs(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List organizations with pagination.
        
        Args:
            limit: Maximum number of organizations to return
            offset: Number of organizations to skip
            
        Returns:
            List of organizations
        """
        return self._make_request("/orgs", params={"limit": limit, "offset": offset}) 