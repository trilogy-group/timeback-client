"""
Caliper API endpoints for the TimeBack platform.

Provides endpoints to receive and validate Caliper events, specifically TimebackTimeSpentEvent.
"""
from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any, Optional
from timeback_client.models import (
    TimebackTimeSpentEvent,
)

router = APIRouter()

class CaliperEnvelope(BaseModel):
    """
    Represents a Caliper event envelope as per the Caliper API spec.
    """
    sensor: str
    sendTime: str
    dataVersion: str
    data: List[TimebackTimeSpentEvent]

@router.post("/caliper/event", status_code=status.HTTP_200_OK)
def receive_caliper_event(
    envelope: CaliperEnvelope = Body(..., description="Caliper event envelope containing TimebackTimeSpentEvent(s)")
) -> Dict[str, Any]:
    """
    Receives a Caliper event envelope and validates the contained events.
    Returns a success message if valid.
    """
    # Here you would add business logic to process/store the event(s)
    return {"status": "success", "message": "The events were processed successfully"}

@router.post("/caliper/event/validate", status_code=status.HTTP_200_OK)
def validate_caliper_event(
    envelope: CaliperEnvelope = Body(..., description="Caliper event envelope to validate")
) -> Dict[str, Any]:
    """
    Validates the Caliper event envelope and returns validation results.
    """
    try:
        envelope_dict = envelope.dict()
        # Attempt to re-parse to trigger validation
        CaliperEnvelope(**envelope_dict)
        return {"status": "success", "message": "The envelope is valid"}
    except ValidationError as e:
        return {"status": "error", "message": "Validation failed", "errors": e.errors()} 