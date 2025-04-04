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
from urllib.parse import urljoin, urlparse
import logging
import importlib
import inspect
import json
import time

logger = logging.getLogger(__name__)

class TimeBackService:
    """Base class for TimeBack API services.
    
    This class provides common functionality for all TimeBack services,
    including URL construction and request handling.
    
    Args:
        base_url: The base URL of the TimeBack API (e.g., http://staging.alpha-1edtech.com/)
        service: The service name (rostering, gradebook, or resources)
        client_id: OAuth2 client ID for authentication
        client_secret: OAuth2 client secret for authentication
    """
    
    def __init__(self, base_url: str, service: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize service with base URL and service name.
        
        Args:
            base_url: The base URL of the TimeBack API
            service: The service name (rostering, gradebook, or resources)
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        self.base_url = "" if base_url is None else base_url.rstrip('/')
        self.service = service
        self.api_path = f"/ims/oneroster/{service}/v1p2"
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
        self._token_expiry = None
        
    def _get_auth_token(self) -> str:
        """Get a valid OAuth2 access token.
        
        Returns:
            str: The access token
            
        Raises:
            requests.exceptions.RequestException: If token request fails
        """
        if self._access_token and self._token_expiry and time.time() < self._token_expiry:
            return self._access_token
            
        if not (self.client_id and self.client_secret):
            return None
            
        # Always use production IDP URL
        idp_url = "https://alpha-auth-production-idp.auth.us-west-2.amazoncognito.com"
        logger.info(f"Using production IDP URL for authentication: {idp_url}")
            
        response = requests.post(
            f"{idp_url}/oauth2/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        )
        response.raise_for_status()
        
        token_data = response.json()
        self._access_token = token_data["access_token"]
        self._token_expiry = time.time() + token_data["expires_in"] - 60  # Refresh 1 minute early
        
        return self._access_token
        
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
        
        # Add authorization if credentials are provided
        token = self._get_auth_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        logger.info("Making request to %s", url)
        logger.info("Method: %s", method)
        logger.info("Headers: %s", {k: v for k, v in headers.items() if k != 'Authorization'})
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
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize rostering service.
        
        Args:
            base_url: The base URL of the TimeBack API (e.g., http://staging.alpha-1edtech.com/)
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "rostering", client_id, client_secret)
        self._api_registry = {}
        self._load_api_modules()
        
    def _load_api_modules(self):
        """Dynamically load all API modules in the api package."""
        try:
            # Import the api package using absolute import
            api_package = importlib.import_module("timeback_client.api")
            logger.info("Successfully imported API package")
            
            # Get all modules in the api package
            all_modules = getattr(api_package, "__all__", [])
            logger.info(f"Found modules in __all__: {all_modules}")
            
            for module_name in all_modules:
                try:
                    logger.info(f"Attempting to import module: {module_name}")
                    # Import the module using absolute import
                    module = importlib.import_module(f"timeback_client.api.{module_name}")
                    logger.info(f"Successfully imported module: {module_name}")
                    
                    # Find all classes that inherit from TimeBackService
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        logger.info(f"Found class {name} in module {module_name}")
                        if issubclass(obj, TimeBackService) and obj != TimeBackService:
                            # Register the API class
                            entity_name = module_name.lower()
                            logger.info(f"Registering {name} as {entity_name}")
                            self._api_registry[entity_name] = obj(self.base_url, self.client_id, self.client_secret)
                            logger.info(f"Registered API class {name} for entity {entity_name}")
                except ImportError as e:
                    logger.warning(f"Could not import API module {module_name}: {e}")
                    logger.warning(f"Import error details: {str(e)}")
                    logger.warning(f"Module path: timeback_client.api.{module_name}")
                    # Log the full traceback for debugging
                    import traceback
                    logger.warning(f"Full traceback:\n{traceback.format_exc()}")
        except ImportError as e:
            # If the api package doesn't have __all__, manually register known APIs
            logger.warning(f"Could not import API package: {e}")
            self._register_known_apis()
    
    def _register_known_apis(self):
        """Manually register known API classes."""
        try:
            # Import and register UsersAPI
            from ..api.users import UsersAPI
            self._api_registry["users"] = UsersAPI(self.base_url, self.client_id, self.client_secret)
            logger.info("Registered UsersAPI")
            
            # Import and register OrgsAPI
            from ..api.orgs import OrgsAPI
            self._api_registry["orgs"] = OrgsAPI(self.base_url, self.client_id, self.client_secret)
            logger.info("Registered OrgsAPI")
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
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize gradebook service.
        
        Args:
            base_url: The base URL of the TimeBack API (e.g., http://staging.alpha-1edtech.com/)
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "gradebook", client_id, client_secret)

class ResourcesService(TimeBackService):
    """Client for TimeBack Resources API.
    
    This service handles all learning resource operations
    as defined in the OneRoster 1.2 specification.
    """
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize resources service."""
        logger.info("Initializing ResourcesService")  # Debug log
        super().__init__(base_url, "resources", client_id, client_secret)
        self._api_registry = {}
        self._load_api_modules()
        logger.info(f"ResourcesService initialized with registry: {self._api_registry}")  # Debug log
        
    def _load_api_modules(self):
        """Dynamically load all API modules for Resources."""
        try:
            logger.info("Attempting to load ResourcesAPI")  # Debug log
            # Import the resources API module
            from ..api.resources import ResourcesAPI
            logger.info("Successfully imported ResourcesAPI")  # Debug log
            
            # Register API class
            api_instance = ResourcesAPI(self.base_url, self.client_id, self.client_secret)
            self._api_registry["resources"] = api_instance
            logger.info("Registered ResourcesAPI for entity resources")
            logger.info(f"Available methods on ResourcesAPI: {dir(api_instance)}")  # Debug log
        except ImportError as e:
            logger.error(f"Could not import Resources API modules: {str(e)}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error loading Resources API: {str(e)}", exc_info=True)
            
    def __getattr__(self, name):
        """Dynamically access API classes by name."""
        logger.info(f"Attempting to access attribute: {name}")  # Debug log
        logger.info(f"Available registry keys: {list(self._api_registry.keys())}")  # Debug log
        if name in self._api_registry:
            return self._api_registry[name]
        
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

class QTIService(TimeBackService):
    """Client for TimeBack QTI API.
    
    This service handles all assessment content operations
    as defined in the QTI 3.0 specification.
    """
    
    # Default QTI staging URL
    DEFAULT_QTI_URL = "https://alpha-qti-api-43487de62e73.herokuapp.com/api"
    
    def __init__(self, base_url: str, qti_api_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize QTI service.
        
        Args:
            base_url: The base URL of the TimeBack API (e.g., http://staging.alpha-1edtech.com/)
            qti_api_url: The base URL of the QTI API. If not provided, uses the default staging URL.
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        # QTI service doesn't use the standard OneRoster base URL
        # Instead it has its own API endpoint
        self.qti_url = (qti_api_url or self.DEFAULT_QTI_URL).rstrip('/')
        
        # We still call the parent constructor, but override the methods to use qti_url
        super().__init__(base_url, "qti", client_id, client_secret)
        self._api_registry = {}
        self._load_api_modules()
    
    def _load_api_modules(self):
        """Dynamically load all API modules for QTI."""
        try:
            # Import the assessment_items API module
            from ..api.assessment_items import AssessmentItemsAPI
            
            # Register API classes with QTI URL
            self._api_registry["assessment_items"] = AssessmentItemsAPI(self.qti_url, self.client_id, self.client_secret)
            logger.info("Registered AssessmentItemsAPI with QTI URL: %s", self.qti_url)
        except ImportError as e:
            logger.error(f"Could not import QTI API modules: {e}")
    
    def __getattr__(self, name):
        """Dynamically access API classes by name."""
        if name in self._api_registry:
            return self._api_registry[name]
        
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

class PowerPathService(TimeBackService):
    """Client for PowerPath-specific API endpoints.
    
    This service handles PowerPath-specific operations that don't follow
    the standard OneRoster URL pattern.
    """
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize PowerPath service.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        # Call parent but override api_path since PowerPath doesn't use OneRoster path
        super().__init__(base_url, "powerpath", client_id, client_secret)
        self.api_path = "/powerpath"  # Override the OneRoster path
        self._api_registry = {}
        self._load_api_modules()
        
    def _load_api_modules(self):
        """Load PowerPath API modules."""
        try:
            from ..api.powerpath import PowerPathAPI
            # Register API directly since PowerPath is self-contained
            self._api_registry["powerpath"] = PowerPathAPI(self.base_url, self.client_id, self.client_secret)
            logger.info("Registered PowerPathAPI")
        except ImportError as e:
            logger.error(f"Could not import PowerPath API module: {e}")
            
    def __getattr__(self, name):
        """Access PowerPath API methods directly."""
        if name in self._api_registry:
            return self._api_registry[name]
            
        # Allow direct access to PowerPath methods for convenience
        if "powerpath" in self._api_registry:
            return getattr(self._api_registry["powerpath"], name)
            
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

class TimeBackClient:
    """Main client for TimeBack API.
    
    This is the main entry point for the TimeBack API client.
    It provides access to all OneRoster services through dedicated
    service clients.
    
    Example:
        >>> client = TimeBackClient()
        >>> users = client.rostering.users.list_users()
        >>> grades = client.gradebook.get_grades()  # Coming soon
        >>> resources = client.resources.list_resources()  # Coming soon
        >>> qti_items = client.qti.assessment_items.list_assessment_items()  # Using QTI API
        >>> syllabus = client.powerpath.get_course_syllabus("course-id")  # Using PowerPath API
    """
    
    # Update default URLs
    DEFAULT_STAGING_URL = "http://staging.alpha-1edtech.com/"
    DEFAULT_PRODUCTION_URL = "https://api.alpha-1edtech.com/"  # Updated to use api subdomain
    DEFAULT_QTI_URL = "https://qti.alpha-1edtech.com"  # QTI only has production
    
    def __init__(
        self, 
        api_url: Optional[str] = None,
        qti_api_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        environment: str = "production"  # Default to production
    ):
        """Initialize TimeBack client with API URLs and authentication.
        
        Args:
            api_url: The base URL of the TimeBack OneRoster API. If not provided, uses the production URL.
            qti_api_url: The base URL of the QTI API. If not provided, uses the default production URL.
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
            environment: Parameter kept for backward compatibility, but ignored. Always uses production.
        """
        # Force production URL regardless of environment parameter
        self.api_url = (api_url or self.DEFAULT_PRODUCTION_URL).rstrip('/')
        self.qti_api_url = (qti_api_url or self.DEFAULT_QTI_URL).rstrip('/')
        
        # Log the URL being used
        logger.info(f"Initializing TimeBack client with production URL: {self.api_url}")
        
        # Initialize services with authentication
        self.rostering = RosteringService(self.api_url, client_id, client_secret)
        self.gradebook = GradebookService(self.api_url, client_id, client_secret)
        self.resources = ResourcesService(self.api_url, client_id, client_secret)
        self.qti = QTIService(self.api_url, self.qti_api_url, client_id, client_secret)
        self.powerpath = PowerPathService(self.api_url, client_id, client_secret) 