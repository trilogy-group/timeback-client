# Release Process

## Overview
This document outlines the steps to publish a new release of the timeback-client package.

## Steps

### 1. Update Version Numbers
Update version numbers in:
- `pyproject.toml` (both `[project]` and `[tool.poetry]` sections)
- `src/timeback_client/__init__.py`

### 2. Build and Test
```bash
# Install dev dependencies
poetry install

# Run tests
poetry run pytest

# Run integration tests
poetry run pytest -v -m "integration"
```

### 3. Commit Changes
```bash
# Stage all changes
git add .

# Commit with semantic versioning message
git commit -m "feat: release version x.y.z"
```

### 4. Create and Push Tag
```bash
# Create new version tag
git tag vx.y.z

# Push commits and tags
git push origin main --tags
```

### 5. Build Distribution
```bash
# Build both wheel and source distributions
poetry build
```
This creates:
- Source distribution: `dist/timeback_client-x.y.z.tar.gz`
- Wheel distribution: `dist/timeback_client-x.y.z-py3-none-any.whl`

### 6. Update Dependencies
Update the version in dependent projects' requirements.txt:
```
git+https://github.com/trilogy-group/timeback-client.git@vx.y.z
```

## Installation Methods
The package can be installed in several ways:

1. From GitHub release tag:
```bash
pip install git+https://github.com/trilogy-group/timeback-client.git@vx.y.z
```

2. From source distribution:
```bash
pip install timeback_client-x.y.z.tar.gz
```

3. From wheel distribution:
```bash
pip install timeback_client-x.y.z-py3-none-any.whl
```

## Versioning
We follow [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for added functionality in a backward compatible manner
- PATCH version for backward compatible bug fixes

## Version History

### v0.2.13
- Added submit quiz endpoint

### v0.2.12
- Version bump

### v0.2.11

### v0.2.10
- Fixed Google Sheets integration to use correct sheet name
- Enhanced error handling for sheet operations
- Added better logging for sheet updates

### v0.2.9
- Enhanced logging for client initialization and API calls
- Added caller tracking for better debugging
- Added environment validation and logging
- Improved error handling for API responses
- Added detailed logging for component operations

### v0.2.8
- Added support for course and component operations
- Improved error handling for API responses
- Enhanced logging for debugging

### v0.2.6
- Modified TimeBackClient to always use production environment
- Forced all API calls to connect to production URL
- Fixed authentication to always use production IDP
- Improved logging to show actual environment being used

### v0.2.5
- Added OrgsAPI class for managing organizations
- Added support for organization creation and retrieval
- Fixed migration script to handle organization dependencies
- Added better error handling for 422 responses
- Improved metadata handling during user migration

### v0.2.3
- Fixed error handling in delete_user method to properly handle empty responses
- Added special handling for 404 errors during deletion (treating them as success)
- Improved JSON response parsing to handle empty or invalid responses
- Added check to avoid redundant updates when a user is already marked for deletion

### v0.2.2
- Improved error handling in delete_user method
- Removed fallback to minimal user data in delete_user method
- Added proper logging for better debugging

### v0.2.1
- Added delete_user method to UsersAPI class
- Fixed error handling in client methods

### v0.2.0
- Implemented service registry pattern for better architecture
- Refactored RosteringService to use UsersAPI internally
- Added dynamic loading of API modules
- Improved documentation and examples
- Backward compatibility for direct method access (with deprecation warning)

### v0.1.4
- Added create_user and update_user methods to RosteringService
- Made API URL parameter optional with default staging URL

### v0.1.3
- Initial public release
- Basic implementation of RosteringService
- Support for listing and getting users 