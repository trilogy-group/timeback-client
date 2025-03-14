"""TimeBack API client.

A Python client for the TimeBack API, implementing the OneRoster 1.2 specification.
This package provides a simple interface to interact with the TimeBack API's
three main services:

1. RosteringService - User and organization management
2. GradebookService - Grades and assessments
3. ResourcesService - Learning resources

Example:
    Basic usage of the client:

    >>> from timeback_client import TimeBackClient
    >>> client = TimeBackClient("http://oneroster-staging.us-west-2.elasticbeanstalk.com")
    >>> users = client.rostering.list_users(limit=10)
    >>> user = client.rostering.get_user("user-id")

    Direct service usage:

    >>> from timeback_client import RosteringService
    >>> rostering = RosteringService("http://oneroster-staging.us-west-2.elasticbeanstalk.com")
    >>> users = rostering.list_users()
"""

__version__ = "0.1.0"

from .core.client import (
    TimeBackClient,
    RosteringService,
    GradebookService,
    ResourcesService,
    TimeBackService
)

__all__ = [
    "TimeBackClient",
    "RosteringService",
    "GradebookService",
    "ResourcesService",
    "TimeBackService"
] 