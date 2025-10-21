"""
Test cases for Transactions API
"""

import pytest
from unittest.mock import Mock, patch
from marzpay import MarzPay
from marzpay.errors import MarzPayError


class TestTransactionsAPI:
    """Test cases for Transactions API"""

    def setup_method(self):
        """Setup test client"""
        self.client = MarzPay(api_key="test_key", api_secret="test_secret")

    def test_get_transactions(self):
        """Test getting transactions list"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "transactions": [
                        {"id": "tx1", "amount": 1000, "status": "completed"},
                        {"id": "tx2", "amount": 2000, "status": "pending"}
                    ]
                }
            }
            
            result = self.client.transactions.get_transactions()
            
            assert result["status"] == "success"
            assert "transactions" in result["data"]
            mock_request.assert_called_once_with('/transactions')

    def test_get_transactions_with_params(self):
        """Test getting transactions with parameters"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {"transactions": []}
            }
            
            params = {
                "page": 1,
                "limit": 20,
                "status": "completed"
            }
            
            result = self.client.transactions.get_transactions(params)
            
            assert result["status"] == "success"
            mock_request.assert_called_once_with('/transactions', data=params)

    def test_get_transaction(self):
        """Test getting specific transaction details"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "transaction": {
                        "id": "tx123",
                        "amount": 1000,
                        "status": "completed",
                        "created_at": "2024-01-20T10:30:00Z"
                    }
                }
            }
            
            result = self.client.transactions.get_transaction("tx123")
            
            assert result["status"] == "success"
            assert result["data"]["transaction"]["id"] == "tx123"
            mock_request.assert_called_once_with('/transactions/tx123')

    def test_search_transactions(self):
        """Test searching transactions"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "results": [
                        {"id": "tx1", "amount": 1000, "reference": "ref123"}
                    ]
                }
            }
            
            result = self.client.transactions.search_transactions("ref123")
            
            assert result["status"] == "success"
            assert "results" in result["data"]
            mock_request.assert_called_once_with('/transactions/search', data={'query': 'ref123'})

    def test_search_transactions_with_params(self):
        """Test searching transactions with additional parameters"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {"results": []}
            }
            
            params = {
                "from_date": "2024-01-01",
                "to_date": "2024-01-31"
            }
            
            result = self.client.transactions.search_transactions("test", params)
            
            assert result["status"] == "success"
            call_data = mock_request.call_args[1]['data']
            assert call_data['query'] == 'test'
            assert call_data['from_date'] == '2024-01-01'

    def test_export_transactions(self):
        """Test exporting transactions"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "export_url": "https://example.com/export.csv",
                    "expires_at": "2024-01-21T10:30:00Z"
                }
            }
            
            result = self.client.transactions.export_transactions()
            
            assert result["status"] == "success"
            assert "export_url" in result["data"]
            mock_request.assert_called_once_with('/transactions/export')

    def test_export_transactions_with_params(self):
        """Test exporting transactions with parameters"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {"export_url": "https://example.com/export.csv"}
            }
            
            params = {
                "format": "csv",
                "from_date": "2024-01-01",
                "to_date": "2024-01-31"
            }
            
            result = self.client.transactions.export_transactions(params)
            
            assert result["status"] == "success"
            mock_request.assert_called_once_with('/transactions/export', data=params)
