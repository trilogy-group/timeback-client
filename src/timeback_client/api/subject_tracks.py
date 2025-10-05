"""Subject Tracks API endpoints for the TimeBack API.

This module provides access to the EduBridge subject tracks endpoint hosted
at `/edubridge/subject-track/` on the main API domain.

Usage:
    >>> from timeback_client import TimeBackClient
    >>> client = TimeBackClient()  # defaults to production base URL
    >>> tracks = client.rostering.subject_tracks.list_subject_tracks()

Notes:
- This API does NOT use the OneRoster path. We override the default
  `api_path` to point to `/edubridge` so requests hit:
  `{base_url}/edubridge/subject-track/`.
"""

from typing import Dict, Any, Optional
import logging
from ..core.client import TimeBackService

# Set up logger
logger = logging.getLogger(__name__)


class SubjectTracksAPI(TimeBackService):
    """API client for subject track endpoints.

    This class is auto-registered by `RosteringService` because it resides in
    the `timeback_client.api` package and inherits `TimeBackService`.
    It overrides the default OneRoster path to use the EduBridge path.
    """

    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the Subject Tracks API client.

        Args:
            base_url: Base API URL, e.g., https://api.alpha-1edtech.ai/
            client_id: OAuth2 client ID (optional)
            client_secret: OAuth2 client secret (optional)
        """
        # Initialize with a placeholder service; immediately override api_path.
        super().__init__(base_url, "edubridge", client_id=client_id, client_secret=client_secret)
        # Critical: EduBridge lives at /edubridge (not OneRoster). Keep this minimal.
        self.api_path = "/edubridge"

    def list_subject_tracks(self, **query_params: Any) -> Dict[str, Any]:
        """List all subject tracks.

        Steps:
        1) Build URL: {base_url}/edubridge/subject-track/
        2) Make GET request
        3) Return parsed JSON

        Args:
            **query_params: Optional query parameters to forward to the API.

        Returns:
            dict: JSON response from the API.

        Example:
            >>> api.list_subject_tracks()
        """
        logger.info("Listing subject tracks with params: %s", query_params)
        return self._make_request(endpoint="/subject-track/", params=query_params)

