# TimeBack Client

A simple Python client for the TimeBack API.

## Installation

```bash
pip install git+https://github.com/trilogy-group/timeback-client
```

## Usage

```python
from timeback_client import TimeBackClient

client = TimeBackClient("https://api.url")
user = client.get_user("user-id")
print(user)
``` 