"""Tests for course-related API functionality.

This module contains tests for the TimeBack API course endpoints following
the OneRoster 1.2 specification. The tests verify:

1. Complete CRUD cycle (test_update_course)
2. Course listing with filtering and pagination (test_list_courses)

Note: Per OneRoster 1.2 spec, courses are marked as 'tobedeleted' rather than
being physically deleted.
"""

import pytest
import logging
import uuid
from timeback_client.models.course import Course
from timeback_client.api.courses import CoursesAPI
import requests

STAGING_URL = "https://staging.alpha-1edtech.com"
TEST_ORG_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"  # Default test org ID

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_update_course():
    """Test a complete CRUD cycle for a course using frontend-style data structures.
    
    This test:
    1. Creates a new course with required org field
    2. Verifies the creation with a GET request
    3. Updates the course with new data
    4. Verifies the update through a GET request
    5. Marks the course as 'tobedeleted' and verifies the status change
    
    Note: Per OneRoster 1.2 spec:
    - Update endpoint returns an empty response on success
    - Courses are marked as 'tobedeleted' rather than being physically deleted
    """
    api = CoursesAPI(STAGING_URL)
    
    # CREATE: Create a course
    test_id = f"course-{str(uuid.uuid4())}"
    course_data = {
        "course": {  # Wrap in course object per spec
            "sourcedId": test_id,
            "title": "Grade 4 Mathematics (Before Update)",
            "courseCode": "MATH-4-UPDATE",
            "grades": ["4"],
            "subjects": ["Mathematics"],
            "subjectCodes": ["MATH"],
            "status": "active",
            "org": {
                "sourcedId": TEST_ORG_ID
            }
        }
    }
    
    # Create the course and verify response
    create_response = api.create_course(course_data)
    assert "sourcedIdPairs" in create_response
    assert create_response["sourcedIdPairs"]["allocatedSourcedId"] == test_id
    
    # READ: Verify initial creation
    initial_get = api.get_course(test_id)
    assert "course" in initial_get
    initial_course = initial_get["course"]
    assert initial_course["title"] == "Grade 4 Mathematics (Before Update)"
    assert initial_course["courseCode"] == "MATH-4-UPDATE"
    assert initial_course["grades"] == ["4"]
    assert initial_course["subjects"] == ["Mathematics"]
    assert initial_course["subjectCodes"] == ["MATH"]
    assert initial_course["status"] == "active"
    
    # UPDATE: Update the course
    update_data = {
        "course": {
            "sourcedId": test_id,
            "title": "Grade 4 Mathematics (After Update)",
            "courseCode": "MATH-4-UPDATED",
            "grades": ["4", "5"],  # Added grade 5
            "subjects": ["Mathematics", "STEM"],  # Added STEM subject
            "subjectCodes": ["MATH", "STEM"],
            "status": "active",
            "org": {
                "sourcedId": TEST_ORG_ID
            }
        }
    }
    
    # Update returns empty response on success
    api.update_course(test_id, update_data)
    
    # READ: Verify the update
    get_response = api.get_course(test_id)
    print("\n=== Updated Course Data ===")
    print(get_response)
    
    # Verify the course was updated correctly
    assert "course" in get_response
    retrieved_course = get_response["course"]
    assert retrieved_course["sourcedId"] == test_id
    assert retrieved_course["title"] == "Grade 4 Mathematics (After Update)"
    assert retrieved_course["courseCode"] == "MATH-4-UPDATED"
    assert set(retrieved_course["grades"]) == {"4", "5"}
    assert set(retrieved_course["subjects"]) == {"Mathematics", "STEM"}
    assert set(retrieved_course["subjectCodes"]) == {"MATH", "STEM"}
    assert retrieved_course["status"] == "active"
    
    # DELETE: Mark course as 'tobedeleted'
    delete_data = {
        "course": {
            "sourcedId": test_id,
            "status": "tobedeleted",
            "title": retrieved_course["title"],
            "courseCode": retrieved_course["courseCode"],
            "org": {
                "sourcedId": TEST_ORG_ID
            }
        }
    }
    api.update_course(test_id, delete_data)
    
    # Verify course is marked as 'tobedeleted'
    final_get = api.get_course(test_id)
    assert final_get["course"]["status"] == "tobedeleted"

def test_list_courses():
    """Test listing courses with various parameters.
    
    Tests the following functionality:
    - Basic listing (no parameters)
    - Pagination (limit)
    - Field selection
    - Sorting
    - Filtering by title
    """
    api = CoursesAPI(STAGING_URL)
    
    # Test 1: Basic listing
    response = api.list_courses()
    print("\n=== List Courses Response ===")
    print(response)
    assert "courses" in response
    assert isinstance(response["courses"], list)
    
    # Test 2: Pagination
    response = api.list_courses(limit=3)
    assert len(response["courses"]) <= 3
    
    # Test 3: Sort by title
    response = api.list_courses(
        sort="title",
        order_by="asc",
        fields=['sourcedId', 'title', 'courseCode']
    )
    print("\n=== Sorted Courses ===")
    print(response)
    if len(response["courses"]) > 1:
        titles = [course["title"].lower() for course in response["courses"]]
        assert titles == sorted(titles)
    
    # Test 4: Field selection
    response = api.list_courses(
        fields=['sourcedId', 'title', 'courseCode']
    )
    for course in response["courses"]:
        assert set(course.keys()) <= {"sourcedId", "title", "courseCode"}
        assert "grades" not in course  # Verify excluded field is not present

    # Test 5: Filter by title
    # Create a course with a unique title for filtering
    unique_title = f"Grade 4 Mathematics FILTER-{uuid.uuid4()}"
    api.create_course({
        "course": {  # Wrap in course object per spec
            "title": unique_title,
            "courseCode": "MATH-4-FILTER",
            "grades": ["4"],
            "subjects": ["Mathematics"],
            "status": "active",
            "org": {
                "sourcedId": TEST_ORG_ID  # Use the test org ID defined at top of file
            }
        }
    })
    
    # Now filter by that unique title
    response = api.list_courses(
        filter_expr=f"title='{unique_title}'",
        fields=['sourcedId', 'title', 'courseCode']
    )
    print("\n=== Filtered Courses ===")
    print(response)
    assert len(response["courses"]) >= 1
    assert response["courses"][0]["title"] == unique_title
    
    # Clean up by marking the test course as 'tobedeleted'
    course_id = response["courses"][0]["sourcedId"]
    delete_data = {
        "course": {
            "sourcedId": course_id,
            "status": "tobedeleted",
            "title": unique_title,
            "courseCode": "MATH-4-FILTER",
            "org": {
                "sourcedId": TEST_ORG_ID
            }
        }
    }
    api.update_course(course_id, delete_data)

if __name__ == "__main__":
    # This allows running the tests directly with python tests/test_courses.py
    # It will run each test individually and print output
    print("Running test_update_course()")
    test_update_course()
    
    print("\nRunning test_list_courses()")
    test_list_courses() 