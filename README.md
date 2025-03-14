# OneRoster Client

A simple Python client for the OneRoster API.

## Installation

```bash
pip install git+https://github.com/your-org/oneroster-client.git
```

## Usage

```python
from oneroster_client import OneRosterClient

client = OneRosterClient("https://api.url")
user = client.get_user("user-id")
print(user)
``` 