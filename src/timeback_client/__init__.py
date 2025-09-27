"""TimeBack API client for OneRoster 1.2.

This package provides a Python client for the TimeBack API, which implements the OneRoster 1.2 specification.
"""

__version__ = "1.4.5"

from .core.client import TimeBackClient, RosteringService, GradebookService, ResourcesService, QTIService

__all__ = [
    "TimeBackClient",
    "RosteringService",
    "GradebookService",
    "ResourcesService",
    "QTIService"
] 