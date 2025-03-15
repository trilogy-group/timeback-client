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

from typing import Optional, Dict, Any, List
import requests
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

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
        
        logger.info("Making request to %s", url)
        logger.info("Method: %s", method)
        logger.info("Headers: %s", headers)
        logger.info("Data: %s", data)
        logger.info("Params: %s", params)
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data if data else None,
            params=params
        )
        
        if not response.ok:
            logger.error("Request failed with status %d", response.status_code)
            logger.error("Response body: %s", response.text)
            
        response.raise_for_status()
        response_data = response.json()
        
        # Apply case-insensitive sorting if needed
        if params and 'sort' in params and 'orderBy' in params:
            response_data = self._apply_case_insensitive_sort(
                response_data,
                params['sort'],
                params['orderBy']
            )
            
        return response_data

    def _apply_case_insensitive_sort(
        self,
        response_data: Dict[str, Any],
        sort_field: str,
        order_by: str
    ) -> Dict[str, Any]:
        """Apply case-insensitive sorting to API response data.
        
        This method is called automatically by _make_request when sort and orderBy
        parameters are present. It ensures consistent case-insensitive sorting
        regardless of the API's sorting behavior.
        
        Args:
            response_data: The API response data
            sort_field: The field to sort by
            order_by: The sort direction ('asc' or 'desc')
            
        Returns:
            The response data with sorted results
            
        Example:
            >>> service._apply_case_insensitive_sort(
            ...     {'users': [{'familyName': 'ADAMS'}, {'familyName': 'brown'}]},
            ...     'familyName',
            ...     'asc'
            ... )
            {'users': [{'familyName': 'ADAMS'}, {'familyName': 'brown'}]}
        """
        # Determine the collection key (e.g., 'users', 'classes', etc.)
        collection_key = next((k for k in response_data.keys() if isinstance(response_data[k], list)), None)
        if not collection_key or not response_data[collection_key]:
            return response_data
            
        # Sort the collection case-insensitively
        items = response_data[collection_key]
        sorted_items = sorted(
            items,
            key=lambda x: str(x.get(sort_field, '')).lower(),
            reverse=(order_by.lower() == 'desc')
        )
        
        response_data[collection_key] = sorted_items
        return response_data

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
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List users with optional pagination, sorting, filtering and field selection.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            sort: Field to sort by (e.g., 'familyName')
            order_by: Sort direction ('asc' or 'desc')
            filter_expr: Filter expression (e.g., "role='student'")
            fields: List of fields to return
            
        Returns:
            A dictionary containing the users and pagination information
            
        Example:
            >>> service.list_users(
            ...     limit=10,
            ...     sort='familyName',
            ...     order_by='asc',
            ...     filter_expr="role='student'",
            ...     fields=['sourcedId', 'givenName', 'familyName']
            ... )
        """
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        if sort:
            params['sort'] = sort
        if order_by:
            params['orderBy'] = order_by
        if filter_expr:
            params['filter'] = filter_expr
        if fields:
            params['fields'] = ','.join(fields)
            
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