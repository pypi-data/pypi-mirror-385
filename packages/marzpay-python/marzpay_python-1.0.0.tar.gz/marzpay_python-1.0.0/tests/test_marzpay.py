"""
Test cases for main MarzPay client
"""

import pytest
import os
from unittest.mock import Mock, patch
from marzpay import MarzPay
from marzpay.errors import MarzPayError


class TestMarzPay:
    """Test cases for MarzPay client"""

    def test_initialization_with_credentials(self):
        """Test MarzPay initialization with valid credentials"""
        client = MarzPay(
            api_key="test_key",
            api_secret="test_secret"
        )
        
        assert client.config["api_key"] == "test_key"
        assert client.config["api_secret"] == "test_secret"
        assert client.config["base_url"] == "https://wallet.wearemarz.com/api/v1"

    def test_initialization_without_credentials(self):
        """Test MarzPay initialization without credentials raises error"""
        with pytest.raises(MarzPayError) as exc_info:
            MarzPay(api_key="", api_secret="")
        
        assert "API credentials are required" in str(exc_info.value)
        assert exc_info.value.code == "MISSING_CREDENTIALS"

    def test_initialization_with_custom_config(self):
        """Test MarzPay initialization with custom configuration"""
        client = MarzPay(
            api_key="test_key",
            api_secret="test_secret",
            base_url="https://custom.api.com",
            timeout=60,
            max_retries=5
        )
        
        assert client.config["base_url"] == "https://custom.api.com"
        assert client.config["timeout"] == 60

    def test_get_auth_header(self):
        """Test authentication header generation"""
        client = MarzPay(api_key="test_key", api_secret="test_secret")
        auth_header = client.get_auth_header()
        
        assert auth_header.startswith("Basic ")
        # Decode and verify credentials
        import base64
        credentials = base64.b64decode(auth_header.split(" ")[1]).decode()
        assert credentials == "test_key:test_secret"

    def test_set_credentials(self):
        """Test updating credentials at runtime"""
        client = MarzPay(api_key="old_key", api_secret="old_secret")
        
        client.set_credentials("new_key", "new_secret")
        
        assert client.config["api_key"] == "new_key"
        assert client.config["api_secret"] == "new_secret"

    def test_set_credentials_validation(self):
        """Test credential validation"""
        client = MarzPay(api_key="test_key", api_secret="test_secret")
        
        with pytest.raises(MarzPayError) as exc_info:
            client.set_credentials("", "test_secret")
        
        assert "Both API key and secret are required" in str(exc_info.value)

    def test_get_info(self):
        """Test SDK information retrieval"""
        client = MarzPay(api_key="test_key", api_secret="test_secret")
        info = client.get_info()
        
        assert info["name"] == "MarzPay Python SDK"
        assert info["version"] == "1.0.0"
        assert "Collections API" in info["features"]
        assert "Disbursements API" in info["features"]

    @patch('marzpay.marzpay.MarzPay.request')
    def test_test_connection_success(self, mock_request):
        """Test successful connection test"""
        mock_request.return_value = {
            "data": {
                "account": {
                    "status": {"account_status": "active"},
                    "business_name": "Test Business"
                }
            }
        }
        
        client = MarzPay(api_key="test_key", api_secret="test_secret")
        result = client.test_connection()
        
        assert result["status"] == "success"
        assert "API connection successful" in result["message"]

    @patch('marzpay.marzpay.MarzPay.request')
    def test_test_connection_failure(self, mock_request):
        """Test connection test failure"""
        mock_request.side_effect = MarzPayError("Connection failed", "CONNECTION_ERROR", 500)
        
        client = MarzPay(api_key="test_key", api_secret="test_secret")
        result = client.test_connection()
        
        assert result["status"] == "error"
        assert "API connection failed" in result["message"]

    def test_utility_methods(self):
        """Test utility methods"""
        client = MarzPay(api_key="test_key", api_secret="test_secret")
        
        # Test phone number formatting
        formatted = client.format_phone_number("0759983853")
        assert formatted == "+256759983853"
        
        # Test phone number validation
        assert client.is_valid_phone_number("0759983853") == True
        assert client.is_valid_phone_number("123456789") == False
        
        # Test reference generation
        ref1 = client.generate_reference()
        ref2 = client.generate_reference()
        assert ref1 != ref2
        assert len(ref1) == 32
        
        # Test reference with prefix
        prefixed_ref = client.generate_reference_with_prefix("PAY")
        assert prefixed_ref.startswith("PAY_")

    def test_api_modules_initialization(self):
        """Test that all API modules are properly initialized"""
        client = MarzPay(api_key="test_key", api_secret="test_secret")
        
        # Check that all API modules exist
        assert hasattr(client, 'collections')
        assert hasattr(client, 'disbursements')
        assert hasattr(client, 'accounts')
        assert hasattr(client, 'balance')
        assert hasattr(client, 'transactions')
        assert hasattr(client, 'services')
        assert hasattr(client, 'webhooks')
        assert hasattr(client, 'phone_verification')
        
        # Check utility modules
        assert hasattr(client, 'phone_utils')
        assert hasattr(client, 'utils')
        assert hasattr(client, 'callback_handler')

    @patch('requests.Session.request')
    def test_request_method_json(self, mock_request):
        """Test request method with JSON data"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        client = MarzPay(api_key="test_key", api_secret="test_secret")
        result = client.request("/test", method="POST", data={"key": "value"})
        
        assert result == {"status": "success"}
        mock_request.assert_called_once()

    @patch('requests.Session.request')
    def test_request_method_multipart(self, mock_request):
        """Test request method with multipart data"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        client = MarzPay(api_key="test_key", api_secret="test_secret")
        result = client.request("/test", method="POST", data={"key": "value"}, content_type="multipart")
        
        assert result == {"status": "success"}
        mock_request.assert_called_once()

    @patch('requests.Session.request')
    def test_request_method_form(self, mock_request):
        """Test request method with form data"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        client = MarzPay(api_key="test_key", api_secret="test_secret")
        result = client.request("/test", method="POST", data={"key": "value"}, content_type="form")
        
        assert result == {"status": "success"}
        mock_request.assert_called_once()

    @patch('requests.Session.request')
    def test_request_error_handling(self, mock_request):
        """Test request error handling"""
        from requests.exceptions import RequestException
        
        mock_request.side_effect = RequestException("Network error")
        
        client = MarzPay(api_key="test_key", api_secret="test_secret")
        
        with pytest.raises(MarzPayError) as exc_info:
            client.request("/test")
        
        assert "Network error" in str(exc_info.value)
        assert exc_info.value.code == "NETWORK_ERROR"
