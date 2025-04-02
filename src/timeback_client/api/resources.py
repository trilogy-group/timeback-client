"""Resource API endpoints for the TimeBack API.

This module provides methods for managing resources in the TimeBack API
following the OneRoster 1.2 specification.
"""

from typing import Dict, Any, Optional, List, Union
import logging
from ..models.resource import Resource
from ..core.client import TimeBackService

# Set up logger
logger = logging.getLogger(__name__)

class ResourcesAPI(TimeBackService):
    """API client for resource-related endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the resources API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        # Use 'resources' as the service name per OneRoster 1.2 spec
        super().__init__(base_url, "resources", client_id=client_id, client_secret=client_secret)
    
    def create_resource(self, resource: Union[Resource, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new resource in the TimeBack API.
        
        Args:
            resource: The resource to create. Can be a Resource model instance
                   or a dictionary.
                   Required fields per OneRoster 1.2 spec:
                   - title: Display title
                   - vendorResourceId: Vendor-specific identifier
            
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
            ValueError: If resource does not have required fields
            
        Examples:
            # Using keyword arguments
            api.create_resource({
                "resource": {
                    "title": "Chapter 1 Video",
                    "vendorResourceId": "vendor-123",
                    "status": "active"
                }
            })
            
            # Using the Resource model
            resource = Resource.create(
                title="Chapter 1 Video",
                vendor_resource_id="vendor-123"
            )
            api.create_resource(resource)
        """
        # Convert to dictionary if needed
        if isinstance(resource, Resource):
            request_data = resource.to_dict()
        else:
            # If input is a dictionary, validate it has required fields
            if 'resource' in resource:
                data = resource['resource']
            else:
                data = resource
                resource = {'resource': data}
                
            required_fields = ['title', 'vendorResourceId']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
                
            request_data = resource
            
        return self._make_request(
            endpoint="/resources",
            method="POST",
            data=request_data
        )
    
    def get_resource(self, resource_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific resource by ID.
        
        Args:
            resource_id: The unique identifier of the resource
            fields: Optional list of fields to return
            
        Returns:
            The resource data from the API
            
        Raises:
            requests.exceptions.HTTPError: If resource not found (404) or other API error
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
            
        return self._make_request(
            endpoint=f"/resources/{resource_id}",
            params=params
        )
    
    def update_resource(self, resource_id: str, resource: Union[Resource, Dict[str, Any]]) -> Dict[str, Any]:
        """Update an existing resource in the TimeBack API.
        
        Args:
            resource_id: The ID of the resource to update
            resource: The updated resource data. Can be a Resource model instance
                   or a dictionary.
            
        Returns:
            The updated resource data from the API
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        # Convert dictionary to Resource model if needed
        if isinstance(resource, dict):
            if 'resource' in resource:
                data = resource['resource']
            else:
                data = resource
                
            if 'sourcedId' not in data:
                data['sourcedId'] = resource_id
                
            resource = Resource(**data)
        
        # Ensure sourcedId matches the URL parameter
        if resource.sourcedId != resource_id:
            logger.warning(f"Resource sourcedId ({resource.sourcedId}) doesn't match URL parameter ({resource_id})")
            logger.warning(f"Using URL parameter as the definitive ID")
            resource.sourcedId = resource_id
            
        # Convert to dictionary and send request
        return self._make_request(
            endpoint=f"/resources/{resource_id}",
            method="PUT",
            data=resource.to_dict()
        )
    
    def delete_resource(self, resource_id: str) -> Dict[str, Any]:
        """Delete a resource from the TimeBack API.
        
        Args:
            resource_id: The ID of the resource to delete
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        return self._make_request(
            endpoint=f"/resources/{resource_id}",
            method="DELETE"
        )
    
    def list_resources(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        fields: Optional[List[str]] = None,
        filter_expr: Optional[str] = None
    ) -> Dict[str, Any]:
        """List resources with optional filtering and pagination.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            sort: Field to sort by
            order_by: Sort direction ('asc' or 'desc')
            fields: List of fields to include in response
            filter_expr: Additional filter expression

        Returns:
            dict: Response containing list of resources
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
        if filter_expr is not None:
            params['filter'] = filter_expr

        return self._make_request("/resources", params=params)
    
    def get_resources_for_course(
        self,
        course_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get resources associated with a specific course.
        
        This method calls the OneRoster v1.2 endpoint:
        /ims/oneroster/resources/v1p2/resources/courses/{courseSourcedId}/resources
        
        Args:
            course_id: The course ID (courseSourcedId) to get resources for
            limit: Maximum number of results to return
            offset: Number of results to skip
            sort: Field to sort by
            order_by: Sort direction ('asc' or 'desc')
            fields: List of fields to include in response
            
        Returns:
            dict: Response containing list of resources for the course
            
        Example:
            >>> api.get_resources_for_course("course-123")
            {
                "resources": [
                    {
                        "sourcedId": "resource-456",
                        "title": "Chapter 1 Video",
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
        if sort is not None:
            params['sort'] = sort
        if order_by is not None:
            params['orderBy'] = order_by
        if fields is not None:
            params['fields'] = ','.join(fields)
            
        return self._make_request(
            endpoint=f"/resources/courses/{course_id}/resources",
            params=params
        )
    
    def assign_resource_to_course(self, course_id: str, resource_id: str) -> Dict[str, Any]:
        """Assign an existing resource to a course.
        
        Args:
            course_id: The ID of the course to assign the resource to
            resource_id: The ID of the resource to assign
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        data = {
            "resource": {
                "sourcedId": resource_id
            }
        }
        
        return self._make_request(
            endpoint=f"/resources/courses/{course_id}/resources",
            method="POST",
            data=data
        ) 