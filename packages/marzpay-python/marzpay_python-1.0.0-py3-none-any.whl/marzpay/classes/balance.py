"""
Balance API class for balance operations
"""

from typing import Dict, Any
from ..errors import MarzPayError


class BalanceAPI:
    """
    Balance API for balance operations
    """

    def __init__(self, marzpay_client):
        """
        Initialize Balance API
        
        Args:
            marzpay_client: MarzPay client instance
        """
        self.marzpay = marzpay_client

    def get_balance(self) -> Dict[str, Any]:
        """
        Get current balance
        
        Returns:
            API response with balance information
        """
        return self.marzpay.request('/balance')

    def get_balance_history(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get balance history
        
        Args:
            params: Optional parameters for filtering
            
        Returns:
            API response with balance history
        """
        if params:
            return self.marzpay.request('/balance/history', data=params)
        return self.marzpay.request('/balance/history')

