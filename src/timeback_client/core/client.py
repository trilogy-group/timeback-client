"""TimeBack API client implementation.

This module provides a Python client for the TimeBack API, which implements the OneRoster 1.2 specification.
The client is organized into three main services:

1. RosteringService - User and organization management
2. GradebookService - Grades and assessments
3. ResourcesService - Learning resources

Example:
    >>> from timeback_client import TimeBackClient
    >>> client = TimeBackClient("http://staging.alpha-1edtech.com/")
    >>> users = client.rostering.users.list_users(limit=10)
    >>> user = client.rostering.users.get_user("user-id")
"""

from typing import Optional, Dict, Any, List, Type
import requests
from urllib.parse import urljoin
import logging
import importlib
import inspect
import json

logger = logging.getLogger(__name__)

class TimeBackService:
    """Base class for TimeBack API services.
    
    This class provides common functionality for all TimeBack services,
    including URL construction and request handling.
    
    Args:
        base_url: The base URL of the TimeBack API (e.g., http://staging.alpha-1edtech.com/)
        service: The service name (rostering, gradebook, or resources)
    """
    
    def __init__(self, base_url: str, service: str):
        """Initialize service with base URL and service name.
        
        Args:
            base_url: The base URL of the TimeBack API (e.g., http://staging.alpha-1edtech.com/)
            service: The service name (rostering, gradebook, or resources)
        """
        # Handle None for base_url
        self.base_url = "" if base_url is None else base_url.rstrip('/')
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
            The JSON response from the API or an empty dict if no content
            
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
        
        # Handle empty responses
        if not response.text.strip():
            logger.info("Empty response received from %s", url)
            return {"message": "Success (empty response)"}
            
        try:
            response_data = response.json()
            logger.info("Successful response from %s", url)
            
            # Apply case-insensitive sorting if needed
            if params and 'sort' in params and 'orderBy' in params:
                response_data = self._apply_case_insensitive_sort(
                    response_data,
                    params['sort'],
                    params['orderBy']
                )
                
            return response_data
        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse response as JSON: {e}")
            return {"message": "Success (non-JSON response)", "text": response.text}

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
    as defined in the OneRoster 1.2 specification. It dynamically loads
    specialized API classes for each entity type.
    
    Example:
        >>> client = TimeBackClient("http://staging.alpha-1edtech.com/")
        >>> rostering = client.rostering
        >>> users = rostering.users.list_users(limit=10)
        >>> orgs = rostering.orgs.list_orgs()  # When implemented
    """
    
    def __init__(self, base_url: str):
        """Initialize rostering service.
        
        Args:
            base_url: The base URL of the TimeBack API (e.g., http://staging.alpha-1edtech.com/)
        """
        super().__init__(base_url, "rostering")
        self._api_registry = {}
        self._load_api_modules()
        
    def _load_api_modules(self):
        """Dynamically load all API modules in the api package."""
        try:
            # Import the api package using absolute import
            api_package = importlib.import_module("timeback_client.api")
            
            # Get all modules in the api package
            for module_name in getattr(api_package, "__all__", []):
                try:
                    # Import the module using absolute import
                    module = importlib.import_module(f"timeback_client.api.{module_name}")
                    
                    # Find all classes that inherit from TimeBackService
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, TimeBackService) and obj != TimeBackService:
                            # Register the API class
                            entity_name = module_name.lower()
                            self._api_registry[entity_name] = obj(self.base_url)
                            logger.info(f"Registered API class {name} for entity {entity_name}")
                except ImportError as e:
                    logger.warning(f"Could not import API module {module_name}: {e}")
        except ImportError as e:
            # If the api package doesn't have __all__, manually register known APIs
            logger.warning(f"Could not import API package: {e}")
            self._register_known_apis()
    
    def _register_known_apis(self):
        """Manually register known API classes."""
        try:
            # Import and register UsersAPI
            from ..api.users import UsersAPI
            self._api_registry["users"] = UsersAPI(self.base_url)
            logger.info("Registered UsersAPI")
            
            # Add more API classes here as they are implemented
            # Example:
            # from ..api.orgs import OrgsAPI
            # self._api_registry["orgs"] = OrgsAPI(self.base_url)
        except ImportError as e:
            logger.error(f"Could not import known API classes: {e}")
    
    def __getattr__(self, name):
        """Dynamically access API classes by name.
        
        This allows for syntax like:
        client.rostering.users.list_users()
        client.rostering.orgs.list_orgs()
        
        Args:
            name: The name of the API to access (e.g., "users", "orgs")
            
        Returns:
            The API instance
            
        Raises:
            AttributeError: If the API is not registered
        """
        if name in self._api_registry:
            return self._api_registry[name]
        
        # For backward compatibility, provide direct access to methods
        # This will be deprecated in a future version
        for api in self._api_registry.values():
            if hasattr(api, name):
                logger.warning(
                    f"Direct method access '{name}' is deprecated. "
                    f"Use '{api.__class__.__name__.lower()}.{name}' instead."
                )
                return getattr(api, name)
        
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

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
            base_url: The base URL of the TimeBack API (e.g., http://staging.alpha-1edtech.com/)
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
            base_url: The base URL of the TimeBack API (e.g., http://staging.alpha-1edtech.com/)
        """
        super().__init__(base_url, "resources")

class QTIService(TimeBackService):
    """Client for TimeBack QTI API.
    
    This service handles all assessment content operations
    as defined in the QTI 3.0 specification.
    """
    
    # Default QTI staging URL
    DEFAULT_QTI_URL = "https://alpha-qti-api-43487de62e73.herokuapp.com/api"
    
    def __init__(self, base_url: str = None, qti_api_url: str = None):
        """Initialize QTI service.
        
        Args:
            base_url: The base URL of the TimeBack API (e.g., http://staging.alpha-1edtech.com/)
            qti_api_url: The base URL of the QTI API. If not provided, uses the default staging URL.
        """
        # QTI service doesn't use the standard OneRoster base URL
        # Instead it has its own API endpoint
        self.qti_url = (qti_api_url or self.DEFAULT_QTI_URL).rstrip('/')
        
        # We still call the parent constructor, but override the methods to use qti_url
        super().__init__(base_url, "qti")
        self._api_registry = {}
        self._load_api_modules()
    
    def _make_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make request to QTI API.
        
        Override the parent _make_request method to use the QTI URL instead of the
        standard OneRoster URL construction.
        
        Args:
            endpoint: The API endpoint (e.g., "/assessment-items")
            method: The HTTP method to use
            data: The request payload for POST/PUT requests
            params: Query parameters for GET requests
            
        Returns:
            The JSON response from the API or an empty dict if no content
        """
        url = urljoin(self.qti_url + "/", endpoint.lstrip('/'))
        
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
        
        # Handle empty responses
        if not response.text.strip():
            logger.info("Empty response received from %s", url)
            return {"message": "Success (empty response)"}
            
        try:
            response_data = response.json()
            logger.info("Successful response from %s", url)
            return response_data
        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse response as JSON: {e}")
            return {"message": "Success (non-JSON response)", "text": response.text}
        
    def _load_api_modules(self):
        """Dynamically load all API modules for QTI."""
        try:
            # Import the assessment_items API module
            from ..api.assessment_items import AssessmentItemsAPI
            
            # Register API classes with QTI URL
            self._api_registry["assessment_items"] = AssessmentItemsAPI(None, self.qti_url)
            logger.info("Registered AssessmentItemsAPI with QTI URL: %s", self.qti_url)
        except ImportError as e:
            logger.error(f"Could not import QTI API modules: {e}")
    
    def __getattr__(self, name):
        """Dynamically access API classes by name."""
        if name in self._api_registry:
            return self._api_registry[name]
        
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

class TimeBackClient:
    """Main client for TimeBack API.
    
    This is the main entry point for the TimeBack API client.
    It provides access to all OneRoster services through dedicated
    service clients.
    
    Example:
        >>> client = TimeBackClient("http://staging.alpha-1edtech.com/")
        >>> users = client.rostering.users.list_users()
        >>> grades = client.gradebook.get_grades()  # Coming soon
        >>> resources = client.resources.list_resources()  # Coming soon
        >>> qti_items = client.qti.assessment_items.list_assessment_items()  # Using QTI API
    """
    
    # Default staging URL for OneRoster
    DEFAULT_URL = "http://staging.alpha-1edtech.com/"
    
    # Default staging URL for QTI API
    DEFAULT_QTI_URL = "https://alpha-qti-api-43487de62e73.herokuapp.com/api"
    
    def __init__(self, api_url: str = None, qti_api_url: str = None):
        """Initialize TimeBack client with API URLs.
        
        Args:
            api_url: The base URL of the TimeBack OneRoster API. If not provided, uses the default staging URL.
            qti_api_url: The base URL of the QTI API. If not provided, uses the default QTI staging URL.
        """
        self.api_url = (api_url or self.DEFAULT_URL).rstrip('/')
        self.qti_api_url = (qti_api_url or self.DEFAULT_QTI_URL).rstrip('/')
        
        self.rostering = RosteringService(self.api_url)
        self.gradebook = GradebookService(self.api_url)
        self.resources = ResourcesService(self.api_url)
        self.qti = QTIService(self.api_url, self.qti_api_url) 