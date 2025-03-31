"""Course model for OneRoster API.

This module defines the Course model according to the OneRoster 1.2 specification.
Courses represent a curriculum within a school or district that typically has a shared
curriculum although it may be taught to different students by different teachers.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime, UTC
import logging
import uuid

logger = logging.getLogger(__name__)

# Valid status values according to OneRoster 1.2 specification
VALID_STATUSES = ['active', 'tobedeleted']

class Course:
    """Course model for OneRoster API.
    
    In OneRoster, a Course is a course of study that has a shared curriculum.
    Multiple classes may be teaching the same course.
    
    Required fields (per OneRoster 1.2 spec):
        sourcedId (str): The unique identifier for this course
        status (str): The status of this course - 'active' or 'tobedeleted'
        dateLastModified (str): When this course was last modified (ISO 8601) - auto-generated if not provided
        title (str): The title of this course
        courseCode (str): The code identifying this course
        org (dict): The organization this course belongs to - must have sourcedId
        
    Optional fields:
        schoolYear (dict): The school year associated with this course
        grades (list): The grade levels this course is for
        subjects (list): The subjects covered by this course
        subjectCodes (list): Machine readable codes that match the subjects
        resources (list): Links to associated resources
        metadata (dict): Additional properties not defined in the spec
    """
    
    def __init__(
        self,
        sourcedId: Optional[str] = None,
        title: str = None,
        courseCode: str = None,
        status: str = "active",
        dateLastModified: str = None,
        org: Dict[str, Any] = None,  # Now required
        schoolYear: Optional[Dict[str, Any]] = None,
        grades: Optional[List[str]] = None,
        subjects: Optional[List[str]] = None,
        subjectCodes: Optional[List[str]] = None,
        resources: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        """Initialize a Course model.
        
        Args:
            sourcedId: Unique identifier for this course (auto-generated if None)
            title: The title of this course (REQUIRED)
            courseCode: The code identifying this course (REQUIRED)
            status: Status of this course - 'active' or 'tobedeleted' (default: 'active')
            dateLastModified: When this course was last modified (auto-generated if None)
            org: The organization this course belongs to (REQUIRED) - must have sourcedId
            schoolYear: The school year associated with this course
            grades: The grade levels this course is for
            subjects: The subjects covered by this course
            subjectCodes: Machine readable codes that match the subjects
            resources: Links to associated resources
            **kwargs: Additional properties that will be stored in metadata
        
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Generate sourcedId if not provided
        if not sourcedId:
            sourcedId = f"course-{str(uuid.uuid4())}"
            logger.info(f"Auto-generating sourcedId: {sourcedId}")
            
        # Validate required fields
        if not title:
            raise ValueError("title is required for Course")
            
        if not courseCode:
            raise ValueError("courseCode is required for Course")
            
        if not org or not isinstance(org, dict) or 'sourcedId' not in org:
            raise ValueError("org with sourcedId is required for Course")
        
        # Validate status is one of the allowed values
        if status not in VALID_STATUSES:
            logger.warning(f"Invalid status '{status}' for Course. Valid values are: {VALID_STATUSES}")
            logger.warning(f"Defaulting to 'active'")
            status = 'active'
        
        # Set required fields
        self.sourcedId = sourcedId
        self.title = title
        self.courseCode = courseCode
        self.status = status
        self.org = self._validate_reference(org, 'org')  # Now required
        
        # Set dateLastModified (auto-generate if not provided)
        if dateLastModified is None:
            # Use current time in ISO format with UTC timezone
            self.dateLastModified = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
            logger.debug(f"Auto-generating dateLastModified: {self.dateLastModified}")
        else:
            self.dateLastModified = dateLastModified
        
        # Set optional fields
        self.schoolYear = self._validate_reference(schoolYear, 'academicSession')
        self.grades = grades or []
        self.subjects = subjects or []
        self.subjectCodes = subjectCodes or []
        self.resources = self._validate_resources(resources)
        
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
    
    def _validate_resources(self, resources: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Validate and format a list of resource references.
        
        Args:
            resources: List of resource references to validate
            
        Returns:
            Validated list of resource references
        """
        if not resources:
            return []
            
        validated_resources = []
        for resource in resources:
            if isinstance(resource, str):
                # Convert string ID to proper reference
                validated_resources.append({
                    'sourcedId': resource,
                    'type': 'resource',
                    'href': f"/oneroster/v1p2/resources/{resource}"
                })
            elif isinstance(resource, dict) and 'sourcedId' in resource:
                # Ensure it has all required fields
                if 'type' not in resource:
                    resource['type'] = 'resource'
                if 'href' not in resource:
                    source_id = resource['sourcedId']
                    resource['href'] = f"/oneroster/v1p2/resources/{source_id}"
                validated_resources.append(resource)
            else:
                logger.warning(f"Invalid resource reference: {resource}")
                
        return validated_resources
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['Course']:
        """Create a Course instance from a dictionary.
        
        Args:
            data: Dictionary containing course data
            
        Returns:
            A Course instance or None if data is invalid
        """
        if not data:
            return None
            
        # Handle different response formats
        if 'course' in data:
            data = data['course']
            
        # Extract known fields
        course_args = {}
        
        # Required fields
        required_fields = ['title', 'courseCode', 'org']
        for field in required_fields:
            if field in data:
                course_args[field] = data.pop(field)
            else:
                logger.warning(f"Required field '{field}' missing from course data")
                return None
                
        # Always copy sourcedId if present
        if 'sourcedId' in data:
            course_args['sourcedId'] = data.pop('sourcedId')
                
        # Semi-required fields (we have defaults)
        if 'status' in data:
            course_args['status'] = data.pop('status')
            
        if 'dateLastModified' in data:
            course_args['dateLastModified'] = data.pop('dateLastModified')
                
        # Optional fields with special handling
        if 'metadata' in data:
            metadata = data.pop('metadata')
            # Add metadata fields to kwargs
            if isinstance(metadata, dict):
                for k, v in metadata.items():
                    data[k] = v
                    
        # Handle reference types
        for field in ['schoolYear']:
            if field in data:
                course_args[field] = data.pop(field)
                
        # List fields
        for field in ['grades', 'subjects', 'subjectCodes', 'resources']:
            if field in data:
                course_args[field] = data.pop(field)
                
        # Add remaining fields as kwargs
        course_args.update(data)
        
        try:
            return cls(**course_args)
        except ValueError as e:
            logger.error(f"Failed to create Course: {str(e)}")
            return None
    
    @classmethod
    def create(cls, title: str, courseCode: str, **kwargs) -> 'Course':
        """Helper method to create a new course with minimal required fields.
        
        Args:
            title: The title of the course (REQUIRED)
            courseCode: The code for the course (REQUIRED)
            **kwargs: Additional course attributes
            
        Returns:
            A new Course instance with auto-generated sourcedId and dateLastModified
        """
        return cls(
            sourcedId=None,  # Will be auto-generated
            title=title,
            courseCode=courseCode,
            org=None,  # Will be set later
            **kwargs
        )
    
    def to_dict(self, wrapped: bool = True) -> Dict[str, Any]:
        """Convert Course object to dictionary.
        
        Args:
            wrapped: Whether to wrap the result in a {'course': {...}} object
                    for single course responses
        
        Returns:
            Dictionary representation of the course
        """
        result = {
            'sourcedId': self.sourcedId,
            'status': self.status,
            'dateLastModified': self.dateLastModified,
            'title': self.title,
            'courseCode': self.courseCode,
        }
        
        # Add optional fields if they have values
        if self.schoolYear:
            result['schoolYear'] = self.schoolYear
        if self.grades:
            result['grades'] = self.grades
        if self.subjects:
            result['subjects'] = self.subjects
        if self.org:
            result['org'] = self.org
        if self.subjectCodes:
            result['subjectCodes'] = self.subjectCodes
        if self.resources:
            result['resources'] = self.resources
        
        # Add any additional metadata
        if self.metadata:
            result['metadata'] = self.metadata
        
        return {'course': result} if wrapped else result
    
    @classmethod
    def to_courses_response(cls, courses: List['Course']) -> Dict[str, Any]:
        """Convert a list of Course objects to a OneRoster courses response.
        
        This follows the CourseSetDType structure from the OneRoster spec.
        
        Args:
            courses: List of Course objects
            
        Returns:
            Response in the format {'courses': [...]}
        """
        return {
            'courses': [course.to_dict(wrapped=False) for course in courses]
        }
    
    def __repr__(self) -> str:
        """String representation of the Course.
        
        Returns:
            String representation
        """
        return f"Course(sourcedId='{self.sourcedId}', title='{self.title}')"

    def update_timestamp(self):
        """Update the last modified timestamp to current UTC time."""
        self.dateLastModified = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ') 