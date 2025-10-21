# Contributing to MarzPay Python SDK

Thank you for your interest in contributing to the MarzPay Python SDK! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip
- git

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/marzpay-python.git
   cd marzpay-python
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write comprehensive docstrings for all public methods
- Keep functions small and focused

### Testing

- Write tests for all new functionality
- Ensure all tests pass before submitting PR
- Maintain at least 90% test coverage
- Use descriptive test names

Run tests:
```bash
pytest tests/ -v
```

### Documentation

- Update README.md for new features
- Add examples for new functionality
- Update API documentation
- Keep CHANGELOG.md updated

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

### PR Requirements

- All tests must pass
- Code must be properly formatted
- Documentation must be updated
- PR description must explain changes
- Link any related issues

## Architecture

### Project Structure

```
marzpay/
├── __init__.py
├── marzpay.py              # Main client class
├── classes/                 # API classes
│   ├── collections.py
│   ├── disbursements.py
│   ├── phone_verification.py
│   └── ...
├── errors/                  # Exception classes
│   └── marzpay_error.py
└── utils/                   # Utility classes
    ├── phone_number_utils.py
    ├── general_utils.py
    └── callback_handler.py
```

### Design Principles

- **Single Responsibility**: Each class has one clear purpose
- **Composition over Inheritance**: Use composition for API modules
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Type Safety**: Use type hints throughout
- **Testability**: Design for easy testing

## API Design

### Client Initialization

```python
from marzpay import MarzPay

client = MarzPay(
    api_key="your_api_key",
    api_secret="your_api_secret"
)
```

### API Methods

All API methods follow consistent patterns:
- Accept parameters as dictionaries
- Return structured response data
- Raise `MarzPayError` for failures
- Support optional parameters with sensible defaults

### Error Handling

```python
from marzpay.errors import MarzPayError

try:
    result = client.collections.collect_money(params)
except MarzPayError as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.code}")
    print(f"Status: {e.status}")
```

## Security

- Never commit API credentials
- Use environment variables for sensitive data
- Validate all input parameters
- Sanitize user input
- Follow secure coding practices

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release tag
4. Build and publish to PyPI

## Support

- GitHub Issues: [https://github.com/Katznicho/marzpay-python/issues](https://github.com/Katznicho/marzpay-python/issues)
- Email: dev@wearemarz.com
- Documentation: [https://wallet.wearemarz.com/documentation](https://wallet.wearemarz.com/documentation)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
