# Archer API Client Library

A comprehensive Python library for seamless integration with Archer IRM APIs.

## Features

- 🔐 **Secure Authentication**: Built-in session management and token handling
- 🎯 **OOP Architecture**: Clean, intuitive class-based design
- 📦 **Multiple API Support**: RESTful, Web Services, and Content APIs
- 🔄 **Automatic Retries**: Configurable retry logic for failed requests
- 📝 **Type Hints**: Full type annotation support
- 📚 **Extensive Documentation**: Detailed guides and examples

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from archer_api import ArcherClient

# Initialize the client
client = ArcherClient(
    base_url="https://your-archer-instance.com",
    instance_name="YourInstance",
    username="your_username",
    password="your_password"
)

# Get applications
applications = client.rest.applications.get_all()

# Create a record
new_record = client.rest.records.create(
    application_id=123,
    field_values={
        "Field Name": "Field Value",
        "Another Field": "Another Value"
    }
)
```

## Documentation

See the `docs/` directory for detailed documentation.

## License

MIT License