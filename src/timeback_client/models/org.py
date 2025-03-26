"""Organization models for the TimeBack API.

This module provides Pydantic models for organizations in the OneRoster system.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class OrgType(str, Enum):
    """Types of organizations in OneRoster."""
    DEPARTMENT = "department"
    DISTRICT = "district"
    LOCAL = "local"
    NATIONAL = "national"
    SCHOOL = "school"
    STATE = "state"

class OrgStatus(str, Enum):
    """Status values for organizations."""
    ACTIVE = "active"
    TOBEDELETED = "tobedeleted"
    INACTIVE = "inactive"

class OrgRef(BaseModel):
    """Reference to an organization."""
    sourcedId: str
    type: str = "org"

class Org(BaseModel):
    """Organization model following OneRoster specification.
    
    This model represents an organization in the OneRoster system,
    which could be a school, district, department, etc.
    """
    sourcedId: str
    status: OrgStatus = OrgStatus.ACTIVE
    dateLastModified: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    name: str
    type: OrgType
    identifier: str
    parent: Optional[OrgRef] = None
    children: Optional[List[OrgRef]] = None 