"""Component Resource API endpoints for the TimeBack API.

This module provides methods for managing component resources in the TimeBack API
following the OneRoster 1.2 specification.
"""

from typing import Dict, Any, Optional, List, Union
import logging
from ..models.component_resource import ComponentResource
from ..core.client import TimeBackService

# Set up logger
logger = logging.getLogger(__name__)

class ComponentResourcesAPI(TimeBackService):
    """API client for component resource-related endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the component resources API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "rostering", client_id=client_id, client_secret=client_secret)
    
    def create_component_resource(self, resource: Union[ComponentResource, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new component resource in the TimeBack API.
        
        Args:
            resource: The component resource to create. Can be a ComponentResource model instance
                   or a dictionary.
                   Required fields per OneRoster 1.2 spec:
                   - sourcedId: Unique identifier
                   - status: 'active' or 'tobedeleted'
                   - courseComponent: Object with sourcedId of parent component
                   - resource: Object with sourcedId of associated resource
                   - title: Display title
            
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
            api.create_component_resource({
                "componentResource": {
                    "sourcedId": "cr-123",
                    "title": "Chapter 1 Video",
                    "courseComponent": {"sourcedId": "comp-123"},
                    "resource": {"sourcedId": "res-456"},
                    "status": "active"
                }
            })
            
            # Using the ComponentResource model
            resource = ComponentResource.create(
                title="Chapter 1 Video",
                component_id="comp-123",
                resource_id="res-456"
            )
            api.create_component_resource(resource)
        """
        # Convert to dictionary if needed
        if isinstance(resource, ComponentResource):
            request_data = resource.to_dict()
        else:
            # If input is a dictionary, validate it has required fields
            if 'componentResource' in resource:
                data = resource['componentResource']
            else:
                data = resource
                resource = {'componentResource': data}
                
            required_fields = ['sourcedId', 'status', 'courseComponent', 'resource', 'title']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
                
            request_data = resource
            
        return self._make_request(
            endpoint="/courses/component-resources",
            method="POST",
            data=request_data
        )
    
    def get_component_resource(self, resource_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific component resource by ID.
        
        Args:
            resource_id: The unique identifier of the component resource
            fields: Optional list of fields to return
            
        Returns:
            The component resource data from the API
            
        Raises:
            requests.exceptions.HTTPError: If resource not found (404) or other API error
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
            
        return self._make_request(
            endpoint=f"/courses/component-resources/{resource_id}",
            params=params
        )
    
    def update_component_resource(self, resource_id: str, resource: Union[ComponentResource, Dict[str, Any]]) -> Dict[str, Any]:
        """Update an existing component resource in the TimeBack API.
        
        Args:
            resource_id: The ID of the component resource to update
            resource: The updated resource data. Can be a ComponentResource model instance
                   or a dictionary.
            
        Returns:
            The updated component resource data from the API
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        # Convert dictionary to ComponentResource model if needed
        if isinstance(resource, dict):
            if 'componentResource' in resource:
                data = resource['componentResource']
            else:
                data = resource
                
            if 'sourcedId' not in data:
                data['sourcedId'] = resource_id
                
            resource = ComponentResource(**data)
        
        # Ensure sourcedId matches the URL parameter
        if resource.sourcedId != resource_id:
            logger.warning(f"Resource sourcedId ({resource.sourcedId}) doesn't match URL parameter ({resource_id})")
            logger.warning(f"Using URL parameter as the definitive ID")
            resource.sourcedId = resource_id
            
        # Convert to dictionary and send request
        return self._make_request(
            endpoint=f"/courses/component-resources/{resource_id}",
            method="PUT",
            data=resource.to_dict()
        )
    
    def delete_component_resource(self, resource_id: str) -> Dict[str, Any]:
        """Delete a component resource from the TimeBack API.
        
        Args:
            resource_id: The ID of the component resource to delete
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        return self._make_request(
            endpoint=f"/courses/component-resources/{resource_id}",
            method="DELETE"
        )
    
    def list_component_resources(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        fields: Optional[List[str]] = None,
        component_id: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List component resources with optional filtering and pagination.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            sort: Field to sort by
            order_by: Sort direction ('asc' or 'desc')
            fields: List of fields to include in response
            component_id: Filter by parent component ID
            resource_id: Filter by resource ID

        Returns:
            dict: Response containing list of component resources
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
        if component_id is not None:
            filters.append(f"courseComponent.sourcedId='{component_id}'")
        if resource_id is not None:
            filters.append(f"resource.sourcedId='{resource_id}'")
            
        if filters:
            params['filter'] = ' AND '.join(filters)

        return self._make_request("/courses/component-resources", params=params) 