"""Line Item models for the TimeBack API.

This module defines the data models for assessment line items following the OneRoster v1.2 specification.

API Endpoints:
- GET /assessmentLineItems - List line items
- GET /assessmentLineItems/{id} - Get a specific line item
- POST /assessmentLineItems - Create a new line item
- PUT /assessmentLineItems/{id} - Update a line item
- DELETE /assessmentLineItems/{id} - Delete a line item
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
import uuid

class Status(str, Enum):
    """Universal status values."""
    ACTIVE = "active"
    TOBEDELETED = "tobedeleted"

class SourcedIdRef(BaseModel):
    """Simple reference with just sourcedId."""
    sourcedId: str

class LineItem(BaseModel):
    """OneRoster Line Item model.

    Required Fields (for creation):
    - title: Title of the line item
    - status: Must be 'active'

    Optional Fields:
    - sourcedId: Unique identifier (auto-generated if not provided)
    - description: Description of the line item
    - resultValueMin: Minimum score value
    - resultValueMax: Maximum score value
    - metadata: Custom metadata dict
    - dateLastModified: Last modification timestamp
    - class: Reference to class
    - parentAssessmentLineItem: Reference to parent line item
    - scoreScale: Reference to score scale
    - component: Reference to component
    - componentResource: Reference to component resource
    - learningObjectiveSet: Learning objectives
    - course: Reference to course
    """
    # Required fields
    title: str = Field(..., description="Title of the line item")
    status: Status = Field(default=Status.ACTIVE, description="Status (must be 'active')")

    # Optional fields
    sourcedId: Optional[str] = Field(None, description="Unique identifier")
    dateLastModified: Optional[str] = Field(None, description="Last modification timestamp")
    description: Optional[str] = Field(None, description="Description of the line item")
    resultValueMin: Optional[float] = Field(None, description="Minimum result value")
    resultValueMax: Optional[float] = Field(None, description="Maximum result value")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")

    # References (optional)
    class_: Optional[SourcedIdRef] = Field(None, alias="class", description="Reference to class")
    parentAssessmentLineItem: Optional[SourcedIdRef] = Field(None, description="Reference to parent line item")
    scoreScale: Optional[SourcedIdRef] = Field(None, description="Reference to score scale")
    component: Optional[SourcedIdRef] = Field(None, description="Reference to component")
    componentResource: Optional[SourcedIdRef] = Field(None, description="Reference to component resource")
    course: Optional[SourcedIdRef] = Field(None, description="Reference to course")
    learningObjectiveSet: Optional[List[Dict[str, Any]]] = Field(None, description="Learning objectives")

    class Config:
        populate_by_name = True  # Allow both 'class' and 'class_'

    def model_post_init(self, __context):
        """Generate sourcedId if not provided."""
        if not self.sourcedId:
            self.sourcedId = str(uuid.uuid4())
        if not self.dateLastModified:
            self.dateLastModified = datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API requests."""
        data = self.model_dump(mode='json', exclude_none=True, by_alias=True)
        return data

    def to_create_dict(self) -> Dict[str, Any]:
        """Convert model to dict for POST operations."""
        return {"assessmentLineItem": self.to_dict()}

    def to_update_dict(self) -> Dict[str, Any]:
        """Convert model to dict for PUT operations."""
        return {"assessmentLineItem": self.to_dict()}

class LineItemsResponse(BaseModel):
    """Response model for paginated line items list."""
    lineItems: List[LineItem] = Field(..., description="List of line items")
    totalCount: int = Field(..., description="Total number of results")
    pageCount: int = Field(..., description="Total number of pages")
    pageNumber: int = Field(..., description="Current page number")
    offset: int = Field(..., description="Offset for pagination")
    limit: int = Field(..., description="Limit per page")
