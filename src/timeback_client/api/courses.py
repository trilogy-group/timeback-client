"""Course-related API endpoints for the TimeBack API.

This module provides methods for retrieving and managing courses
in the TimeBack API following the OneRoster 1.2 specification.
"""

from typing import Dict, Any, Optional, List, Union
import logging
from ..models.course import Course
from ..core.client import TimeBackService
import requests

# Set up logger
logger = logging.getLogger(__name__)

class CoursesAPI(TimeBackService):
    """API client for course-related endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the courses API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "rostering", client_id=client_id, client_secret=client_secret)
    
    def create_course(self, course: Union[Course, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new course in the TimeBack API.
        
        Args:
            course: The course to create. Can be a Course model instance or a dictionary.
                   Required fields per OneRoster 1.2 spec:
                   - title: The title of the course
                   - courseCode: The code identifying this course
                   - status: 'active' or 'tobedeleted' (defaults to 'active')
                   - org: Object with sourcedId of the organization
            
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
            ValueError: If course does not have required fields
            
        Examples:
            # Using keyword arguments (simplest)
            api.create_course({
                "course": {
                    "title": "Introduction to Python",
                    "courseCode": "CS101",
                    "status": "active",
                    "org": {"sourcedId": "org-123"}
                }
            })
            
            # Using the Course model directly
            course = Course.create(
                title="Introduction to Python",
                courseCode="CS101",
                grades=["9", "10"],
                subjects=["Computer Science"],
                org={"sourcedId": "org-123"}
            )
            api.create_course(course)
        """
        # If input is a dictionary, check if it's already wrapped in 'course'
        if isinstance(course, dict):
            if 'course' in course:
                # Already wrapped correctly
                course_dict = course['course']
                request_data = course  # Use as-is
            else:
                # Need to wrap it
                course_dict = course
                request_data = {'course': course}
                
            # Check required fields
            if not course_dict.get('title'):
                raise ValueError("title is required when creating a course")
                
            if not course_dict.get('courseCode'):
                raise ValueError("courseCode is required when creating a course")
                
            # Ensure required fields per OneRoster 1.2 spec
            if 'status' not in course_dict:
                course_dict['status'] = 'active'
                
            if 'org' not in course_dict:
                raise ValueError("org with sourcedId is required when creating a course")
                
        # If it's a Course model, validate and convert to dict
        else:
            if not course.title:
                raise ValueError("title is required when creating a course")
                
            if not course.courseCode:
                raise ValueError("courseCode is required when creating a course")
                
            if not course.org or not course.org.get('sourcedId'):
                raise ValueError("org with sourcedId is required when creating a course")
            
            # Convert to dictionary and wrap in 'course'
            request_data = {'course': course.to_dict()}
            
        # Log the sourcedId
        if isinstance(course, Course):
            logger.info(f"Creating course with sourcedId: {course.sourcedId}")
        else:
            logger.info(f"Creating course with data: {course_dict}")
            
        # Send request - response will contain sourcedIdPairs
        return self._make_request(
            endpoint="/courses",
            method="POST",
            data=request_data
        )
    
    def get_course(self, course_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific course by ID.
        
        Args:
            course_id: The unique identifier of the course
            fields: Optional list of fields to return (e.g. ['sourcedId', 'title'])
            
        Returns:
            The course data from the API
            
        Raises:
            requests.exceptions.HTTPError: If course not found (404) or other API error
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
            
        return self._make_request(
            endpoint=f"/courses/{course_id}",
            params=params
        )
    
    def update_course(self, course_id: str, course: Union[Course, Dict[str, Any]]) -> Dict[str, Any]:
        """Update an existing course in the TimeBack API.
        
        Args:
            course_id: The ID of the course to update
            course: The updated course data. Can be a Course model instance or a dictionary.
            
        Returns:
            The updated course data from the API
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        # If course is a dictionary with 'course' key, extract the inner dict
        if isinstance(course, dict):
            if 'course' in course:
                request_data = course  # Already wrapped correctly
                course_dict = course['course']
            else:
                # Need to wrap it
                course_dict = course
                request_data = {'course': course_dict}

            logger.info(f"Updating course {course_id} with data: {course_dict}")
            return self._make_request(
                endpoint=f"/courses/{course_id}",
                method="PUT",
                data=request_data
            )
        
        # If it's a Course model instance, convert to dictionary
        else:
            # Ensure sourcedId matches the URL parameter
            if course.sourcedId != course_id:
                logger.warning(f"Course sourcedId ({course.sourcedId}) doesn't match URL parameter ({course_id})")
                logger.warning(f"Using URL parameter as the definitive ID")
                course.sourcedId = course_id
                
            # Convert to dictionary and send request
            request_data = course.to_dict()  # This will wrap in 'course' object
            logger.info(f"Updating course {course_id} with data: {request_data}")
            return self._make_request(
                endpoint=f"/courses/{course_id}",
                method="PUT",
                data=request_data
            )
    
    def delete_course(self, course_id: str) -> Dict[str, Any]:
        """Delete a course from the TimeBack API.
        
        Args:
            course_id: The ID of the course to delete
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        return self._make_request(
            endpoint=f"/courses/{course_id}",
            method="DELETE"
        )
    
    def list_courses(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None,
        fields: Optional[List[str]] = None,
        **extra_params
    ) -> Dict[str, Any]:
        """List courses with filtering and pagination.
        Supports arbitrary extra query params (e.g. search='Math').
        
        Args:
            limit: Maximum number of courses to return
            offset: Number of courses to skip
            sort: Field to sort by (e.g. 'title')
            order_by: Sort order ('asc' or 'desc')
            filter_expr: Filter expression (e.g. "title='Math 101'")
            fields: Fields to return (e.g. ['sourcedId', 'title', 'courseCode'])
            **extra_params: Any additional query params (e.g. search='Math')
            
        Returns:
            Dictionary containing courses and pagination information
            
        Example:
            # Get all active courses
            api.list_courses(
                filter_expr="status='active'",
                sort='title',
                order_by='asc',
                fields=['sourcedId', 'title', 'courseCode']
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
        
        # Merge in any extra query params (e.g. search)
        params.update(extra_params)
            
        return self._make_request("/courses", params=params)
    
    def get_classes_for_course(
        self,
        course_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get all classes for a course.
        
        Args:
            course_id: The course ID
            limit: Maximum number of classes to return
            offset: Number of classes to skip
            sort: Field to sort by
            order_by: Sort order ('asc' or 'desc')
            filter_expr: Additional filter expression
            fields: Fields to return
            
        Returns:
            Dictionary containing classes for the course
            
        Example:
            # Get all active classes for a course
            api.get_classes_for_course(
                course_id="course-123",
                filter_expr="status='active'",
                sort='title',
                order_by='asc'
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
            
        return self._make_request(
            endpoint=f"/courses/{course_id}/classes",
            params=params
        )
    
    def get_school_for_course(self, course_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get the school that offers a specific course.
        
        Args:
            course_id: The course ID
            fields: Optional list of fields to return
            
        Returns:
            The school data from the API
            
        Raises:
            requests.exceptions.HTTPError: If course or school not found
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
            
        return self._make_request(
            endpoint=f"/courses/{course_id}/school",
            params=params
        )
    
    def get_subjects_for_course(self, course_id: str) -> Dict[str, Any]:
        """Get the subjects for a specific course.
        
        Args:
            course_id: The course ID
            
        Returns:
            Dictionary containing the subjects for the course
            
        Raises:
            requests.exceptions.HTTPError: If course not found or has no subjects
        """
        return self._make_request(
            endpoint=f"/courses/{course_id}/subjects"
        )
    
    def get_resources_for_course(
        self,
        course_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get resources associated with a course.
        
        Args:
            course_id: The course ID
            limit: Maximum number of resources to return
            offset: Number of resources to skip
            sort: Field to sort by
            order_by: Sort order ('asc' or 'desc')
            filter_expr: Additional filter expression
            fields: Fields to return
            
        Returns:
            Dictionary containing resources for the course
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
            endpoint=f"/courses/{course_id}/resources",
            params=params
        ) 