"""User-related API endpoints for the TimeBack API.

This module provides methods for creating, updating, and managing users
in the TimeBack API.
"""

from typing import Dict, Any, Optional
from ..models.user import User, Address, UserRole
from ..core.client import TimeBackService

class UsersAPI(TimeBackService):
    """API client for user-related endpoints."""
    
    def __init__(self, base_url: str):
        """Initialize the users API client.
        
        Args:
            base_url: The base URL of the TimeBack API
        """
        super().__init__(base_url, "rostering")
    
    def create_user(self, user: User) -> Dict[str, Any]:
        """Create a new user in the TimeBack API.
        
        Args:
            user: The user to create
            
        Returns:
            The created user data from the API
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        return self._make_request(
            endpoint="/users",
            method="POST",
            data=user.to_dict()
        )
    
    def update_user(self, user_id: str, user: User) -> Dict[str, Any]:
        """Update an existing user in the TimeBack API.
        
        Args:
            user_id: The ID of the user to update
            user: The updated user data
            
        Returns:
            The updated user data from the API
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        return self._make_request(
            endpoint=f"/users/{user_id}",
            method="PUT",
            data=user.to_dict()
        )
    
    def create_parent(
        self,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        address: Optional[Address] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new parent user.
        
        This is a convenience method that wraps create_user with parent-specific defaults.
        
        Args:
            first_name: Parent's first name
            last_name: Parent's last name
            phone: Optional phone number
            address: Optional address information
            metadata: Optional additional metadata
            
        Returns:
            The created parent user data from the API
        """
        user = User(
            first_name=first_name,
            last_name=last_name,
            role=UserRole.PARENT,
            phone=phone,
            address=address,
            metadata=metadata
        )
        return self.create_user(user) 