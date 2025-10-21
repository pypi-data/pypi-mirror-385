"""
Disbursements API class for sending money to recipients
"""

import uuid
from typing import Dict, Any, Optional
from ..errors import MarzPayError


class DisbursementsAPI:
    """
    Disbursements API for sending money to recipients
    """

    def __init__(self, marzpay_client):
        """
        Initialize Disbursements API
        
        Args:
            marzpay_client: MarzPay client instance
        """
        self.marzpay = marzpay_client

    def send_money(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send money to recipient
        
        Args:
            params: Parameters for sending money
                - phone_number (str): Recipient phone number
                - amount (int): Amount to send
                - country (str): Country code (default: UG)
                - description (str): Payment description
                - reference (str): Unique reference (optional, auto-generated if not provided)
                - callback_url (str): Webhook callback URL (optional)
        
        Returns:
            API response with transaction details
            
        Raises:
            MarzPayError: When request fails or validation fails
        """
        self._validate_send_money_params(params)

        # Generate a valid UUID if no reference provided
        reference = params.get('reference') or self._generate_uuid()
        
        payload = {
            'amount': str(params['amount']),  # API expects string
            'phone_number': self._format_phone_number(params['phone_number']),
            'reference': reference,
            'description': params.get('description', 'Payment to customer'),
            'callback_url': params.get('callback_url'),
            'country': params.get('country', 'UG'),
        }

        return self.marzpay.request('/send-money', method='POST', data=payload, content_type='multipart')

    def get_services(self) -> Dict[str, Any]:
        """
        Get available disbursement services
        
        Returns:
            API response with available services
        """
        return self.marzpay.request('/send-money/services')

    def get_send_money_details(self, uuid: str) -> Dict[str, Any]:
        """
        Get send money details by UUID
        
        Args:
            uuid: Transaction UUID
            
        Returns:
            API response with transaction details
        """
        return self.marzpay.request(f'/send-money/{uuid}')

    def get_disbursement(self, uuid: str) -> Dict[str, Any]:
        """
        Alias for get_send_money_details for backward compatibility
        
        Args:
            uuid: Transaction UUID
            
        Returns:
            API response with transaction details
        """
        return self.get_send_money_details(uuid)

    def _validate_send_money_params(self, params: Dict[str, Any]) -> None:
        """
        Validate send money parameters
        
        Args:
            params: Parameters to validate
            
        Raises:
            MarzPayError: When validation fails
        """
        if 'phone_number' not in params:
            raise MarzPayError("phone_number is required", "MISSING_PHONE_NUMBER", 400)
        
        if 'amount' not in params:
            raise MarzPayError("amount is required", "MISSING_AMOUNT", 400)
        
        if not isinstance(params['amount'], (int, float)) or params['amount'] <= 0:
            raise MarzPayError("amount must be a positive number", "INVALID_AMOUNT", 400)

    def _format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number for Uganda
        
        Args:
            phone_number: Raw phone number
            
        Returns:
            Formatted phone number
        """
        # Remove any non-digit characters except +
        phone_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # Remove + if present
        phone_number = phone_number.replace('+', '')
        
        # Add country code if not present
        if not phone_number.startswith('256'):
            if phone_number.startswith('0'):
                phone_number = '256' + phone_number[1:]
            else:
                phone_number = '256' + phone_number
        
        # Add + prefix for API
        return '+' + phone_number

    def _generate_uuid(self) -> str:
        """
        Generate a valid UUID v4
        
        Returns:
            UUID v4 string
        """
        return str(uuid.uuid4())

    def _format_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format request parameters
        
        Args:
            params: Raw parameters
            
        Returns:
            Formatted parameters
        """
        formatted = params.copy()
        
        if 'phone_number' in formatted:
            formatted['phone_number'] = self._format_phone_number(formatted['phone_number'])
        
        return formatted
