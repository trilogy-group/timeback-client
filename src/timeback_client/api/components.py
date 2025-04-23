"""Component-related API endpoints for the TimeBack API.

This module provides methods for retrieving and managing course components
in the TimeBack API following the OneRoster 1.2 specification.
"""

from typing import Dict, Any, Optional, List, Union
import logging
from ..models.component import Component
from ..core.client import TimeBackService
import requests

# Set up logger
logger = logging.getLogger(__name__)

class ComponentsAPI(TimeBackService):
    """API client for course component-related endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the components API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "rostering", client_id=client_id, client_secret=client_secret)
    
    def create_component(self, component: Union[Component, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new course component in the TimeBack API.
        
        Args:
            component: The component to create. Can be a Component model instance or a dictionary.
                   Required fields per OneRoster 1.2 spec:
                   - title: The title of the component
                   - status: 'active' or 'tobedeleted' (defaults to 'active')
                   - course: Object with sourcedId of the parent course
                   - sortOrder: Position within siblings
            
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
            ValueError: If component does not have required fields
            
        Examples:
            # Using keyword arguments
            api.create_component({
                "courseComponent": {
                    "title": "Unit 1: Introduction",
                    "status": "active",
                    "course": {"sourcedId": "course-123"},
                    "sortOrder": 1
                }
            })
            
            # Using the Component model
            component = Component.create(
                title="Unit 1: Introduction",
                course={"sourcedId": "course-123"},
                sortOrder=1
            )
            api.create_component(component)
        """
        # If input is a dictionary, check if it's already wrapped in 'courseComponent'
        if isinstance(component, dict):
            if 'courseComponent' in component:
                component_dict = component['courseComponent']
                request_data = component  # Use as-is
            else:
                component_dict = component
                request_data = {'courseComponent': component}
                
            # Check required fields
            if not component_dict.get('title'):
                raise ValueError("title is required when creating a component")
                
            if not component_dict.get('course'):
                raise ValueError("course with sourcedId is required when creating a component")
                
            # Ensure required fields per OneRoster 1.2 spec
            if 'status' not in component_dict:
                component_dict['status'] = 'active'
                
            if 'sortOrder' not in component_dict:
                raise ValueError("sortOrder is required when creating a component")
                
        # If it's a Component model, validate and convert to dict
        else:
            if not component.title:
                raise ValueError("title is required when creating a component")
                
            if not component.course or not component.course.get('sourcedId'):
                raise ValueError("course with sourcedId is required when creating a component")
            
            # Convert to dictionary and wrap in 'courseComponent'
            request_data = {'courseComponent': component.to_dict()}
            
        # Log the sourcedId
        if isinstance(component, Component):
            logger.info(f"Creating component with sourcedId: {component.sourcedId}")
        else:
            logger.info(f"Creating component with data: {component_dict}")
            
        # Send request - response will contain sourcedIdPairs
        return self._make_request(
            endpoint="/courses/components",
            method="POST",
            data=request_data
        )
    
    def get_component(self, component_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific course component by ID.
        
        Args:
            component_id: The unique identifier of the component
            fields: Optional list of fields to return (e.g. ['sourcedId', 'title'])
            
        Returns:
            The component data from the API
            
        Raises:
            requests.exceptions.HTTPError: If component not found (404) or other API error
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
            
        return self._make_request(
            endpoint=f"/courses/components/{component_id}",
            params=params
        )
    
    def update_component(self, component_id: str, component: Union[Component, Dict[str, Any]]) -> Dict[str, Any]:
        """Update an existing course component in the TimeBack API.
        
        Args:
            component_id: The ID of the component to update
            component: The updated component data. Can be a Component model instance or a dictionary.
            
        Returns:
            The updated component data from the API
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        # Convert dictionary to Component model if needed
        if isinstance(component, dict):
            if 'courseComponent' in component:
                component_dict = component['courseComponent']
            else:
                component_dict = component
                
            if 'sourcedId' not in component_dict:
                component_dict['sourcedId'] = component_id
                
            component = Component(**component_dict)
        
        # Ensure sourcedId matches the URL parameter
        if component.sourcedId != component_id:
            logger.warning(f"Component sourcedId ({component.sourcedId}) doesn't match URL parameter ({component_id})")
            logger.warning(f"Using URL parameter as the definitive ID")
            component.sourcedId = component_id
            
        # Convert to dictionary and send request
        return self._make_request(
            endpoint=f"/courses/components/{component_id}",
            method="PUT",
            data=component.to_dict()
        )
    
    def delete_component(self, component_id: str) -> Dict[str, Any]:
        """Delete a course component from the TimeBack API.
        
        Args:
            component_id: The ID of the component to delete
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        return self._make_request(
            endpoint=f"/courses/components/{component_id}",
            method="DELETE"
        )
    
    def list_components(
        self,
        limit=None,
        offset=None,
        sort=None,
        order_by=None,
        fields=None,
        parent_id=None,
        course_id=None,
        filter_expr=None
    ):
        """List course components with optional filtering and pagination.

        Args:
            limit (int, optional): Maximum number of results to return
            offset (int, optional): Number of results to skip
            sort (str, optional): Field to sort by
            order_by (str, optional): Sort direction ('asc' or 'desc')
            fields (list, optional): List of fields to include in response
            parent_id (str, optional): Filter by parent component ID
            course_id (str, optional): Filter by course ID
            filter_expr (str, optional): Additional filter expression (passed as 'filter' query param)

        Returns:
            dict: Response containing list of components
        """
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        if sort is not None:
            params['sort'] = sort
        if order_by is not None:
            params['orderBy'] = order_by
        if fields is not None:
            params['fields'] = ','.join(fields)
        # Build filter expression
        filters = []
        if parent_id is not None:
            filters.append(f"parent='{parent_id}'")
        if course_id is not None:
            filters.append(f"course.sourcedId='{course_id}'")
        if filter_expr is not None:
            filters.append(filter_expr)
        if filters:
            params['filter'] = ' AND '.join(filters)
        return self._make_request("/courses/components", params=params)
    
    def get_resources_for_component(
        self,
        component_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get resources associated with a course component.
        
        Args:
            component_id: The component ID
            limit: Maximum number of resources to return
            offset: Number of resources to skip
            sort: Field to sort by
            order_by: Sort order ('asc' or 'desc')
            filter_expr: Additional filter expression
            fields: Fields to return
            
        Returns:
            Dictionary containing resources for the component
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
            endpoint=f"/courses/components/{component_id}/resources",
            params=params
        ) 