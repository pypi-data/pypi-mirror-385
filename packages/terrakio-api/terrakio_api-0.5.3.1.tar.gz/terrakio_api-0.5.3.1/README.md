# Terrakio API Client

A Python client for Terrakio API. This package provides a user-friendly interface for accessing Terrakio's data services.

## Features

- Authentication
- WCS queries and data retrieval
- Mass stats related functionalities

## Installation

```bash
pip install terrakio-api
```

## Usage Example

```python
from terrakio_api import Client
from shapely.geometry import Point

# Initialize the client
client = Client( url = "https://dev-au.terrak.io")

# Login to your account
token = client.auth.login(email = "XXX", password = "XXX")
print(f"✓ Login successful, personal token: {token[:10]}...")

# The login account will automatically be used for the requests

# View API key
api_key = client.auth.view_api_key()
print(f"✓ Current API key: {api_key[:10]}...")

# Create a geographic feature
point = Point(149.057, -35.1548)

# Make a WCS request
dataset = client.geoquery(
     expr="prec=MSWX.precipitation@(year=2024, month=1)\nprec",
     feature=point,
     output="netcdf"
)
```

For more documentation, see the [main repository](https://github.com/HaizeaAnalytics/terrakio-python-api). 