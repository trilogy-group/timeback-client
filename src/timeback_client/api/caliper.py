"""Caliper-related API endpoints for the TimeBack API.

This module provides methods for interacting with Caliper events
in the TimeBack API.
"""

from typing import Dict, Any, Optional, List
from ..core.client import TimeBackService
import logging

# Set up logger
logger = logging.getLogger(__name__)


class CaliperAPI(TimeBackService):
    """API client for Caliper-related endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the Caliper API client.
        
        Args:
            base_url: The base URL of the Caliper API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        # Note: Caliper API uses a different base URL and doesn't follow OneRoster paths
        super().__init__(base_url, "caliper", client_id=client_id, client_secret=client_secret)
        # Override the api_path since Caliper doesn't use OneRoster paths
        self.api_path = ""
        # Ensure environment is initialized (will be set by TimeBackClient)
        self.environment = "production"  # Default value that will be overridden
    
    def send_event(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """Send a Caliper event envelope to the API.
        
        Args:
            envelope: The Caliper event envelope containing:
                - sensor: The sensor identifier
                - sendTime: ISO 8601 timestamp
                - dataVersion: Caliper version URL
                - data: List of Caliper events
                
        Returns:
            The API response
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        return self._make_request(
            endpoint="/caliper/event",
            method="POST",
            data=envelope
        )
    
    def validate_event(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a Caliper event envelope.
        
        Args:
            envelope: The Caliper event envelope to validate
                
        Returns:
            The validation response with status and any errors
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        return self._make_request(
            endpoint="/caliper/event/validate",
            method="POST",
            data=envelope
        )
    
    def list_events(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sensor: Optional[str] = None,
        startDate: Optional[str] = None,
        endDate: Optional[str] = None,
        actorId: Optional[str] = None,
        actorEmail: Optional[str] = None
    ) -> Dict[str, Any]:
        """List Caliper events with filtering and pagination.
        
        Args:
            limit: Maximum number of events to return
            offset: Number of events to skip for pagination
            sensor: Filter by sensor identifier
            startDate: Filter events from this date (ISO 8601 format)
            endDate: Filter events until this date (ISO 8601 format)
            actorId: Filter by actor ID
            actorEmail: Filter by actor email address
            
        Returns:
            Dictionary containing:
                - status: Response status
                - message: Response message
                - data: List of Caliper events (if successful)
                - errors: Any errors (if unsuccessful)
                
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        params = {}
        
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        if sensor:
            params['sensor'] = sensor
        if startDate:
            params['startDate'] = startDate
        if endDate:
            params['endDate'] = endDate
        if actorId:
            params['actorId'] = actorId
        if actorEmail:
            params['actorEmail'] = actorEmail
            
        logger.info(f"Listing Caliper events with params: {params}")
        
        return self._make_request(
            endpoint="/caliper/events",
            method="GET",
            params=params
        ) 