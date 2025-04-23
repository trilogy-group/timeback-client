"""Assessment Results API for the TimeBack API.

This module provides methods for retrieving assessment results
through the TimeBack API's gradebook service.
"""

from typing import Dict, Any, Optional, List, Union
from ..core.client import TimeBackService
import logging
import requests
import json

# Set up logger
logger = logging.getLogger(__name__)

class AssessmentResultsAPI(TimeBackService):
    """API client for assessment results endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the assessment results API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "gradebook", client_id, client_secret)
    
    def get_assessment_results(
        self,
        student_id: Optional[str] = None,
        component_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        filter_expr: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get assessment results with optional filtering.
        
        Args:
            student_id: Filter results by student ID
            component_id: Filter results by component ID
            limit: Maximum number of results to return
            offset: Number of results to skip for pagination
            filter_expr: Optional filter expression (e.g. "status='active'")
            
        Returns:
            Dictionary containing assessment results data
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        endpoint = "/assessmentResults"
        
        # Build query parameters
        params = {}
        if student_id is not None:
            params["student_id"] = student_id
        if component_id is not None:
            params["component_id"] = component_id
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if filter_expr is not None:
            params["filter"] = filter_expr
            
        return self._make_request(endpoint, params=params)
    
    def get_assessment_result(self, result_id: str) -> Dict[str, Any]:
        """Get a single assessment result by ID.
        
        Args:
            result_id: The ID of the assessment result to retrieve
            
        Returns:
            The assessment result data
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        endpoint = f"/assessmentResults/{result_id}"
        return self._make_request(endpoint) 