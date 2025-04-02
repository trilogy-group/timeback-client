"""Resource model for the TimeBack API.

This module defines the Resource class which represents a learning resource
following the OneRoster 1.2 specification.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Resource:
    """Represents a learning resource.
    
    Required fields per OneRoster 1.2 spec:
    - title: Display title for the resource
    - vendorResourceId: Vendor-specific identifier for the resource
    
    Optional fields:
    - sourcedId: Unique identifier (required for updates)
    - status: Current status ('active' or 'tobedeleted')
    - dateLastModified: Timestamp of last modification
    - metadata: Additional metadata as key-value pairs
    - roles: List of roles that can access this resource ('primary' or 'secondary')
    - importance: Priority level ('primary' or 'secondary')
    - vendorId: Identifier for the resource vendor
    - applicationId: Associated application identifier
    - org: Organization this resource belongs to
    """
    
    title: str
    vendorResourceId: str
    sourcedId: Optional[str] = None
    status: str = 'active'
    dateLastModified: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    roles: Optional[List[str]] = field(default_factory=list)
    importance: Optional[str] = None
    vendorId: Optional[str] = None
    applicationId: Optional[str] = None
    org: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        """Validate fields after initialization."""
        if self.status not in ['active', 'tobedeleted']:
            raise ValueError("status must be either 'active' or 'tobedeleted'")
            
        if self.roles:
            valid_roles = ['primary', 'secondary']
            invalid_roles = [r for r in self.roles if r not in valid_roles]
            if invalid_roles:
                raise ValueError(f"Invalid roles: {invalid_roles}. Must be one of: {valid_roles}")
                
        if self.importance and self.importance not in ['primary', 'secondary']:
            raise ValueError("importance must be either 'primary' or 'secondary'")
    
    @classmethod
    def create(cls, title: str, vendor_resource_id: str, **kwargs) -> 'Resource':
        """Create a new Resource with the minimum required fields.
        
        Args:
            title: Display title for the resource
            vendor_resource_id: Vendor-specific identifier
            **kwargs: Additional fields to set on the resource
            
        Returns:
            A new Resource instance
            
        Example:
            >>> resource = Resource.create(
            ...     title="Chapter 1 Video",
            ...     vendor_resource_id="vendor-123",
            ...     importance="primary"
            ... )
        """
        return cls(
            title=title,
            vendorResourceId=vendor_resource_id,
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the resource to a dictionary format for API requests.
        
        Returns:
            Dict containing all non-None fields formatted for the API
        """
        data = {
            'title': self.title,
            'vendorResourceId': self.vendorResourceId,
            'status': self.status
        }
        
        # Add optional fields if present
        if self.sourcedId:
            data['sourcedId'] = self.sourcedId
            
        if self.dateLastModified:
            data['dateLastModified'] = self.dateLastModified.isoformat()
            
        if self.metadata:
            data['metadata'] = self.metadata
            
        if self.roles:
            data['roles'] = self.roles
            
        if self.importance:
            data['importance'] = self.importance
            
        if self.vendorId:
            data['vendorId'] = self.vendorId
            
        if self.applicationId:
            data['applicationId'] = self.applicationId
            
        if self.org:
            data['org'] = self.org
            
        return {'resource': data}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resource':
        """Create a Resource instance from API response data.
        
        Args:
            data: Dictionary containing resource data
            
        Returns:
            A new Resource instance
            
        Example:
            >>> data = {
            ...     'sourcedId': 'res-123',
            ...     'title': 'Chapter 1 Video',
            ...     'vendorResourceId': 'vendor-123',
            ...     'status': 'active'
            ... }
            >>> resource = Resource.from_dict(data)
        """
        # Handle nested response format
        if 'resource' in data:
            data = data['resource']
            
        # Convert dateLastModified if present
        if 'dateLastModified' in data and data['dateLastModified']:
            data['dateLastModified'] = datetime.fromisoformat(data['dateLastModified'].replace('Z', '+00:00'))
            
        return cls(**data) 