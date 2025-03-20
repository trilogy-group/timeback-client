"""Tests for user-related API functionality."""

import pytest
import logging
import uuid
from timeback_client.models.user import User, Address, UserRole, RoleAssignment, OrgRef
from timeback_client.api.users import UsersAPI

STAGING_URL = "http://staging.alpha-1edtech.com"
TEST_ORG_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"  # Default test org ID

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_create_user():
    """Test creating a user with required fields.
    
    The API returns a sourcedIdPairs object that maps between:
    1. suppliedSourcedId: The ID we provided in our request
    2. allocatedSourcedId: The ID that was actually assigned by the server
    
    These may be the same (if server accepts our ID) or different (if server assigns new ID).
    """
    api = UsersAPI(STAGING_URL)
    
    # Generate a random sourcedId for this test
    test_id = str(uuid.uuid4())
    
    # Create test user with sourcedId
    user = User(
        sourcedId=test_id,  # This will be the suppliedSourcedId
        givenName="Test",
        familyName="User",
        roles=[
            RoleAssignment(
                role=UserRole.STUDENT,
                org=OrgRef(sourcedId=TEST_ORG_ID)
            )
        ]
    )
    
    # Create user
    response = api.create_user(user)
    print("\n=== Create User Response ===")
    print(response)
    
    # Verify response contains sourcedId mapping
    assert "sourcedIdPairs" in response
    pairs = response["sourcedIdPairs"]
    assert pairs["suppliedSourcedId"] == test_id  # ID we provided
    assert pairs["allocatedSourcedId"] == test_id  # ID server assigned

def test_create_user_without_sourceid():
    """Test that creating a user without sourcedId raises an error."""
    api = UsersAPI(STAGING_URL)
    
    with pytest.raises(ValueError):  # sourcedId is required by Pydantic model
        user = User(
            givenName="Test",
            familyName="User",
            roles=[
                RoleAssignment(
                    role=UserRole.STUDENT,
                    org=OrgRef(sourcedId=TEST_ORG_ID)
                )
            ]
        )

def test_get_user():
    """Test retrieving a user after creation.
    
    This test:
    1. Creates a new user
    2. Gets the allocated sourcedId from the response
    3. Retrieves the user using that ID
    4. Verifies the user data matches what we created
    """
    api = UsersAPI(STAGING_URL)
    
    # First create a user
    test_id = str(uuid.uuid4())
    test_given_name = "Get"
    test_family_name = "TestUser"
    
    user = User(
        sourcedId=test_id,
        givenName=test_given_name,
        familyName=test_family_name,
        roles=[
            RoleAssignment(
                role=UserRole.STUDENT,
                org=OrgRef(sourcedId=TEST_ORG_ID)
            )
        ]
    )
    
    # Create the user and get the allocated ID
    create_response = api.create_user(user)
    allocated_id = create_response["sourcedIdPairs"]["allocatedSourcedId"]
    
    # Now retrieve the user
    get_response = api.get_user(allocated_id)
    print("\n=== Get User Response ===")
    print(get_response)
    
    # Verify the retrieved user matches what we created
    assert "user" in get_response
    retrieved_user = get_response["user"]
    assert retrieved_user["sourcedId"] == allocated_id
    assert retrieved_user["givenName"] == test_given_name
    assert retrieved_user["familyName"] == test_family_name
    assert retrieved_user["status"] == "active"
    assert len(retrieved_user["roles"]) == 1
    assert retrieved_user["roles"][0]["role"] == UserRole.STUDENT
    assert retrieved_user["roles"][0]["org"]["sourcedId"] == TEST_ORG_ID 

def test_list_users():
    """Test listing users with various parameters.
    
    Tests the following functionality:
    - Basic listing (no parameters)
    - Pagination (limit)
    - Field selection
    - Sorting (case-insensitive)
    - Filtering by familyName
    """
    api = UsersAPI(STAGING_URL)
    
    # Test 1: Basic listing
    response = api.list_users()
    print("\n=== List Users Response ===")
    print(response)
    assert "users" in response
    assert isinstance(response["users"], list)
    assert len(response["users"]) > 0  # Verify we got some users
    
    # Test 2: Pagination
    response = api.list_users(limit=2)
    assert len(response["users"]) <= 2
    
    # Test 3: Sort by familyName
    response = api.list_users(
        sort="familyName",  # Using familyName as it's a standard OneRoster field
        order_by="asc",
        fields=['sourcedId', 'familyName']
    )
    print("\n=== Sorted Users ===")
    print(response)
    family_names = [user["familyName"] for user in response["users"]]
    # Case-insensitive comparison
    assert [name.lower() for name in family_names] == sorted([name.lower() for name in family_names])
    
    # Test 4: Field selection
    response = api.list_users(
        fields=['sourcedId', 'givenName', 'familyName']
    )
    for user in response["users"]:
        assert set(user.keys()) <= {"sourcedId", "givenName", "familyName"}
        assert "roles" not in user  # Verify excluded field is not present

    # Test 5: Filter by familyName
    response = api.list_users(
        filter_expr="familyName='Garcia'",
        fields=['sourcedId', 'givenName', 'familyName']
    )
    print("\n=== Filtered Users ===")
    print(response)
    for user in response["users"]:
        assert user["familyName"] == "Garcia"

    # TODO: Add test for filtering by roles.role once dot notation filtering is supported
    # Example of future test:
    # response = api.list_users(
    #     filter_expr="roles.role='student'",
    #     fields=['sourcedId', 'givenName', 'familyName', 'roles']
    # ) 