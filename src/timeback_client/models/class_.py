"""Class model for the TimeBack API.

This module provides a Pydantic model for working with classes
in the TimeBack API following the OneRoster 1.2 specification.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator

class CourseRef(BaseModel):
    """Reference to a course in a class."""
    sourcedId: str
    
    def __init__(self, **kwargs):
        """Allow initialization with just a sourcedId string."""
        if isinstance(kwargs, str):
            kwargs = {"sourcedId": kwargs}
        super().__init__(**kwargs)

class OrgRef(BaseModel):
    """Reference to an organization in a class."""
    sourcedId: str
    
    def __init__(self, **kwargs):
        """Allow initialization with just a sourcedId string."""
        if isinstance(kwargs, str):
            kwargs = {"sourcedId": kwargs}
        super().__init__(**kwargs)

class TermRef(BaseModel):
    """Reference to an academic term/session in a class."""
    sourcedId: str
    
    def __init__(self, **kwargs):
        """Allow initialization with just a sourcedId string."""
        if isinstance(kwargs, str):
            kwargs = {"sourcedId": kwargs}
        super().__init__(**kwargs)

class ResourceRef(BaseModel):
    """Reference to a resource in a class."""
    sourcedId: str
    
    def __init__(self, **kwargs):
        """Allow initialization with just a sourcedId string."""
        if isinstance(kwargs, str):
            kwargs = {"sourcedId": kwargs}
        super().__init__(**kwargs)

class Class(BaseModel):
    """
    Represents a class (specific instance of a course) in the system.
    
    A class represents a specific section or instance of a course, typically 
    for a particular term/semester. Classes are what students actually 
    enroll in, rather than enrolling in courses directly.
    
    Required fields per OneRoster 1.2 spec:
    - title: Name of the class
    - course: Reference to the parent course
    - org: Reference to the organization (school)
    - terms: References to academic terms
    """
    sourcedId: Optional[str] = None
    status: str = "active"
    dateLastModified: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    title: str
    classCode: Optional[str] = None
    classType: Optional[str] = None
    location: Optional[str] = None
    grades: Optional[List[str]] = None
    subjects: Optional[List[str]] = None
    course: CourseRef
    org: OrgRef
    subjectCodes: Optional[List[str]] = None
    periods: Optional[List[str]] = None
    resources: Optional[List[ResourceRef]] = None
    terms: List[TermRef]
    
    class Config:
        """Pydantic config for the Class model."""
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
    
    @validator("classType")
    def validate_class_type(cls, v):
        """Validate that the class type is valid."""
        if v is not None:
            valid_types = ["homeroom", "scheduled"]
            if v not in valid_types:
                raise ValueError(f"Class type must be one of {valid_types}")
        return v
    
    @validator("status")
    def validate_status(cls, v):
        """Validate that the status is a valid OneRoster status."""
        valid_statuses = ["active", "tobedeleted"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the class to a dictionary for API requests."""
        class_dict = {
            "class": self.dict(
                exclude_none=True,
                exclude_unset=True
            )
        }
        return class_dict
    
    @classmethod
    def create(cls,
               title: str,
               course_id: str,
               org_id: str,
               term_ids: List[str],
               class_code: Optional[str] = None,
               class_type: Optional[str] = None,
               location: Optional[str] = None,
               grades: Optional[List[str]] = None,
               subjects: Optional[List[str]] = None,
               status: str = "active") -> "Class":
        """
        Create a new class with the required fields.
        
        Args:
            title: The name of the class
            course_id: The sourcedId of the parent course
            org_id: The sourcedId of the organization
            term_ids: List of sourcedIds for academic terms
            class_code: Optional class code or identifier
            class_type: Optional class type (homeroom, scheduled)
            location: Optional location (room number)
            grades: Optional list of grade levels
            subjects: Optional list of subjects
            status: The status of the class (active or tobedeleted)
            
        Returns:
            A new Class instance
            
        Example:
            class_ = Class.create(
                title="Algebra I - Period 3",
                course_id="course-123",
                org_id="school-456",
                term_ids=["term-789"],
                class_code="ALG1-P3",
                class_type="scheduled",
                location="Room 202",
                grades=["9"],
                subjects=["Mathematics"]
            )
        """
        # Convert term IDs to term references
        terms = [TermRef(sourcedId=term_id) for term_id in term_ids]
            
        return cls(
            title=title,
            course=CourseRef(sourcedId=course_id),
            org=OrgRef(sourcedId=org_id),
            terms=terms,
            classCode=class_code,
            classType=class_type,
            location=location,
            grades=grades,
            subjects=subjects,
            status=status
        ) 