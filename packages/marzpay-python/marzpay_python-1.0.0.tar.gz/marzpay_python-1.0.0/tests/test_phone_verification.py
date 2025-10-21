"""
Test cases for Phone Verification API
"""

import pytest
from unittest.mock import Mock, patch
from marzpay import MarzPay
from marzpay.errors import MarzPayError


class TestPhoneVerificationAPI:
    """Test cases for Phone Verification API"""

    def setup_method(self):
        """Setup test client"""
        self.client = MarzPay(api_key="test_key", api_secret="test_secret")

    def test_verify_phone_number_success(self):
        """Test successful phone number verification"""
        with patch.object(self.client, 'request') as mock_request:
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
            
            result = self.client.phone_verification.verify_phone_number("256759983853")
            
            assert result["success"] == True
            assert result["data"]["full_name"] == "MARY NAKAMYA"
            mock_request.assert_called_once_with(
                '/phone-verification/verify', 
                method='POST', 
                data={'phone_number': '256759983853'}, 
                content_type='json'
            )

    def test_verify_phone_number_failure(self):
        """Test phone number verification failure"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "success": False,
                "message": "Phone number not found or not registered",
                "error": "Number not found in database"
            }
            
            result = self.client.phone_verification.verify_phone_number("256759983853")
            
            assert result["success"] == False
            assert "not found" in result["message"]

    def test_get_service_info(self):
        """Test getting service information"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "success": True,
                "data": {
                    "service_name": "Phone Number Verification",
                    "provider": "Phone Number Verification",
                    "type": "verification",
                    "country": "UG",
                    "currency": "UGX",
                    "is_active": True,
                    "api_configured": True
                }
            }
            
            result = self.client.phone_verification.get_service_info()
            
            assert result["success"] == True
            assert result["data"]["service_name"] == "Phone Number Verification"
            mock_request.assert_called_once_with('/phone-verification/service-info')

    def test_get_subscription_status(self):
        """Test getting subscription status"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "success": True,
                "data": {
                    "is_subscribed": True,
                    "service_name": "Phone Number Verification"
                }
            }
            
            result = self.client.phone_verification.get_subscription_status()
            
            assert result["success"] == True
            assert result["data"]["is_subscribed"] == True
            mock_request.assert_called_once_with('/phone-verification/subscription-status')

    def test_phone_number_formatting(self):
        """Test phone number formatting for verification API"""
        # Test local number
        formatted = self.client.phone_verification._format_phone_number("0759983853")
        assert formatted == "256759983853"
        
        # Test number with country code
        formatted = self.client.phone_verification._format_phone_number("256759983853")
        assert formatted == "256759983853"
        
        # Test number with + prefix (should remove +)
        formatted = self.client.phone_verification._format_phone_number("+256759983853")
        assert formatted == "256759983853"

    def test_verify_with_different_formats(self):
        """Test verification with different phone number formats"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {"success": True}
            
            # Test with local format
            self.client.phone_verification.verify_phone_number("0759983853")
            call_data = mock_request.call_args[1]['data']
            assert call_data['phone_number'] == '256759983853'
            
            # Test with country code
            self.client.phone_verification.verify_phone_number("256759983853")
            call_data = mock_request.call_args[1]['data']
            assert call_data['phone_number'] == '256759983853'
            
            # Test with + prefix
            self.client.phone_verification.verify_phone_number("+256759983853")
            call_data = mock_request.call_args[1]['data']
            assert call_data['phone_number'] == '256759983853'
