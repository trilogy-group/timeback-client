"""User models for the TimeBack API.

This module defines the data models for users following the OneRoster v1.2 specification
with our simplified reference handling.

API Endpoints:
- GET /users - List users
- GET /users/{id} - Get a specific user
- POST /users - Create a new user
- PUT /users/{id} - Update a user
- DELETE /users/{id} - Delete a user (sets status to tobedeleted)
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import uuid
import pytz

class RoleName(str, Enum):
    """Valid user roles in the TimeBack API."""
    ADMINISTRATOR = "administrator"
    AIDE = "aide"
    GUARDIAN = "guardian"
    PARENT = "parent"
    PROCTOR = "proctor"
    RELATIVE = "relative"
    STUDENT = "student"
    TEACHER = "teacher"

class RoleType(str, Enum):
    """Role types in OneRoster."""
    PRIMARY = "primary"
    SECONDARY = "secondary"

class Status(str, Enum):
    """Universal status values."""
    ACTIVE = "active"
    TOBEDELETED = "tobedeleted"

class Reference(BaseModel):
    """Base reference type without href."""
    sourcedId: str
    type: str

class OrgRef(Reference):
    """Organization reference."""
    type: str = "org"

class AgentRef(Reference):
    """Agent reference with limited types."""
    type: str = Field(..., description="Type of agent reference")

    @field_validator('type')
    def validate_type(cls, v):
        """Validate agent type is either student or user."""
        if v not in ['student', 'user']:
            raise ValueError('Agent type must be either student or user')
        return v

class UserId(BaseModel):
    """External user identifier."""
    type: str
    identifier: str

class UserRole(BaseModel):
    """Role assignment with organization reference."""
    roleType: RoleType
    role: RoleName
    org: OrgRef
    userProfile: Optional[str] = None
    beginDate: Optional[str] = None
    endDate: Optional[str] = None

class User(BaseModel):
    """OneRoster User model with simplified reference handling.
    
    Required Fields:
    - sourcedId: Unique identifier
    - status: active or tobedeleted
    - enabledUser: Whether user has system access
    - givenName: First name
    - familyName: Last name
    - roles: List of role assignments (at least one required)
    """
    # Required fields
    sourcedId: str = Field(..., description="Unique identifier")
    status: Status = Field(default=Status.ACTIVE, description="User's status")
    enabledUser: bool = Field(..., description="Whether user has system access")
    givenName: str = Field(..., description="First name")
    familyName: str = Field(..., description="Last name")
    roles: List[UserRole] = Field(..., description="User's roles and organizations")
    
    # Optional fields
    dateLastModified: Optional[str] = Field(None, description="Last modification timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")
    userMasterIdentifier: Optional[str] = Field(None, description="Master identifier across systems")
    username: Optional[str] = Field(None, description="Legacy username")
    userIds: Optional[List[UserId]] = Field(None, description="External system identifiers")
    middleName: Optional[str] = Field(None, description="Middle name")
    agents: Optional[List[AgentRef]] = Field(None, description="Related user references")
    primaryOrg: Optional[OrgRef] = Field(None, description="Primary organization")
    email: Optional[str] = Field(None, description="Email address")
    preferredFirstName: Optional[str] = Field(None, description="Preferred first name")
    preferredMiddleName: Optional[str] = Field(None, description="Preferred middle name")
    preferredLastName: Optional[str] = Field(None, description="Preferred last name")
    pronouns: Optional[str] = Field(None, description="Preferred pronouns")
    grades: Optional[List[str]] = Field(None, description="Grade levels")
    password: Optional[str] = Field(None, description="User password")
    sms: Optional[str] = Field(None, description="SMS number")
    phone: Optional[str] = Field(None, description="Phone number")

    @field_validator('roles')
    def validate_roles(cls, v):
        """Validate that at least one role is provided."""
        if not v:
            raise ValueError('At least one role is required')
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API requests."""
        data = self.model_dump(exclude_none=True)
        
        # Set dateLastModified if not provided
        if not self.dateLastModified:
            data['dateLastModified'] = datetime.utcnow().isoformat() + 'Z'
            
        return {"user": data}

    def to_create_dict(self) -> Dict[str, Any]:
        """Convert model to dict for POST operations."""
        return self.to_dict()
        
    def to_update_dict(self) -> Dict[str, Any]:
        """Convert model to dict for PUT operations."""
        return self.to_dict() 