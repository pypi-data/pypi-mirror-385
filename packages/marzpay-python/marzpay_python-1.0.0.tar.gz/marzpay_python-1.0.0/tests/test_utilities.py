"""
Test cases for utility classes
"""

import pytest
from marzpay.utils.phone_number_utils import PhoneNumberUtils
from marzpay.utils.general_utils import GeneralUtils
from marzpay.utils.callback_handler import CallbackHandler
from marzpay import MarzPay


class TestPhoneNumberUtils:
    """Test cases for PhoneNumberUtils"""

    def test_format_phone_number(self):
        """Test phone number formatting"""
        # Test local number
        formatted = PhoneNumberUtils.format_phone_number("0759983853")
        assert formatted == "+256759983853"
        
        # Test number with country code
        formatted = PhoneNumberUtils.format_phone_number("256759983853")
        assert formatted == "+256759983853"
        
        # Test number with + prefix
        formatted = PhoneNumberUtils.format_phone_number("+256759983853")
        assert formatted == "+256759983853"

    def test_is_valid_uganda_phone_number(self):
        """Test Uganda phone number validation"""
        # Valid local number
        assert PhoneNumberUtils.is_valid_uganda_phone_number("0759983853") == True
        
        # Valid number with country code
        assert PhoneNumberUtils.is_valid_uganda_phone_number("256759983853") == True
        
        # Valid number with + prefix
        assert PhoneNumberUtils.is_valid_uganda_phone_number("+256759983853") == True
        
        # Invalid number
        assert PhoneNumberUtils.is_valid_uganda_phone_number("123456789") == False
        
        # Invalid length
        assert PhoneNumberUtils.is_valid_uganda_phone_number("25675998") == False

    def test_normalize_phone_number(self):
        """Test phone number normalization"""
        # Test with + prefix
        normalized = PhoneNumberUtils.normalize_phone_number("0759983853", include_plus=True)
        assert normalized == "+256759983853"
        
        # Test without + prefix
        normalized = PhoneNumberUtils.normalize_phone_number("0759983853", include_plus=False)
        assert normalized == "256759983853"


class TestGeneralUtils:
    """Test cases for GeneralUtils"""

    def test_generate_reference(self):
        """Test reference generation"""
        ref1 = GeneralUtils.generate_reference()
        ref2 = GeneralUtils.generate_reference()
        
        assert ref1 != ref2
        assert len(ref1) == 32  # UUID without dashes

    def test_generate_reference_with_prefix(self):
        """Test reference generation with prefix"""
        ref = GeneralUtils.generate_reference_with_prefix("PAY")
        
        assert ref.startswith("PAY_")
        assert len(ref) > 4  # Should have prefix + underscore + reference

    def test_format_amount(self):
        """Test amount formatting"""
        formatted = GeneralUtils.format_amount(1000.50, "UGX")
        
        assert formatted["formatted"] == "1,000.50"
        assert formatted["raw"] == 1000.50
        assert formatted["currency"] == "UGX"

    def test_cents_to_amount(self):
        """Test cents to amount conversion"""
        amount = GeneralUtils.cents_to_amount(1000)
        assert amount == 10.0

    def test_amount_to_cents(self):
        """Test amount to cents conversion"""
        cents = GeneralUtils.amount_to_cents(10.50)
        assert cents == 1050

    def test_format_currency(self):
        """Test currency formatting"""
        formatted = GeneralUtils.format_currency(1000, "UGX")
        assert formatted == "UGX 1,000.00"

    def test_is_valid_email(self):
        """Test email validation"""
        assert GeneralUtils.is_valid_email("test@example.com") == True
        assert GeneralUtils.is_valid_email("user.name@domain.co.uk") == True
        assert GeneralUtils.is_valid_email("invalid-email") == False
        assert GeneralUtils.is_valid_email("@domain.com") == False

    def test_sanitize_input(self):
        """Test input sanitization"""
        sanitized = GeneralUtils.sanitize_input("  test input  ")
        assert sanitized == "test input"

    def test_generate_random_string(self):
        """Test random string generation"""
        random_str = GeneralUtils.generate_random_string(10)
        assert len(random_str) == 10
        assert random_str.isalnum()

    def test_build_query_string(self):
        """Test query string building"""
        params = {"page": 1, "limit": 10, "status": None}
        query_string = GeneralUtils.build_query_string(params)
        assert "page=1" in query_string
        assert "limit=10" in query_string
        assert "status" not in query_string  # None values should be excluded

    def test_parse_query_string(self):
        """Test query string parsing"""
        query_string = "page=1&limit=10&status=active"
        params = GeneralUtils.parse_query_string(query_string)
        
        assert params["page"] == "1"
        assert params["limit"] == "10"
        assert params["status"] == "active"

    def test_deep_merge_dict(self):
        """Test deep dictionary merging"""
        dict1 = {"a": 1, "b": {"c": 2}}
        dict2 = {"b": {"d": 3}, "e": 4}
        
        merged = GeneralUtils.deep_merge_dict(dict1, dict2)
        
        assert merged["a"] == 1
        assert merged["b"]["c"] == 2
        assert merged["b"]["d"] == 3
        assert merged["e"] == 4

    def test_remove_none_values(self):
        """Test removing None values from dictionary"""
        data = {"a": 1, "b": None, "c": "test", "d": None}
        cleaned = GeneralUtils.remove_none_values(data)
        
        assert "a" in cleaned
        assert "c" in cleaned
        assert "b" not in cleaned
        assert "d" not in cleaned

    def test_truncate_string(self):
        """Test string truncation"""
        text = "This is a very long string that should be truncated"
        truncated = GeneralUtils.truncate_string(text, 20)
        
        assert len(truncated) <= 23  # 20 + "..."
        assert truncated.endswith("...")

    def test_format_json(self):
        """Test JSON formatting"""
        data = {"a": 1, "b": "test"}
        json_str = GeneralUtils.format_json(data)
        
        assert '"a": 1' in json_str
        assert '"b": "test"' in json_str


class TestCallbackHandler:
    """Test cases for CallbackHandler"""

    def setup_method(self):
        """Setup test client and callback handler"""
        self.client = MarzPay(api_key="test_key", api_secret="test_secret")
        self.handler = CallbackHandler(self.client)

    def test_handle_collection_callback(self):
        """Test handling collection callback"""
        callback_data = {
            "type": "collection",
            "data": {
                "transaction_id": "test-tx-123",
                "status": "completed"
            },
            "timestamp": "2024-01-20T10:30:00Z"
        }
        
        result = self.handler.handle_callback(callback_data)
        
        assert result["type"] == "collection"
        assert result["transaction_id"] == "test-tx-123"
        assert result["status"] == "completed"
        assert result["success"] == True

    def test_handle_disbursement_callback(self):
        """Test handling disbursement callback"""
        callback_data = {
            "type": "disbursement",
            "data": {
                "transaction_id": "test-tx-456",
                "status": "failed"
            },
            "timestamp": "2024-01-20T10:30:00Z"
        }
        
        result = self.handler.handle_callback(callback_data)
        
        assert result["type"] == "disbursement"
        assert result["transaction_id"] == "test-tx-456"
        assert result["status"] == "failed"
        assert result["success"] == False

    def test_handle_transaction_callback(self):
        """Test handling transaction callback"""
        callback_data = {
            "type": "transaction",
            "data": {
                "transaction_id": "test-tx-789",
                "status": "processing"
            },
            "timestamp": "2024-01-20T10:30:00Z"
        }
        
        result = self.handler.handle_callback(callback_data)
        
        assert result["type"] == "transaction"
        assert result["transaction_id"] == "test-tx-789"
        assert result["status"] == "processing"
        assert result["success"] == False  # processing is not completed

    def test_handle_generic_callback(self):
        """Test handling generic callback"""
        callback_data = {
            "type": "unknown",
            "data": {
                "some_field": "some_value"
            },
            "timestamp": "2024-01-20T10:30:00Z"
        }
        
        result = self.handler.handle_callback(callback_data)
        
        assert result["type"] == "generic"
        assert result["success"] == True

    def test_validate_callback_data(self):
        """Test callback data validation"""
        # Valid callback data
        valid_data = {
            "type": "collection",
            "data": {"transaction_id": "test-123"}
        }
        assert self.handler._validate_callback_data(valid_data) == True
        
        # Invalid callback data
        invalid_data = {"type": "collection"}  # Missing 'data' field
        assert self.handler._validate_callback_data(invalid_data) == False

    def test_verify_signature(self):
        """Test signature verification"""
        payload = '{"test": "data"}'
        secret = "test_secret"
        
        import hmac
        import hashlib
        
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        assert self.handler.verify_signature(payload, expected_signature, secret) == True
        assert self.handler.verify_signature(payload, "invalid_signature", secret) == False

    def test_get_callback_url(self):
        """Test callback URL generation"""
        url = self.handler.get_callback_url("test-tx-123")
        assert url == "https://your-app.com/webhook/marzpay/callback/test-tx-123"
        
        # Test with custom base URL
        url = self.handler.get_callback_url("test-tx-123", "https://custom.com")
        assert url == "https://custom.com/marzpay/callback/test-tx-123"
