"""Student-related API endpoints for the TimeBack API.

This module provides methods for retrieving and managing students
in the TimeBack API following the OneRoster 1.2 specification.

Students are users with the 'student' role and have specific endpoints
in the OneRoster API for operations like listing students and getting 
their classes.
"""

from typing import Dict, Any, Optional, List, Union
import logging
from ..core.client import TimeBackService

# Set up logger
logger = logging.getLogger(__name__)

class StudentsAPI(TimeBackService):
    """API client for student-related endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the students API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "rostering", client_id=client_id, client_secret=client_secret)
    
    def list_students(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None,
        fields: Optional[List[str]] = None,
        **extra_params
    ) -> Dict[str, Any]:
        """List students using the OneRoster v1.2 students endpoint.
        Supports arbitrary extra query params (e.g. search='Amanda').
        This method uses the dedicated students endpoint which automatically filters
        for users with the student role. It supports all standard OneRoster filtering
        and sorting capabilities including dot notation for nested fields.
        Args:
            limit: Maximum number of students to return
            offset: Number of students to skip
            sort: Field to sort by (e.g. 'familyName' or 'metadata.grade')
            order_by: Sort order ('asc' or 'desc')
            filter_expr: Filter expression (e.g. "status='active'")
            fields: Fields to return (e.g. ['sourcedId', 'givenName'])
            **extra_params: Any additional query params (e.g. search='Amanda')
        Returns:
            Dictionary containing students and pagination information
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
        # Merge in any extra query params (e.g. search)
        params.update(extra_params)
        return self._make_request("/students", params=params)
    
    def get_student(self, student_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific student by ID.
        
        Args:
            student_id: The unique identifier of the student
            fields: Optional list of fields to return (e.g. ['sourcedId', 'givenName'])
            
        Returns:
            The student data from the API
            
        Raises:
            requests.exceptions.HTTPError: If student not found (404) or other API error
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
            
        return self._make_request(
            endpoint=f"/students/{student_id}",
            params=params
        )
    
    def get_classes_for_student(
        self, 
        student_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get all classes that a student is enrolled in.
        
        This method follows the OneRoster v1.2 specification for accessing a student's
        classes through the /students/{id}/classes endpoint.
        
        Args:
            student_id: The unique identifier of the student
            limit: Maximum number of classes to return
            offset: Number of classes to skip
            sort: Field to sort by (e.g. 'title')
            order_by: Sort order ('asc' or 'desc')
            filter_expr: Filter expression (e.g. "status='active'")
            fields: Fields to return (e.g. ['sourcedId', 'title'])
            
        Returns:
            Dictionary containing classes for the student:
            {
                "classes": [
                    {
                        "sourcedId": "class-123",
                        "title": "Algebra I",
                        ...
                    },
                    ...
                ]
            }
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
            
        logger.info(f"Fetching classes for student {student_id}")
        return self._make_request(
            endpoint=f"/students/{student_id}/classes",
            params=params
        ) 