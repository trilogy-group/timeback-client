"""Assessment Test API for the TimeBack API.

This module provides methods for creating, retrieving, updating, and managing
QTI assessment tests through the TimeBack API, following the 1EdTech ATI API specification.
"""

from typing import Dict, Any, Optional, List, Union
import uuid
from ..models.qti import QTIAssessmentTest, QTITestPart, QTISection, QTIItemRef
from ..core.client import TimeBackService
import logging
from urllib.parse import urljoin
import requests
import json

# Set up logger
logger = logging.getLogger(__name__)

class AssessmentTestAPI(TimeBackService):
    """API client for assessment test endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the assessment tests API client.
        
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
            endpoint: The API endpoint (e.g., "/assessment-tests")
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
    
    # ===================================================
    # Assessment Test Endpoints
    # ===================================================
    
    def create_assessment_test(
        self, 
        assessment_test: Union[QTIAssessmentTest, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a new assessment test in the TimeBack API.
        
        Args:
            assessment_test: The assessment test to create. Can be a QTIAssessmentTest model
                           instance or a dictionary. Must have identifier set.
            
        Returns:
            The API response containing the created assessment test
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
            ValueError: If assessment_test does not have an identifier
        """
        # Convert dictionary to QTIAssessmentTest model if needed
        if isinstance(assessment_test, dict):
            assessment_test = QTIAssessmentTest(**assessment_test)
        
        # Ensure the assessment test has an identifier
        if not assessment_test.identifier:
            # Generate an identifier that follows XML NCName format
            assessment_test.identifier = f"test_{uuid.uuid4().hex}"
            logger.info(f"Generated identifier for assessment test: {assessment_test.identifier}")
        
        # Make the API request
        endpoint = "/assessment-tests"
        data = assessment_test.model_dump(by_alias=True)
        
        # Log request details at debug level
        logger.debug(f"Creating assessment test with data: {json.dumps(data, indent=2)}")
        
        return self._make_request(endpoint, method="POST", data=data)
    
    def get_assessment_test(self, identifier: str) -> Dict[str, Any]:
        """Get an assessment test by identifier.
        
        Args:
            identifier: The identifier of the assessment test to retrieve
            
        Returns:
            The assessment test data
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        endpoint = f"/assessment-tests/{identifier}"
        return self._make_request(endpoint)
    
    def list_assessment_tests(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List assessment tests with pagination and search.
        
        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip
            search: Search query to filter items by title or identifier
            
        Returns:
            Dictionary containing a list of assessment tests and pagination info
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        endpoint = "/assessment-tests"
        
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if search is not None:
            params["search"] = search
        
        return self._make_request(endpoint, params=params)
    
    def update_assessment_test(
        self, 
        identifier: str, 
        assessment_test: Union[QTIAssessmentTest, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update an assessment test.
        
        Args:
            identifier: The identifier of the assessment test to update
            assessment_test: The updated assessment test data
            
        Returns:
            The updated assessment test
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        endpoint = f"/assessment-tests/{identifier}"
        
        # Convert to model if it's a dict
        if isinstance(assessment_test, dict):
            assessment_test = QTIAssessmentTest(**assessment_test)
        
        data = assessment_test.model_dump(by_alias=True)
        
        return self._make_request(endpoint, method="PUT", data=data)
    
    def delete_assessment_test(self, identifier: str) -> Dict[str, Any]:
        """Delete an assessment test.
        
        Args:
            identifier: The identifier of the assessment test to delete
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        endpoint = f"/assessment-tests/{identifier}"
        return self._make_request(endpoint, method="DELETE")
    
    # ===================================================
    # Test Part Endpoints
    # ===================================================
    
    def create_test_part(
        self,
        assessment_test_id: str,
        test_part: Union[QTITestPart, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a test part within an assessment test.
        
        Args:
            assessment_test_id: The identifier of the assessment test
            test_part: The test part to create
            
        Returns:
            The created test part
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        # Convert to model if it's a dict
        if isinstance(test_part, dict):
            test_part = QTITestPart(**test_part)
            
        endpoint = f"/assessment-tests/{assessment_test_id}/test-parts"
        data = test_part.model_dump(by_alias=True)
        
        return self._make_request(endpoint, method="POST", data=data)
    
    def get_test_part(
        self,
        assessment_test_id: str,
        test_part_id: str
    ) -> Dict[str, Any]:
        """Get a specific test part.
        
        Args:
            assessment_test_id: The identifier of the assessment test
            test_part_id: The identifier of the test part
            
        Returns:
            The test part data
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        endpoint = f"/assessment-tests/{assessment_test_id}/test-parts/{test_part_id}"
        return self._make_request(endpoint)
    
    def list_test_parts(
        self,
        assessment_test_id: str,
        navigation_mode: Optional[str] = None,
        submission_mode: Optional[str] = None,
        query: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None
    ) -> Dict[str, Any]:
        """List test parts in an assessment test.
        
        Args:
            assessment_test_id: The identifier of the assessment test
            navigation_mode: Filter by navigation mode ('linear' or 'nonlinear')
            submission_mode: Filter by submission mode ('individual' or 'simultaneous')
            query: Text search on identifier
            page: Page number for pagination
            limit: Number of items per page
            sort: Field to sort by
            order: Sort order ('asc' or 'desc')
            
        Returns:
            Dictionary containing test parts and pagination information
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        endpoint = f"/assessment-tests/{assessment_test_id}/test-parts"
        
        params = {}
        if navigation_mode:
            params["navigationMode"] = navigation_mode
        if submission_mode:
            params["submissionMode"] = submission_mode
        if query:
            params["query"] = query
        if page:
            params["page"] = page
        if limit:
            params["limit"] = limit
        if sort:
            params["sort"] = sort
        if order:
            params["order"] = order
            
        return self._make_request(endpoint, params=params)
    
    def update_test_part(
        self,
        assessment_test_id: str,
        test_part_id: str,
        test_part: Union[QTITestPart, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update a test part.
        
        Args:
            assessment_test_id: The identifier of the assessment test
            test_part_id: The identifier of the test part to update
            test_part: The updated test part data
            
        Returns:
            The updated test part
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        # Convert to model if it's a dict
        if isinstance(test_part, dict):
            test_part = QTITestPart(**test_part)
            
        endpoint = f"/assessment-tests/{assessment_test_id}/test-parts/{test_part_id}"
        data = test_part.model_dump(by_alias=True)
        
        return self._make_request(endpoint, method="PUT", data=data)
    
    def delete_test_part(
        self,
        assessment_test_id: str,
        test_part_id: str
    ) -> Dict[str, Any]:
        """Delete a test part.
        
        Args:
            assessment_test_id: The identifier of the assessment test
            test_part_id: The identifier of the test part to delete
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        endpoint = f"/assessment-tests/{assessment_test_id}/test-parts/{test_part_id}"
        return self._make_request(endpoint, method="DELETE")
    
    # ===================================================
    # Section Endpoints
    # ===================================================
    
    def create_section(
        self,
        assessment_test_id: str,
        section: Union[QTISection, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a section within an assessment test.
        
        Args:
            assessment_test_id: The identifier of the assessment test
            section: The section to create
            
        Returns:
            The created section
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        # Convert to model if it's a dict
        if isinstance(section, dict):
            section = QTISection(**section)
            
        endpoint = f"/assessment-tests/{assessment_test_id}/sections"
        data = section.model_dump(by_alias=True)
        
        return self._make_request(endpoint, method="POST", data=data)
    
    def get_section(
        self,
        assessment_test_id: str,
        section_id: str
    ) -> Dict[str, Any]:
        """Get a specific section.
        
        Args:
            assessment_test_id: The identifier of the assessment test
            section_id: The identifier of the section
            
        Returns:
            The section data
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        endpoint = f"/assessment-tests/{assessment_test_id}/sections/{section_id}"
        return self._make_request(endpoint)
    
    def update_section(
        self,
        assessment_test_id: str,
        section_id: str,
        section: Union[QTISection, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update a section.
        
        Args:
            assessment_test_id: The identifier of the assessment test
            section_id: The identifier of the section to update
            section: The updated section data
            
        Returns:
            The updated section
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        # Convert to model if it's a dict
        if isinstance(section, dict):
            section = QTISection(**section)
            
        endpoint = f"/assessment-tests/{assessment_test_id}/sections/{section_id}"
        data = section.model_dump(by_alias=True)
        
        return self._make_request(endpoint, method="PUT", data=data)
    
    def delete_section(
        self,
        assessment_test_id: str,
        section_id: str
    ) -> Dict[str, Any]:
        """Delete a section.
        
        Args:
            assessment_test_id: The identifier of the assessment test
            section_id: The identifier of the section to delete
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        endpoint = f"/assessment-tests/{assessment_test_id}/sections/{section_id}"
        return self._make_request(endpoint, method="DELETE")
    
    # ===================================================
    # Item Reference Endpoints
    # ===================================================
    
    def add_item_to_section(
        self,
        assessment_test_id: str,
        test_part_id: str,
        section_id: str,
        item_id: str
    ) -> Dict[str, Any]:
        """Add an assessment item to a section.
        
        Args:
            assessment_test_id: The identifier of the assessment test
            test_part_id: The identifier of the test part
            section_id: The identifier of the section
            item_id: The identifier of the assessment item to add
            
        Returns:
            Success message with added item information
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        endpoint = f"/assessment-tests/{assessment_test_id}/test-parts/{test_part_id}/sections/{section_id}/items"
        data = {"itemIdentifier": item_id}
        
        return self._make_request(endpoint, method="POST", data=data)
    
    def remove_item_from_section(
        self,
        assessment_test_id: str,
        test_part_id: str,
        section_id: str,
        item_id: str
    ) -> Dict[str, Any]:
        """Remove an assessment item from a section.
        
        Args:
            assessment_test_id: The identifier of the assessment test
            test_part_id: The identifier of the test part
            section_id: The identifier of the section
            item_id: The identifier of the assessment item to remove
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        endpoint = f"/assessment-tests/{assessment_test_id}/test-parts/{test_part_id}/sections/{section_id}/items/{item_id}"
        return self._make_request(endpoint, method="DELETE")