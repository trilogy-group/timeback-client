# TimeBack Client Tests

This directory contains tests for the TimeBack API client. The tests are designed to validate that the client correctly implements the OneRoster 1.2 specification.

## Test Structure

Tests are organized into these categories:

- **Unit tests**: Test individual API client methods in isolation.
- **Integration tests**: Test the client's interaction with the OneRoster API.
- **Application tests**: Simulate how real applications would use the client.

## Running Tests

### Prerequisites

Make sure you have the following:

1. Python 3.8+ installed
2. The timeback-client package installed (e.g., in development mode with `pip install -e .`)
3. Access to the staging API (or a test environment)

### Running All Tests

```bash
# From the root of the repository
pytest
```

### Running Only Integration Tests

```bash
# Run only integration tests
pytest -m integration

# Run all tests except integration tests
pytest -m "not integration"
```

### Running Specific Test Files

```bash
# Run all tests in a specific file
pytest tests/test_courses.py

# Run a specific test
pytest tests/test_courses.py::test_create_course
```

### Running Application Tests

```bash
# Run all application tests
pytest tests/application/

# Run a specific application test
pytest tests/application/test_course_application.py::test_application_create_course
```

## Test Environment

All tests run against the staging API by default:

- OneRoster API: `http://staging.alpha-1edtech.ai`
- QTI API: `https://alpha-qti-api-43487de62e73.herokuapp.com/api`

No authentication is required for the staging API.

## Test Data

Tests create and manage their own test data. Each test should:

1. Create any needed test data
2. Run the test
3. Clean up the created data

For example, course tests will:
- Create a test course with a unique ID
- Perform operations on the course
- Delete the course at the end of the test

## Writing New Tests

When writing new tests:

1. Make sure to use the `STAGING_URL` constant when initializing API clients
2. For TimeBackClient tests, always explicitly specify `api_url=STAGING_URL`
3. Mark integration tests with `@pytest.mark.integration`
4. Clean up any created data, even if the test fails
5. Add a docstring explaining what the test does 