# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Best Practices

### API Credentials

- **Never commit API credentials** to version control
- Use environment variables for sensitive data:
  ```python
  import os
  from marzpay import MarzPay
  
  client = MarzPay(
      api_key=os.getenv('MARZPAY_API_KEY'),
      api_secret=os.getenv('MARZPAY_API_SECRET')
  )
  ```

### Webhook Security

- Always verify webhook signatures:
  ```python
  is_valid = client.callback_handler.verify_signature(
      payload, signature, webhook_secret
  )
  ```

### Input Validation

- The SDK validates all input parameters
- Phone numbers are automatically formatted and validated
- Amounts are validated for positive values
- References are generated as secure UUIDs

### Network Security

- All API calls use HTTPS
- Basic authentication is used for API access
- Request/response data is not logged by default

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **DO NOT** create a public GitHub issue
2. Email security details to: security@wearemarz.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- We will acknowledge receipt within 24 hours
- We will provide updates every 72 hours
- We aim to resolve critical issues within 7 days

### Security Checklist

Before using the SDK in production:

- [ ] API credentials are stored securely
- [ ] Environment variables are used for configuration
- [ ] Webhook signatures are verified
- [ ] Input validation is enabled
- [ ] Error handling is implemented
- [ ] Logging is configured appropriately
- [ ] HTTPS is used for all communications
- [ ] Regular security updates are applied

## Security Audit

The MarzPay Python SDK has been designed with security in mind:

- **Input Validation**: All parameters are validated before API calls
- **Error Handling**: Secure error messages that don't leak sensitive information
- **Authentication**: Secure credential handling
- **Network Security**: HTTPS-only communications
- **Webhook Security**: Signature verification for webhook authenticity

## Contact

For security-related questions or concerns:
- Email: security@wearemarz.com
- Response time: Within 24 hours

## Acknowledgments

We appreciate the security research community and responsible disclosure practices.
