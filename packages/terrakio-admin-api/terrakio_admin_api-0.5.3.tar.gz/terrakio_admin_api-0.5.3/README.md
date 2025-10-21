# Terrakio Admin API Client

Administrative API client for Terrakio services. This package extends the regular Terrakio API client with additional administrative capabilities.

## Features

- All features from the regular API client
- User management (create, view, edit, delete users)
- Dataset management (create, edit, update, delete datasets)
- Mass stats functionality (create pyramid)

## Installation

```bash
pip install terrakio-admin-api
```

## Usage Example

```python
from terrakio_admin_api import Client

# Initialize the admin client, default url is https://api.terrak.io
admin_client = Client(url = "https://dev-au.terrak.io")

# Login to your admin account
token = admin_client.auth.login(email = "XXX", password = "XXX")
print(f"✓ Login successful, personal token: {token[:10]}...")

# The login account will automatically be used for the requests

# View API key
api_key = admin_client.auth.view_api_key()
print(f"✓ Current API key: {api_key[:10]}...")

# List number of datasets
datasets = admin_client.datasets.list_datasets()
print(f"✓ Listed {len(datasets)} datasets")

# List number of users
users = admin_client.users.list_users()
print(f"✓ Listed {len(users)} users")
```

For more documentation, see the [main repository](https://github.com/HaizeaAnalytics/terrakio-python-api). 