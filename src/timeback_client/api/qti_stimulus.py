"""Stimulus API for the TimeBack API.

This module provides methods for creating, retrieving, updating, and deleting
QTI stimuli through the TimeBack API.
"""

from typing import Dict, Any, Optional, List, Union
import uuid
from ..models.qti import QTIStimulus  # You'll need to create this model
from ..core.client import TimeBackService
import logging
from urllib.parse import urljoin
import requests
import json

# Set up logger
logger = logging.getLogger(__name__)

class StimulusAPI(TimeBackService):
    """API client for stimulus endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the stimulus API client.
        
        Args:
            base_url: The base URL of the QTI API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        self.qti_url = base_url
        super().__init__(base_url, "qti", client_id=client_id, client_secret=client_secret)
    
    def _make_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make request to QTI API.
        
        Args:
            endpoint: The API endpoint (e.g., "/stimuli")
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
        
        # Add authorization if credentials are provided
        token = self._get_auth_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        logger.info("Making request to %s", url)
        logger.info("Method: %s", method)
        logger.info("Data: %s", data)
        logger.info("Params: %s", params)
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data if data else None,
            params=params
        )
        
        # Retry logic: if QTI staging returns 404, retry against production QTI endpoint
        if response.status_code == 404 and getattr(self, 'environment', '').lower() == 'staging':
            logger.warning("QTI staging endpoint returned 404, retrying against production QTI")
            from ..core.client import QTIService
            prod_url = urljoin(QTIService.DEFAULT_QTI_PRODUCTION_URL.rstrip('/') + '/', endpoint.lstrip('/'))
            logger.info("Retrying request to production QTI URL: %s", prod_url)
            response = requests.request(
                method=method,
                url=prod_url,
                headers=headers,
                json=data if data else None,
                params=params
            )
        
        if not response.ok:
            logger.error("Request failed with status %d", response.status_code)
            logger.error("Response body: %s", response.text)
            
        response.raise_for_status()
        
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
    
    def create_stimulus(
        self, 
        stimulus: Union[QTIStimulus, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a new stimulus in the TimeBack API.
        
        Args:
            stimulus: The stimulus to create. Can be a QTIStimulus model
                instance or a dictionary. Must have identifier set.
            
        Returns:
            The API response containing the created stimulus
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
            ValueError: If stimulus does not have required fields
        """
        # Convert dictionary to QTIStimulus model if needed
        if isinstance(stimulus, dict):
            stimulus = QTIStimulus(**stimulus)
        
        # Ensure the stimulus has an identifier
        if not stimulus.identifier:
            stimulus.identifier = f"stim_{uuid.uuid4().hex}"
            logger.info(f"Generated identifier for stimulus: {stimulus.identifier}")
        
        # Make the API request
        endpoint = "/stimuli"
        data = stimulus.model_dump(by_alias=True)
        
        logger.debug(f"Creating stimulus with data: {json.dumps(data, indent=2)}")
        
        return self._make_request(endpoint, method="POST", data=data)
    
    def get_stimulus(self, identifier: str) -> Dict[str, Any]:
        """Get a stimulus by identifier.
        
        Args:
            identifier: The identifier of the stimulus to retrieve. 
            This can be a full URL or just the stimulus identifier.
            
        Returns:
            The stimulus data
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        # Handle the case where a full URL is provided
        if identifier.startswith('http'):
            parts = identifier.split('/')
            stim_id = parts[-1]
            logger.info(f"Extracted stimulus ID {stim_id} from URL {identifier}")
            
            if any(domain in identifier for domain in ['qti.alpha-1edtech.ai', 'alpha-qti-api']):
                endpoint = f"/stimuli/{stim_id}"
                return self._make_request(endpoint)
            else:
                logger.info(f"Making direct HTTP request to external URL: {identifier}")
                headers = {"Accept": "application/json"}
                response = requests.get(identifier, headers=headers)
                response.raise_for_status()
                return response.json()
        else:
            endpoint = f"/stimuli/{identifier}"
            return self._make_request(endpoint)
    
    def list_stimuli(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None,
        language: Optional[str] = None,
        filter_expr: Optional[str] = None
    ) -> Dict[str, Any]:
        """List stimuli with pagination, search, language, and optional filtering.
        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip
            search: Search query to filter items by title or identifier
            language: Filter by language code (e.g. 'en')
            filter_expr: Optional filter expression (passed as 'filter' query param)
        Returns:
            Dictionary containing a list of stimuli and pagination info
        """
        endpoint = "/stimuli"
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if search is not None:
            params["search"] = search
        if language is not None:
            params["language"] = language
        if filter_expr is not None:
            params["filter"] = filter_expr
        return self._make_request(endpoint, params=params)
    
    def update_stimulus(
        self, 
        identifier: str, 
        stimulus: Union[QTIStimulus, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update a stimulus.
        
        Args:
            identifier: The identifier of the stimulus to update
            stimulus: The updated stimulus data
            
        Returns:
            The updated stimulus
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        endpoint = f"/stimuli/{identifier}"
        
        # Convert to model if it's a dict
        if isinstance(stimulus, dict):
            stimulus = QTIStimulus(**stimulus)
        
        data = stimulus.model_dump(by_alias=True)
        
        return self._make_request(endpoint, method="PUT", data=data)
    
    def delete_stimulus(self, identifier: str) -> Dict[str, Any]:
        """Delete a stimulus.
        
        Args:
            identifier: The identifier of the stimulus to delete
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        endpoint = f"/stimuli/{identifier}"
        return self._make_request(endpoint, method="DELETE") 