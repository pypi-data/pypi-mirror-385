"""
Test cases for Services API
"""

import pytest
from unittest.mock import Mock, patch
from marzpay import MarzPay
from marzpay.errors import MarzPayError


class TestServicesAPI:
    """Test cases for Services API"""

    def setup_method(self):
        """Setup test client"""
        self.client = MarzPay(api_key="test_key", api_secret="test_secret")

    def test_get_services(self):
        """Test getting all available services"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "services": [
                        {"id": "mtn", "name": "MTN Mobile Money", "type": "collection"},
                        {"id": "airtel", "name": "Airtel Money", "type": "collection"}
                    ]
                }
            }
            
            result = self.client.services.get_services()
            
            assert result["status"] == "success"
            assert "services" in result["data"]
            mock_request.assert_called_once_with('/services')

    def test_get_service(self):
        """Test getting specific service details"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "service": {
                        "id": "mtn",
                        "name": "MTN Mobile Money",
                        "type": "collection",
                        "status": "active",
                        "fees": {"percentage": 0.5, "fixed": 0}
                    }
                }
            }
            
            result = self.client.services.get_service("mtn")
            
            assert result["status"] == "success"
            assert result["data"]["service"]["id"] == "mtn"
            mock_request.assert_called_once_with('/services/mtn')

    def test_get_service_providers(self):
        """Test getting service providers"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "providers": [
                        {"id": "mtn", "name": "MTN", "country": "UG"},
                        {"id": "airtel", "name": "Airtel", "country": "UG"}
                    ]
                }
            }
            
            result = self.client.services.get_service_providers()
            
            assert result["status"] == "success"
            assert "providers" in result["data"]
            mock_request.assert_called_once_with('/services/providers')

    def test_get_service_providers_with_country(self):
        """Test getting service providers filtered by country"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {"providers": []}
            }
            
            result = self.client.services.get_service_providers("UG")
            
            assert result["status"] == "success"
            mock_request.assert_called_once_with('/services/providers?country=UG')

    def test_get_service_categories(self):
        """Test getting service categories"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "categories": [
                        {"id": "collections", "name": "Money Collections"},
                        {"id": "disbursements", "name": "Money Disbursements"}
                    ]
                }
            }
            
            result = self.client.services.get_service_categories()
            
            assert result["status"] == "success"
            assert "categories" in result["data"]
            mock_request.assert_called_once_with('/services/categories')
