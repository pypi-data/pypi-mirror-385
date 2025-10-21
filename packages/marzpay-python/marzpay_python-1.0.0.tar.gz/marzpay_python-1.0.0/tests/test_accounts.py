"""
Test cases for Accounts API
"""

import pytest
from unittest.mock import Mock, patch
from marzpay import MarzPay
from marzpay.errors import MarzPayError


class TestAccountsAPI:
    """Test cases for Accounts API"""

    def setup_method(self):
        """Setup test client"""
        self.client = MarzPay(api_key="test_key", api_secret="test_secret")

    def test_get_account(self):
        """Test getting account information"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "account": {
                        "business_name": "Test Business",
                        "status": "active"
                    }
                }
            }
            
            result = self.client.accounts.get_account()
            
            assert result["status"] == "success"
            assert "account" in result["data"]
            mock_request.assert_called_once_with('/account')

    def test_update_account(self):
        """Test updating account information"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "message": "Account updated successfully"
            }
            
            account_data = {
                "business_name": "Updated Business Name",
                "contact_email": "new@example.com"
            }
            
            result = self.client.accounts.update_account(account_data)
            
            assert result["status"] == "success"
            mock_request.assert_called_once_with('/account', method='PUT', data=account_data)

    def test_get_account_settings(self):
        """Test getting account settings"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "settings": {
                        "notifications": True,
                        "webhooks": True
                    }
                }
            }
            
            result = self.client.accounts.get_account_settings()
            
            assert result["status"] == "success"
            assert "settings" in result["data"]
            mock_request.assert_called_once_with('/account/settings')

    def test_update_account_settings(self):
        """Test updating account settings"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "message": "Settings updated successfully"
            }
            
            settings = {
                "notifications": False,
                "webhooks": True
            }
            
            result = self.client.accounts.update_account_settings(settings)
            
            assert result["status"] == "success"
            mock_request.assert_called_once_with('/account/settings', method='PUT', data=settings)
