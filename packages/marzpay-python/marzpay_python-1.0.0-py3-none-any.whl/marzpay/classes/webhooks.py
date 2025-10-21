"""
Webhooks API class for webhook operations
"""

import hmac
import hashlib
from typing import Dict, Any, Optional
from ..errors import MarzPayError


class WebhooksAPI:
    """
    Webhooks API for webhook operations
    """

    def __init__(self, marzpay_client):
        """
        Initialize Webhooks API
        
        Args:
            marzpay_client: MarzPay client instance
        """
        self.marzpay = marzpay_client

    def handle_webhook(self, payload: Dict[str, Any], signature: str, secret: str) -> Dict[str, Any]:
        """
        Handle webhook payload
        
        Args:
            payload: Webhook payload
            signature: Webhook signature
            secret: Webhook secret
            
        Returns:
            Processed webhook data
            
        Raises:
            MarzPayError: When signature verification fails
        """
        if not self._verify_signature(payload, signature, secret):
            raise MarzPayError("Invalid webhook signature", "INVALID_SIGNATURE", 401)
        
        return self._process_webhook_payload(payload)

    def create_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new webhook
        
        Args:
            webhook_data: Webhook configuration
            
        Returns:
            API response with created webhook
        """
        required_fields = ['url', 'events']
        for field in required_fields:
            if field not in webhook_data:
                raise MarzPayError(f"{field} is required", "MISSING_FIELD", 400)
        
        return self.marzpay.request('/webhooks', method='POST', data=webhook_data)

    def get_webhooks(self) -> Dict[str, Any]:
        """
        Get all webhooks
        
        Returns:
            API response with webhooks list
        """
        return self.marzpay.request('/webhooks')

    def get_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """
        Get specific webhook details
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            API response with webhook details
        """
        return self.marzpay.request(f'/webhooks/{webhook_id}')

    def update_webhook(self, webhook_id: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update webhook configuration
        
        Args:
            webhook_id: Webhook ID
            webhook_data: Updated webhook configuration
            
        Returns:
            API response with updated webhook
        """
        return self.marzpay.request(f'/webhooks/{webhook_id}', method='PUT', data=webhook_data)

    def delete_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """
        Delete webhook
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            API response with deletion status
        """
        return self.marzpay.request(f'/webhooks/{webhook_id}', method='DELETE')

    def test_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """
        Test webhook
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            API response with test result
        """
        return self.marzpay.request(f'/webhooks/{webhook_id}/test', method='POST')

    def _verify_signature(self, payload: Dict[str, Any], signature: str, secret: str) -> bool:
        """
        Verify webhook signature
        
        Args:
            payload: Webhook payload
            signature: Received signature
            secret: Webhook secret
            
        Returns:
            True if signature is valid
        """
        import json
        payload_string = json.dumps(payload, sort_keys=True)
        expected_signature = hmac.new(
            secret.encode(),
            payload_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

    def _process_webhook_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook payload
        
        Args:
            payload: Raw webhook payload
            
        Returns:
            Processed webhook data
        """
        event_type = payload.get('type', 'unknown')
        
        return {
            'event_type': event_type,
            'transaction_id': payload.get('data', {}).get('transaction_id'),
            'status': payload.get('data', {}).get('status'),
            'processed_at': payload.get('timestamp'),
            'raw_data': payload
        }


class WebhookPayload:
    """
    Webhook payload handler
    """

    def __init__(self, data: Dict[str, Any], marzpay_client):
        """
        Initialize webhook payload
        
        Args:
            data: Webhook payload data
            marzpay_client: MarzPay client instance
        """
        self.data = data
        self.marzpay = marzpay_client
        self.is_valid = self._validate_payload()

    def is_valid_payload(self) -> bool:
        """
        Check if payload is valid
        
        Returns:
            True if payload is valid
        """
        return self.is_valid

    def get_transaction_id(self) -> Optional[str]:
        """
        Get transaction ID from payload
        
        Returns:
            Transaction ID or None
        """
        return self.data.get('data', {}).get('transaction_id')

    def get_status(self) -> Optional[str]:
        """
        Get status from payload
        
        Returns:
            Status or None
        """
        return self.data.get('data', {}).get('status')

    def get_event_type(self) -> str:
        """
        Get event type from payload
        
        Returns:
            Event type
        """
        return self.data.get('type', 'unknown')

    def get_data(self) -> Dict[str, Any]:
        """
        Get payload data
        
        Returns:
            Payload data
        """
        return self.data

    def _validate_payload(self) -> bool:
        """
        Validate webhook payload structure
        
        Returns:
            True if payload structure is valid
        """
        return (
            isinstance(self.data, dict) and
            'type' in self.data and
            'data' in self.data
        )

