"""Tests for the TimeBack client."""

import pytest
import json
from timeback_client import TimeBackClient, RosteringService

STAGING_URL = "http://staging.alpha-1edtech.com"

def test_client_initialization():
    """Test that the client initializes correctly."""
    client = TimeBackClient(STAGING_URL)
    assert client.api_url == STAGING_URL
    assert isinstance(client.rostering, RosteringService)
    assert client.rostering.base_url == STAGING_URL
    assert client.rostering.api_path == "/ims/oneroster/rostering/v1p2"

def test_url_construction():
    """Test that URLs are constructed correctly."""
    client = TimeBackClient(STAGING_URL)
    
    # Test rostering service URL
    rostering = client.rostering
    assert rostering.base_url + rostering.api_path == f"{STAGING_URL}/ims/oneroster/rostering/v1p2"
    
    # Test gradebook service URL
    gradebook = client.gradebook
    assert gradebook.base_url + gradebook.api_path == f"{STAGING_URL}/ims/oneroster/gradebook/v1p2"
    
    # Test resources service URL
    resources = client.resources
    assert resources.base_url + resources.api_path == f"{STAGING_URL}/ims/oneroster/resources/v1p2"

@pytest.mark.integration
def test_list_users():
    """Test listing users (integration test)."""
    client = TimeBackClient(STAGING_URL)
    response = client.rostering.list_users()  # Removed limit to see all users
    print("\n=== List Users Response ===")
    print(json.dumps(response, indent=2))
    assert isinstance(response, dict)
    assert 'users' in response
    print(f"\nTotal users found: {len(response['users'])}")

@pytest.mark.integration
def test_get_user():
    """Test getting a specific user (integration test)."""
    client = TimeBackClient(STAGING_URL)
    # First get a user ID from the list
    users = client.rostering.list_users(limit=1)
    if 'users' in users and users['users']:
        user_id = users['users'][0]['sourcedId']
        user = client.rostering.get_user(user_id)
        print("\n=== Get User Response ===")
        print(json.dumps(user, indent=2))
        assert isinstance(user, dict)
        assert 'user' in user
        assert user['user']['sourcedId'] == user_id
    else:
        pytest.skip("No users available to test with")
