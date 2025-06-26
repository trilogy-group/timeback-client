"""Lesson Plan model for PowerPath API.

This module defines the Lesson Plan model for student-specific lesson plans.
Lesson plans are automatically created when courses are assigned to students
and can be customized without affecting the base course.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ComponentProgress:
    """Progress data for a component or resource."""
    
    def __init__(
        self,
        sourcedId: str,
        progress: int = 0,
        status: str = "not_started",
        xp: int = 0,
        results: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        """Initialize component progress.
        
        Args:
            sourcedId: The component/resource ID this progress is for
            progress: Progress percentage (0-100)
            status: Status (not_started, in_progress, completed)
            xp: Experience points earned
            results: List of assessment results
            **kwargs: Additional progress metadata
        """
        self.sourcedId = sourcedId
        self.progress = progress
        self.status = status
        self.xp = xp
        self.results = results or []
        self.metadata = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "sourcedId": self.sourcedId,
            "progress": self.progress,
            "status": self.status,
            "xp": self.xp
        }
        if self.results:
            result["results"] = self.results
        if self.metadata:
            result.update(self.metadata)
        return result


class LessonPlanResource:
    """Resource within a lesson plan component."""
    
    def __init__(
        self,
        resource: Dict[str, Any],
        sortOrder: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
        componentProgress: Optional[ComponentProgress] = None,
        **kwargs
    ):
        """Initialize lesson plan resource.
        
        Args:
            resource: The resource data
            sortOrder: Order within parent component
            metadata: Additional metadata
            componentProgress: Progress data for this resource
            **kwargs: Additional properties
        """
        self.resource = resource
        self.sortOrder = sortOrder
        self.metadata = metadata or {}
        self.componentProgress = componentProgress
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "resource": self.resource,
            "sortOrder": self.sortOrder
        }
        if self.metadata:
            result["metadata"] = self.metadata
        if self.componentProgress:
            result["componentProgress"] = self.componentProgress.to_dict()
        return result


class LessonPlanComponent:
    """Component within a lesson plan (unit, lesson, etc)."""
    
    def __init__(
        self,
        sourcedId: str,
        title: str,
        status: str = "active",
        sortOrder: int = 1,
        type: str = "lesson",  # container, lesson, virtual_lesson
        unlockDate: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        prerequisites: Optional[List[str]] = None,
        prerequisiteCriteria: Optional[str] = None,
        componentResources: Optional[List[LessonPlanResource]] = None,
        componentProgress: Optional[ComponentProgress] = None,
        subComponents: Optional[List['LessonPlanComponent']] = None,
        items: Optional[List['LessonPlanComponent']] = None,  # Alternative to subComponents
        **kwargs
    ):
        """Initialize lesson plan component.
        
        Args:
            sourcedId: Unique identifier
            title: Component title
            status: Component status
            sortOrder: Order within parent
            type: Type of component (container, lesson, etc)
            unlockDate: When component becomes available
            metadata: Additional metadata
            prerequisites: List of prerequisite component IDs
            prerequisiteCriteria: How prerequisites are evaluated
            componentResources: Resources within this component
            componentProgress: Progress data for this component
            subComponents: Child components (for containers)
            items: Alternative name for child components
            **kwargs: Additional properties
        """
        self.sourcedId = sourcedId
        self.title = title
        self.status = status
        self.sortOrder = sortOrder
        self.type = type
        self.unlockDate = unlockDate
        self.metadata = metadata or {}
        self.prerequisites = prerequisites or []
        self.prerequisiteCriteria = prerequisiteCriteria
        self.componentResources = componentResources or []
        self.componentProgress = componentProgress
        # Handle both subComponents and items
        self.subComponents = subComponents or items or []
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LessonPlanComponent':
        """Create component from dictionary data."""
        # Extract component resources
        resources = []
        if "componentResources" in data:
            for res_data in data["componentResources"]:
                # Create ComponentProgress if present
                comp_progress = None
                if "componentProgress" in res_data:
                    comp_progress = ComponentProgress(**res_data["componentProgress"])
                
                resources.append(LessonPlanResource(
                    resource=res_data.get("resource", {}),
                    sortOrder=res_data.get("sortOrder", 1),
                    metadata=res_data.get("metadata"),
                    componentProgress=comp_progress
                ))
        
        # Extract component progress
        comp_progress = None
        if "componentProgress" in data:
            comp_progress = ComponentProgress(**data["componentProgress"])
        
        # Extract sub-components recursively
        sub_components = []
        if "subComponents" in data:
            for sub_data in data["subComponents"]:
                sub_components.append(cls.from_dict(sub_data))
        elif "items" in data:
            for sub_data in data["items"]:
                sub_components.append(cls.from_dict(sub_data))
        
        return cls(
            sourcedId=data.get("sourcedId"),
            title=data.get("title"),
            status=data.get("status", "active"),
            sortOrder=data.get("sortOrder", 1),
            type=data.get("type", "lesson"),
            unlockDate=data.get("unlockDate"),
            metadata=data.get("metadata"),
            prerequisites=data.get("prerequisites"),
            prerequisiteCriteria=data.get("prerequisiteCriteria"),
            componentResources=resources,
            componentProgress=comp_progress,
            subComponents=sub_components
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "sourcedId": self.sourcedId,
            "title": self.title,
            "status": self.status,
            "sortOrder": self.sortOrder,
            "type": self.type
        }
        
        if self.unlockDate:
            result["unlockDate"] = self.unlockDate
        if self.metadata:
            result["metadata"] = self.metadata
        if self.prerequisites:
            result["prerequisites"] = self.prerequisites
        if self.prerequisiteCriteria:
            result["prerequisiteCriteria"] = self.prerequisiteCriteria
        if self.componentResources:
            result["componentResources"] = [r.to_dict() for r in self.componentResources]
        if self.componentProgress:
            result["componentProgress"] = self.componentProgress.to_dict()
        if self.subComponents:
            result["subComponents"] = [c.to_dict() for c in self.subComponents]
            
        return result


class LessonPlan:
    """Student-specific lesson plan with progress data."""
    
    def __init__(
        self,
        course: Dict[str, Any],
        subComponents: List[LessonPlanComponent],
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize lesson plan.
        
        Args:
            course: Course information
            subComponents: Top-level components in the plan
            metadata: Additional metadata about the plan
            **kwargs: Additional properties
        """
        self.course = course
        self.subComponents = subComponents
        self.metadata = metadata or {}
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LessonPlan':
        """Create lesson plan from API response.
        
        Args:
            data: Response data from API
            
        Returns:
            LessonPlan instance
        """
        # Handle nested response structure
        if "lessonPlan" in data:
            data = data["lessonPlan"]
            if "lessonPlan" in data:  # Double nested
                data = data["lessonPlan"]
        
        # Parse components
        components = []
        if "subComponents" in data:
            for comp_data in data["subComponents"]:
                components.append(LessonPlanComponent.from_dict(comp_data))
        elif "components" in data:  # Alternative key
            for comp_data in data["components"]:
                components.append(LessonPlanComponent.from_dict(comp_data))
        
        return cls(
            course=data.get("course", {}),
            subComponents=components,
            metadata=data.get("metadata")
        )
    
    def to_dict(self, wrapped: bool = True) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Args:
            wrapped: Whether to wrap in lessonPlan key
            
        Returns:
            Dictionary representation
        """
        result = {
            "course": self.course,
            "subComponents": [c.to_dict() for c in self.subComponents]
        }
        
        if self.metadata:
            result["metadata"] = self.metadata
            
        if wrapped:
            return {"lessonPlan": {"lessonPlan": result}}
        return result
    
    def get_total_progress(self) -> Dict[str, Any]:
        """Calculate total progress across all components.
        
        Returns:
            Dict with total_xp, completion_percentage, completed_count, total_count
        """
        total_xp = 0
        completed_count = 0
        total_count = 0
        
        def count_progress(component: LessonPlanComponent):
            nonlocal total_xp, completed_count, total_count
            
            if component.type == "lesson" and component.componentProgress:
                total_count += 1
                if component.componentProgress.status == "completed":
                    completed_count += 1
                total_xp += component.componentProgress.xp
            
            # Recurse into sub-components
            for sub in component.subComponents:
                count_progress(sub)
        
        for component in self.subComponents:
            count_progress(component)
        
        completion_percentage = (completed_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "total_xp": total_xp,
            "completion_percentage": round(completion_percentage, 2),
            "completed_count": completed_count,
            "total_count": total_count
        } 