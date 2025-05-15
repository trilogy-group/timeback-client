"""
Caliper models for the TimeBack API.

Defines Pydantic models for Caliper TimebackTimeSpentEvent and related entities, based on the Caliper YAML spec.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum

# --- ENUMS ---

class TimeSpentType(str, Enum):
    """Type of time spent metric (active, inactive, waste)."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    WASTE = "waste"

# --- METRIC MODELS ---

class TimeSpentMetric(BaseModel):
    """
    Represents a time spent metric for a segment of activity.
    Used in TimebackTimeSpentMetricsCollection.
    """
    type: TimeSpentType = Field(description="Type of time spent (active, inactive, waste)")
    subType: Optional[str] = Field(None, description="Subtype for more specific activity representation")
    value: float = Field(description="Duration in seconds")
    startDate: Optional[str] = Field(None, description="ISO 8601 start timestamp")
    endDate: Optional[str] = Field(None, description="ISO 8601 end timestamp")
    extensions: Optional[Dict[str, Any]] = Field(None, description="Additional attributes")

class TimebackTimeSpentMetricsCollection(BaseModel):
    """
    Collection of time spent metrics for a single event.
    """
    id: Optional[str] = Field(None, description="Unique identifier for the collection (URI) - Backend generated")
    type: Literal["TimebackTimeSpentMetricsCollection"] = "TimebackTimeSpentMetricsCollection"
    items: List[TimeSpentMetric] = Field(description="List of time spent metrics")
    extensions: Optional[Dict[str, Any]] = Field(None, description="Additional attributes")

# --- ACTOR & CONTEXT MODELS ---

class TimebackUser(BaseModel):
    """
    Represents a user (actor) in a Caliper event.
    """
    id: str = Field(description="Unique user identifier (URI)")
    type: Literal["TimebackUser"] = "TimebackUser"
    email: str = Field(description="User's email address (format validation handled by consuming backend or client)")
    name: Optional[str] = Field(None, description="User's full name")
    role: Optional[str] = Field(None, description="User's role (student, teacher, etc.)")
    extensions: Optional[Dict[str, Any]] = Field(None, description="Additional attributes")

class TimebackActivityContext(BaseModel):
    """
    Context of the activity where the event was recorded.
    """
    id: Optional[str] = Field(None, description="Unique identifier for the activity context (URI) - Backend generated")
    type: Literal["TimebackActivityContext"] = "TimebackActivityContext"
    subject: str = Field(description="Subject of the activity (e.g., Reading)")
    app: Dict[str, Any] = Field(description="Application info (id, name, etc.)")
    activity: Dict[str, Any] = Field(description="Activity info (id, name, etc.)")
    course: Optional[Dict[str, Any]] = Field(None, description="Course info if applicable")
    extensions: Optional[Dict[str, Any]] = Field(None, description="Additional attributes")

# --- MAIN EVENT MODEL ---

class TimebackTimeSpentEvent(BaseModel):
    """
    Represents a student time spent activity in the context of an app using the timeback platform.
    """
    context: Literal["http://purl.imsglobal.org/ctx/caliper/v1p2"] = Field("http://purl.imsglobal.org/ctx/caliper/v1p2", alias="@context", description="Caliper context URI")
    id: Optional[str] = Field(None, description="Unique event identifier (URN:UUID) - Backend generated")
    type: Literal["TimeSpentEvent"] = "TimeSpentEvent"
    actor: TimebackUser = Field(description="The user who spent time on the activity")
    action: Literal["SpentTime"] = "SpentTime"
    object: TimebackActivityContext = Field(description="The activity context where the event was recorded")
    eventTime: str = Field(description="ISO 8601 datetime when this event occurred")
    profile: Literal["TimebackProfile"] = "TimebackProfile"
    edApp: Dict[str, Any] = Field(description="Application context info")
    generated: TimebackTimeSpentMetricsCollection = Field(description="Collection of time spent metrics")
    target: Optional[Any] = Field(None, description="Entity representing a segment/location within the object")
    referrer: Optional[Any] = Field(None, description="Entity representing the referring context")
    session: Optional[Any] = Field(None, description="Current user session info")
    federatedSession: Optional[Any] = Field(None, description="LTI session info if applicable")
    extensions: Optional[Dict[str, Any]] = Field(None, description="Additional attributes") 