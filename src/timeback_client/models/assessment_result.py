"""Assessment Result models for the TimeBack API.

This module defines the data models for assessment results following the OneRoster v1.2 specification
with our simplified reference handling.

API Endpoints:
- GET /assessmentResults - List assessment results
- GET /assessmentResults/{id} - Get a specific assessment result
- POST /assessmentResults - Create a new assessment result
- PUT /assessmentResults/{id} - Update an assessment result
- DELETE /assessmentResults/{id} - Delete an assessment result (sets status to tobedeleted)
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import uuid
import pytz

class Status(str, Enum):
    """Universal status values."""
    ACTIVE = "active"
    TOBEDELETED = "tobedeleted"

class ScoreStatus(str, Enum):
    """Valid score status values."""
    EXEMPT = "exempt"
    FULLY_GRADED = "fully graded"
    NOT_SUBMITTED = "not submitted"
    PARTIALLY_GRADED = "partially graded"
    SUBMITTED = "submitted"

class AssessmentType(str, Enum):
    """Assessment type values for metadata."""
    BRACKETING = "BRACKETING"
    MANUAL = "MANUAL"  # Manual placement tests
    MAP_GROWTH = "MAP_GROWTH"
    MAP_SCREENING = "MAP_SCREENING"
    MAP_SCREENER = "MAP_SCREENER"  # Add missing type
    TEST_OUT = "TEST_OUT"

class Reference(BaseModel):
    """Base reference type without href."""
    sourcedId: str
    type: Optional[str] = None

class AssessmentLineItemRef(Reference):
    """Assessment line item reference."""
    type: str = "assessmentLineItem"

class StudentRef(Reference):
    """Student reference."""
    type: str = "student"

class ScoreScaleRef(Reference):
    """Score scale reference."""
    type: str = "scoreScale"

class LearningObjectiveResult(BaseModel):
    """Individual learning objective result."""
    learningObjectiveId: str = Field(..., description="ID of the learning objective")
    score: Optional[float] = Field(None, description="Numeric score for this objective")
    textScore: Optional[str] = Field(None, description="Text representation of the score")

class LearningObjectiveSet(BaseModel):
    """Set of learning objective results."""
    source: str = Field(..., description="Source of the learning objectives")
    learningObjectiveResults: List[LearningObjectiveResult] = Field(
        ..., 
        description="Results for individual learning objectives"
    )

class AssessmentMetadata(BaseModel):
    """Assessment metadata structure."""
    model_config = {"extra": "allow"}  # Allow extra fields to be parsed
    
    studentEmail: Optional[str] = Field(None, description="Student's email address")
    assignmentId: Optional[str] = Field(None, description="Assignment identifier")
    assessmentType: Optional[AssessmentType] = Field(None, description="Type of assessment")
    subject: Optional[str] = Field(None, description="Subject of the assessment")
    grade: Optional[float] = Field(None, description="Numeric grade representation")
    testname: Optional[str] = Field(None, description="Name of the test from metadata")

    @field_validator('assignmentId', mode='before')
    @classmethod
    def stringify_assignment_id(cls, v):
        if v is not None:
            return str(v)
        return v

class AssessmentResult(BaseModel):
    """OneRoster Assessment Result model with simplified reference handling.
    
    Required Fields:
    - sourcedId: Unique identifier
    - status: active or tobedeleted
    - assessmentLineItem: Reference to the assessment line item
    - student: Reference to the student
    - scoreDate: Date when the score was recorded
    - scoreStatus: Status of the score
    """
    # Required fields
    sourcedId: str = Field(..., description="Unique identifier")
    status: Status = Field(default=Status.ACTIVE, description="Assessment result's status")
    assessmentLineItem: AssessmentLineItemRef = Field(..., description="Reference to assessment line item")
    student: StudentRef = Field(..., description="Reference to the student")
    scoreDate: str = Field(..., description="Date when the score was recorded")
    scoreStatus: ScoreStatus = Field(..., description="Status of the score")
    
    # Optional fields
    dateLastModified: Optional[str] = Field(None, description="Last modification timestamp")
    metadata: Optional[AssessmentMetadata] = Field(None, description="Custom metadata")
    score: Optional[float] = Field(None, description="Numeric score value")
    textScore: Optional[str] = Field(None, description="Text representation of the score")
    scoreScale: Optional[ScoreScaleRef] = Field(None, description="Reference to score scale")
    scorePercentile: Optional[float] = Field(None, description="Percentile rank of the score")
    comment: Optional[str] = Field(None, description="Comment about the assessment result")
    learningObjectiveSet: Optional[List[LearningObjectiveSet]] = Field(
        None, 
        description="Learning objective results"
    )
    inProgress: Optional[str] = Field(None, description="In progress indicator")
    incomplete: Optional[str] = Field(None, description="Incomplete indicator")
    late: Optional[str] = Field(None, description="Late submission indicator")
    missing: Optional[str] = Field(None, description="Missing submission indicator")

    @field_validator('dateLastModified', 'scoreDate', mode='before')
    def convert_datetime_to_string(cls, v):
        """Convert datetime to ISO string format."""
        if isinstance(v, datetime):
            return v.isoformat() + 'Z'
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API requests."""
        data = self.model_dump(exclude_none=True)
        
        # Set dateLastModified if not provided
        if not self.dateLastModified:
            data['dateLastModified'] = datetime.utcnow().isoformat() + 'Z'
            
        return {"assessmentResult": data}

    def to_create_dict(self) -> Dict[str, Any]:
        """Convert model to dict for POST operations."""
        return self.to_dict()
        
    def to_update_dict(self) -> Dict[str, Any]:
        """Convert model to dict for PUT operations."""
        return self.to_dict()

class AssessmentResultsResponse(BaseModel):
    """Response model for paginated assessment results list."""
    assessmentResults: List[AssessmentResult] = Field(..., description="List of assessment results")
    totalCount: int = Field(..., description="Total number of results")
    pageCount: int = Field(..., description="Total number of pages")
    pageNumber: int = Field(..., description="Current page number")
    offset: int = Field(..., description="Offset for pagination")
    limit: int = Field(..., description="Limit per page") 