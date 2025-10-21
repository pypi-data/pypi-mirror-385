# MarzPay Python SDK

Official Python SDK for MarzPay - Mobile Money Payment Platform for Uganda.

## Features

- **Complete API Coverage** - Collections, Disbursements, Accounts, Balance, Transactions, Services, Webhooks, and Phone Verification
- **Error Handling** - Comprehensive error handling with custom exception classes
- **Phone Number Utilities** - Built-in phone number validation and formatting
- **Webhook Support** - Easy webhook handling and validation
- **Testing** - Full test coverage with pytest
- **Documentation** - Comprehensive documentation and examples
- **Professional Grade** - Production-ready SDK with comprehensive error handling

## Installation

### pip

```bash
pip install marzpay-python
```

### Development

```bash
git clone https://github.com/Katznicho/marzpay-python.git
cd marzpay-python
pip install -e .
```

## Quick Start

### Basic Usage

```python
from marzpay import MarzPay

# Initialize the client
client = MarzPay(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Collect money from customer
result = client.collections.collect_money({
    "phone_number": "256759983853",
    "amount": 5000,
    "description": "Payment for services"
})

print(f"Collection ID: {result['data']['collection_id']}")
```

### Phone Verification

```python
from marzpay import MarzPay

client = MarzPay(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Verify phone number
result = client.phone_verification.verify_phone_number("256759983853")

if result["success"]:
    print(f"User: {result['data']['full_name']}")
    print(f"Phone: {result['data']['phone_number']}")
```

## API Reference

### Collections API

```python
# Collect money
result = client.collections.collect_money({
    "phone_number": "256759983853",
    "amount": 10000,
    "description": "Payment for services"
})

# Get collection details
collection = client.collections.get_collection_details("collection-uuid")

# Get available services
services = client.collections.get_services()

# Get all collections with filters
collections = client.collections.get_collections(
    page=1,
    limit=20,
    status="completed"
)
```

### Disbursements API

```python
# Send money
result = client.disbursements.send_money({
    "phone_number": "256759983853",
    "amount": 5000,
    "description": "Refund payment"
})

# Get disbursement details
disbursement = client.disbursements.get_send_money_details("disbursement-uuid")
```

### Phone Verification API

```python
# Verify phone number
result = client.phone_verification.verify_phone_number("256759983853")

# Get service information
service_info = client.phone_verification.get_service_info()

# Check subscription status
subscription = client.phone_verification.get_subscription_status()
```

### Webhooks

```python
# Handle webhook callback
result = client.callback_handler.handle_callback(webhook_data)

# Verify webhook signature
is_valid = client.callback_handler.verify_signature(payload, signature, secret)
```

## Configuration

```python
from marzpay import MarzPay

client = MarzPay(
    api_key="your_api_key",
    api_secret="your_api_secret",
    base_url="https://wallet.wearemarz.com/api/v1",  # optional
    timeout=30,  # optional, in seconds
)
```

## Error Handling

```python
from marzpay import MarzPay
from marzpay.errors import MarzPayError

try:
    result = client.collections.collect_money(request_data)
except MarzPayError as e:
    print(f"Error Code: {e.code}")
    print(f"HTTP Status: {e.status}")
    print(f"Message: {e.message}")
    print(f"Details: {e.details}")
```

## Environment Variables

```python
import os
from marzpay import MarzPay

client = MarzPay(
    api_key=os.getenv("MARZPAY_API_KEY"),
    api_secret=os.getenv("MARZPAY_API_SECRET"),
)
```

## Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=marzpay

# Run specific test file
pytest tests/test_collections.py
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Format code
black marzpay tests

# Lint code
flake8 marzpay tests

# Type checking
mypy marzpay
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Official Documentation

For complete API documentation, visit: [https://wallet.wearemarz.com/documentation](https://wallet.wearemarz.com/documentation)

## Support

- Issues: [https://github.com/Katznicho/marzpay-python/issues](https://github.com/Katznicho/marzpay-python/issues)
- Email: dev@wearemarz.com


