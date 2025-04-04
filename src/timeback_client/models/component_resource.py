"""Component Resource model for the TimeBack API.

This module defines the ComponentResource class which represents a resource
associated with a course component following the OneRoster 1.2 specification.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ComponentResource:
    """Represents a resource associated with a course component.
    
    Required fields per OneRoster 1.2 spec:
    - sourcedId: Unique identifier for the component resource
    - courseComponent: Object containing sourcedId of the parent component
    - resource: Object containing sourcedId of the associated resource
    - title: Display title for the component resource
    
    Optional fields:
    - status: Current status ('active' or 'tobedeleted')
    - dateLastModified: Timestamp of last modification
    - metadata: Additional metadata as key-value pairs
    - sortOrder: Position within siblings (defaults to 0)
    """
    
    # Required fields (no defaults)
    sourcedId: str
    courseComponent: Dict[str, str]  # Must contain sourcedId
    resource: Dict[str, str]  # Must contain sourcedId
    title: str
    
    # Optional fields (with defaults)
    status: str = 'active'
    dateLastModified: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    sortOrder: int = 0
    
    def __post_init__(self):
        """Validate required nested fields and types after initialization."""
        if not isinstance(self.courseComponent, dict) or 'sourcedId' not in self.courseComponent:
            raise ValueError("courseComponent must be a dict containing 'sourcedId'")
            
        if not isinstance(self.resource, dict) or 'sourcedId' not in self.resource:
            raise ValueError("resource must be a dict containing 'sourcedId'")
            
        if self.status not in ['active', 'tobedeleted']:
            raise ValueError("status must be either 'active' or 'tobedeleted'")
    
    @classmethod
    def create(cls, title: str, component_id: str, resource_id: str, **kwargs) -> 'ComponentResource':
        """Create a new ComponentResource with the minimum required fields.
        
        Args:
            title: Display title for the component resource
            component_id: sourcedId of the parent component
            resource_id: sourcedId of the associated resource
            **kwargs: Additional fields to set on the component resource
            
        Returns:
            A new ComponentResource instance
            
        Example:
            >>> resource = ComponentResource.create(
            ...     title="Chapter 1 Video",
            ...     component_id="comp-123",
            ...     resource_id="res-456",
            ...     sortOrder=1
            ... )
        """
        return cls(
            title=title,
            courseComponent={'sourcedId': component_id},
            resource={'sourcedId': resource_id},
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the component resource to a dictionary format for API requests.
        
        Returns:
            Dict containing all non-None fields formatted for the API
        """
        data = {
            'sourcedId': self.sourcedId,
            'status': self.status,
            'courseComponent': self.courseComponent,
            'resource': self.resource,
            'title': self.title,
            'sortOrder': self.sortOrder
        }
        
        if self.dateLastModified:
            data['dateLastModified'] = self.dateLastModified.isoformat()
            
        if self.metadata:
            data['metadata'] = self.metadata
            
        return {'componentResource': data}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentResource':
        """Create a ComponentResource instance from API response data.
        
        Args:
            data: Dictionary containing component resource data
            
        Returns:
            A new ComponentResource instance
            
        Example:
            >>> data = {
            ...     'sourcedId': 'cr-123',
            ...     'title': 'Chapter 1 Video',
            ...     'courseComponent': {'sourcedId': 'comp-123'},
            ...     'resource': {'sourcedId': 'res-456'},
            ...     'status': 'active'
            ... }
            >>> resource = ComponentResource.from_dict(data)
        """
        # Handle nested response format
        if 'componentResource' in data:
            data = data['componentResource']
            
        # Convert dateLastModified if present
        if 'dateLastModified' in data and data['dateLastModified']:
            data['dateLastModified'] = datetime.fromisoformat(data['dateLastModified'].replace('Z', '+00:00'))
            
        return cls(**data) 