"""Enrollment model for the TimeBack API.

This module provides a Pydantic model for working with student/teacher enrollments
in the TimeBack API following the OneRoster 1.2 specification.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, validator

class UserRef(BaseModel):
    """Reference to a user in an enrollment."""
    sourcedId: str
    
    def __init__(self, **kwargs):
        """Allow initialization with just a sourcedId string."""
        if isinstance(kwargs, str):
            kwargs = {"sourcedId": kwargs}
        super().__init__(**kwargs)

class ClassRef(BaseModel):
    """Reference to a class in an enrollment."""
    sourcedId: str
    
    def __init__(self, **kwargs):
        """Allow initialization with just a sourcedId string."""
        if isinstance(kwargs, str):
            kwargs = {"sourcedId": kwargs}
        super().__init__(**kwargs)

class Enrollment(BaseModel):
    """
    Represents a student or teacher's enrollment in a class.
    
    Enrollments link users to classes with a specific role and period of time.
    
    Required fields per OneRoster 1.2 spec:
    - role: The role of the user in the class
    - user: Reference to the user
    - class: Reference to the class
    """
    sourcedId: Optional[str] = None
    status: str = "active"
    dateLastModified: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    role: str
    primary: bool = False
    beginDate: Optional[date] = None
    endDate: Optional[date] = None
    user: UserRef
    class_: ClassRef = Field(..., alias="class")
    
    class Config:
        """Pydantic config for the Enrollment model."""
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
    
    @validator("role")
    def validate_role(cls, v):
        """Validate that the role is a valid OneRoster role."""
        valid_roles = ["administrator", "proctor", "student", "teacher"]
        if v not in valid_roles:
            raise ValueError(f"Role must be one of {valid_roles}")
        return v
    
    @validator("status")
    def validate_status(cls, v):
        """Validate that the status is a valid OneRoster status."""
        valid_statuses = ["active", "tobedeleted"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the enrollment to a dictionary for API requests."""
        enrollment_dict = {
            "enrollment": self.dict(
                by_alias=True,
                exclude_none=True,
                exclude_unset=True
            )
        }
        return enrollment_dict
    
    @classmethod
    def create(cls, 
               role: str,
               user_id: str,
               class_id: str,
               primary: bool = False,
               begin_date: Optional[Union[str, date]] = None,
               end_date: Optional[Union[str, date]] = None,
               status: str = "active") -> "Enrollment":
        """
        Create a new enrollment with the required fields.
        
        Args:
            role: The role of the user in the class (student, teacher, etc.)
            user_id: The sourcedId of the user
            class_id: The sourcedId of the class
            primary: Whether this is the primary enrollment for the user
            begin_date: The date the enrollment begins
            end_date: The date the enrollment ends
            status: The status of the enrollment (active or tobedeleted)
            
        Returns:
            A new Enrollment instance
            
        Example:
            enrollment = Enrollment.create(
                role="student",
                user_id="user-123",
                class_id="class-456",
                primary=True,
                begin_date="2023-09-01",
                end_date="2024-06-15"
            )
        """
        # Process dates if they're strings
        if isinstance(begin_date, str):
            begin_date = date.fromisoformat(begin_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
            
        return cls(
            role=role,
            user=UserRef(sourcedId=user_id),
            class_=ClassRef(sourcedId=class_id),
            primary=primary,
            beginDate=begin_date,
            endDate=end_date,
            status=status
        ) 