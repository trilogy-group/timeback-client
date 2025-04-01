"""Component model for OneRoster API.

This module defines the Component model according to the OneRoster 1.2 specification.
Components represent structural elements within a course (units, lessons, etc) that
organize the course content into a hierarchical structure.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime, UTC
import logging
import uuid

logger = logging.getLogger(__name__)

# Valid status values according to OneRoster 1.2 specification
VALID_STATUSES = ['active', 'tobedeleted']

class Component:
    """Component model for OneRoster API.
    
    In OneRoster, a Component is a structural element within a course that helps
    organize the course content into a hierarchical structure (units, lessons, etc).
    
    Required fields (per OneRoster 1.2 spec):
        sourcedId (str): The unique identifier for this component
        status (str): The status of this component - 'active' or 'tobedeleted'
        dateLastModified (str): When this component was last modified (ISO 8601)
        title (str): The title of this component
        course (dict): The course this component belongs to - must have sourcedId
        sortOrder (int): The position of this component within its siblings
        
    Optional fields:
        courseComponent (dict): The parent component (if not top-level)
        prerequisites (list): Component sourcedIds that must be completed first
        prerequisiteCriteria (str): How prerequisites should be evaluated ('ALL', 'ANY')
        unlockDate (str): When this component becomes available to students
        metadata (dict): Additional properties not defined in the spec
    """
    
    def __init__(
        self,
        sourcedId: Optional[str] = None,
        title: str = None,
        status: str = "active",
        dateLastModified: str = None,
        course: Dict[str, Any] = None,  # Required
        courseComponent: Optional[Dict[str, Any]] = None,
        sortOrder: int = None,  # Required
        prerequisites: Optional[List[str]] = None,
        prerequisiteCriteria: Optional[str] = None,
        unlockDate: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a Component model.
        
        Args:
            sourcedId: Unique identifier for this component (auto-generated if None)
            title: The title of this component (REQUIRED)
            status: Status of this component - 'active' or 'tobedeleted'
            dateLastModified: When this component was last modified (auto-generated if None)
            course: The course this component belongs to (REQUIRED) - must have sourcedId
            courseComponent: The parent component if not top-level
            sortOrder: Position within siblings (REQUIRED)
            prerequisites: Component sourcedIds that must be completed first
            prerequisiteCriteria: How prerequisites should be evaluated ('ALL', 'ANY')
            unlockDate: When this component becomes available (ISO 8601)
            metadata: Additional properties not defined in the spec
            **kwargs: Additional properties that will be stored in metadata
        
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Generate sourcedId if not provided
        if not sourcedId:
            sourcedId = f"component-{str(uuid.uuid4())}"
            logger.info(f"Auto-generating sourcedId: {sourcedId}")
            
        # Validate required fields
        if not title:
            raise ValueError("title is required for Component")
            
        if not course or not isinstance(course, dict) or 'sourcedId' not in course:
            raise ValueError("course with sourcedId is required for Component")
            
        if sortOrder is None:
            raise ValueError("sortOrder is required for Component")
        
        # Validate status is one of the allowed values
        if status not in VALID_STATUSES:
            logger.warning(f"Invalid status '{status}' for Component. Valid values are: {VALID_STATUSES}")
            logger.warning(f"Defaulting to 'active'")
            status = 'active'
        
        # Set required fields
        self.sourcedId = sourcedId
        self.title = title
        self.status = status
        self.course = self._validate_reference(course, 'course')
        self.sortOrder = sortOrder
        
        # Set dateLastModified (auto-generate if not provided)
        if dateLastModified is None:
            self.dateLastModified = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
            logger.debug(f"Auto-generating dateLastModified: {self.dateLastModified}")
        else:
            self.dateLastModified = dateLastModified
        
        # Set optional fields
        self.courseComponent = self._validate_reference(courseComponent, 'courseComponent')
        self.prerequisites = prerequisites or []
        self.prerequisiteCriteria = prerequisiteCriteria
        self.unlockDate = unlockDate
        
        # Handle metadata
        self.metadata = metadata or {}
        if kwargs:
            self.metadata.update(kwargs)
    
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
    def from_dict(cls, data: Dict[str, Any]) -> Optional['Component']:
        """Create a Component instance from a dictionary.
        
        Args:
            data: Dictionary containing component data
            
        Returns:
            A Component instance or None if data is invalid
        """
        if not data:
            return None
            
        # Handle different response formats
        if 'courseComponent' in data:
            data = data['courseComponent']
            
        # Extract known fields
        component_args = {}
        
        # Required fields
        required_fields = ['title', 'course', 'sortOrder']
        for field in required_fields:
            if field in data:
                component_args[field] = data.pop(field)
            else:
                logger.warning(f"Required field '{field}' missing from component data")
                return None
                
        # Always copy sourcedId if present
        if 'sourcedId' in data:
            component_args['sourcedId'] = data.pop('sourcedId')
                
        # Semi-required fields (we have defaults)
        if 'status' in data:
            component_args['status'] = data.pop('status')
            
        if 'dateLastModified' in data:
            component_args['dateLastModified'] = data.pop('dateLastModified')
                
        # Optional fields with special handling
        if 'metadata' in data:
            metadata = data.pop('metadata')
            # Add metadata fields to kwargs
            if isinstance(metadata, dict):
                for k, v in metadata.items():
                    data[k] = v
                    
        # Handle reference types
        for field in ['courseComponent']:
            if field in data:
                component_args[field] = data.pop(field)
                
        # List fields
        for field in ['prerequisites']:
            if field in data:
                component_args[field] = data.pop(field)
                
        # Add remaining fields as kwargs
        component_args.update(data)
        
        try:
            return cls(**component_args)
        except ValueError as e:
            logger.error(f"Failed to create Component: {str(e)}")
            return None
    
    @classmethod
    def create(cls, title: str, course_id: str, sort_order: int, **kwargs) -> 'Component':
        """Helper method to create a new component with minimal required fields.
        
        Args:
            title: The title of the component (REQUIRED)
            course_id: The sourcedId of the parent course (REQUIRED)
            sort_order: Position within siblings (REQUIRED)
            **kwargs: Additional component attributes
            
        Returns:
            A new Component instance with auto-generated sourcedId and dateLastModified
        """
        return cls(
            sourcedId=None,  # Will be auto-generated
            title=title,
            course={'sourcedId': course_id},
            sortOrder=sort_order,
            **kwargs
        )
    
    def to_dict(self, wrapped: bool = True) -> Dict[str, Any]:
        """Convert Component object to dictionary.
        
        Args:
            wrapped: Whether to wrap the result in a {'courseComponent': {...}} object
                    for single component responses
        
        Returns:
            Dictionary representation of the component
        """
        result = {
            'sourcedId': self.sourcedId,
            'status': self.status,
            'dateLastModified': self.dateLastModified,
            'title': self.title,
            'course': self.course,
            'sortOrder': self.sortOrder,
        }
        
        # Add optional fields if they have values
        if self.courseComponent:
            result['courseComponent'] = self.courseComponent
        if self.prerequisites:
            result['prerequisites'] = self.prerequisites
        if self.prerequisiteCriteria:
            result['prerequisiteCriteria'] = self.prerequisiteCriteria
        if self.unlockDate:
            result['unlockDate'] = self.unlockDate
        
        # Add metadata
        if self.metadata:
            result['metadata'] = self.metadata
        
        return {'courseComponent': result} if wrapped else result
    
    @classmethod
    def to_components_response(cls, components: List['Component']) -> Dict[str, Any]:
        """Convert a list of Component objects to a OneRoster components response.
        
        This follows the ComponentSetDType structure from the OneRoster spec.
        
        Args:
            components: List of Component objects
            
        Returns:
            Response in the format {'courseComponents': [...]}
        """
        return {
            'courseComponents': [component.to_dict(wrapped=False) for component in components]
        }
    
    def __repr__(self) -> str:
        """String representation of the Component.
        
        Returns:
            String representation
        """
        return f"Component(sourcedId='{self.sourcedId}', title='{self.title}')"

    def update_timestamp(self):
        """Update the last modified timestamp to current UTC time."""
        self.dateLastModified = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ') 