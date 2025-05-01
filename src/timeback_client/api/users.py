"""User-related API endpoints for the TimeBack API.

This module provides methods for creating, updating, and managing users
in the TimeBack API.
"""

from typing import Dict, Any, Optional, List, Union
import uuid
from ..models.user import User
from ..core.client import TimeBackService
import requests
import logging

# Set up logger
logger = logging.getLogger(__name__)

class UsersAPI(TimeBackService):
    """API client for user-related endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the users API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "rostering", client_id=client_id, client_secret=client_secret)
    
    def create_user(self, user: Union[User, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new user in the TimeBack API.
        
        Args:
            user: The user to create. Can be a User model instance or a dictionary.
                 Must have sourcedId set.
            
        Returns:
            The API response containing sourcedIdPairs
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
            ValueError: If user does not have a sourcedId
        """
        # Convert dictionary to User model if needed
        if isinstance(user, dict):
            # If user_data is a dict with 'user' key, extract the inner dict
            if 'user' in user:
                user_dict = user['user']
            else:
                user_dict = user
                
            # Create User model from dict
            user = User(**user_dict)
            
        # Validate sourcedId
        if not user.sourcedId:
            raise ValueError("sourcedId is required when creating a user")
            
        return self._make_request(
            endpoint="/users",
            method="POST",
            data=user.to_dict()
        )
    
    def get_user(self, user_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific user by ID.
        
        Args:
            user_id: The unique identifier of the user
            fields: Optional list of fields to return (e.g. ['sourcedId', 'givenName'])
            
        Returns:
            The user data from the API
            
        Raises:
            requests.exceptions.HTTPError: If user not found (404) or other API error
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
            
        return self._make_request(
            endpoint=f"/users/{user_id}",
            params=params
        )
    
    def list_users(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None,
        filter: Optional[str] = None,
        fields: Optional[List[str]] = None,
        **extra_params
    ) -> Dict[str, Any]:
        """List users with filtering and pagination.
        Always filters for status='active' unless another status is provided.
        Supports arbitrary extra query params (e.g. search='Amanda').
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            sort: Field to sort by (e.g. 'familyName')
            order_by: Sort order ('asc' or 'desc')
            filter_expr: Filter expression (e.g. "role='student'")
            filter: Alias for filter_expr for compatibility
            fields: Fields to return (e.g. ['sourcedId', 'givenName'])
            **extra_params: Any additional query params (e.g. search='Amanda')
        Returns:
            Dictionary containing users and pagination information
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
        filter_value = filter_expr or filter
        if filter_value:
            if "status=" not in filter_value:
                filter_value = f"{filter_value} AND status='active'"
        else:
            filter_value = "status='active'"
        params['filter'] = filter_value
        if fields:
            params['fields'] = ','.join(fields)
        # Merge in any extra query params (e.g. search)
        params.update(extra_params)
        return self._make_request("/users", params=params)
    
    def update_user(self, user_id: str, user: Union[User, Dict[str, Any]]) -> Dict[str, Any]:
        """Update an existing user in the TimeBack API.
        
        Args:
            user_id: The ID of the user to update
            user: The updated user data. Can be a User model instance or a dictionary.
            
        Returns:
            The updated user data from the API
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        # Convert dictionary to User model if needed
        if isinstance(user, dict):
            # If user_data is a dict with 'user' key, extract the inner dict
            if 'user' in user:
                user_dict = user['user']
            else:
                user_dict = user
                
            # Create User model from dict
            user = User(**user_dict)
            
        return self._make_request(
            endpoint=f"/users/{user_id}",
            method="PUT",
            data=user.to_dict()
        )
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Mark a user for deletion in the TimeBack API.
        
        In OneRoster, users are not immediately deleted but rather marked with status='tobedeleted'.
        This method first fetches the current user data and then updates only the status field.
        
        Args:
            user_id: The ID of the user to delete
            
        Returns:
            The API response or a success message if the API returns an empty response
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails (except 404)
        """
        try:
            # First get the current user data
            logger.info(f"Fetching user {user_id} before marking for deletion")
            try:
                current_user_data = self.get_user(user_id)
                
                if 'user' not in current_user_data:
                    logger.error(f"Invalid response format when fetching user {user_id}")
                    raise ValueError(f"Invalid response format when fetching user {user_id}")
                    
                # Update only the status field
                user_data = current_user_data['user']
                previous_status = user_data.get('status')
                
                # If already marked for deletion, return success
                if previous_status == 'tobedeleted':
                    logger.info(f"User {user_id} is already marked for deletion")
                    return {"message": f"User {user_id} is already marked for deletion"}
                    
                user_data['status'] = 'tobedeleted'
                
                logger.info(f"Updating user {user_id} status from '{previous_status}' to 'tobedeleted'")
                
                # Update the user with the new status
                return self._make_request(
                    endpoint=f"/users/{user_id}",
                    method="PUT",
                    data={"user": user_data}
                )
            except requests.exceptions.HTTPError as e:
                # If user doesn't exist (404) when trying to get it, consider it already deleted
                if hasattr(e, 'response') and e.response and e.response.status_code == 404:
                    logger.info(f"User {user_id} not found during initial fetch, considering delete successful")
                    return {"message": f"User {user_id} not found or already deleted"}
                raise
                
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            # If it's a 404 error, consider it a success (user already deleted)
            if isinstance(e, requests.exceptions.HTTPError) and hasattr(e, 'response') and e.response and e.response.status_code == 404:
                logger.info(f"User {user_id} not found, considering delete successful")
                return {"message": f"User {user_id} not found or already deleted"}
            raise

    def list_students(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List students using the OneRoster v1.2 students endpoint.
        
        DEPRECATED: This method has been moved to the StudentsAPI class.
        Please use StudentsAPI.list_students() instead.
        
        This method uses the dedicated students endpoint which automatically filters
        for users with the student role. It supports all standard OneRoster filtering
        and sorting capabilities including dot notation for nested fields.
        
        Args:
            limit: Maximum number of students to return
            offset: Number of students to skip
            sort: Field to sort by (e.g. 'familyName' or 'metadata.grade')
            order_by: Sort order ('asc' or 'desc')
            filter: Filter expression (e.g. "status='active'")
            fields: Fields to return (e.g. ['sourcedId', 'givenName'])
            
        Returns:
            Dictionary containing students and pagination information
            
        Example:
            # Get all active students sorted by grade
            api.list_students(
                filter="status='active'",
                sort='metadata.grade',
                order_by='asc',
                fields=['sourcedId', 'givenName', 'familyName', 'email']
            )
            
            # Filter by metadata field
            api.list_students(
                filter="metadata.emergencyContact='true'"
            )
        """
        import warnings
        warnings.warn(
            "UsersAPI.list_students is deprecated. Please use StudentsAPI.list_students instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        if sort:
            params['sort'] = sort
        if order_by:
            params['orderBy'] = order_by
        if filter:
            params['filter'] = filter
        if fields:
            params['fields'] = ','.join(fields)
            
        return self._make_request("/students", params=params) 