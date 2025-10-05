"""Assessment Item API for the TimeBack API.

This module provides methods for creating, retrieving, updating, and deleting
QTI assessment items through the TimeBack API.
"""

from typing import Dict, Any, Optional, List, Union
import uuid
from ..models.qti import QTIAssessmentItem
from ..core.client import TimeBackService
import logging
from urllib.parse import urljoin
import requests
import json

# Set up logger
logger = logging.getLogger(__name__)

class AssessmentItemsAPI(TimeBackService):
    """API client for assessment item endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the assessment items API client.
        
        Args:
            base_url: The base URL of the QTI API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        # QTI API has a different base URL than OneRoster
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
        
        Override the parent _make_request method to use the QTI URL.
        
        Args:
            endpoint: The API endpoint (e.g., "/assessment-items")
            method: The HTTP method to use
            data: The request payload for POST/PUT requests
            params: Query parameters for GET requests
            
        Returns:
            The JSON response from the API or an empty dict if no content
        """
        # Use QTI URL instead of standard OneRoster URL construction
        url = urljoin(self.qti_url + "/", endpoint.lstrip('/'))
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        logger.info("Making request to %s", url)
        logger.info("Method: %s", method)
        logger.info("Data: %s", data)
        logger.info("Params: %s", params)
        
        # Make the request directly instead of calling parent implementation
        # because the parent implementation would use the wrong URL construction
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
    
    def create_assessment_item(
        self, 
        assessment_item: Union[QTIAssessmentItem, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a new assessment item in the TimeBack API.
        
        Args:
            assessment_item: The assessment item to create. Can be a QTIAssessmentItem model
                            instance or a dictionary. Must have identifier set.
            
        Returns:
            The API response containing the created assessment item
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
            ValueError: If assessment_item does not have an identifier
        """
        # Convert dictionary to QTIAssessmentItem model if needed
        if isinstance(assessment_item, dict):
            assessment_item = QTIAssessmentItem(**assessment_item)
        
        # Ensure the assessment item has an identifier
        if not assessment_item.identifier:
            # Generate an identifier that follows XML NCName format (no hyphens, colons, spaces)
            assessment_item.identifier = f"item_{uuid.uuid4().hex}"
            logger.info(f"Generated identifier for assessment item: {assessment_item.identifier}")
        
        # Ensure the type on both the assessment item and interaction match
        if hasattr(assessment_item, 'interaction') and hasattr(assessment_item, 'type'):
            # Update interaction type if needed
            if assessment_item.interaction.type != assessment_item.type:
                logger.warning(
                    f"Interaction type '{assessment_item.interaction.type}' doesn't match "
                    f"assessment item type '{assessment_item.type}'. Updating interaction type."
                )
                assessment_item.interaction.type = assessment_item.type
        
        # Make the API request
        endpoint = "/assessment-items"
        data = assessment_item.model_dump(by_alias=True)
        
        # Log request details at debug level
        logger.debug(f"Creating assessment item with data: {json.dumps(data, indent=2)}")
        
        return self._make_request(endpoint, method="POST", data=data)
    
    def get_assessment_item(self, identifier: str) -> Dict[str, Any]:
        """Get an assessment item by identifier.
        
        Args:
            identifier: The identifier of the assessment item to retrieve.
                       This can be a full URL or just the item identifier.
            
        Returns:
            The assessment item data
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        # Handle the case where a full URL is provided
        if identifier.startswith('http'):
            # Extract the item ID from the URL
            parts = identifier.split('/')
            item_id = parts[-1]
            logger.info(f"Extracted item ID {item_id} from URL {identifier}")
            
            # If the URL is from the same QTI API, use the local endpoint
            if any(domain in identifier for domain in ['qti.alpha-1edtech.ai', 'alpha-qti-api']):
                endpoint = f"/assessment-items/{item_id}"
                return self._make_request(endpoint)
            else:
                # If it's a different domain, make a direct HTTP request
                logger.info(f"Making direct HTTP request to external URL: {identifier}")
                headers = {"Accept": "application/json"}
                response = requests.get(identifier, headers=headers)
                response.raise_for_status()
                return response.json()
        else:
            # Standard case - just the item ID
            endpoint = f"/assessment-items/{identifier}"
            return self._make_request(endpoint)
    
    def list_assessment_items(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None,
        filter_expr: Optional[str] = None
    ) -> Dict[str, Any]:
        """List assessment items with pagination, search, and optional filtering.
        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip
            search: Search query to filter items by title or identifier
            filter_expr: Optional filter expression (passed as 'filter' query param)
        Returns:
            Dictionary containing a list of assessment items and pagination info
        """
        endpoint = "/assessment-items"
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if search is not None:
            params["search"] = search
        if filter_expr is not None:
            params["filter"] = filter_expr
        return self._make_request(endpoint, params=params)
    
    def update_assessment_item(
        self, 
        identifier: str, 
        assessment_item: Union[QTIAssessmentItem, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update an assessment item.
        
        Args:
            identifier: The identifier of the assessment item to update
            assessment_item: The updated assessment item data
            
        Returns:
            The updated assessment item
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        endpoint = f"/assessment-items/{identifier}"
        
        # Convert to model if it's a dict
        if isinstance(assessment_item, dict):
            assessment_item = QTIAssessmentItem(**assessment_item)
        
        data = assessment_item.model_dump(by_alias=True)
        
        return self._make_request(endpoint, method="PUT", data=data)
    
    def delete_assessment_item(self, identifier: str) -> Dict[str, Any]:
        """Delete an assessment item.
        
        Args:
            identifier: The identifier of the assessment item to delete
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        endpoint = f"/assessment-items/{identifier}"
        return self._make_request(endpoint, method="DELETE") 

    def process_response(
        self,
        identifier: str,
        response: Optional[Union[str, Dict[str, Any]]] = None,
        response_identifier: Optional[str] = None,
        responses: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process a candidate response for an assessment item.
        
        This calls the QTI API endpoint:
        - v1 (single response): POST /assessment-items/{identifier}/process-response
        - v2 (multiple responses): POST /assessment-items/{identifier}/process-response?v2
        
        Args:
            identifier: The assessment item identifier
            response: Single response payload (raw string or structured object)
            response_identifier: ResponseDeclaration identifier for single-response (default: "RESPONSE")
            responses: Mapping for multi-input items when using v2, e.g. { responseIdentifier: value }
                See `tests/test_assessment_items.py` for usage of QTI models.
        
        Returns:
            Dict[str, Any]: The processing result from the QTI API
        
        Raises:
            requests.exceptions.HTTPError: If the API request fails
            ValueError: If neither 'responses' nor 'response' is provided
        
        Steps:
            1) Build endpoint; append "?v2" when using the multi-response 'responses' payload.
            2) Build request body: {identifier, response} for v1; {responses} for v2.
            3) POST to QTI API via _make_request.
        """
        # Validate inputs and decide versioned behavior
        if responses is not None:
            # v2 path: multiple responses, use query flag and 'responses' body
            endpoint = f"/assessment-items/{identifier}/process-response?v2"
            data: Dict[str, Any] = {"responses": responses}
        elif response is not None:
            # v1 path: single response, include response declaration identifier
            endpoint = f"/assessment-items/{identifier}/process-response"
            data = {
                # The body 'identifier' refers to the responseDeclaration identifier, not the item id
                "identifier": response_identifier or "RESPONSE",
                "response": response,
            }
        else:
            raise ValueError("Either 'responses' or 'response' must be provided")

        logger.info(
            "Processing response for assessment item %s via endpoint %s",
            identifier,
            endpoint,
        )
        return self._make_request(endpoint, method="POST", data=data)