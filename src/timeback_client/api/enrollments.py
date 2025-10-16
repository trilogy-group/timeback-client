"""Enrollment-related API endpoints for the TimeBack API.

This module provides methods for retrieving and managing enrollments
in the TimeBack API following the OneRoster 1.2 specification.

Enrollments link users (students/teachers) to classes with specific roles
and timeframes, allowing for tracking of class participation.
"""

from typing import Dict, Any, Optional, List, Union
import logging
import time
from ..core.client import TimeBackService

# Set up logger
logger = logging.getLogger(__name__)

class EnrollmentsAPI(TimeBackService):
    """API client for enrollment-related endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the enrollments API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "rostering", client_id=client_id, client_secret=client_secret)
    
    def create_enrollment(self, enrollment: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new enrollment in the TimeBack API.
        
        Args:
            enrollment: The enrollment to create as a dictionary.
                Required fields per OneRoster 1.2 spec:
                - role: The role of the user in the class (student, teacher, etc.)
                - user: Object with sourcedId of the user
                - class: Object with sourcedId of the class
            
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
            ValueError: If enrollment does not have required fields
            
        Examples:
            # Create a student enrollment
            api.create_enrollment({
                "enrollment": {
                    "role": "student",
                    "primary": True,
                    "beginDate": "2023-09-01",
                    "endDate": "2024-06-15",
                    "user": {
                        "sourcedId": "user-123"
                    },
                    "class": {
                        "sourcedId": "class-456"
                    }
                }
            })
        """
        # Check if input is already wrapped in 'enrollment'
        if 'enrollment' in enrollment:
            enrollment_dict = enrollment['enrollment']
            request_data = enrollment  # Use as-is
        else:
            enrollment_dict = enrollment
            request_data = {'enrollment': enrollment}
                
        # Check required fields
        if not enrollment_dict.get('role'):
            raise ValueError("role is required when creating an enrollment")
            
        if not enrollment_dict.get('user') or not enrollment_dict.get('user').get('sourcedId'):
            raise ValueError("user.sourcedId is required when creating an enrollment")
            
        if not enrollment_dict.get('class') or not enrollment_dict.get('class').get('sourcedId'):
            raise ValueError("class.sourcedId is required when creating an enrollment")
            
        # Log the creation attempt
        logger.info(f"Creating enrollment for user {enrollment_dict.get('user', {}).get('sourcedId')} in class {enrollment_dict.get('class', {}).get('sourcedId')}")
            
        # Send request - response will contain sourcedIdPairs
        return self._make_request(
            endpoint="/enrollments",
            method="POST",
            data=request_data
        )
    
    def get_enrollment(self, enrollment_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific enrollment by ID.
        
        Args:
            enrollment_id: The unique identifier of the enrollment
            fields: Optional list of fields to return (e.g. ['sourcedId', 'role'])
            
        Returns:
            The enrollment data from the API
            
        Raises:
            requests.exceptions.HTTPError: If enrollment not found (404) or other API error
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
            
        return self._make_request(
            endpoint=f"/enrollments/{enrollment_id}",
            params=params
        )
    
    def update_enrollment(self, enrollment_id: str, enrollment: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing enrollment in the TimeBack API.
        
        Args:
            enrollment_id: The ID of the enrollment to update
            enrollment: The updated enrollment data as a dictionary
            
        Returns:
            The updated enrollment data from the API
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        # If enrollment is a dict with 'enrollment' key, extract the inner dict
        if 'enrollment' in enrollment:
            enrollment_dict = enrollment['enrollment']
        else:
            enrollment_dict = enrollment
                
        # Ensure sourcedId matches the URL parameter
        if 'sourcedId' in enrollment_dict and enrollment_dict['sourcedId'] != enrollment_id:
            logger.warning(f"Enrollment sourcedId ({enrollment_dict['sourcedId']}) doesn't match URL parameter ({enrollment_id})")
            logger.warning(f"Using URL parameter as the definitive ID")
            enrollment_dict['sourcedId'] = enrollment_id
            
        # Prepare request data
        request_data = {'enrollment': enrollment_dict}
            
        # Send request
        return self._make_request(
            endpoint=f"/enrollments/{enrollment_id}",
            method="PUT",
            data=request_data
        )
    
    def delete_enrollment(self, enrollment_id: str) -> Dict[str, Any]:
        """Delete an enrollment from the TimeBack API.
        
        Note: This typically sets the status to 'tobedeleted' rather than performing a hard delete.
        
        Args:
            enrollment_id: The ID of the enrollment to delete
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        return self._make_request(
            endpoint=f"/enrollments/{enrollment_id}",
            method="DELETE"
        )
    
    def list_enrollments(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List enrollments with filtering and pagination.
        
        Args:
            limit: Maximum number of enrollments to return
            offset: Number of enrollments to skip
            sort: Field to sort by (e.g. 'beginDate')
            order_by: Sort order ('asc' or 'desc')
            filter_expr: Filter expression (e.g. "role='student'")
            fields: Fields to return (e.g. ['sourcedId', 'role', 'user'])
            
        Returns:
            Dictionary containing enrollments and pagination information
            
        Example:
            # Get all active student enrollments
            api.list_enrollments(
                filter_expr="status='active' AND role='student'",
                sort='beginDate',
                order_by='desc',
                fields=['sourcedId', 'role', 'user', 'class']
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
            
        # Add cache-busting parameter
        params['_'] = int(time.time())
            
        return self._make_request("/enrollments", params=params)
    
    def get_enrollments_for_student(
        self,
        student_id: str,
        filter_expr: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get all enrollments for a specific student, with optional filtering.
        Args:
            student_id: The unique identifier of the student
            filter_expr: Optional filter expression (e.g. "status='active'")
            limit, offset, sort, order_by, fields: Standard listing params
        Returns:
            Dictionary containing the student's enrollments
        """
        # Always filter by user.sourcedId
        base_filter = f"user.sourcedId='{student_id}'"
        combined_filter = base_filter
        if filter_expr:
            combined_filter = f"{base_filter} AND {filter_expr}"
        return self.list_enrollments(
            filter_expr=combined_filter,
            limit=limit,
            offset=offset,
            sort=sort,
            order_by=order_by,
            fields=fields
        )

    def get_enrollments_for_class(
        self,
        class_id: str,
        filter_expr: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get all enrollments for a specific class, with optional filtering.
        Args:
            class_id: The unique identifier of the class
            filter_expr: Optional filter expression (e.g. "status='active' AND role='student'")
            limit, offset, sort, order_by, fields: Standard listing params
        Returns:
            Dictionary containing the class's enrollments
        """
        # Always filter by class.sourcedId
        base_filter = f"class.sourcedId='{class_id}'"
        combined_filter = base_filter
        if filter_expr:
            combined_filter = f"{base_filter} AND {filter_expr}"
        return self.list_enrollments(
            filter_expr=combined_filter,
            limit=limit,
            offset=offset,
            sort=sort,
            order_by=order_by,
            fields=fields
        )

    def reset_progress(self, user_id: str, course_id: str) -> Dict[str, Any]:
        """Reset a student's progress in a course by deleting all assessment results.

        This calls the edubridge API endpoint to delete all progress data
        for a specific student in a specific course.

        Args:
            user_id: The student's user ID (sourcedId)
            course_id: The course ID (sourcedId)

        Returns:
            Dictionary containing the API response

        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        logger.info(f"Resetting progress for user {user_id} in course {course_id}")

        # Use edubridge service instead of rostering
        # Temporarily override api_path for this request
        original_api_path = self.api_path
        self.api_path = "/edubridge"

        try:
            result = self._make_request(
                endpoint=f"/enrollments/resetProgress/{user_id}/{course_id}",
                method="DELETE"
            )
            return result
        finally:
            # Restore original api_path
            self.api_path = original_api_path 