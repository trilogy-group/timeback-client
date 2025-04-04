"""Organization models for the TimeBack API.

This module defines the data models for organizations following the OneRoster v1.2 specification.
Organizations represent educational institutions such as departments, schools, districts,
and other administrative units in the hierarchy.

API Endpoints:
- GET /orgs - List organizations
- GET /orgs/{id} - Get a specific organization
- POST /orgs - Create a new organization
- PUT /orgs/{id} - Update an organization
- DELETE /orgs/{id} - Delete an organization (sets status to tobedeleted)
"""

from datetime import datetime, UTC
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
import uuid
import logging

logger = logging.getLogger(__name__)

class OrgType(str, Enum):
    """Valid organization types in the TimeBack API."""
    DEPARTMENT = "department"
    SCHOOL = "school"
    DISTRICT = "district"
    LOCAL = "local"
    STATE = "state"
    NATIONAL = "national"

class Status(str, Enum):
    """Universal status values."""
    ACTIVE = "active"
    TOBEDELETED = "tobedeleted"

class OrgRef(BaseModel):
    """Reference to an organization."""
    sourcedId: str = Field(..., description="The unique identifier of the referenced organization")
    type: str = "org"

class Org(BaseModel):
    """OneRoster Organization model.
    
    Required Fields:
    - name: Name of the organization
    - type: Type of organization (department, school, district, etc.)
    
    Optional Fields:
    - sourcedId: Unique identifier (auto-generated if not provided)
    - status: active or tobedeleted (defaults to active)
    - metadata: Additional custom properties
    - identifier: External identifier for the organization
    - parent: Reference to parent organization
    """
    
    # Required fields
    name: str = Field(..., description="Name of the organization")
    type: OrgType = Field(..., description="Type of organization")
    
    # Optional fields with defaults
    sourcedId: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    status: Status = Field(default=Status.ACTIVE, description="Organization's status")
    dateLastModified: str = Field(
        default_factory=lambda: datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
        description="Last modification timestamp"
    )
    
    # Optional fields
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")
    identifier: Optional[str] = Field(None, description="External identifier")
    parent: Optional[OrgRef] = Field(None, description="Reference to parent organization")

    def to_dict(self, wrapped: bool = True) -> Dict[str, Any]:
        """Convert model to dictionary for API requests.
        
        Args:
            wrapped: Whether to wrap the result in an {'org': {...}} object
            
        Returns:
            Dictionary representation of the organization
        """
        data = self.model_dump(exclude_none=True)
        
        # Update timestamp if not provided
        if 'dateLastModified' not in data:
            data['dateLastModified'] = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
            
        return {"org": data} if wrapped else data

    def to_create_dict(self) -> Dict[str, Any]:
        """Convert model to dict for POST operations.
        
        Returns:
            Dictionary formatted for create operation
        """
        return self.to_dict()
        
    def to_update_dict(self) -> Dict[str, Any]:
        """Convert model to dict for PUT operations.
        
        Returns:
            Dictionary formatted for update operation
        """
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Org':
        """Create an Org instance from a dictionary.
        
        Args:
            data: Dictionary containing organization data
            
        Returns:
            An Org instance
            
        Raises:
            ValueError: If required fields are missing
        """
        # Handle wrapped response
        if 'org' in data:
            data = data['org']
            
        # Convert string type to enum if needed
        if 'type' in data and isinstance(data['type'], str):
            try:
                data['type'] = OrgType(data['type'])
            except ValueError:
                logger.warning(f"Invalid organization type: {data['type']}")
                raise
                
        # Convert string status to enum if needed
        if 'status' in data and isinstance(data['status'], str):
            try:
                data['status'] = Status(data['status'])
            except ValueError:
                logger.warning(f"Invalid status: {data['status']}")
                raise
                
        return cls(**data)

    @classmethod
    def create(cls, name: str, type: str, **kwargs) -> 'Org':
        """Helper method to create a new organization with minimal required fields.
        
        Args:
            name: The name of the organization
            type: The type of organization (must be valid OrgType)
            **kwargs: Additional organization attributes
            
        Returns:
            A new Org instance
            
        Raises:
            ValueError: If type is not a valid OrgType
        """
        # Convert string type to enum
        org_type = OrgType(type)
        
        return cls(
            name=name,
            type=org_type,
            **kwargs
        )

    @classmethod
    def to_orgs_response(cls, orgs: List['Org']) -> Dict[str, Any]:
        """Convert a list of Org objects to a OneRoster orgs response.
        
        Args:
            orgs: List of Org objects
            
        Returns:
            Response in the format {'orgs': [...]}
        """
        return {
            'orgs': [org.to_dict(wrapped=False) for org in orgs]
        }

    def __repr__(self) -> str:
        """String representation of the Organization.
        
        Returns:
            String representation
        """
        return f"Org(sourcedId='{self.sourcedId}', name='{self.name}', type='{self.type.value}')" 