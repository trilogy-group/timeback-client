"""User models for the TimeBack API.

This module defines the data models for users in the TimeBack API,
including parents, students, and teachers.

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
from pydantic import BaseModel, Field, validator
import uuid

class UserRole(str, Enum):
    """Valid user roles in the TimeBack API."""
    AIDE = "aide"
    COUNSELOR = "counselor"
    DISTRICT_ADMIN = "districtAdministrator"
    GUARDIAN = "guardian"
    PARENT = "parent"
    PRINCIPAL = "principal"
    PROCTOR = "proctor"
    RELATIVE = "relative"
    SITE_ADMIN = "siteAdministrator"
    STUDENT = "student"
    SYSTEM_ADMIN = "systemAdministrator"
    TEACHER = "teacher"

class UserStatus(str, Enum):
    """Valid user status values."""
    ACTIVE = "active"
    TOBEDELETED = "tobedeleted"

class EnabledUser(bool):
    """Whether the user account is enabled."""
    pass

class Address(BaseModel):
    """User address information stored in metadata."""
    country: str
    city: str
    state: str
    zip: str

class OrgRef(BaseModel):
    """Reference to an organization."""
    href: str
    sourcedId: str
    type: str = "org"

class RoleAssignment(BaseModel):
    """Role assignment with organization reference."""
    role: UserRole
    roleType: str = "primary"
    org: Optional[OrgRef] = None
    userProfile: Optional[str] = Field(None, description="URI of associated user profile")
    beginDate: Optional[str] = Field(None, description="ISO date when role begins")
    endDate: Optional[str] = Field(None, description="ISO date when role ends")

class UserId(BaseModel):
    """External user identifier."""
    type: str
    identifier: str

class Credential(BaseModel):
    """Credentials for a user profile."""
    type: str
    username: str
    password: Optional[str] = None

class UserProfile(BaseModel):
    """System/app/tool profile for user."""
    profileId: str = Field(..., description="Unique identifier within user scope")
    profileType: str = Field(..., description="Human readable label")
    vendorId: str = Field(..., description="Vendor identifier")
    applicationId: Optional[str] = Field(None, description="Application identifier")
    description: Optional[str] = None
    credentials: List[Credential] = Field(default_factory=list)

class ResourceRef(BaseModel):
    """Reference to a learning resource."""
    href: str
    sourcedId: str
    type: str = "resource"

class User(BaseModel):
    """OneRoster User model.
    
    This model represents a user in the OneRoster system, which could be a
    student, teacher, parent, or other role. Users can be associated with
    organizations and have relationships with other users (e.g. parent-student).

    Required Fields:
    - sourcedId: Unique identifier (UUID)
    - status: active or tobedeleted
    - dateLastModified: Last update timestamp
    - enabledUser: Whether user has system access (boolean)
    - givenName: First name
    - familyName: Last name
    - roles: List of role assignments (at least one required)
    """
    # Required fields
    givenName: str = Field(description="User's first name")
    familyName: str = Field(description="User's last name")
    roles: List[RoleAssignment] = Field(description="User's roles and organizations")
    sourcedId: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="User's status")
    dateLastModified: datetime = Field(default_factory=datetime.utcnow, description="Last modification time")
    enabledUser: bool = Field(default=True, description="Whether user has system access")
    
    # Optional fields
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number (stored in metadata)")
    address: Optional[Address] = Field(None, description="Address information (stored in metadata)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")
    userMasterIdentifier: Optional[str] = Field(None, description="Master identifier across systems")
    username: Optional[str] = Field(None, description="Legacy username")
    userIds: List[UserId] = Field(default_factory=list, description="External system identifiers")
    middleName: Optional[str] = Field(None, description="Middle name(s)")
    preferredFirstName: Optional[str] = Field(None, description="Preferred first name")
    preferredMiddleName: Optional[str] = Field(None, description="Preferred middle name")
    preferredLastName: Optional[str] = Field(None, description="Preferred last name")
    pronouns: Optional[str] = Field(None, description="Preferred pronouns")
    userProfiles: List[UserProfile] = Field(default_factory=list, description="System/app profiles")
    primaryOrg: Optional[OrgRef] = Field(None, description="Primary organization")
    identifier: Optional[str] = Field(None, description="Legacy identifier (use userIds instead)")
    sms: Optional[str] = Field(None, description="SMS number")
    agents: List[str] = Field(default_factory=list, description="Related user IDs (e.g. parents)")
    grades: List[str] = Field(default_factory=list, description="Grade levels for students")
    password: Optional[str] = Field(None, description="Top-level password (should be encrypted)")
    resources: List[ResourceRef] = Field(default_factory=list, description="Associated learning resources")

    @validator('roles')
    def validate_roles(cls, v):
        if not v:
            raise ValueError('At least one role is required')
        return v

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API requests.
        
        Returns:
            Dict with user data wrapped in 'user' key as required by API
        """
        # Start with basic model dict
        data = self.model_dump(exclude_none=True)
        
        # Convert datetime to ISO format with Z
        data['dateLastModified'] = self.dateLastModified.isoformat() + "Z"
        
        # Handle metadata fields
        metadata = self.metadata or {}
        if self.phone:
            metadata['phone'] = self.phone
        if self.address:
            metadata['address'] = self.address.model_dump()
        if metadata:
            data['metadata'] = metadata
            
        # Format agent references
        if self.agents:
            data['agents'] = [
                {"href": f"/users/{agent}", "sourcedId": agent, "type": "user"}
                for agent in self.agents
            ]
            
        # Wrap in user object as required by API
        return {"user": data}

    def to_create_dict(self) -> Dict[str, Any]:
        """Convert model to dict for POST operations.
        
        Returns:
            Dict formatted for creating a new user
        """
        return self.to_api_dict()
        
    def to_update_dict(self) -> Dict[str, Any]:
        """Convert model to dict for PUT operations.
        
        Returns:
            Dict formatted for updating an existing user
        """
        return self.to_api_dict() 