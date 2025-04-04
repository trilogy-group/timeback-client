"""Academic Session related API endpoints for the TimeBack API.

This module provides methods for retrieving and managing academic sessions
in the TimeBack API following the OneRoster 1.2 specification.
"""

from typing import Dict, Any, Optional, List, Union
import logging
from ..models.academic_session import AcademicSession
from ..core.client import TimeBackService
import requests

# Set up logger
logger = logging.getLogger(__name__)

class AcademicSessionsAPI(TimeBackService):
    """API client for academic session related endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the academic sessions API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "rostering", client_id=client_id, client_secret=client_secret)
    
    def create_academic_session(self, session: Union[AcademicSession, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new academic session in the TimeBack API.
        
        Args:
            session: The academic session to create. Can be an AcademicSession model instance or a dictionary.
                    Required fields per OneRoster 1.2 spec:
                    - title: The title of the session
                    - type: Type of session (gradingPeriod, semester, schoolYear, term)
                    - startDate: When the session starts (ISO 8601)
                    - endDate: When the session ends (ISO 8601)
                    - schoolYear: The school year this session belongs to
                    - org: Object with sourcedId of the organization
            
        Returns:
            The API response containing sourcedIdPairs:
            {
                "sourcedIdPairs": {
                    "suppliedSourcedId": str,  # The ID provided in the request
                    "allocatedSourcedId": str  # The ID assigned by the server
                }
            }
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
            ValueError: If session does not have required fields
            
        Examples:
            # Using keyword arguments
            api.create_academic_session({
                "academicSession": {
                    "title": "Fall 2024",
                    "type": "term",
                    "startDate": "2024-09-01",
                    "endDate": "2024-12-20",
                    "schoolYear": "2024-25",
                    "org": {"sourcedId": "org-123"}
                }
            })
            
            # Using the AcademicSession model
            session = AcademicSession.create(
                title="Fall 2024",
                type="term",
                startDate="2024-09-01",
                endDate="2024-12-20",
                schoolYear="2024-25",
                org={"sourcedId": "org-123"}
            )
            api.create_academic_session(session)
        """
        # If input is a dictionary, check if it's already wrapped in 'academicSession'
        if isinstance(session, dict):
            if 'academicSession' in session:
                # Already wrapped correctly
                session_dict = session['academicSession']
                request_data = session  # Use as-is
            else:
                # Need to wrap it
                session_dict = session
                request_data = {'academicSession': session}
                
            # Check required fields
            required_fields = ['title', 'type', 'startDate', 'endDate', 'schoolYear']
            for field in required_fields:
                if not session_dict.get(field):
                    raise ValueError(f"{field} is required when creating an academic session")
                    
            # Ensure required fields per OneRoster 1.2 spec
            if 'status' not in session_dict:
                session_dict['status'] = 'active'
                
            if 'org' not in session_dict:
                raise ValueError("org with sourcedId is required when creating an academic session")
                
        # If it's an AcademicSession model, validate and convert to dict
        else:
            required_fields = ['title', 'type', 'startDate', 'endDate', 'schoolYear']
            for field in required_fields:
                if not getattr(session, field):
                    raise ValueError(f"{field} is required when creating an academic session")
                    
            if not session.org or not session.org.get('sourcedId'):
                raise ValueError("org with sourcedId is required when creating an academic session")
            
            # Convert to dictionary and wrap in 'academicSession'
            request_data = {'academicSession': session.to_dict()}
            
        # Log the sourcedId
        if isinstance(session, AcademicSession):
            logger.info(f"Creating academic session with sourcedId: {session.sourcedId}")
        else:
            logger.info(f"Creating academic session with data: {session_dict}")
            
        # Send request - response will contain sourcedIdPairs
        return self._make_request(
            endpoint="/academicSessions",
            method="POST",
            data=request_data
        )
    
    def get_academic_session(self, session_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific academic session by ID.
        
        Args:
            session_id: The unique identifier of the academic session
            fields: Optional list of fields to return (e.g. ['sourcedId', 'title'])
            
        Returns:
            The academic session data from the API
            
        Raises:
            requests.exceptions.HTTPError: If session not found (404) or other API error
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
            
        return self._make_request(
            endpoint=f"/academicSessions/{session_id}",
            params=params
        )
    
    def update_academic_session(self, session_id: str, session: Union[AcademicSession, Dict[str, Any]]) -> Dict[str, Any]:
        """Update an existing academic session in the TimeBack API.
        
        Args:
            session_id: The ID of the academic session to update
            session: The updated session data. Can be an AcademicSession model instance or a dictionary.
            
        Returns:
            The updated academic session data from the API
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        # Convert dictionary to AcademicSession model if needed
        if isinstance(session, dict):
            # If session_data is a dict with 'academicSession' key, extract the inner dict
            if 'academicSession' in session:
                session_dict = session['academicSession']
            else:
                session_dict = session
                
            # Create AcademicSession model from dict, using session_id if sourcedId isn't set
            if 'sourcedId' not in session_dict:
                session_dict['sourcedId'] = session_id
                
            # Create AcademicSession model from dict
            session = AcademicSession(**session_dict)
        
        # Ensure sourcedId matches the URL parameter
        if session.sourcedId != session_id:
            logger.warning(f"Academic session sourcedId ({session.sourcedId}) doesn't match URL parameter ({session_id})")
            logger.warning(f"Using URL parameter as the definitive ID")
            session.sourcedId = session_id
            
        # Convert to dictionary and send request
        return self._make_request(
            endpoint=f"/academicSessions/{session_id}",
            method="PUT",
            data=session.to_dict()
        )
    
    def delete_academic_session(self, session_id: str) -> Dict[str, Any]:
        """Delete an academic session from the TimeBack API.
        
        Args:
            session_id: The ID of the academic session to delete
            
        Returns:
            Success message
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        return self._make_request(
            endpoint=f"/academicSessions/{session_id}",
            method="DELETE"
        )
    
    def list_academic_sessions(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List academic sessions with filtering and pagination.
        
        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            sort: Field to sort by (e.g. 'title', 'startDate')
            order_by: Sort order ('asc' or 'desc')
            filter_expr: Filter expression (e.g. "type='term'")
            fields: Fields to return (e.g. ['sourcedId', 'title', 'type'])
            
        Returns:
            Dictionary containing academic sessions and pagination information
            
        Example:
            # Get all active terms for current school year
            api.list_academic_sessions(
                filter_expr="status='active' AND type='term' AND schoolYear='2024-25'",
                sort='startDate',
                order_by='asc',
                fields=['sourcedId', 'title', 'startDate', 'endDate']
            )
        """
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        if sort:
            params['sort'] = sort
        if order_by:
            params['orderBy'] = order_by
        if filter_expr:
            params['filter'] = filter_expr
        if fields:
            params['fields'] = ','.join(fields)
            
        return self._make_request("/academicSessions", params=params) 