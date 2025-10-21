"""
Test cases for Balance API
"""

import pytest
from unittest.mock import Mock, patch
from marzpay import MarzPay
from marzpay.errors import MarzPayError


class TestBalanceAPI:
    """Test cases for Balance API"""

    def setup_method(self):
        """Setup test client"""
        self.client = MarzPay(api_key="test_key", api_secret="test_secret")

    def test_get_balance(self):
        """Test getting current balance"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "balance": {
                        "available": 10000,
                        "currency": "UGX",
                        "formatted": "10,000.00 UGX"
                    }
                }
            }
            
            result = self.client.balance.get_balance()
            
            assert result["status"] == "success"
            assert "balance" in result["data"]
            mock_request.assert_called_once_with('/balance')

    def test_get_balance_history(self):
        """Test getting balance history"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "history": [
                        {"date": "2024-01-20", "amount": 1000, "type": "credit"},
                        {"date": "2024-01-19", "amount": -500, "type": "debit"}
                    ]
                }
            }
            
            result = self.client.balance.get_balance_history()
            
            assert result["status"] == "success"
            assert "history" in result["data"]
            mock_request.assert_called_once_with('/balance/history')

    def test_get_balance_history_with_params(self):
        """Test getting balance history with parameters"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {"history": []}
            }
            
            params = {
                "from_date": "2024-01-01",
                "to_date": "2024-01-31",
                "limit": 50
            }
            
            result = self.client.balance.get_balance_history(params)
            
            assert result["status"] == "success"
            mock_request.assert_called_once_with('/balance/history', data=params)
