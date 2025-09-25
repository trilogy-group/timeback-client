# TimeBack Client

A Python client for the TimeBack API (OneRoster 1.2 implementation).

## Installation

```bash
pip install git+https://github.com/trilogy-group/timeback-client.git@v0.2.0
```

## Usage

The TimeBack client is organized into three main services following the OneRoster 1.2 specification:

- Rostering Service (`/ims/oneroster/rostering/v1p2`) - User and organization management
- Gradebook Service (`/ims/oneroster/gradebook/v1p2`) - Grades and assessments
- Resources Service (`/ims/oneroster/resources/v1p2`) - Learning resources
- QTI Service (`/api`) - Assessment content operations (QTI 3.0)
- PowerPath Service - Course syllabus and pathway operations

Each service provides access to specialized API classes for different entity types.

### Basic Usage

```python
from timeback_client import TimeBackClient

# Initialize the client (uses default production URL)
client = TimeBackClient()

# Use the users API through the rostering service
users = client.rostering.users.list_users(limit=10)
user = client.rostering.users.get_user("user-id")

# Use the QTI service
qti_items = client.qti.assessment_items.list_assessment_items()

# Use the PowerPath service
syllabus = client.powerpath.get_course_syllabus("course-id")

# Use the gradebook service (coming soon)
# grades = client.gradebook.grades.list_grades()

# Use the resources service (coming soon)
# resources = client.resources.resources.list_resources()
```

### Services and APIs

#### Rostering Service

The rostering service provides access to various entity APIs:

```python
# Get the rostering service
rostering = client.rostering

# Access the users API
users_api = rostering.users

# List users with pagination, filtering, and sorting
users = users_api.list_users(
    limit=10,                        # Maximum number of users to return
    offset=0,                        # Number of users to skip
    sort="familyName",               # Sort by family name
    order_by="asc",                  # Sort ascending
    filter_expr="role='student'",    # Only get students
    fields=['sourcedId', 'givenName', 'familyName', 'email']  # Fields to return
)

# Get a specific user
user = users_api.get_user("user-id")

# Create a new user
from timeback_client.models.user import User, RoleAssignment, OrgRef, UserRole
new_user = User(
    sourcedId="unique-id",
    givenName="John",
    familyName="Doe",
    email="john.doe@example.com",
    roles=[
        RoleAssignment(
            role=UserRole.STUDENT,
            org=OrgRef(sourcedId="org-id")
        )
    ]
)
result = users_api.create_user(new_user)

# Update a user
user.givenName = "Jonathan"
result = users_api.update_user(user.sourcedId, user)
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
students = users_api.list_users(filter_expr="role='student' AND status='active'")

# Get all parents
parents = users_api.list_users(filter_expr="role='parent'")

# Get users by organization
org_users = users_api.list_users(filter_expr="org.sourcedId='org-id'")
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

#### QTI Service

The QTI service provides access to assessment content APIs (QTI 3.0):

```python
# Get the QTI service
qti = client.qti

# List assessment items
items = qti.assessment_items.list_assessment_items()
```

#### PowerPath Service

The PowerPath service provides access to course syllabus and pathway APIs:

```python
# Get the PowerPath service
powerpath = client.powerpath

# Get course syllabus
syllabus = powerpath.get_course_syllabus("course-id")
```

### PowerPath Test Assignments

Endpoints exposed by this client (thin wrappers, no client-side data manipulation):

- POST `/powerpath/test-assignments`: Create an individual test assignment
- PUT `/powerpath/test-assignments/{id}`: Update an individual test assignment
- GET `/powerpath/test-assignments/{id}`: Get a test assignment
- DELETE `/powerpath/test-assignments/{id}`: Delete (soft-delete) a test assignment
- GET `/powerpath/test-assignments`: List test assignments for students (query: `student`, `status`, `subject`, `grade`, `page`, `limit`)
- GET `/powerpath/test-assignments/admin`: List test assignments for admins (same optional filters)

Example usage:

```python
from timeback_client import TimeBackClient

client = TimeBackClient()

# List test assignments for a student
assignments = client.powerpath.list_test_assignments(
    student="student-id",
    status="active",    # optional
    subject="Math",     # optional
    grade="5",          # optional
    page=1,              # optional
    limit=25             # optional
)

# Create a test assignment
created = client.powerpath.create_test_assignment({
    "student": "student-id",
    "subject": "Math",
    "grade": "5",
    # ... additional fields as required by the API ...
})
```

## API Structure

The client follows the OneRoster 1.2 API structure:

```
Base URL (http://staging.alpha-1edtech.com/)
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

## Architecture

The client uses a service registry pattern to dynamically load specialized API classes for different entity types:

```
TimeBackClient
├── rostering (RosteringService)
│   ├── users (UsersAPI)
│   ├── orgs (OrgsAPI) - coming soon
│   └── ... other entity APIs
├── gradebook (GradebookService)
│   └── ... entity APIs coming soon
├── resources (ResourcesService)
│   └── ... entity APIs coming soon
├── qti (QTIService)
│   └── assessment_items (AssessmentItemsAPI)
└── powerpath (PowerPathService)
    └── ... entity APIs coming soon
```

This architecture allows for:
- Clean separation of concerns
- No code duplication
- Easy addition of new entity types
- Consistent API access patterns

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
    users = client.rostering.users.list_users()
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

## Environment Configuration

The TimeBack client always uses the production API URL by default. The `environment` parameter is kept for backward compatibility but is ignored. You can specify custom URLs if needed:

```python
from timeback_client import TimeBackClient

# Default (production)
client = TimeBackClient(
    client_id="your-production-client-id",
    client_secret="your-production-client-secret"
)

# Custom API URLs (advanced usage)
client = TimeBackClient(
    api_url="http://staging.alpha-1edtech.com/",
    qti_api_url="https://qti.alpha-1edtech.com/api",
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

### Authentication

The client uses OAuth2 client credentials flow for authentication. You'll need to request Client ID and Secret pairs from AE Studio for both staging and production environments. Contact:
- carlos@ae.studio
- wellington.santos@ae.studio
- ege@ae.studio

The client will automatically handle token generation and renewal.

### Migrating from Staging to Production

The package includes a migration script to help transfer data from staging to production. To migrate users:

1. First, request production credentials from AE Studio
2. Run the migration script:

```bash
python -m timeback_client.scripts.migrate_users \
    --staging-client-id YOUR_STAGING_CLIENT_ID \
    --staging-client-secret YOUR_STAGING_CLIENT_SECRET \
    --prod-client-id YOUR_PROD_CLIENT_ID \
    --prod-client-secret YOUR_PROD_CLIENT_SECRET
```

You can also use the `--dry-run` flag to see what would be migrated without making any changes.

The script will:
1. Fetch all users from staging
2. Create them in production
3. Verify the migration was successful
4. Provide detailed logs of the process

You can also use the migration functions in your own code:

```python
from timeback_client import TimeBackClient, migrate_users, verify_migration

staging_client = TimeBackClient(
    environment="staging",
    client_id="staging-client-id",
    client_secret="staging-client-secret"
)

prod_client = TimeBackClient(
    environment="production",
    client_id="prod-client-id",
    client_secret="prod-client-secret"
)

# Perform migration
total, successful, failed = migrate_users(staging_client, prod_client)

# Verify migration
success = verify_migration(staging_client, prod_client) 