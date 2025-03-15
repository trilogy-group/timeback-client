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
    
    def __init__(self, base_url: str):
        """Initialize the users API client.
        
        Args:
            base_url: The base URL of the TimeBack API
        """
        super().__init__(base_url, "rostering")
    
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
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List users with filtering and pagination.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            sort: Field to sort by (e.g. 'familyName')
            order_by: Sort order ('asc' or 'desc')
            filter_expr: Filter expression (e.g. "role='student'")
            fields: Fields to return (e.g. ['sourcedId', 'givenName'])
            
        Returns:
            Dictionary containing users and pagination information
            
        Example:
            # Get all active students
            api.list_users(
                filter_expr="role='student' AND status='active'",
                sort='familyName',
                order_by='asc',
                fields=['sourcedId', 'givenName', 'familyName', 'email']
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