# Stateset Python SDK

A comprehensive Python SDK for the Stateset API, providing easy access to all Stateset resources including returns, warranties, orders, inventory management, work orders, and more.

[![PyPI version](https://badge.fury.io/py/stateset-python.svg)](https://pypi.org/project/stateset-python/)
[![Python Versions](https://img.shields.io/pypi/pyversions/stateset-python)](https://pypi.org/project/stateset-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install stateset-python
```

## Quick Start

```python
import asyncio
from stateset import Stateset

async def main():
    async with Stateset(api_key="your_api_key") as client:
        # Retrieve orders
        orders = await client.orders.list(status="processing")
        print(orders)

        # Create a return
        new_return = await client.returns.create({
            "order_id": "order_123",
            "customer_id": "cust_456",
            "items": [{"order_item_id": "item_1", "quantity": 1}],
            "shipping_address": {
                "name": "Ada Lovelace",
                "address_line1": "123 Analytical Engine Way",
                "city": "London",
                "postal_code": "N1 9GU",
                "country": "GB"
            }
        })
        print(new_return)

# Run the async function
asyncio.run(main())
```

> **Note:** The SDK is asynchronous-only. Use `asyncio.run` or anyio-compatible frameworks to drive client calls.

## Available Resources

The high-level client exposes typed helpers for the most common workflows:

- `client.orders` – CRUD helpers for order management plus `mark_as_shipped` and `cancel`.
- `client.returns` – Create returns, list existing ones, and transition states (`approve`, `cancel`, `mark_received`).
- `client.inventory` – Inspect inventory and issue simple adjustments.
- `client.workflows` – Manage automations (list, get, create, update, delete).
- `client.warranties` – Manage warranty lifecycle transitions.

Any attribute that is not explicitly implemented falls back to a `GenericResource`, giving you thin CRUD wrappers for the corresponding REST collection (for example, `client.agents`, `client.channels`, `client.purchase_orders`). If you need richer semantics, add a dedicated resource module under `stateset/resources/` and wire it up in `stateset/client.py`.

## Configuration

### Custom Base URL

```python
client = Stateset(
    api_key="your_api_key",
    base_url="https://your-custom-stateset-instance.com/api"
)
```

### Custom Timeout or HTTPX Client

```python
import httpx

async_client = httpx.AsyncClient(
    base_url="https://your-custom-stateset-instance.com/api",
    timeout=60.0,
)

client = Stateset(
    api_key="your_api_key",
    client=async_client,  # SDK will not close externally supplied clients
)

# Later, close the shared client when your app shuts down.
await async_client.aclose()
```

## Error Handling

The SDK provides comprehensive error handling:

```python
from stateset import StatesetError, StatesetAPIError, StatesetAuthenticationError

async with Stateset(api_key="your_api_key") as client:
    try:
        result = await client.returns.get("invalid_id")
    except StatesetAuthenticationError:
        print("Authentication failed")
    except StatesetAPIError as e:
        print(f"API error: {e}")
    except StatesetError as e:
        print(f"General error: {e}")
```

## Advanced Usage

### Custom Requests

For advanced use cases, you can make direct API requests:

```python
async with Stateset(api_key="your_api_key") as client:
    # Custom GET request
    response = await client.request("GET", "custom/endpoint", params={"expand": "items"})
    
    # Custom POST request
    response = await client.request(
        "POST", 
        "custom/endpoint",
        data={"key": "value"}
    )
```

## Development

### Setting up for development

```bash
git clone https://github.com/stateset/stateset-python.git
cd stateset-python
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

### Building the package

```bash
pip install build
python -m build
```

### Publishing to PyPI

```bash
pip install twine
twine upload dist/*
```

## Contributing

We welcome issues and pull requests that improve the SDK.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- 📧 Email: support@stateset.com
- 📚 Documentation: [docs.stateset.com](https://docs.stateset.com)
- 🐛 Issues: [GitHub Issues](https://github.com/stateset/stateset-python/issues)
