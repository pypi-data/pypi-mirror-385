"""
Test cases for Disbursements API
"""

import pytest
from unittest.mock import Mock, patch
from marzpay import MarzPay
from marzpay.errors import MarzPayError


class TestDisbursementsAPI:
    """Test cases for Disbursements API"""

    def setup_method(self):
        """Setup test client"""
        self.client = MarzPay(api_key="test_key", api_secret="test_secret")

    def test_send_money_success(self):
        """Test successful money sending"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "message": "Send money initiated successfully",
                "data": {
                    "transaction": {
                        "uuid": "test-uuid",
                        "reference": "test-ref",
                        "status": "processing"
                    }
                }
            }
            
            params = {
                "phone_number": "256759983853",
                "amount": 1000,
                "description": "Test payment"
            }
            
            result = self.client.disbursements.send_money(params)
            
            assert result["status"] == "success"
            mock_request.assert_called_once_with(
                '/send-money', 
                method='POST', 
                data={
                    'amount': '1000',
                    'phone_number': '256759983853',
                    'reference': mock_request.call_args[1]['data']['reference'],
                    'description': 'Test payment',
                    'callback_url': None,
                    'country': 'UG'
                }, 
                content_type='multipart'
            )

    def test_send_money_with_reference(self):
        """Test money sending with provided reference"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {"status": "success"}
            
            params = {
                "phone_number": "256759983853",
                "amount": 1000,
                "reference": "custom-ref-123",
                "description": "Test payment"
            }
            
            result = self.client.disbursements.send_money(params)
            
            # Verify the reference was used
            call_data = mock_request.call_args[1]['data']
            assert call_data['reference'] == "custom-ref-123"

    def test_send_money_validation_errors(self):
        """Test money sending validation errors"""
        # Missing phone number
        with pytest.raises(MarzPayError) as exc_info:
            self.client.disbursements.send_money({"amount": 1000})
        assert "phone_number is required" in str(exc_info.value)
        
        # Missing amount
        with pytest.raises(MarzPayError) as exc_info:
            self.client.disbursements.send_money({"phone_number": "256759983853"})
        assert "amount is required" in str(exc_info.value)
        
        # Invalid amount
        with pytest.raises(MarzPayError) as exc_info:
            self.client.disbursements.send_money({
                "phone_number": "256759983853",
                "amount": -100
            })
        assert "amount must be a positive number" in str(exc_info.value)

    def test_get_services(self):
        """Test getting available services"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {"services": ["mtn", "airtel"]}
            }
            
            result = self.client.disbursements.get_services()
            
            assert result["status"] == "success"
            mock_request.assert_called_once_with('/send-money/services')

    def test_get_send_money_details(self):
        """Test getting send money details"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {"transaction": {"uuid": "test-uuid"}}
            }
            
            result = self.client.disbursements.get_send_money_details("test-uuid")
            
            assert result["status"] == "success"
            mock_request.assert_called_once_with('/send-money/test-uuid')

    def test_get_disbursement_alias(self):
        """Test get_disbursement alias method"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {"status": "success"}
            
            result = self.client.disbursements.get_disbursement("test-uuid")
            
            mock_request.assert_called_once_with('/send-money/test-uuid')

    def test_phone_number_formatting(self):
        """Test phone number formatting"""
        # Test local number
        formatted = self.client.disbursements._format_phone_number("0759983853")
        assert formatted == "256759983853"
        
        # Test number with country code
        formatted = self.client.disbursements._format_phone_number("256759983853")
        assert formatted == "256759983853"
        
        # Test number with + prefix
        formatted = self.client.disbursements._format_phone_number("+256759983853")
        assert formatted == "256759983853"

    def test_generate_uuid(self):
        """Test UUID generation"""
        uuid1 = self.client.disbursements._generate_uuid()
        uuid2 = self.client.disbursements._generate_uuid()
        
        assert uuid1 != uuid2
        assert len(uuid1) == 36  # Standard UUID length
        assert uuid1.count('-') == 4  # Standard UUID format
