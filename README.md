# TimeBack Client

A Python client for the TimeBack API (OneRoster 1.2 implementation).

## Installation

```bash
pip install git+https://github.com/trilogy-group/timeback-client.git@v0.1.3
```

## Usage

The TimeBack client is organized into three main services following the OneRoster 1.2 specification:

- Rostering Service (`/ims/oneroster/rostering/v1p2`) - User and organization management
- Gradebook Service (`/ims/oneroster/gradebook/v1p2`) - Grades and assessments
- Resources Service (`/ims/oneroster/resources/v1p2`) - Learning resources

### Basic Usage

```python
from timeback_client import TimeBackClient

# Initialize the client (uses default staging URL)
client = TimeBackClient()

# Use the rostering service
users = client.rostering.list_users(limit=10)
user = client.rostering.get_user("user-id")

# Use the gradebook service
grades = client.gradebook.get_grades()  # Coming soon

# Use the resources service
resources = client.resources.list_resources()  # Coming soon
```

### Services

#### Rostering Service

The rostering service handles all user and organization-related operations:

```python
# Get the rostering service
rostering = client.rostering

# List users with pagination, filtering, and sorting
users = rostering.list_users(
    limit=10,                        # Maximum number of users to return
    offset=0,                        # Number of users to skip
    sort="familyName:asc",          # Sort by family name ascending
    filter_expr="role='student'",    # Only get students
    fields=['sourcedId', 'givenName', 'familyName', 'email']  # Fields to return
)

# Get a specific user
user = rostering.get_user("user-id")
```

##### Response Structure

The API returns user objects with the following structure:

```python
{
    "user": {
        "sourcedId": "unique-id",
        "status": "active",  # or "tobedeleted"
        "dateLastModified": "2025-03-14T12:07:50.211Z",
        "metadata": {
            "phone": "123-456-7890",
            "address": {
                "country": "United States",
                "city": "Example City",
                "state": "CA",
                "zip": "12345"
            }
        },
        "enabledUser": true,
        "givenName": "John",
        "familyName": "Doe",
        "roles": [
            {
                "roleType": "primary",
                "role": "student",  # or "parent" or "teacher"
                "org": {
                    "href": "org-url",
                    "sourcedId": "org-id",
                    "type": "org"
                }
            }
        ],
        "email": "john.doe@example.com"
    }
}
```

##### Filtering Users

You can filter users by various fields using the `filter_expr` parameter:

```python
# Get all active students
students = rostering.list_users(filter_expr="role='student' AND status='active'")

# Get all parents
parents = rostering.list_users(filter_expr="role='parent'")

# Get users by organization
org_users = rostering.list_users(filter_expr="org.sourcedId='org-id'")
```

#### Gradebook Service

The gradebook service handles all grade and assessment-related operations (coming soon):

```python
# Get the gradebook service
gradebook = client.gradebook

# Methods coming soon
```

#### Resources Service

The resources service handles all learning resource operations (coming soon):

```python
# Get the resources service
resources = client.resources

# Methods coming soon
```

## API Structure

The client follows the OneRoster 1.2 API structure:

```
Base URL (http://oneroster-staging.us-west-2.elasticbeanstalk.com)
└── /ims/oneroster
    ├── /rostering/v1p2
    │   ├── /users
    │   ├── /orgs
    │   └── ...
    ├── /gradebook/v1p2
    │   ├── /grades
    │   └── ...
    └── /resources/v1p2
        ├── /resources
        └── ...
```

## Error Handling

The client will raise standard `requests` exceptions:
- `requests.exceptions.HTTPError` for HTTP errors (4xx, 5xx)
- `requests.exceptions.ConnectionError` for network problems
- `requests.exceptions.Timeout` for timeout errors
- `requests.exceptions.RequestException` for all other errors

Example error handling:

```python
from requests.exceptions import HTTPError, ConnectionError

try:
    users = client.rostering.list_users()
except HTTPError as e:
    if e.response.status_code == 404:
        print("Resource not found")
    elif e.response.status_code == 401:
        print("Authentication failed")
    else:
        print(f"HTTP error occurred: {e}")
except ConnectionError as e:
    print(f"Network error occurred: {e}")
```

## Development

```bash
# Clone the repository
git clone https://github.com/trilogy-group/timeback-client.git

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run integration tests only
poetry run pytest -v -m "integration"
```

For release procedures and versioning guidelines, see [RELEASE.md](RELEASE.md).

## Security Best Practices

1. Always use HTTPS for production environments
2. Never commit API keys or sensitive data to version control
3. Use environment variables for configuration
4. Implement proper error handling to avoid exposing sensitive information
5. Validate and sanitize all input data before making API calls 