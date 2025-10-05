"""Tests for component-related API functionality.

This module contains tests for the TimeBack API course component endpoints following
the OneRoster 1.2 specification. Tests cover basic CRUD operations and parent-child
relationships between components.
"""

import pytest
import logging
import uuid
from timeback_client.api.components import ComponentsAPI
from timeback_client.api.courses import CoursesAPI

STAGING_URL = "https://staging.alpha-1edtech.ai"
TEST_ORG_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"

# Configure logging
logging.basicConfig(level=logging.INFO)

@pytest.fixture(scope="module")
def test_course():
    """Create a test course to use for component tests."""
    courses_api = CoursesAPI(STAGING_URL)
    
    # Create a unique test course
    course_id = f"course-test-{str(uuid.uuid4())}"
    course_data = {
        "course": {
            "sourcedId": course_id,
            "title": "Test Course for Components",
            "courseCode": "TEST-COMP-101",
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
            "title": "Test Course for Components",
            "courseCode": "TEST-COMP-101",
            "org": {"sourcedId": TEST_ORG_ID}
        }
    })

def test_component_lifecycle(test_course):
    """Test complete component lifecycle including CRUD operations and relationships.
    
    Args:
        test_course: Fixture providing the test course ID
    """
    api = ComponentsAPI(STAGING_URL)
    
    # 1. Create parent component (unit)
    unit_id = f"component-unit-{str(uuid.uuid4())}"
    unit_data = {
        "courseComponent": {
            "sourcedId": unit_id,
            "title": "Unit 1: Test Unit",
            "status": "active",
            "course": {"sourcedId": test_course},
            "sortOrder": 1
        }
    }
    create_response = api.create_component(unit_data)
    assert create_response["sourcedIdPairs"]["allocatedSourcedId"] == unit_id
    
    # 2. Create child component (lesson)
    lesson_id = f"component-lesson-{str(uuid.uuid4())}"
    lesson_data = {
        "courseComponent": {
            "sourcedId": lesson_id,
            "title": "Lesson 1.1: Test Lesson",
            "status": "active",
            "course": {"sourcedId": test_course},
            "courseComponent": {"sourcedId": unit_id},  # Reference parent
            "sortOrder": 1
        }
    }
    api.create_component(lesson_data)
    
    # 3. Verify components exist and relationship is correct
    unit = api.get_component(unit_id)
    assert unit["courseComponent"]["title"] == "Unit 1: Test Unit"
    
    lesson = api.get_component(lesson_id)
    assert lesson["courseComponent"]["courseComponent"]["sourcedId"] == unit_id
    
    # 4. List components and verify they appear
    components = api.list_components(
        fields=["sourcedId", "title"],
        course_id=test_course  # Filter by test course
    )
    print("\n=== List Components Response ===")
    print(components)
    
    # Check response structure
    assert "courseComponents" in components, f"Expected 'courseComponents' in response, got: {components}"
    assert isinstance(components["courseComponents"], list), f"Expected list of components, got: {type(components['courseComponents'])}"
    
    # Check for specific components with more detailed error messages
    unit_found = any(c["sourcedId"] == unit_id for c in components["courseComponents"])
    lesson_found = any(c["sourcedId"] == lesson_id for c in components["courseComponents"])
    
    if not unit_found:
        print(f"\nUnit {unit_id} not found in components:")
        for comp in components["courseComponents"]:
            print(f"- {comp.get('sourcedId')}: {comp.get('title')}")
    if not lesson_found:
        print(f"\nLesson {lesson_id} not found in components:")
        for comp in components["courseComponents"]:
            print(f"- {comp.get('sourcedId')}: {comp.get('title')}")
            
    assert unit_found, f"Unit component {unit_id} not found in list response"
    assert lesson_found, f"Lesson component {lesson_id} not found in list response"
    
    # 5. Update a component
    api.update_component(lesson_id, {
        "courseComponent": {
            "sourcedId": lesson_id,
            "title": "Lesson 1.1: Updated Title",
            "status": "active",
            "course": {"sourcedId": test_course},
            "courseComponent": {"sourcedId": unit_id},
            "sortOrder": 1
        }
    })
    
    updated_lesson = api.get_component(lesson_id)
    assert updated_lesson["courseComponent"]["title"] == "Lesson 1.1: Updated Title"
    
    # 6. Mark components as 'tobedeleted'
    for component_id in [lesson_id, unit_id]:
        component = api.get_component(component_id)
        api.update_component(component_id, {
            "courseComponent": {
                "sourcedId": component_id,
                "title": component["courseComponent"]["title"],  # Keep existing title
                "status": "tobedeleted",
                "course": {"sourcedId": test_course},
                "sortOrder": 1
            }
        })
        
        # Verify deletion
        component = api.get_component(component_id)
        assert component["courseComponent"]["status"] == "tobedeleted"

if __name__ == "__main__":
    print("\nCreating test course...")
    test_course_gen = test_course()
    course_id = next(test_course_gen)
    
    print("\nRunning component lifecycle test...")
    test_component_lifecycle(course_id)
    
    print("\nCleaning up test course...")
    try:
        next(test_course_gen)
    except StopIteration:
        pass 