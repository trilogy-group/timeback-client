"""Tests for user-related API functionality."""

import pytest
from timeback_client.models.user import User, Address, UserRole
from timeback_client.api.users import UsersAPI

STAGING_URL = "http://oneroster-staging.us-west-2.elasticbeanstalk.com"

def test_user_model_serialization():
    """Test that User model serializes correctly for API requests."""
    user = User(
        first_name="John",
        last_name="Doe",
        role=UserRole.PARENT,
        email="john.doe@example.com",
        phone="123-456-7890",
        address=Address(
            country="United States",
            city="Example City",
            state="CA",
            zip="12345"
        )
    )
    
    data = user.to_dict()
    assert data["user"]["givenName"] == "John"
    assert data["user"]["familyName"] == "Doe"
    assert data["user"]["roles"][0]["role"] == "parent"
    assert data["user"]["email"] == "john.doe@example.com"
    assert data["user"]["metadata"]["phone"] == "123-456-7890"
    assert data["user"]["metadata"]["address"]["country"] == "United States"

@pytest.mark.integration
def test_create_parent():
    """Test creating a parent user via the API."""
    api = UsersAPI(STAGING_URL)
    
    # Create test parent data
    address = Address(
        country="United States",
        city="Test City",
        state="CA",
        zip="12345"
    )
    
    # Create parent with full data
    response = api.create_parent(
        first_name="Test",
        last_name="Parent",
        phone="123-456-7890",
        address=address,
        metadata={"interested_in_premium": True}
    )
    
    print("\n=== Create Parent Response ===")
    print(response)
    
    # Verify response
    assert "user" in response
    user = response["user"]
    assert user["givenName"] == "Test"
    assert user["familyName"] == "Parent"
    assert user["roles"][0]["role"] == "parent"
    assert user["metadata"]["phone"] == "123-456-7890"
    assert user["metadata"]["address"]["country"] == "United States"
    assert user["metadata"]["interested_in_premium"] is True

@pytest.mark.integration
def test_update_parent():
    """Test updating a parent user via the API."""
    api = UsersAPI(STAGING_URL)
    
    # First create a parent
    create_response = api.create_parent(
        first_name="Update",
        last_name="Test",
        phone="123-456-7890"
    )
    user_id = create_response["user"]["sourcedId"]
    
    # Update the parent
    updated_user = User(
        first_name="Updated",
        last_name="Name",
        role=UserRole.PARENT,
        phone="987-654-3210"
    )
    
    update_response = api.update_user(user_id, updated_user)
    print("\n=== Update Parent Response ===")
    print(update_response)
    
    # Verify response
    assert "user" in update_response
    user = update_response["user"]
    assert user["givenName"] == "Updated"
    assert user["familyName"] == "Name"
    assert user["metadata"]["phone"] == "987-654-3210" 