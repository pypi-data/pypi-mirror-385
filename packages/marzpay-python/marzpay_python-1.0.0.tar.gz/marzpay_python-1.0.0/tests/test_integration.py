"""
Integration tests for MarzPay Python SDK
"""

import pytest
import os
from unittest.mock import patch
from marzpay import MarzPay
from marzpay.errors import MarzPayError


class TestMarzPayIntegration:
    """Integration tests for MarzPay SDK"""

    def setup_method(self):
        """Setup test client"""
        # Use environment variables if available, otherwise use test values
        api_key = os.getenv('MARZPAY_API_KEY', 'test_key')
        api_secret = os.getenv('MARZPAY_API_SECRET', 'test_secret')
        
        self.client = MarzPay(api_key=api_key, api_secret=api_secret)

    @pytest.mark.integration
    def test_full_collection_workflow(self):
        """Test complete collection workflow"""
        with patch.object(self.client, 'request') as mock_request:
            # Mock successful collection
            mock_request.return_value = {
                "status": "success",
                "message": "Collection initiated successfully",
                "data": {
                    "transaction": {
                        "uuid": "test-uuid-123",
                        "reference": "test-ref-456",
                        "status": "processing"
                    },
                    "collection": {
                        "amount": {"formatted": "1,000.00", "raw": 1000, "currency": "UGX"},
                        "provider": "mtn",
                        "phone_number": "+256759983853",
                        "mode": "live"
                    }
                }
            }
            
            # Step 1: Collect money
            collection_params = {
                "phone_number": "256759983853",
                "amount": 1000,
                "description": "Test payment",
                "callback_url": "https://example.com/webhook"
            }
            
            collection_result = self.client.collections.collect_money(collection_params)
            
            assert collection_result["status"] == "success"
            assert "transaction" in collection_result["data"]
            
            # Step 2: Get collection details
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "transaction": {
                        "uuid": "test-uuid-123",
                        "status": "completed"
                    }
                }
            }
            
            details = self.client.collections.get_collection_details("test-uuid-123")
            assert details["status"] == "success"

    @pytest.mark.integration
    def test_full_disbursement_workflow(self):
        """Test complete disbursement workflow"""
        with patch.object(self.client, 'request') as mock_request:
            # Mock successful disbursement
            mock_request.return_value = {
                "status": "success",
                "message": "Send money initiated successfully",
                "data": {
                    "transaction": {
                        "uuid": "test-uuid-456",
                        "reference": "test-ref-789",
                        "status": "processing"
                    },
                    "disbursement": {
                        "amount": {"formatted": "1,000.00", "raw": 1000, "currency": "UGX"},
                        "provider": "airtel",
                        "phone_number": "+256759983853",
                        "mode": "live"
                    }
                }
            }
            
            # Step 1: Send money
            disbursement_params = {
                "phone_number": "256759983853",
                "amount": 1000,
                "description": "Payment to customer",
                "callback_url": "https://example.com/webhook"
            }
            
            disbursement_result = self.client.disbursements.send_money(disbursement_params)
            
            assert disbursement_result["status"] == "success"
            assert "transaction" in disbursement_result["data"]
            
            # Step 2: Get disbursement details
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "transaction": {
                        "uuid": "test-uuid-456",
                        "status": "completed"
                    }
                }
            }
            
            details = self.client.disbursements.get_send_money_details("test-uuid-456")
            assert details["status"] == "success"

    @pytest.mark.integration
    def test_phone_verification_workflow(self):
        """Test phone verification workflow"""
        with patch.object(self.client, 'request') as mock_request:
            # Mock service info
            mock_request.return_value = {
                "success": True,
                "data": {
                    "service_name": "Phone Number Verification",
                    "is_active": True,
                    "api_configured": True
                }
            }
            
            # Step 1: Get service info
            service_info = self.client.phone_verification.get_service_info()
            assert service_info["success"] == True
            
            # Step 2: Check subscription status
            mock_request.return_value = {
                "success": True,
                "data": {
                    "is_subscribed": True,
                    "service_name": "Phone Number Verification"
                }
            }
            
            subscription = self.client.phone_verification.get_subscription_status()
            assert subscription["success"] == True
            
            # Step 3: Verify phone number
            mock_request.return_value = {
                "success": True,
                "message": "Phone number verified successfully",
                "data": {
                    "phone_number": "256759983853",
                    "first_name": "MARY",
                    "last_name": "NAKAMYA",
                    "full_name": "MARY NAKAMYA",
                    "verification_status": "verified"
                }
            }
            
            verification = self.client.phone_verification.verify_phone_number("256759983853")
            assert verification["success"] == True
            assert verification["data"]["full_name"] == "MARY NAKAMYA"

    @pytest.mark.integration
    def test_webhook_handling_workflow(self):
        """Test webhook handling workflow"""
        # Test webhook payload processing
        webhook_payload = {
            "type": "collection",
            "data": {
                "transaction_id": "test-tx-123",
                "status": "completed",
                "amount": 1000
            },
            "timestamp": "2024-01-20T10:30:00Z"
        }
        
        # Process webhook
        result = self.client.callback_handler.handle_callback(webhook_payload)
        
        assert result["type"] == "collection"
        assert result["transaction_id"] == "test-tx-123"
        assert result["success"] == True

    @pytest.mark.integration
    def test_utility_functions_integration(self):
        """Test utility functions integration"""
        # Test phone number utilities
        formatted = self.client.format_phone_number("0759983853")
        assert formatted == "+256759983853"
        
        is_valid = self.client.is_valid_phone_number("256759983853")
        assert is_valid == True
        
        # Test reference generation
        ref1 = self.client.generate_reference()
        ref2 = self.client.generate_reference()
        assert ref1 != ref2
        
        # Test reference with prefix
        prefixed_ref = self.client.generate_reference_with_prefix("PAY")
        assert prefixed_ref.startswith("PAY_")

    @pytest.mark.integration
    def test_error_handling_integration(self):
        """Test error handling integration"""
        with patch.object(self.client, 'request') as mock_request:
            # Mock API error
            mock_request.side_effect = MarzPayError("API Error", "API_ERROR", 400)
            
            with pytest.raises(MarzPayError) as exc_info:
                self.client.collections.collect_money({
                    "phone_number": "256759983853",
                    "amount": 1000
                })
            
            assert "API Error" in str(exc_info.value)
            assert exc_info.value.code == "API_ERROR"

    @pytest.mark.integration
    def test_connection_test(self):
        """Test connection test functionality"""
        with patch.object(self.client, 'request') as mock_request:
            # Mock successful connection
            mock_request.return_value = {
                "data": {
                    "account": {
                        "status": {"account_status": "active"},
                        "business_name": "Test Business"
                    }
                }
            }
            
            result = self.client.test_connection()
            assert result["status"] == "success"
            
            # Mock connection failure
            mock_request.side_effect = MarzPayError("Connection failed", "CONNECTION_ERROR", 500)
            
            result = self.client.test_connection()
            assert result["status"] == "error"
            assert "API connection failed" in result["message"]
