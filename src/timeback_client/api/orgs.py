"""Organization-related API endpoints for the TimeBack API.

This module provides methods for retrieving and managing organizations
in the TimeBack API following the OneRoster 1.2 specification.

Organizations represent educational institutions such as departments, schools,
districts, and other administrative units in the hierarchy.
"""

from typing import Dict, Any, Optional, List, Union
import logging
from ..models.org import Org
from ..core.client import TimeBackService

# Set up logger
logger = logging.getLogger(__name__)

class OrgsAPI(TimeBackService):
    """API client for organization-related endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the organizations API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "rostering", client_id=client_id, client_secret=client_secret)
    
    def create_org(self, org: Union[Org, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new organization in the TimeBack API.
        
        Args:
            org: The organization to create. Can be an Org model instance or a dictionary.
                Required fields per OneRoster 1.2 spec:
                - name: The name of the organization
                - type: The type of organization (department, school, district, etc.)
            
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
            ValueError: If org does not have required fields
            
        Examples:
            # Using keyword arguments
            api.create_org({
                "org": {
                    "name": "Springfield High School",
                    "type": "school",
                    "status": "active"
                }
            })
            
            # Using the Org model
            org = Org.create(
                name="Springfield High School",
                type="school",
                identifier="SHS-001"
            )
            api.create_org(org)
        """
        # If input is a dictionary, check if it's already wrapped in 'org'
        if isinstance(org, dict):
            if 'org' in org:
                org_dict = org['org']
                request_data = org  # Use as-is
            else:
                org_dict = org
                request_data = {'org': org}
                
            # Check required fields
            if not org_dict.get('name'):
                raise ValueError("name is required when creating an organization")
                
            if not org_dict.get('type'):
                raise ValueError("type is required when creating an organization")
                
        # If it's an Org model, validate and convert to dict
        else:
            if not org.name:
                raise ValueError("name is required when creating an organization")
                
            # Convert to dictionary and wrap in 'org'
            request_data = org.to_dict()
            
        # Log the sourcedId
        if isinstance(org, Org):
            logger.info(f"Creating organization with sourcedId: {org.sourcedId}")
        else:
            logger.info(f"Creating organization with data: {org_dict}")
            
        # Send request - response will contain sourcedIdPairs
        return self._make_request(
            endpoint="/orgs",
            method="POST",
            data=request_data
        )
    
    def get_org(self, org_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific organization by ID.
        
        Args:
            org_id: The unique identifier of the organization
            fields: Optional list of fields to return (e.g. ['sourcedId', 'name'])
            
        Returns:
            The organization data from the API
            
        Raises:
            requests.exceptions.HTTPError: If organization not found (404) or other API error
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
            
        return self._make_request(
            endpoint=f"/orgs/{org_id}",
            params=params
        )
    
    def update_org(self, org_id: str, org: Union[Org, Dict[str, Any]]) -> Dict[str, Any]:
        """Update an existing organization in the TimeBack API.
        
        Args:
            org_id: The ID of the organization to update
            org: The updated organization data. Can be an Org model instance or a dictionary.
            
        Returns:
            The updated organization data from the API
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        # Convert dictionary to Org model if needed
        if isinstance(org, dict):
            # If org_data is a dict with 'org' key, extract the inner dict
            if 'org' in org:
                org_dict = org['org']
            else:
                org_dict = org
                
            # Create Org model from dict, using org_id if sourcedId isn't set
            if 'sourcedId' not in org_dict:
                org_dict['sourcedId'] = org_id
                
            # Create Org model from dict
            org = Org(**org_dict)
        
        # Ensure sourcedId matches the URL parameter
        if org.sourcedId != org_id:
            logger.warning(f"Organization sourcedId ({org.sourcedId}) doesn't match URL parameter ({org_id})")
            logger.warning(f"Using URL parameter as the definitive ID")
            org.sourcedId = org_id
            
        # Convert to dictionary and send request
        return self._make_request(
            endpoint=f"/orgs/{org_id}",
            method="PUT",
            data=org.to_dict()
        )
    
    def delete_org(self, org_id: str) -> Dict[str, Any]:
        """Delete an organization from the TimeBack API.
        
        Note: This typically sets the status to 'tobedeleted' rather than performing a hard delete.
        
        Args:
            org_id: The ID of the organization to delete
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        return self._make_request(
            endpoint=f"/orgs/{org_id}",
            method="DELETE"
        )
    
    def list_orgs(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List organizations with filtering and pagination.
        
        Args:
            limit: Maximum number of organizations to return
            offset: Number of organizations to skip
            sort: Field to sort by (e.g. 'name')
            order_by: Sort order ('asc' or 'desc')
            filter_expr: Filter expression (e.g. "type='school'")
            fields: Fields to return (e.g. ['sourcedId', 'name', 'type'])
            
        Returns:
            Dictionary containing organizations and pagination information
            
        Example:
            # Get all active schools
            api.list_orgs(
                filter_expr="status='active' AND type='school'",
                sort='name',
                order_by='asc',
                fields=['sourcedId', 'name', 'type']
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
            
        return self._make_request("/orgs", params=params)
    