"""Tests for resource-related API functionality.

This module contains tests for the TimeBack API resource endpoints following
the OneRoster 1.2 specification. The tests verify:

1. Complete CRUD cycle (test_resource_crud_lifecycle)
2. Resource listing with filtering and pagination (test_list_resources)
3. Resource validation and model methods

Note: Per OneRoster 1.2 spec:
- sourcedId is assigned by the system, not provided during creation
- vendorResourceId is required and is your local identifier
- Resources are marked as 'tobedeleted' rather than being physically deleted
"""

import pytest
import logging
import uuid
from datetime import datetime
from timeback_client.models.resource import Resource
from timeback_client.api.resources import ResourcesAPI
import requests

STAGING_URL = "https://staging.alpha-1edtech.com"
TEST_ORG_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"  # Default test org ID

# Configure logging
logging.basicConfig(level=logging.INFO)

@pytest.fixture
def test_resource_data():
    """Create test resource data with frontend-style structure.
    
    Returns:
        Dict containing test resource data with required fields, wrapped in 'resource' object
    """
    unique_id = str(uuid.uuid4())
    return {
        "resource": {  # Wrap in resource object per spec
            "title": f"Test Resource {unique_id}",
            "vendorResourceId": f"vendor-{unique_id}",
            "status": "active",
            "importance": "primary",
            "metadata": {
                "subject": "Mathematics",
                "grade": "9",
                "type": "video"
            },
            "org": {  # Add org reference like courses
                "sourcedId": TEST_ORG_ID
            }
        }
    }

def test_resource_crud_lifecycle():
    """Test a complete CRUD cycle for a resource using frontend-style data structures.
    
    This test:
    1. Creates a new resource with required fields (title, vendorResourceId)
    2. Verifies the creation response contains sourcedIdPairs
    3. Uses the allocated sourcedId for subsequent operations
    4. Updates the resource with new data
    5. Verifies the update through a GET request
    6. Marks the resource as 'tobedeleted' and verifies the status change
    """
    api = ResourcesAPI(STAGING_URL)
    
    # CREATE: Create a resource
    test_id = str(uuid.uuid4())  # This will be our vendorResourceId
    resource_data = {
        "resource": {
            "title": "Math Video Resource (Before Update)",
            "vendorResourceId": f"vendor-{test_id}",
            "status": "active",
            "importance": "primary",
            "metadata": {
                "subject": "Mathematics",
                "grade": "9",
                "type": "video"
            },
            "org": {
                "sourcedId": TEST_ORG_ID
            }
        }
    }
    
    # Create the resource and verify response contains sourcedIdPairs
    create_response = api.create_resource(resource_data)
    assert "sourcedIdPairs" in create_response
    allocated_id = create_response["sourcedIdPairs"]["allocatedSourcedId"]
    assert allocated_id  # Verify we got a sourcedId back
    
    # READ: Verify initial creation using allocated sourcedId
    initial_get = api.get_resource(allocated_id)
    assert "resource" in initial_get
    initial_resource = initial_get["resource"]
    assert initial_resource["title"] == "Math Video Resource (Before Update)"
    assert initial_resource["vendorResourceId"] == f"vendor-{test_id}"
    assert initial_resource["status"] == "active"
    assert initial_resource["importance"] == "primary"
    
    # UPDATE: Update the resource using allocated sourcedId
    update_data = {
        "resource": {
            "sourcedId": allocated_id,  # Required for updates
            "title": "Math Video Resource (After Update)",
            "vendorResourceId": f"vendor-{test_id}",  # Keep same vendorResourceId
            "status": "active",
            "importance": "secondary",
            "metadata": {
                "subject": "Mathematics",
                "grade": "9,10",  # Added grade 10
                "type": "video",
                "updated": True
            },
            "org": {
                "sourcedId": TEST_ORG_ID
            }
        }
    }
    
    # Update and verify response contains updated resource
    updated = api.update_resource(allocated_id, update_data)
    assert "resource" in updated
    assert updated["resource"]["title"] == "Math Video Resource (After Update)"
    assert updated["resource"]["importance"] == "secondary"
    assert updated["resource"]["metadata"]["grade"] == "9,10"
    
    # READ: Verify the update through GET
    get_response = api.get_resource(allocated_id)
    print("\n=== Updated Resource Data ===")
    print(get_response)
    
    # Verify the resource was updated correctly
    assert "resource" in get_response
    retrieved_resource = get_response["resource"]
    assert retrieved_resource["sourcedId"] == allocated_id
    assert retrieved_resource["title"] == "Math Video Resource (After Update)"
    assert retrieved_resource["importance"] == "secondary"
    assert retrieved_resource["metadata"]["updated"] is True
    
    # DELETE: Mark resource as 'tobedeleted'
    delete_data = {
        "resource": {
            "sourcedId": allocated_id,
            "status": "tobedeleted",
            "title": retrieved_resource["title"],
            "vendorResourceId": retrieved_resource["vendorResourceId"],
            "org": {
                "sourcedId": TEST_ORG_ID
            }
        }
    }
    api.update_resource(allocated_id, delete_data)
    
    # Verify resource is marked as 'tobedeleted'
    final_get = api.get_resource(allocated_id)
    assert final_get["resource"]["status"] == "tobedeleted"

def test_list_resources():
    """Test listing resources with various parameters.
    
    Tests the following functionality:
    - Basic listing (no parameters)
    - Pagination (limit)
    - Field selection
    - Sorting
    - Filtering by title
    """
    api = ResourcesAPI(STAGING_URL)
    
    # Test 1: Basic listing
    response = api.list_resources()
    print("\n=== List Resources Response ===")
    print(response)
    assert "resources" in response
    assert isinstance(response["resources"], list)
    
    # Test 2: Pagination
    response = api.list_resources(limit=3)
    assert len(response["resources"]) <= 3
    
    # Test 3: Sort by title
    response = api.list_resources(
        sort="title",
        order_by="asc",
        fields=['sourcedId', 'title', 'vendorResourceId']
    )
    print("\n=== Sorted Resources ===")
    print(response)
    if len(response["resources"]) > 1:
        titles = [resource["title"].lower() for resource in response["resources"]]
        assert titles == sorted(titles)
    
    # Test 4: Field selection
    response = api.list_resources(
        fields=['sourcedId', 'title', 'vendorResourceId']
    )
    for resource in response["resources"]:
        assert set(resource.keys()) <= {"sourcedId", "title", "vendorResourceId"}
        assert "metadata" not in resource  # Verify excluded field is not present

    # Test 5: Filter by title
    # Create a resource with a unique title for filtering
    unique_title = f"Math Video Resource FILTER-{uuid.uuid4()}"
    api.create_resource({
        "resource": {
            "title": unique_title,
            "vendorResourceId": f"vendor-filter-{uuid.uuid4()}",
            "status": "active",
            "importance": "primary",
            "org": {
                "sourcedId": TEST_ORG_ID
            }
        }
    })
    
    # Now filter by that unique title
    response = api.list_resources(
        filter_expr=f"title='{unique_title}'",
        fields=['sourcedId', 'title', 'vendorResourceId']
    )
    print("\n=== Filtered Resources ===")
    print(response)
    assert len(response["resources"]) >= 1
    assert response["resources"][0]["title"] == unique_title
    
    # Clean up by marking the test resource as 'tobedeleted'
    resource_id = response["resources"][0]["sourcedId"]
    delete_data = {
        "resource": {
            "sourcedId": resource_id,
            "status": "tobedeleted",
            "title": unique_title,
            "vendorResourceId": response["resources"][0]["vendorResourceId"],
            "org": {
                "sourcedId": TEST_ORG_ID
            }
        }
    }
    api.update_resource(resource_id, delete_data)

if __name__ == "__main__":
    # This allows running the tests directly with python tests/test_resources.py
    print("Running test_resource_crud_lifecycle()")
    test_resource_crud_lifecycle()
    
    print("\nRunning test_list_resources()")
    test_list_resources() 