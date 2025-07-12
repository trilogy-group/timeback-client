"""API client for TimeBack assessment results endpoints.

This module provides a client for interacting with the TimeBack assessment results API,
which follows the OneRoster v1.2 specification.
"""

from typing import Dict, Any, Optional, List
from ..core.client import TimeBackService
from ..models.assessment_result import (
    AssessmentResult, 
    AssessmentResultsResponse,
    AssessmentMetadata,
    AssessmentType
)


class AssessmentResultsAPI(TimeBackService):
    """API client for assessment results endpoints."""

    def __init__(self, base_url: str, client_id: str, client_secret: str):
        """Initialize the assessment results API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
        """
        super().__init__(base_url, "gradebook", client_id=client_id, client_secret=client_secret)
    
    def get_assessment_results(
        self,
        student_id: Optional[str] = None,
        component_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        filter_expr: Optional[str] = None
    ) -> AssessmentResultsResponse:
        """Get assessment results with optional filtering.
        
        Args:
            student_id: Filter results by student ID
            component_id: Filter results by component ID
            limit: Maximum number of results to return
            offset: Number of results to skip for pagination
            filter_expr: Optional filter expression (e.g. "status='active'")
            
        Returns:
            AssessmentResultsResponse containing assessment results data
            
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
            
        response_data = self._make_request(endpoint, params=params)
        return AssessmentResultsResponse(**response_data)
    
    def get_assessment_result(self, result_id: str) -> AssessmentResult:
        """Get a single assessment result by ID.
        
        Args:
            result_id: The ID of the assessment result to retrieve
            
        Returns:
            The assessment result data
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (404 if not found)
        """
        endpoint = f"/assessmentResults/{result_id}"
        response_data = self._make_request(endpoint)
        # The API returns a single assessmentResult object
        if "assessmentResult" in response_data:
            return AssessmentResult(**response_data["assessmentResult"])
        return AssessmentResult(**response_data)
    
    def create_assessment_result(self, assessment_result: AssessmentResult) -> Dict[str, Any]:
        """Create a new assessment result.
        
        Args:
            assessment_result: The assessment result data to create
            
        Returns:
            Dictionary containing the created assessment result's sourcedId
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        endpoint = "/assessmentResults"
        data = assessment_result.to_create_dict()
        return self._make_request(endpoint, method="POST", json=data)
    
    def update_assessment_result(self, result_id: str, assessment_result: AssessmentResult) -> Dict[str, Any]:
        """Update an existing assessment result.
        
        Args:
            result_id: The ID of the assessment result to update
            assessment_result: The updated assessment result data
            
        Returns:
            Dictionary containing the update response
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        endpoint = f"/assessmentResults/{result_id}"
        data = assessment_result.to_update_dict()
        return self._make_request(endpoint, method="PUT", json=data)
    
    def delete_assessment_result(self, result_id: str) -> Dict[str, Any]:
        """Delete an assessment result (sets status to tobedeleted).
        
        Args:
            result_id: The ID of the assessment result to delete
            
        Returns:
            Dictionary containing the deletion response
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        endpoint = f"/assessmentResults/{result_id}"
        return self._make_request(endpoint, method="DELETE")
    
    def get_assessment_results_by_metadata(
        self,
        assessment_type: Optional[AssessmentType] = None,
        student_email: Optional[str] = None,
        subject: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> AssessmentResultsResponse:
        """Get assessment results filtered by metadata fields.
        
        Args:
            assessment_type: Filter by assessment type (MAP_GROWTH, MAP_SCREENING, etc.)
            student_email: Filter by student email in metadata
            subject: Filter by subject in metadata
            limit: Maximum number of results to return
            offset: Number of results to skip for pagination
            
        Returns:
            AssessmentResultsResponse containing filtered assessment results
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        # Build filter expression based on metadata fields
        filters = []
        
        if assessment_type:
            filters.append(f"metadata.assessmentType='{assessment_type.value}'")
        if student_email:
            filters.append(f"metadata.studentEmail='{student_email}'")
        if subject:
            filters.append(f"metadata.subject='{subject}'")
            
        filter_expr = " AND ".join(filters) if filters else None
        
        return self.get_assessment_results(
            limit=limit,
            offset=offset,
            filter_expr=filter_expr
        ) 