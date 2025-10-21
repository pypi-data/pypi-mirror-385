"""
Test cases for Webhooks API
"""

import pytest
import hmac
import hashlib
from unittest.mock import Mock, patch
from marzpay import MarzPay
from marzpay.errors import MarzPayError


class TestWebhooksAPI:
    """Test cases for Webhooks API"""

    def setup_method(self):
        """Setup test client"""
        self.client = MarzPay(api_key="test_key", api_secret="test_secret")

    def test_handle_webhook_success(self):
        """Test successful webhook handling"""
        payload = {"type": "collection", "data": {"transaction_id": "tx123"}}
        secret = "test_secret"
        
        # Generate valid signature
        import json
        payload_string = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        result = self.client.webhooks.handle_webhook(payload, signature, secret)
        
        assert result["event_type"] == "collection"
        assert result["transaction_id"] == "tx123"

    def test_handle_webhook_invalid_signature(self):
        """Test webhook handling with invalid signature"""
        payload = {"type": "collection", "data": {"transaction_id": "tx123"}}
        secret = "test_secret"
        invalid_signature = "invalid_signature"
        
        with pytest.raises(MarzPayError) as exc_info:
            self.client.webhooks.handle_webhook(payload, invalid_signature, secret)
        
        assert "Invalid webhook signature" in str(exc_info.value)

    def test_create_webhook(self):
        """Test creating a new webhook"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "webhook": {
                        "id": "wh123",
                        "url": "https://example.com/webhook",
                        "events": ["collection", "disbursement"]
                    }
                }
            }
            
            webhook_data = {
                "url": "https://example.com/webhook",
                "events": ["collection", "disbursement"]
            }
            
            result = self.client.webhooks.create_webhook(webhook_data)
            
            assert result["status"] == "success"
            assert "webhook" in result["data"]
            mock_request.assert_called_once_with('/webhooks', method='POST', data=webhook_data)

    def test_create_webhook_missing_fields(self):
        """Test creating webhook with missing required fields"""
        webhook_data = {"url": "https://example.com/webhook"}  # Missing 'events'
        
        with pytest.raises(MarzPayError) as exc_info:
            self.client.webhooks.create_webhook(webhook_data)
        
        assert "events is required" in str(exc_info.value)

    def test_get_webhooks(self):
        """Test getting all webhooks"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "webhooks": [
                        {"id": "wh1", "url": "https://example.com/webhook1"},
                        {"id": "wh2", "url": "https://example.com/webhook2"}
                    ]
                }
            }
            
            result = self.client.webhooks.get_webhooks()
            
            assert result["status"] == "success"
            assert "webhooks" in result["data"]
            mock_request.assert_called_once_with('/webhooks')

    def test_get_webhook(self):
        """Test getting specific webhook details"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "data": {
                    "webhook": {
                        "id": "wh123",
                        "url": "https://example.com/webhook",
                        "events": ["collection"],
                        "status": "active"
                    }
                }
            }
            
            result = self.client.webhooks.get_webhook("wh123")
            
            assert result["status"] == "success"
            assert result["data"]["webhook"]["id"] == "wh123"
            mock_request.assert_called_once_with('/webhooks/wh123')

    def test_update_webhook(self):
        """Test updating webhook configuration"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "message": "Webhook updated successfully"
            }
            
            webhook_data = {
                "url": "https://new-example.com/webhook",
                "events": ["collection", "disbursement"]
            }
            
            result = self.client.webhooks.update_webhook("wh123", webhook_data)
            
            assert result["status"] == "success"
            mock_request.assert_called_once_with('/webhooks/wh123', method='PUT', data=webhook_data)

    def test_delete_webhook(self):
        """Test deleting webhook"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "message": "Webhook deleted successfully"
            }
            
            result = self.client.webhooks.delete_webhook("wh123")
            
            assert result["status"] == "success"
            mock_request.assert_called_once_with('/webhooks/wh123', method='DELETE')

    def test_test_webhook(self):
        """Test testing webhook"""
        with patch.object(self.client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "success",
                "message": "Test webhook sent successfully"
            }
            
            result = self.client.webhooks.test_webhook("wh123")
            
            assert result["status"] == "success"
            mock_request.assert_called_once_with('/webhooks/wh123/test', method='POST')

    def test_webhook_payload_validation(self):
        """Test webhook payload validation"""
        from marzpay.classes.webhooks import WebhookPayload
        
        # Valid payload
        valid_payload = {
            "type": "collection",
            "data": {"transaction_id": "tx123"}
        }
        
        payload = WebhookPayload(valid_payload, self.client)
        assert payload.is_valid_payload() == True
        assert payload.get_transaction_id() == "tx123"
        assert payload.get_event_type() == "collection"
        
        # Invalid payload
        invalid_payload = {"type": "collection"}  # Missing 'data' field
        
        payload = WebhookPayload(invalid_payload, self.client)
        assert payload.is_valid_payload() == False
