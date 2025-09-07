"""API modules for the TimeBack client.

This package contains specialized API classes for different entity types
in the OneRoster specification.
"""

__all__ = [
    "users",
    "assessment_items",  # QTI assessment items API
    "assessment_tests",  # QTI assessment tests API
    "orgs",  # Organization management API
    "courses",  # Course management API
    "components",  # Course component management API (units, lessons, etc.)
    "resources",
    "academic_sessions",  # Add academic sessions module
    "classes",
    "enrollments",
    "component_resources",  # Component resource management API
    "students",
    "caliper",  # Caliper events API
    "subject_tracks",  # EduBridge subject tracks API
]
