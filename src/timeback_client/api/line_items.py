"""Line Items API endpoints for the TimeBack API.

This module provides methods for interacting with assessment line items
in the OneRoster Gradebook API.
"""

from typing import Dict, Any, Optional, Union
import logging
from ..core.client import TimeBackService

try:
    from ..models.line_item import LineItem
except ImportError:
    # If LineItem model is not available, we'll work with dicts
    LineItem = None

# Set up logger
logger = logging.getLogger(__name__)

class LineItemsAPI(TimeBackService):
    """API client for Assessment Line Items endpoints."""

    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the Line Items API client.

        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "gradebook", client_id, client_secret)

    def get_line_items(
        self,
        filter_expr: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort: Optional[str] = None,
        order_by: Optional[str] = "asc",
        fields: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get a list of assessment line items.

        Args:
            filter_expr: Filter expression for querying line items
            limit: Maximum number of results to return (default: 100)
            offset: Number of results to skip for pagination (default: 0)
            sort: Field to sort by
            order_by: Sort direction - 'asc' or 'desc' (default: 'asc')
            fields: Comma-separated list of fields to return

        Returns:
            Dict containing:
            - lineItems: List of line item objects

        Raises:
            requests.exceptions.HTTPError: For HTTP errors returned by the API

        Example:
            >>> client = TimeBackClient()
            >>> result = client.gradebook.line_items.get_line_items(
            ...     filter_expr="metadata.subject='Math'",
            ...     limit=50
            ... )
        """
        logger.info(f"Fetching line items with filter: {filter_expr}")

        params = {
            "limit": limit,
            "offset": offset,
        }

        if filter_expr:
            params["filter"] = filter_expr
        if sort:
            params["sort"] = sort
            params["orderBy"] = order_by
        if fields:
            params["fields"] = fields

        return self._make_request(
            endpoint="/assessmentLineItems/",
            method="GET",
            params=params
        )

    def get_line_item(self, line_item_id: str) -> Union[Any, Dict[str, Any]]:
        """Get a specific assessment line item by ID.

        Args:
            line_item_id: The sourcedId of the line item

        Returns:
            LineItem object or dict if model not available

        Raises:
            requests.exceptions.HTTPError: If line item not found (404) or other API error

        Example:
            >>> client = TimeBackClient()
            >>> line_item = client.gradebook.line_items.get_line_item("line-item-123")
        """
        logger.info(f"Fetching line item: {line_item_id}")

        response = self._make_request(
            endpoint=f"/assessmentLineItems/{line_item_id}",
            method="GET"
        )

        # Parse the response into a LineItem object if available
        line_item_data = response.get("assessmentLineItem", response)
        if LineItem is not None:
            return LineItem(**line_item_data)
        return line_item_data

    def create_line_item(self, line_item: Union[Any, Dict[str, Any]]) -> Union[Any, Dict[str, Any]]:
        """Create a new assessment line item.

        Args:
            line_item: LineItem object or dict with the data to create.
                      Only 'status' (must be 'active') and 'title' are required.

        Returns:
            LineItem object or dict representing the created line item

        Raises:
            requests.exceptions.HTTPError: If creation fails or parameters are invalid

        Example:
            >>> from timeback_client.models.line_item import LineItem
            >>> client = TimeBackClient()
            >>> new_line_item = LineItem(
            ...     title="Math Grade 5 - AlphaLearn Assessment",
            ...     description="AlphaLearn assessment for Math Grade 5",
            ...     resultValueMin=0,
            ...     resultValueMax=100,
            ...     metadata={
            ...         'grade': '5',
            ...         'subject': 'Math',
            ...         'appName': 'alphalearn'
            ...     }
            ... )
            >>> created = client.gradebook.line_items.create_line_item(new_line_item)
        """
        # Get title for logging
        title = line_item.title if hasattr(line_item, 'title') else line_item.get('title', 'unknown')
        logger.info(f"Creating line item: {title}")

        # Convert LineItem to dict for API request
        if hasattr(line_item, 'model_dump'):
            line_item_dict = line_item.model_dump(mode='json', exclude_none=True)
        elif hasattr(line_item, 'dict'):
            line_item_dict = line_item.dict(exclude_none=True)
        else:
            line_item_dict = line_item

        # Wrap in assessmentLineItem object for API
        data = {
            "assessmentLineItem": line_item_dict
        }

        response = self._make_request(
            endpoint="/assessmentLineItems/",
            method="POST",
            data=data
        )

        # API returns sourcedIdPairs on successful creation
        # Extract the sourcedId and return a simple object with it
        logger.info(f"Line item creation response: {response}")

        if "sourcedIdPairs" in response:
            sourced_id_pairs = response["sourcedIdPairs"]
            logger.info(f"sourcedIdPairs content: {sourced_id_pairs}")

            # Extract the sourcedId - try allocatedSourcedId first, then suppliedSourcedId
            sourced_id = (
                sourced_id_pairs.get("allocatedSourcedId") or
                sourced_id_pairs.get("suppliedSourcedId") or
                sourced_id_pairs.get("sourcedId") or
                sourced_id_pairs.get("suppliedId")
            )
            logger.info(f"Extracted sourcedId: {sourced_id}")

            # Create a simple response object with the sourcedId as an instance attribute
            class LineItemResponse:
                def __init__(self, sourced_id, raw_response):
                    self.sourcedId = sourced_id
                    self._raw_response = raw_response

            return LineItemResponse(sourced_id, response)

        # Fallback to returning raw response
        logger.warning(f"No sourcedIdPairs in response, returning raw response: {response}")
        return response

    def update_line_item(self, line_item_id: str, line_item: Union[Any, Dict[str, Any]]) -> Union[Any, Dict[str, Any]]:
        """Update an existing assessment line item.

        Args:
            line_item_id: The sourcedId of the line item to update
            line_item: LineItem object or dict with the updated data

        Returns:
            LineItem object or dict representing the updated line item

        Raises:
            requests.exceptions.HTTPError: If update fails or line item not found

        Example:
            >>> client = TimeBackClient()
            >>> line_item = client.gradebook.line_items.get_line_item("line-item-123")
            >>> line_item.title = "Updated Title"
            >>> updated = client.gradebook.line_items.update_line_item("line-item-123", line_item)
        """
        logger.info(f"Updating line item: {line_item_id}")

        # Convert LineItem to dict for API request
        if hasattr(line_item, 'model_dump'):
            line_item_dict = line_item.model_dump(mode='json', exclude_none=True)
        elif hasattr(line_item, 'dict'):
            line_item_dict = line_item.dict(exclude_none=True)
        else:
            line_item_dict = line_item

        # Wrap in assessmentLineItem object for API
        data = {
            "assessmentLineItem": line_item_dict
        }

        response = self._make_request(
            endpoint=f"/assessmentLineItems/{line_item_id}",
            method="PUT",
            data=data
        )

        # Parse the response into a LineItem object if available
        line_item_data = response.get("assessmentLineItem", response)
        if LineItem is not None:
            return LineItem(**line_item_data)
        return line_item_data

    def delete_line_item(self, line_item_id: str) -> Dict[str, Any]:
        """Delete an assessment line item.

        Args:
            line_item_id: The sourcedId of the line item to delete

        Returns:
            Dict containing the response from the API

        Raises:
            requests.exceptions.HTTPError: If deletion fails or line item not found

        Example:
            >>> client = TimeBackClient()
            >>> result = client.gradebook.line_items.delete_line_item("line-item-123")
        """
        logger.info(f"Deleting line item: {line_item_id}")

        return self._make_request(
            endpoint=f"/assessmentLineItems/{line_item_id}",
            method="DELETE"
        )
