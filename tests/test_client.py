"""Test the OneRoster client."""

from oneroster_client import OneRosterClient

def test_client_init():
    """Test client initialization."""
    client = OneRosterClient("https://test.api")
    assert client.api_url == "https://test.api"
