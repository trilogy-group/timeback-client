"""Tests for component resource-related API functionality.

This module contains tests for the TimeBack API course component resource endpoints
following the OneRoster 1.2 specification. Tests cover basic CRUD operations and
relationships between components and resources.
"""

import pytest
import logging
import uuid
from timeback_client.api.components import ComponentsAPI
from timeback_client.api.courses import CoursesAPI
from timeback_client.api.component_resources import ComponentResourcesAPI
from timeback_client.models.component_resource import ComponentResource
from timeback_client.api.resources import ResourcesAPI

STAGING_URL = "https://staging.alpha-1edtech.com"
TEST_ORG_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"

# Configure logging
logging.basicConfig(level=logging.INFO)

@pytest.fixture(scope="module")
def test_course():
    """Create a test course to use for component resource tests."""
    courses_api = CoursesAPI(STAGING_URL)
    
    # Create a unique test course
    course_id = f"course-test-{str(uuid.uuid4())}"
    course_data = {
        "course": {
            "sourcedId": course_id,
            "title": "Test Course for Component Resources",
            "courseCode": "TEST-COMPRES-101",
            "status": "active",
            "org": {"sourcedId": TEST_ORG_ID}
        }
    }
    
    # Create and verify the course
    create_response = courses_api.create_course(course_data)
    course_id = create_response["sourcedIdPairs"]["allocatedSourcedId"]
    yield course_id
    
    # Clean up: Mark course as 'tobedeleted'
    courses_api.update_course(course_id, {
        "course": {
            "sourcedId": course_id,
            "status": "tobedeleted",
            "title": "Test Course for Component Resources",
            "courseCode": "TEST-COMPRES-101",
            "org": {"sourcedId": TEST_ORG_ID}
        }
    })

@pytest.fixture(scope="module")
def test_component(test_course):
    """Create a test component to use for component resource tests."""
    components_api = ComponentsAPI(STAGING_URL)
    
    # Create a unique test component
    component_id = f"component-test-{str(uuid.uuid4())}"
    component_data = {
        "courseComponent": {
            "sourcedId": component_id,
            "title": "Test Component for Resources",
            "status": "active",
            "course": {"sourcedId": test_course},
            "sortOrder": 1
        }
    }
    
    # Create and verify the component
    create_response = components_api.create_component(component_data)
    component_id = create_response["sourcedIdPairs"]["allocatedSourcedId"]
    yield component_id
    
    # Clean up: Mark component as 'tobedeleted'
    components_api.update_component(component_id, {
        "courseComponent": {
            "sourcedId": component_id,
            "status": "tobedeleted",
            "title": "Test Component for Resources",
            "course": {"sourcedId": test_course},
            "sortOrder": 1
        }
    })

@pytest.fixture(scope="module")
def test_resource():
    """Create a real resource for testing."""
    resources_api = ResourcesAPI(STAGING_URL)
    
    # Create a unique test resource
    resource_id = f"resource-test-{str(uuid.uuid4())}"
    resource_data = {
        "resource": {
            "sourcedId": resource_id,
            "title": "Test Resource",
            "type": "reading",
            "content": "Test content for reading resource",
            "status": "active"
        }
    }
    
    # Create and verify the resource
    create_response = resources_api.create_resource(resource_data)
    resource_id = create_response["sourcedIdPairs"]["allocatedSourcedId"]
    yield resource_id
    
    # Clean up: Mark resource as 'tobedeleted'
    resources_api.update_resource(resource_id, {
        "resource": {
            "sourcedId": resource_id,
            "status": "tobedeleted",
            "title": "Test Resource",
            "type": "reading"
        }
    })

def test_component_resource_lifecycle(test_course, test_component, test_resource):
    """Test complete component resource lifecycle including CRUD operations.
    
    Args:
        test_course: Fixture providing the test course ID
        test_component: Fixture providing the test component ID
        test_resource: Fixture providing the test resource ID
    """
    api = ComponentResourcesAPI(STAGING_URL)
    
    # 1. Create component resource using model
    resource_id = f"component-resource-{str(uuid.uuid4())}"
    resource = ComponentResource.create(
        sourcedId=resource_id,
        title="Test Video Resource",
        component_id=test_component,
        resource_id=test_resource,
        sortOrder=1
    )
    
    create_response = api.create_component_resource(resource)
    assert create_response["sourcedIdPairs"]["allocatedSourcedId"] == resource_id
    
    # 2. Create another component resource using dictionary
    resource_id_2 = f"component-resource-{str(uuid.uuid4())}"
    resource_data = {
        "componentResource": {
            "sourcedId": resource_id_2,
            "title": "Test Reading Resource",
            "status": "active",
            "courseComponent": {"sourcedId": test_component},
            "resource": {"sourcedId": test_resource},
            "sortOrder": 2
        }
    }
    api.create_component_resource(resource_data)
    
    # 3. Verify resources exist
    resource_1 = api.get_component_resource(resource_id)
    assert resource_1["componentResource"]["title"] == "Test Video Resource"
    assert resource_1["componentResource"]["courseComponent"]["sourcedId"] == test_component
    
    resource_2 = api.get_component_resource(resource_id_2)
    assert resource_2["componentResource"]["title"] == "Test Reading Resource"
    
    # 4. List resources and verify they appear
    resources = api.list_component_resources(
        fields=["sourcedId", "title"],
        component_id=test_component  # Filter by test component
    )
    print("\n=== List Component Resources Response ===")
    print(resources)
    
    # Check response structure
    assert "componentResources" in resources, f"Expected 'componentResources' in response, got: {resources}"
    assert isinstance(resources["componentResources"], list), f"Expected list of resources, got: {type(resources['componentResources'])}"
    
    # Check for specific resources with more detailed error messages
    resource_1_found = any(r["sourcedId"] == resource_id for r in resources["componentResources"])
    resource_2_found = any(r["sourcedId"] == resource_id_2 for r in resources["componentResources"])
    
    if not resource_1_found:
        print(f"\nResource {resource_id} not found in resources:")
        for res in resources["componentResources"]:
            print(f"- {res.get('sourcedId')}: {res.get('title')}")
    if not resource_2_found:
        print(f"\nResource {resource_id_2} not found in resources:")
        for res in resources["componentResources"]:
            print(f"- {res.get('sourcedId')}: {res.get('title')}")
            
    assert resource_1_found, f"Component resource {resource_id} not found in list response"
    assert resource_2_found, f"Component resource {resource_id_2} not found in list response"
    
    # 5. Update a resource
    api.update_component_resource(resource_id, {
        "componentResource": {
            "sourcedId": resource_id,
            "title": "Updated Video Resource",
            "status": "active",
            "courseComponent": {"sourcedId": test_component},
            "resource": {"sourcedId": test_resource},
            "sortOrder": 1
        }
    })
    
    updated_resource = api.get_component_resource(resource_id)
    assert updated_resource["componentResource"]["title"] == "Updated Video Resource"
    
    # 6. Mark resources as 'tobedeleted'
    for res_id in [resource_id, resource_id_2]:
        resource = api.get_component_resource(res_id)
        api.update_component_resource(res_id, {
            "componentResource": {
                "sourcedId": res_id,
                "title": resource["componentResource"]["title"],  # Keep existing title
                "status": "tobedeleted",
                "courseComponent": {"sourcedId": test_component},
                "resource": {"sourcedId": test_resource},
                "sortOrder": resource["componentResource"]["sortOrder"]  # Keep existing order
            }
        })
        
        # Verify deletion
        resource = api.get_component_resource(res_id)
        assert resource["componentResource"]["status"] == "tobedeleted"

def test_coupled_resource_creation(test_course, test_component):
    """Test creating a resource and component resource together."""
    resources_api = ResourcesAPI(STAGING_URL)
    component_resources_api = ComponentResourcesAPI(STAGING_URL)
    
    # 1. Create resource with content
    resource_data = {
        "resource": {
            "title": "Introduction Video",
            "type": "video",
            "content": "https://example.com/video.mp4",
            "status": "active"
        }
    }
    resource_response = resources_api.create_resource(resource_data)
    resource_id = resource_response["sourcedIdPairs"]["allocatedSourcedId"]
    
    # 2. Create component resource linking
    component_resource_data = {
        "componentResource": {
            "title": "Introduction Video",  # Same title for user consistency
            "status": "active",
            "courseComponent": {"sourcedId": test_component},
            "resource": {"sourcedId": resource_id},
            "sortOrder": 1
        }
    }
    
    component_resource_response = component_resources_api.create_component_resource(
        component_resource_data
    )
    
    # 3. Verify both exist and are linked
    resource = resources_api.get_resource(resource_id)
    assert resource["resource"]["title"] == "Introduction Video"
    
    component_resource = component_resources_api.get_component_resource(
        component_resource_response["sourcedIdPairs"]["allocatedSourcedId"]
    )
    assert component_resource["componentResource"]["resource"]["sourcedId"] == resource_id

if __name__ == "__main__":
    print("\nCreating test course...")
    test_course_gen = test_course()
    course_id = next(test_course_gen)
    
    print("\nCreating test component...")
    test_component_gen = test_component(course_id)
    component_id = next(test_component_gen)
    
    print("\nRunning component resource lifecycle test...")
    test_component_resource_lifecycle(course_id, component_id, test_resource())
    
    print("\nCleaning up test component...")
    try:
        next(test_component_gen)
    except StopIteration:
        pass
    
    print("\nCleaning up test course...")
    try:
        next(test_course_gen)
    except StopIteration:
        pass 