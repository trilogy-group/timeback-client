"""AcademicSession model for OneRoster API.

This module defines the AcademicSession model according to the OneRoster 1.2 specification.
Academic sessions represent time periods like terms, semesters, grading periods, or school years
that are used to organize classes and enrollments.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime, UTC
import logging
import uuid

logger = logging.getLogger(__name__)

# Valid status values according to OneRoster 1.2 specification
VALID_STATUSES = ['active', 'tobedeleted']

# Valid type values for academic sessions
VALID_TYPES = ['gradingPeriod', 'semester', 'schoolYear', 'term']

class AcademicSession:
    """AcademicSession model for OneRoster API.
    
    In OneRoster, an AcademicSession represents a period of time in which classes occur,
    such as a term, semester, grading period, or school year.
    
    Required fields (per OneRoster 1.2 spec):
        sourcedId (str): The unique identifier for this academic session
        status (str): The status of this session - 'active' or 'tobedeleted'
        dateLastModified (str): When this session was last modified (ISO 8601) - auto-generated if not provided
        title (str): The title of this academic session
        type (str): The type of session - gradingPeriod, semester, schoolYear, or term
        startDate (str): When this session starts (ISO 8601 date)
        endDate (str): When this session ends (ISO 8601 date)
        schoolYear (str): The school year this session belongs to
        org (dict): The organization this session belongs to - must have sourcedId
        
    Optional fields:
        parent (dict): Reference to a parent academic session (e.g. semester's parent is schoolYear)
        metadata (dict): Additional properties not defined in the spec
    """
    
    def __init__(
        self,
        sourcedId: Optional[str] = None,
        title: str = None,
        type: str = None,
        status: str = "active",
        dateLastModified: str = None,
        startDate: str = None,
        endDate: str = None,
        schoolYear: str = None,
        org: Dict[str, Any] = None,
        parent: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize an AcademicSession model.
        
        Args:
            sourcedId: Unique identifier for this session (auto-generated if None)
            title: The title of this session (REQUIRED)
            type: Type of session - gradingPeriod, semester, schoolYear, or term (REQUIRED)
            status: Status of this session - 'active' or 'tobedeleted' (default: 'active')
            dateLastModified: When this session was last modified (auto-generated if None)
            startDate: When this session starts - ISO 8601 date (REQUIRED)
            endDate: When this session ends - ISO 8601 date (REQUIRED)
            schoolYear: The school year this session belongs to (REQUIRED)
            org: The organization this session belongs to (REQUIRED) - must have sourcedId
            parent: Reference to parent academic session
            **kwargs: Additional properties that will be stored in metadata
        
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Generate sourcedId if not provided
        if not sourcedId:
            sourcedId = f"academicSession-{str(uuid.uuid4())}"
            logger.info(f"Auto-generating sourcedId: {sourcedId}")
            
        # Validate required fields
        if not title:
            raise ValueError("title is required for AcademicSession")
            
        if not type:
            raise ValueError("type is required for AcademicSession")
            
        if type not in VALID_TYPES:
            raise ValueError(f"Invalid type '{type}'. Must be one of: {VALID_TYPES}")
            
        if not startDate:
            raise ValueError("startDate is required for AcademicSession")
            
        if not endDate:
            raise ValueError("endDate is required for AcademicSession")
            
        if not schoolYear:
            raise ValueError("schoolYear is required for AcademicSession")
            
        if not org or not isinstance(org, dict) or 'sourcedId' not in org:
            raise ValueError("org with sourcedId is required for AcademicSession")
        
        # Validate status is one of the allowed values
        if status not in VALID_STATUSES:
            logger.warning(f"Invalid status '{status}' for AcademicSession. Valid values are: {VALID_STATUSES}")
            logger.warning(f"Defaulting to 'active'")
            status = 'active'
        
        # Set required fields
        self.sourcedId = sourcedId
        self.title = title
        self.type = type
        self.status = status
        self.startDate = startDate
        self.endDate = endDate
        self.schoolYear = schoolYear
        self.org = self._validate_reference(org, 'org')
        
        # Set dateLastModified (auto-generate if not provided)
        if dateLastModified is None:
            # Use current time in ISO format with UTC timezone
            self.dateLastModified = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
            logger.debug(f"Auto-generating dateLastModified: {self.dateLastModified}")
        else:
            self.dateLastModified = dateLastModified
        
        # Set optional fields
        self.parent = self._validate_reference(parent, 'academicSession') if parent else None
        
        # Store additional fields in metadata
        self.metadata = kwargs
    
    def _validate_reference(self, ref_data: Optional[Dict[str, Any]], ref_type: str) -> Optional[Dict[str, Any]]:
        """Validate and format a reference object according to OneRoster spec.
        
        According to the spec, reference objects must have:
        - href: URI for the type of object
        - sourcedId: Globally unique identifier
        - type: Type of the object
        
        Args:
            ref_data: Reference data to validate
            ref_type: The expected type of the reference
            
        Returns:
            Validated reference data
        """
        if not ref_data:
            return None
            
        # If it's just a string ID, convert to proper reference
        if isinstance(ref_data, str):
            return {
                'sourcedId': ref_data,
                'type': ref_type,
                'href': f"/oneroster/v1p2/{ref_type}s/{ref_data}"
            }
            
        # Ensure required fields
        if 'sourcedId' not in ref_data:
            logger.warning(f"Reference object missing required 'sourcedId' field: {ref_data}")
            return None
            
        # Add missing fields if needed
        if 'type' not in ref_data:
            ref_data['type'] = ref_type
            
        if 'href' not in ref_data:
            source_id = ref_data['sourcedId']
            ref_data['href'] = f"/oneroster/v1p2/{ref_type}s/{source_id}"
            
        return ref_data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['AcademicSession']:
        """Create an AcademicSession instance from a dictionary.
        
        Args:
            data: Dictionary containing academic session data
            
        Returns:
            An AcademicSession instance or None if data is invalid
        """
        if not data:
            return None
            
        # Handle different response formats
        if 'academicSession' in data:
            data = data['academicSession']
            
        # Extract known fields
        session_args = {}
        
        # Required fields
        required_fields = ['title', 'type', 'startDate', 'endDate', 'schoolYear', 'org']
        for field in required_fields:
            if field in data:
                session_args[field] = data.pop(field)
            else:
                logger.warning(f"Required field '{field}' missing from academic session data")
                return None
                
        # Always copy sourcedId if present
        if 'sourcedId' in data:
            session_args['sourcedId'] = data.pop('sourcedId')
                
        # Semi-required fields (we have defaults)
        if 'status' in data:
            session_args['status'] = data.pop('status')
            
        if 'dateLastModified' in data:
            session_args['dateLastModified'] = data.pop('dateLastModified')
                
        # Optional fields with special handling
        if 'metadata' in data:
            metadata = data.pop('metadata')
            # Add metadata fields to kwargs
            if isinstance(metadata, dict):
                for k, v in metadata.items():
                    data[k] = v
                    
        # Handle parent reference
        if 'parent' in data:
            session_args['parent'] = data.pop('parent')
                
        # Add remaining fields as kwargs
        session_args.update(data)
        
        try:
            return cls(**session_args)
        except ValueError as e:
            logger.error(f"Failed to create AcademicSession: {str(e)}")
            return None
    
    @classmethod
    def create(cls, title: str, type: str, startDate: str, endDate: str, schoolYear: str, **kwargs) -> 'AcademicSession':
        """Helper method to create a new academic session with minimal required fields.
        
        Args:
            title: The title of the session (REQUIRED)
            type: The type of session (REQUIRED)
            startDate: When the session starts (REQUIRED)
            endDate: When the session ends (REQUIRED)
            schoolYear: The school year (REQUIRED)
            **kwargs: Additional session attributes
            
        Returns:
            A new AcademicSession instance with auto-generated sourcedId and dateLastModified
        """
        return cls(
            sourcedId=None,  # Will be auto-generated
            title=title,
            type=type,
            startDate=startDate,
            endDate=endDate,
            schoolYear=schoolYear,
            org=None,  # Will be set later
            **kwargs
        )
    
    def to_dict(self, wrapped: bool = True) -> Dict[str, Any]:
        """Convert AcademicSession object to dictionary.
        
        Args:
            wrapped: Whether to wrap the result in a {'academicSession': {...}} object
                    for single session responses
        
        Returns:
            Dictionary representation of the academic session
        """
        result = {
            'sourcedId': self.sourcedId,
            'status': self.status,
            'dateLastModified': self.dateLastModified,
            'title': self.title,
            'type': self.type,
            'startDate': self.startDate,
            'endDate': self.endDate,
            'schoolYear': self.schoolYear,
            'org': self.org,
        }
        
        # Add optional fields if they have values
        if self.parent:
            result['parent'] = self.parent
        
        # Add any additional metadata
        if self.metadata:
            result['metadata'] = self.metadata
        
        return {'academicSession': result} if wrapped else result
    
    @classmethod
    def to_sessions_response(cls, sessions: List['AcademicSession']) -> Dict[str, Any]:
        """Convert a list of AcademicSession objects to a OneRoster response.
        
        This follows the AcademicSessionSetDType structure from the OneRoster spec.
        
        Args:
            sessions: List of AcademicSession objects
            
        Returns:
            Response in the format {'academicSessions': [...]}
        """
        return {
            'academicSessions': [session.to_dict(wrapped=False) for session in sessions]
        }
    
    def __repr__(self) -> str:
        """String representation of the AcademicSession.
        
        Returns:
            String representation
        """
        return f"AcademicSession(sourcedId='{self.sourcedId}', title='{self.title}', type='{self.type}')"

    def update_timestamp(self):
        """Update the last modified timestamp to current UTC time."""
        self.dateLastModified = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ') 