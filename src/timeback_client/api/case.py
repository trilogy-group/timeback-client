"""CASE API endpoints for the TimeBack API.

This module provides methods for interacting with the 1EdTech CASE (Competencies and Academic Standards Exchange) API
endpoints in the TimeBack platform. CASE is used for managing competency frameworks, learning standards,
and their relationships.

The CASE API follows the IMS Global CASE v1.0 specification for competency and academic standards exchange.
"""

from typing import Dict, Any, Optional, List
import logging
from ..core.client import TimeBackService

# Set up logger
logger = logging.getLogger(__name__)

class CaseAPI(TimeBackService):
    """API client for 1EdTech CASE (Competencies and Academic Standards Exchange) endpoints.
    
    This class provides access to CASE API endpoints for managing competency frameworks,
    learning standards, and their associations. The CASE API is used to exchange competency
    and academic standards data between systems.
    
    Example:
        >>> case_api = CaseAPI("https://api.staging.alpha-1edtech.ai/")
        >>> documents = case_api.get_all_cf_documents()
        >>> document = case_api.get_cf_document("document-id")
        >>> package = case_api.get_cf_package("document-id")
    """

    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the CASE API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "case", client_id, client_secret)
        # Override the api_path since CASE uses IMS Global path structure
        self.api_path = "/ims/case/v1p1"

    def get_all_cf_documents(self, 
                           limit: Optional[int] = None,
                           offset: Optional[int] = None,
                           sort: Optional[str] = None,
                           order_by: Optional[str] = None,
                           filter_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get all CASE documents (competency frameworks) with optional filtering and pagination.
        
        Retrieves a list of all available competency framework documents. This corresponds to
        the `getAllCFDocuments` operation in the CASE API specification.
        
        Args:
            limit: Maximum number of documents to return (pagination)
            offset: Number of documents to skip (pagination) 
            sort: Field name to sort by (e.g., 'title', 'lastChangeDateTime')
            order_by: Sort direction - 'asc' for ascending, 'desc' for descending
            filter_params: Additional filter parameters as key-value pairs
            
        Returns:
            Dict containing:
            - CFDocuments: List of competency framework documents
            - meta: Optional metadata about the response (pagination info, etc.)
            
        Raises:
            requests.exceptions.HTTPError: If API request fails
            
        Example:
            >>> documents = case_api.get_all_cf_documents(limit=10, sort='title', order_by='asc')
            >>> for doc in documents.get('CFDocuments', []):
            ...     print(f"Document: {doc.get('title')}")
        """
        logger.info("Fetching all CASE competency framework documents")
        
        # Build query parameters
        params = {}
        if limit is not None:
            params['limit'] = str(limit)
        if offset is not None:
            params['offset'] = str(offset)
        if sort:
            params['sort'] = sort
        if order_by:
            params['orderBy'] = order_by
        if filter_params:
            params.update(filter_params)
            
        logger.info(f"Request parameters: {params}")
        
        response = self._make_request(
            endpoint="/CFDocuments",
            method="GET",
            params=params if params else None
        )
        
        logger.info(f"Retrieved {len(response.get('CFDocuments', []))} CASE documents")
        return response

    def get_cf_document(self, sourced_id: str) -> Dict[str, Any]:
        """Get a specific CASE document by its sourcedId.
        
        Retrieves detailed information about a single competency framework document.
        This corresponds to the `getCFDocument` operation in the CASE API specification.
        
        Args:
            sourced_id: The unique identifier of the competency framework document
            
        Returns:
            Dict containing:
            - CFDocument: The competency framework document data
            
        Raises:
            requests.exceptions.HTTPError: If document not found (404) or other API error
            
        Example:
            >>> document = case_api.get_cf_document("doc-12345")
            >>> print(f"Document title: {document['CFDocument']['title']}")
        """
        if not sourced_id:
            raise ValueError("sourced_id is required")
            
        logger.info(f"Fetching CASE document with sourcedId: {sourced_id}")
        
        response = self._make_request(
            endpoint=f"/CFDocuments/{sourced_id}",
            method="GET"
        )
        
        logger.info(f"Retrieved CASE document: {response.get('CFDocument', {}).get('title', 'Unknown')}")
        return response

    def get_cf_package(self, sourced_id: str) -> Dict[str, Any]:
        """Get a complete CASE package for a given document sourcedId.
        
        Retrieves a complete competency framework package that includes the document,
        all its items (competencies), and associations (relationships between competencies).
        This corresponds to the `getCFPackage` operation in the CASE API specification.
        
        Args:
            sourced_id: The unique identifier of the competency framework document
            
        Returns:
            Dict containing:
            - CFPackage: Complete package with document, items, and associations
              - CFDocument: The framework document
              - CFItems: List of competency items
              - CFAssociations: List of relationships between items
              
        Raises:
            requests.exceptions.HTTPError: If package not found (404) or other API error
            
        Example:
            >>> package = case_api.get_cf_package("doc-12345")
            >>> document = package['CFPackage']['CFDocument']
            >>> items = package['CFPackage']['CFItems']
            >>> associations = package['CFPackage']['CFAssociations']
            >>> print(f"Package contains {len(items)} items and {len(associations)} associations")
        """
        if not sourced_id:
            raise ValueError("sourced_id is required")
            
        logger.info(f"Fetching CASE package for document sourcedId: {sourced_id}")
        
        response = self._make_request(
            endpoint=f"/CFPackages/{sourced_id}",
            method="GET"
        )
        
        package = response.get('CFPackage', {})
        items_count = len(package.get('CFItems', []))
        associations_count = len(package.get('CFAssociations', []))
        
        logger.info(f"Retrieved CASE package with {items_count} items and {associations_count} associations")
        return response

    def get_cf_item(self, sourced_id: str) -> Dict[str, Any]:
        """Get a specific CASE item (competency) by its sourcedId.
        
        Retrieves detailed information about a single competency item within a framework.
        This corresponds to the `getCFItem` operation in the CASE API specification.
        
        Args:
            sourced_id: The unique identifier of the competency item
            
        Returns:
            Dict containing:
            - CFItem: The competency item data including statement, grade levels, etc.
            
        Raises:
            requests.exceptions.HTTPError: If item not found (404) or other API error
            
        Example:
            >>> item = case_api.get_cf_item("item-67890")
            >>> competency = item['CFItem']
            >>> print(f"Competency: {competency['fullStatement']}")
            >>> print(f"Grade levels: {competency.get('educationLevel', [])}")
        """
        if not sourced_id:
            raise ValueError("sourced_id is required")
            
        logger.info(f"Fetching CASE item with sourcedId: {sourced_id}")
        
        response = self._make_request(
            endpoint=f"/CFItems/{sourced_id}",
            method="GET"
        )
        
        item = response.get('CFItem', {})
        logger.info(f"Retrieved CASE item: {item.get('fullStatement', 'No statement')[:100]}...")
        return response

    def get_cf_association(self, sourced_id: str) -> Dict[str, Any]:
        """Get a specific CASE association (relationship) by its sourcedId.
        
        Retrieves detailed information about a relationship between competency items.
        This corresponds to the `getCFAssociation` operation in the CASE API specification.
        
        Args:
            sourced_id: The unique identifier of the association
            
        Returns:
            Dict containing:
            - CFAssociation: The association data including relationship type and connected items
            
        Raises:
            requests.exceptions.HTTPError: If association not found (404) or other API error
            
        Example:
            >>> association = case_api.get_cf_association("assoc-11111")
            >>> assoc_data = association['CFAssociation']
            >>> print(f"Association type: {assoc_data['associationType']}")
            >>> print(f"Origin: {assoc_data['originNodeURI']}")
            >>> print(f"Destination: {assoc_data['destinationNodeURI']}")
        """
        if not sourced_id:
            raise ValueError("sourced_id is required")
            
        logger.info(f"Fetching CASE association with sourcedId: {sourced_id}")
        
        response = self._make_request(
            endpoint=f"/CFAssociations/{sourced_id}",
            method="GET"
        )
        
        association = response.get('CFAssociation', {})
        logger.info(f"Retrieved CASE association: {association.get('associationType', 'Unknown type')}")
        return response

    def search_cf_documents(self, 
                          query: Optional[str] = None,
                          title: Optional[str] = None,
                          subject: Optional[str] = None,
                          creator: Optional[str] = None,
                          publisher: Optional[str] = None,
                          education_level: Optional[str] = None,
                          limit: Optional[int] = None,
                          offset: Optional[int] = None) -> Dict[str, Any]:
        """Search for competency framework documents with various filter criteria.
        
        Provides advanced search capabilities for finding specific competency frameworks
        based on multiple criteria such as title, subject area, education level, etc.
        
        Args:
            query: General text search query across document fields
            title: Filter by document title (partial match)
            subject: Filter by subject area
            creator: Filter by document creator
            publisher: Filter by publisher
            education_level: Filter by education level (e.g., "K", "01", "02", "09-12")
            limit: Maximum number of results to return
            offset: Number of results to skip for pagination
            
        Returns:
            Dict containing:
            - CFDocuments: List of matching competency framework documents
            - meta: Metadata about search results and pagination
            
        Raises:
            requests.exceptions.HTTPError: If search request fails
            
        Example:
            >>> results = case_api.search_cf_documents(
            ...     subject="Mathematics",
            ...     education_level="09-12", 
            ...     limit=20
            ... )
            >>> for doc in results.get('CFDocuments', []):
            ...     print(f"Found: {doc['title']}")
        """
        logger.info("Searching CASE documents with filters")
        
        # Build search parameters
        params = {}
        if query:
            params['q'] = query
        if title:
            params['title'] = title
        if subject:
            params['subject'] = subject
        if creator:
            params['creator'] = creator
        if publisher:
            params['publisher'] = publisher
        if education_level:
            params['educationLevel'] = education_level
        if limit is not None:
            params['limit'] = str(limit)
        if offset is not None:
            params['offset'] = str(offset)
            
        logger.info(f"Search parameters: {params}")
        
        if not params:
            logger.warning("No search parameters provided, returning all documents")
            return self.get_all_cf_documents()
        
        response = self._make_request(
            endpoint="/CFDocuments",
            method="GET",
            params=params
        )
        
        results_count = len(response.get('CFDocuments', []))
        logger.info(f"Search returned {results_count} CASE documents")
        return response

    def get_cf_items_for_document(self, 
                                document_sourced_id: str,
                                limit: Optional[int] = None,
                                offset: Optional[int] = None) -> Dict[str, Any]:
        """Get all competency items for a specific document.
        
        Retrieves all competency items (learning standards) that belong to a specific
        competency framework document.
        
        Args:
            document_sourced_id: The unique identifier of the competency framework document
            limit: Maximum number of items to return
            offset: Number of items to skip for pagination
            
        Returns:
            Dict containing:
            - CFItems: List of competency items for the document
            
        Raises:
            requests.exceptions.HTTPError: If document not found or API error
            
        Example:
            >>> items = case_api.get_cf_items_for_document("doc-12345", limit=50)
            >>> for item in items.get('CFItems', []):
            ...     print(f"Competency: {item['fullStatement']}")
        """
        if not document_sourced_id:
            raise ValueError("document_sourced_id is required")
            
        logger.info(f"Fetching CASE items for document: {document_sourced_id}")
        
        params = {}
        if limit is not None:
            params['limit'] = str(limit)
        if offset is not None:
            params['offset'] = str(offset)
            
        response = self._make_request(
            endpoint=f"/CFDocuments/{document_sourced_id}/CFItems",
            method="GET",
            params=params if params else None
        )
        
        items_count = len(response.get('CFItems', []))
        logger.info(f"Retrieved {items_count} CASE items for document {document_sourced_id}")
        return response

    def get_cf_associations_for_document(self, 
                                       document_sourced_id: str,
                                       limit: Optional[int] = None,
                                       offset: Optional[int] = None) -> Dict[str, Any]:
        """Get all associations (relationships) for a specific document.
        
        Retrieves all associations that define relationships between competency items
        within a specific competency framework document.
        
        Args:
            document_sourced_id: The unique identifier of the competency framework document
            limit: Maximum number of associations to return
            offset: Number of associations to skip for pagination
            
        Returns:
            Dict containing:
            - CFAssociations: List of associations for the document
            
        Raises:
            requests.exceptions.HTTPError: If document not found or API error
            
        Example:
            >>> associations = case_api.get_cf_associations_for_document("doc-12345")
            >>> for assoc in associations.get('CFAssociations', []):
            ...     print(f"Relationship: {assoc['associationType']}")
        """
        if not document_sourced_id:
            raise ValueError("document_sourced_id is required")
            
        logger.info(f"Fetching CASE associations for document: {document_sourced_id}")
        
        params = {}
        if limit is not None:
            params['limit'] = str(limit)
        if offset is not None:
            params['offset'] = str(offset)
            
        response = self._make_request(
            endpoint=f"/CFDocuments/{document_sourced_id}/CFAssociations",
            method="GET",
            params=params if params else None
        )
        
        associations_count = len(response.get('CFAssociations', []))
        logger.info(f"Retrieved {associations_count} CASE associations for document {document_sourced_id}")
        return response

    def get_cf_package_groups(self, sourced_id: str) -> Dict[str, Any]:
        """Get a CASE package with pre-structured hierarchical groups.
        
        Retrieves a complete competency framework package with items already organized
        in hierarchical structure, eliminating the need for client-side tree building.
        This corresponds to the `/CFPackages/{sourcedId}/groups` endpoint in the CASE API.
        
        Args:
            sourced_id: The unique identifier of the competency framework document
            
        Returns:
            Dict containing:
            - CFPackageWithGroups: Package with structured hierarchical content
              - CFDocument: The framework document
              - structuredContent: Pre-built hierarchical organization
              
        Raises:
            requests.exceptions.HTTPError: If package not found (404) or other API error
            
        Example:
            >>> groups_package = case_api.get_cf_package_groups("doc-12345")
            >>> structured = groups_package['CFPackageWithGroups']['structuredContent']
            >>> print(f"Found {len(structured)} root level groups")
        """
        if not sourced_id:
            raise ValueError("sourced_id is required")
            
        logger.info(f"Fetching CASE package with groups for document sourcedId: {sourced_id}")
        
        response = self._make_request(
            endpoint=f"/CFPackages/{sourced_id}/groups",
            method="GET"
        )
        
        package = response.get('CFPackageWithGroups', {})
        structured_content = package.get('structuredContent', {})
        
        logger.info(f"Retrieved CASE package with pre-structured groups")
        return response 