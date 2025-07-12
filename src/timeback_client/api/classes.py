"""Class-related API endpoints for the TimeBack API.

This module provides methods for retrieving and managing classes
in the TimeBack API following the OneRoster 1.2 specification.

Classes represent instances of courses that students can enroll in for a specific
academic term/session.
"""

from typing import Dict, Any, Optional, List, Union
import logging
from ..core.client import TimeBackService

# Set up logger
logger = logging.getLogger(__name__)

class ClassesAPI(TimeBackService):
    """API client for class-related endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the classes API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "rostering", client_id=client_id, client_secret=client_secret)
    
    def create_class(self, class_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new class in the TimeBack API.
        
        Args:
            class_data: The class to create as a dictionary.
                Required fields per OneRoster 1.2 spec:
                - title: The name of the class
                - course: Object with sourcedId of the course
                - org: Object with sourcedId of the organization
                - terms: Array of objects with sourcedId of academic terms
            
        Returns:
            The API response containing sourcedIdPairs:
            {
                "sourcedIdPairs": {
                    "suppliedSourcedId": str,  # The ID provided in the request
                    "allocatedSourcedId": str  # The ID assigned by the server
                }
            }
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
            ValueError: If class_data does not have required fields
            
        Examples:
            # Create a math class for a specific term
            api.create_class({
                "class": {
                    "title": "Algebra I - Period 3",
                    "classCode": "ALG1-P3",
                    "classType": "scheduled",
                    "location": "Room 202",
                    "grades": ["9"],
                    "subjects": ["Mathematics"],
                    "course": {
                        "sourcedId": "course-123"
                    },
                    "org": {
                        "sourcedId": "school-456"
                    },
                    "terms": [
                        {
                            "sourcedId": "term-789"
                        }
                    ]
                }
            })
        """
        # Check if input is already wrapped in 'class'
        if 'class' in class_data:
            class_dict = class_data['class']
            request_data = class_data  # Use as-is
        else:
            class_dict = class_data
            request_data = {'class': class_data}
                
        # Check required fields
        if not class_dict.get('title'):
            raise ValueError("title is required when creating a class")
            
        if not class_dict.get('course') or not class_dict.get('course').get('sourcedId'):
            raise ValueError("course.sourcedId is required when creating a class")
            
        if not class_dict.get('org') or not class_dict.get('org').get('sourcedId'):
            raise ValueError("org.sourcedId is required when creating a class")
            
        if not class_dict.get('terms') or not isinstance(class_dict.get('terms'), list) or len(class_dict.get('terms')) == 0:
            raise ValueError("at least one term with sourcedId is required when creating a class")
            
        # Log the creation attempt
        logger.info(f"Creating class '{class_dict.get('title')}' for course {class_dict.get('course', {}).get('sourcedId')}")
            
        # Send request - response will contain sourcedIdPairs
        return self._make_request(
            endpoint="/classes",
            method="POST",
            data=request_data
        )
    
    def get_class(self, class_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific class by ID.
        
        Args:
            class_id: The unique identifier of the class
            fields: Optional list of fields to return (e.g. ['sourcedId', 'title'])
            
        Returns:
            The class data from the API
            
        Raises:
            requests.exceptions.HTTPError: If class not found (404) or other API error
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
            
        return self._make_request(
            endpoint=f"/classes/{class_id}",
            params=params
        )
    
    def update_class(self, class_id: str, class_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing class in the TimeBack API.
        
        Args:
            class_id: The ID of the class to update
            class_data: The updated class data as a dictionary
            
        Returns:
            The updated class data from the API
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        # If class_data is a dict with 'class' key, extract the inner dict
        if 'class' in class_data:
            class_dict = class_data['class']
        else:
            class_dict = class_data
                
        # Ensure sourcedId matches the URL parameter
        if 'sourcedId' in class_dict and class_dict['sourcedId'] != class_id:
            logger.warning(f"Class sourcedId ({class_dict['sourcedId']}) doesn't match URL parameter ({class_id})")
            logger.warning(f"Using URL parameter as the definitive ID")
            class_dict['sourcedId'] = class_id
            
        # Prepare request data
        request_data = {'class': class_dict}
            
        # Send request
        return self._make_request(
            endpoint=f"/classes/{class_id}",
            method="PUT",
            data=request_data
        )
    
    def delete_class(self, class_id: str) -> Dict[str, Any]:
        """Delete a class from the TimeBack API.
        
        Note: This typically sets the status to 'tobedeleted' rather than performing a hard delete.
        
        Args:
            class_id: The ID of the class to delete
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        return self._make_request(
            endpoint=f"/classes/{class_id}",
            method="DELETE"
        )
    
    def list_classes(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List classes with filtering and pagination.
        
        Args:
            limit: Maximum number of classes to return
            offset: Number of classes to skip
            sort: Field to sort by (e.g. 'title')
            order_by: Sort order ('asc' or 'desc')
            filter_expr: Filter expression (e.g. "org.sourcedId='school-123'")
            fields: Fields to return (e.g. ['sourcedId', 'title', 'course'])
            
        Returns:
            Dictionary containing classes and pagination information
            
        Example:
            # Get all active math classes for a specific school
            api.list_classes(
                filter_expr="status='active' AND subjects='Mathematics' AND org.sourcedId='school-123'",
                sort='title',
                order_by='asc',
                fields=['sourcedId', 'title', 'course', 'terms']
            )
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
            
        return self._make_request("/classes", params=params)
    
    def get_classes_for_course(
        self,
        course_id: str,
        filter_expr: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get all classes for a specific course, with optional filtering.
        Args:
            course_id: The unique identifier of the course
            filter_expr: Optional filter expression (e.g. "status='active'")
            limit, offset, sort, order_by, fields: Standard listing params
        Returns:
            Dictionary containing the course's classes
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
        # Always filter by course.sourcedId
        course_filter = f"course.sourcedId='{course_id}'"
        if filter_expr:
            params['filter'] = f"{course_filter} AND {filter_expr}"
        else:
            params['filter'] = course_filter
        return self._make_request(f"/courses/{course_id}/classes", params=params)
    
    def get_classes_for_student(
        self,
        student_id: str,
        filter_expr: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get all classes for a specific student using the OneRoster v1.2 endpoint, with optional filtering.
        Args:
            student_id: The unique identifier of the student
            filter_expr: Optional filter expression (e.g. "status='active'")
            limit, offset, sort, order_by, fields: Standard listing params
        Returns:
            Dictionary containing the student's classes
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
        return self._make_request(
            endpoint=f"/students/{student_id}/classes",
            params=params
        )
    
    def get_classes_for_teacher(
        self,
        teacher_id: str,
        filter_expr: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get all classes taught by a specific teacher, with optional filtering.
        Args:
            teacher_id: The unique identifier of the teacher
            filter_expr: Optional filter expression (e.g. "status='active'")
            limit, offset, sort, order_by, fields: Standard listing params
        Returns:
            Dictionary containing the teacher's classes
        """
        # First get teacher's enrollments
        enroll_filter = f"user.sourcedId='{teacher_id}' AND role='teacher'"
        enrollments = self._make_request("/enrollments", params={"filter": enroll_filter})
        # Extract class IDs from enrollments
        class_ids = [enrollment['class']['sourcedId'] for enrollment in enrollments.get('enrollments', []) if 'class' in enrollment and 'sourcedId' in enrollment['class']]
        if not class_ids:
            return {'classes': []}
        # Build filter for classes
        class_id_filter = " OR ".join([f"sourcedId='{class_id}'" for class_id in class_ids])
        combined_filter = class_id_filter
        if filter_expr:
            combined_filter = f"({class_id_filter}) AND {filter_expr}"
        return self.list_classes(
            filter_expr=combined_filter,
            limit=limit,
            offset=offset,
            sort=sort,
            order_by=order_by,
            fields=fields
        )
    
    def get_students_for_class(
        self,
        class_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get all students for a specific class using the OneRoster v1.2 endpoint, with optional filtering.
        Args:
            class_id: The unique identifier of the class
            filter_expr: Optional filter expression (e.g. "status='active'")
            limit, offset, sort, order_by, fields: Standard listing params
        Returns:
            Dictionary containing the class's students
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
            
        return self._make_request(
            endpoint=f"/classes/{class_id}/students",
            params=params
        ) 