"""Basic TimeBack API client."""

import requests

class TimeBackClient:
    """Simple client for TimeBack API."""
    
    def __init__(self, api_url: str):
        """Initialize client with API URL."""
        self.api_url = api_url.rstrip('/')
        
    def get_user(self, user_id: str) -> dict:
        """Get a user by ID."""
        response = requests.get(f"{self.api_url}/users/{user_id}")
        response.raise_for_status()
        return response.json() 