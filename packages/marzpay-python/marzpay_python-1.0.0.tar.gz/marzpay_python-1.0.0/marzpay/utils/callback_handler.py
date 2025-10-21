"""
Callback handler for webhook processing
"""

from typing import Dict, Any, Optional
from ..errors import MarzPayError


class CallbackHandler:
    """
    Handler for processing webhook callbacks
    """

    def __init__(self, marzpay_client):
        """
        Initialize Callback Handler
        
        Args:
            marzpay_client: MarzPay client instance
        """
        self.marzpay = marzpay_client

    def handle_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming callback data
        
        Args:
            callback_data: Callback data from webhook
            
        Returns:
            Processed callback result
        """
        if not self._validate_callback_data(callback_data):
            raise MarzPayError("Invalid callback data", "INVALID_CALLBACK", 400)
        
        callback_type = callback_data.get('type', 'unknown')
        
        if callback_type == 'collection':
            return self._handle_collection_callback(callback_data)
        elif callback_type == 'disbursement':
            return self._handle_disbursement_callback(callback_data)
        elif callback_type == 'transaction':
            return self._handle_transaction_callback(callback_data)
        else:
            return self._handle_generic_callback(callback_data)

    def process_collection_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process collection callback
        
        Args:
            callback_data: Collection callback data
            
        Returns:
            Processed collection callback
        """
        return self._handle_collection_callback(callback_data)

    def process_disbursement_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process disbursement callback
        
        Args:
            callback_data: Disbursement callback data
            
        Returns:
            Processed disbursement callback
        """
        return self._handle_disbursement_callback(callback_data)

    def process_transaction_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process transaction callback
        
        Args:
            callback_data: Transaction callback data
            
        Returns:
            Processed transaction callback
        """
        return self._handle_transaction_callback(callback_data)

    def _handle_collection_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle collection callback
        
        Args:
            callback_data: Collection callback data
            
        Returns:
            Processed collection callback
        """
        transaction_id = callback_data.get('data', {}).get('transaction_id')
        status = callback_data.get('data', {}).get('status')
        
        self._log_callback('collection', callback_data)
        
        return {
            'type': 'collection',
            'transaction_id': transaction_id,
            'status': status,
            'processed_at': callback_data.get('timestamp'),
            'success': status in ['completed', 'successful']
        }

    def _handle_disbursement_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle disbursement callback
        
        Args:
            callback_data: Disbursement callback data
            
        Returns:
            Processed disbursement callback
        """
        transaction_id = callback_data.get('data', {}).get('transaction_id')
        status = callback_data.get('data', {}).get('status')
        
        self._log_callback('disbursement', callback_data)
        
        return {
            'type': 'disbursement',
            'transaction_id': transaction_id,
            'status': status,
            'processed_at': callback_data.get('timestamp'),
            'success': status in ['completed', 'successful']
        }

    def _handle_transaction_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle transaction callback
        
        Args:
            callback_data: Transaction callback data
            
        Returns:
            Processed transaction callback
        """
        transaction_id = callback_data.get('data', {}).get('transaction_id')
        status = callback_data.get('data', {}).get('status')
        
        self._log_callback('transaction', callback_data)
        
        return {
            'type': 'transaction',
            'transaction_id': transaction_id,
            'status': status,
            'processed_at': callback_data.get('timestamp'),
            'success': status in ['completed', 'successful']
        }

    def _handle_generic_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle generic callback
        
        Args:
            callback_data: Generic callback data
            
        Returns:
            Processed generic callback
        """
        self._log_callback('generic', callback_data)
        
        return {
            'type': 'generic',
            'data': callback_data.get('data', {}),
            'processed_at': callback_data.get('timestamp'),
            'success': True
        }

    def _validate_callback_data(self, callback_data: Dict[str, Any]) -> bool:
        """
        Validate callback data structure
        
        Args:
            callback_data: Callback data to validate
            
        Returns:
            True if valid
        """
        return (
            isinstance(callback_data, dict) and
            'data' in callback_data and
            isinstance(callback_data['data'], dict)
        )

    def _log_callback(self, callback_type: str, data: Dict[str, Any]) -> None:
        """
        Log callback processing
        
        Args:
            callback_type: Type of callback
            data: Callback data
        """
        # Simple logging - in production, use proper logging
        print(f"Processed {callback_type} callback: {data.get('data', {}).get('transaction_id', 'unknown')}")

    def verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        """
        Verify webhook signature
        
        Args:
            payload: Raw payload string
            signature: Received signature
            secret: Webhook secret
            
        Returns:
            True if signature is valid
        """
        import hmac
        import hashlib
        
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

    def get_callback_url(self, transaction_id: str, base_url: Optional[str] = None) -> str:
        """
        Generate callback URL for transaction
        
        Args:
            transaction_id: Transaction ID
            base_url: Base URL for callback
            
        Returns:
            Callback URL
        """
        if not base_url:
            base_url = "https://your-app.com/webhook"
        
        return f"{base_url}/marzpay/callback/{transaction_id}"

