"""
Phone Verification API class for verifying phone numbers and retrieving user information
"""

from typing import Dict, Any
from ..errors import MarzPayError


class PhoneVerificationAPI:
    """
    Phone Verification API for verifying phone numbers and getting user info
    """

    def __init__(self, marzpay_client):
        """
        Initialize Phone Verification API
        
        Args:
            marzpay_client: MarzPay client instance
        """
        self.marzpay = marzpay_client

    def verify_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Verify phone number and get user information
        
        Args:
            phone_number: Phone number to verify (format: 0759983853 or +256759983853)
        
        Returns:
            API response with user information
            
        Raises:
            MarzPayError: When request fails
        """
        formatted_phone = self._format_phone_number(phone_number)
        
        payload = {
            'phone_number': formatted_phone
        }
        
        return self.marzpay.request('/phone-verification/verify', method='POST', data=payload, content_type='json')

    def get_service_info(self) -> Dict[str, Any]:
        """
        Get phone verification service information
        
        Returns:
            API response with service information
        """
        return self.marzpay.request('/phone-verification/service-info')

    def get_subscription_status(self) -> Dict[str, Any]:
        """
        Check subscription status for phone verification service
        
        Returns:
            API response with subscription status
        """
        return self.marzpay.request('/phone-verification/subscription-status')

    def _format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number for API (remove + prefix, ensure 256XXXXXXXXX format)
        
        Args:
            phone_number: Raw phone number
            
        Returns:
            Formatted phone number without + prefix
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
        
        return phone_number
