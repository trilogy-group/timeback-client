"""Test the TimeBack client."""

from timeback_client import TimeBackClient

def test_client_init():
    """Test client initialization."""
    client = TimeBackClient("https://test.api")
    assert client.api_url == "https://test.api"
