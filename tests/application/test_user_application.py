"""Application-focused tests for user operations.

These tests simulate how real applications would use the TimeBackClient
to perform user-related operations.
"""

import pytest
import uuid
from timeback_client import TimeBackClient

# Constants
TEST_ORG_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"  # Default test org ID

@pytest.mark.integration
def test_application_create_user():
    """Test how an application would create a user.
    
    This test simulates the exact flow that an application like
    homeschool-backend would use to create a parent user.
    """
    # 1. Initialize the client as an application would
    client = TimeBackClient()  # Uses default URL
    
    # 2. Generate a unique ID for this test user
    user_id = str(uuid.uuid4())
    
    # 3. Prepare user data as an application would (using a dictionary)
    user_data = {
        "user": {
            "sourcedId": user_id,
            "status": "active",
            "dateLastModified": "2025-03-15T12:00:00Z",  # Applications would use current time
            "enabledUser": True,
            "givenName": "Test",
            "familyName": "Parent",
            "email": "test.parent@example.com",
            "roles": [{
                "roleType": "primary",
                "role": "parent",
                "org": {
                    "sourcedId": TEST_ORG_ID,
                    "type": "org"
                }
            }]
        }
    }
    
    # 4. Create the user via the client
    response = client.rostering.users.create_user(user_data)
    
    # 5. Verify the response as an application would
    assert "sourcedIdPairs" in response
    pairs = response["sourcedIdPairs"]
    assert pairs["suppliedSourcedId"] == user_id
    assert pairs["allocatedSourcedId"] == user_id
    
    # 6. Verify the user was created by retrieving it
    get_response = client.rostering.users.get_user(user_id)
    assert "user" in get_response
    created_user = get_response["user"]
    assert created_user["sourcedId"] == user_id
    assert created_user["givenName"] == "Test"
    assert created_user["familyName"] == "Parent"
    assert created_user["email"] == "test.parent@example.com"
    assert created_user["roles"][0]["role"] == "parent" 