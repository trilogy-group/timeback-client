"""TimeBack API client implementation.

This module provides a Python client for the TimeBack API, which implements the OneRoster 1.2 specification.
The client is organized into three main services:

1. RosteringService - User and organization management
2. GradebookService - Grades and assessments
3. ResourcesService - Learning resources

Example:
    >>> from timeback_client import TimeBackClient
    >>> client = TimeBackClient("http://oneroster-staging.us-west-2.elasticbeanstalk.com")
    >>> users = client.rostering.list_users(limit=10)
    >>> user = client.rostering.get_user("user-id")
"""

from typing import Optional, Dict, Any
import requests
from urllib.parse import urljoin

class TimeBackService:
    """Base class for TimeBack API services.
    
    This class provides common functionality for all TimeBack services,
    including URL construction and request handling.
    
    Args:
        base_url: The base URL of the TimeBack API (e.g., http://oneroster-staging.us-west-2.elasticbeanstalk.com)
        service: The service name (rostering, gradebook, or resources)
    """
    
    def __init__(self, base_url: str, service: str):
        """Initialize service with base URL and service name.
        
        Args:
            base_url: The base URL of the TimeBack API
            service: The service name (rostering, gradebook, or resources)
        """
        self.base_url = base_url.rstrip('/')
        self.service = service
        self.api_path = f"/ims/oneroster/{service}/v1p2"
        
    def _make_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make request to TimeBack API.
        
        Args:
            endpoint: The API endpoint (e.g., "/users")
            method: The HTTP method to use
            data: The request payload for POST/PUT requests
            params: Query parameters for GET requests
            
        Returns:
            The JSON response from the API
            
        Raises:
            requests.exceptions.HTTPError: For HTTP errors (4xx, 5xx)
            requests.exceptions.ConnectionError: For network problems
            requests.exceptions.Timeout: For timeout errors
            requests.exceptions.RequestException: For all other errors
        """
        url = urljoin(self.base_url + self.api_path + "/", endpoint.lstrip('/'))
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data if data else None,
            params=params
        )
        response.raise_for_status()
        return response.json()

class RosteringService(TimeBackService):
    """Client for TimeBack Rostering API.
    
    This service handles all user and organization-related operations
    as defined in the OneRoster 1.2 specification.
    
    Example:
        >>> client = TimeBackClient("http://oneroster-staging.us-west-2.elasticbeanstalk.com")
        >>> rostering = client.rostering
        >>> users = rostering.list_users(limit=10)
    """
    
    def __init__(self, base_url: str):
        """Initialize rostering service.
        
        Args:
            base_url: The base URL of the TimeBack API
        """
        super().__init__(base_url, "rostering")
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get a user by ID.
        
        Args:
            user_id: The unique identifier of the user
            
        Returns:
            The user data as defined in the OneRoster specification
            
        Raises:
            requests.exceptions.HTTPError: If the user is not found (404)
                or other HTTP errors
        """
        return self._make_request(f"/users/{user_id}")
    
    def list_users(
        self, 
        limit: Optional[int] = None, 
        offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """List users with optional pagination.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            A dictionary containing the users and pagination information
        """
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        return self._make_request("/users", params=params)

class GradebookService(TimeBackService):
    """Client for TimeBack Gradebook API.
    
    This service handles all grade and assessment-related operations
    as defined in the OneRoster 1.2 specification.
    
    Note:
        This service is currently a placeholder and will be implemented
        in a future version.
    """
    
    def __init__(self, base_url: str):
        """Initialize gradebook service.
        
        Args:
            base_url: The base URL of the TimeBack API
        """
        super().__init__(base_url, "gradebook")

class ResourcesService(TimeBackService):
    """Client for TimeBack Resources API.
    
    This service handles all learning resource operations
    as defined in the OneRoster 1.2 specification.
    
    Note:
        This service is currently a placeholder and will be implemented
        in a future version.
    """
    
    def __init__(self, base_url: str):
        """Initialize resources service.
        
        Args:
            base_url: The base URL of the TimeBack API
        """
        super().__init__(base_url, "resources")

class TimeBackClient:
    """Main client for TimeBack API.
    
    This is the main entry point for the TimeBack API client.
    It provides access to all OneRoster services through dedicated
    service clients.
    
    Example:
        >>> client = TimeBackClient("http://oneroster-staging.us-west-2.elasticbeanstalk.com")
        >>> users = client.rostering.list_users()
        >>> grades = client.gradebook.get_grades()  # Coming soon
        >>> resources = client.resources.list_resources()  # Coming soon
    """
    
    def __init__(self, api_url: str):
        """Initialize TimeBack client with API URL.
        
        Args:
            api_url: The base URL of the TimeBack API
        """
        self.api_url = api_url.rstrip('/')
        self.rostering = RosteringService(self.api_url)
        self.gradebook = GradebookService(self.api_url)
        self.resources = ResourcesService(self.api_url) 