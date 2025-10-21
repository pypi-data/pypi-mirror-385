"""
Accounts API class for account management
"""

from typing import Dict, Any
from ..errors import MarzPayError


class AccountsAPI:
    """
    Accounts API for account management operations
    """

    def __init__(self, marzpay_client):
        """
        Initialize Accounts API
        
        Args:
            marzpay_client: MarzPay client instance
        """
        self.marzpay = marzpay_client

    def get_account(self) -> Dict[str, Any]:
        """
        Get account information
        
        Returns:
            API response with account details
        """
        return self.marzpay.request('/account')

    def update_account(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update account information
        
        Args:
            data: Account data to update
            
        Returns:
            API response with updated account details
        """
        return self.marzpay.request('/account', method='PUT', data=data)

    def get_account_settings(self) -> Dict[str, Any]:
        """
        Get account settings
        
        Returns:
            API response with account settings
        """
        return self.marzpay.request('/account/settings')

    def update_account_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update account settings
        
        Args:
            settings: Settings to update
            
        Returns:
            API response with updated settings
        """
        return self.marzpay.request('/account/settings', method='PUT', data=settings)
