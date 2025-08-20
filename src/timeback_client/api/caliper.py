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

    def get_user_xp_events(
        self,
        user_email: str,
        start_date: str,
        end_date: str,
        *,  # Force keyword args for clarity
        limit: int = 1000,
        offset: int = 0,
        sensor: Optional[str] = None,  # Remove hardcoded sensor - let it be optional
        course_id: Optional[str] = None  # kept for backward-compat but not sent to API
    ) -> List[Dict[str, Any]]:
        """Retrieve ActivityEvent Caliper events for a user that contain XP information.

        This is a convenience wrapper around ``list_events`` that applies common
        filters used by AlphaLearn when processing FastMath XP.  It will:

        1. Query the Caliper endpoint for the given user and time range.
        2. Filter the results to ``ActivityEvent`` types only.
        3. If ``course_id`` is provided it will further filter the events so the
           ``object.course.id`` (the last URI fragment) matches the supplied ID.

        Note: the Caliper service itself does *not* currently expose a
        ``courseId`` query parameter, so any course filtering must be done
        client-side.  This helper performs that filtering for you.

        Args:
            user_email:  The learner's e-mail address (maps to ``actorEmail``).
            start_date:  ISO-8601 timestamp marking the inclusive start of the window.
            end_date:    ISO-8601 timestamp marking the exclusive end of the window.
            course_id:   Optional OneRoster course identifier to filter on.
            limit:       Maximum number of events to request from the API. Defaults to 1000.
            offset:      Pagination offset. Defaults to 0.
            sensor:      Optional sensor identifier. If None, will not filter by sensor.

        Returns:
            A list of Caliper ``ActivityEvent`` dicts after all filtering.
        """
        # Build query params identical to the JavaScript implementation
        response = self.list_events(
            limit=limit,
            offset=offset,
            sensor=sensor,
            startDate=start_date,
            endDate=end_date,
            actorEmail=user_email
        )

        # The Caliper API sometimes nests the list under ``events`` but can also
        # use ``data`` – handle both to be safe.
        events: List[Dict[str, Any]] = response.get("events", response.get("data", []))  # type: ignore

        if not events:
            logger.info(
                "No Caliper events found for %s between %s and %s", user_email, start_date, end_date
            )
            return []

        # Filter for ActivityEvent only
        activity_events = [e for e in events if e.get("type") == "ActivityEvent"]
        logger.info(
            "Retrieved %d ActivityEvent records for %s (total events: %d)",
            len(activity_events),
            user_email,
            len(events),
        )

        # Optional client-side course filter – Caliper API does not support this natively
        if course_id:
            filtered_events: List[Dict[str, Any]] = []
            for event in activity_events:
                course_obj = (
                    event.get("object", {}).get("course", {}) if isinstance(event.get("object"), dict) else {}
                )
                # ``id`` is usually a URI like ``https://.../courses/<course_id>`` – use last segment
                event_course_id = course_obj.get("id", "").split("/")[-1]
                if event_course_id == course_id:
                    filtered_events.append(event)

            logger.info(
                "After courseId filtering (%s) %d ActivityEvent records remain",
                course_id,
                len(filtered_events),
            )
            activity_events = filtered_events

        # Finally, keep only events that actually contain an XP item
        xp_events: List[Dict[str, Any]] = []
        for event in activity_events:
            generated = event.get("generated", {})
            items = generated.get("items", []) if isinstance(generated, dict) else []
            xp_item = next((i for i in items if i.get("type") == "xpEarned"), None)
            if xp_item is None:
                continue

            try:
                xp_val = float(xp_item.get("value", 0))
            except (TypeError, ValueError):
                xp_val = 0

            if xp_val > 0:
                xp_events.append(event)

        logger.info("After XP filtering %d events remain", len(xp_events))

        return xp_events 