"""
Transactions API class for transaction operations
"""

from typing import Dict, Any, Optional
from ..errors import MarzPayError


class TransactionsAPI:
    """
    Transactions API for transaction operations
    """

    def __init__(self, marzpay_client):
        """
        Initialize Transactions API
        
        Args:
            marzpay_client: MarzPay client instance
        """
        self.marzpay = marzpay_client

    def get_transactions(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get transactions list
        
        Args:
            params: Optional parameters for filtering
            
        Returns:
            API response with transactions list
        """
        if params:
            return self.marzpay.request('/transactions', data=params)
        return self.marzpay.request('/transactions')

    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get transaction details by ID
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            API response with transaction details
        """
        return self.marzpay.request(f'/transactions/{transaction_id}')

    def search_transactions(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Search transactions
        
        Args:
            query: Search query
            params: Optional additional parameters
            
        Returns:
            API response with search results
        """
        search_params = {'query': query}
        if params:
            search_params.update(params)
        
        return self.marzpay.request('/transactions/search', data=search_params)

    def export_transactions(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Export transactions
        
        Args:
            params: Export parameters
            
        Returns:
            API response with export data
        """
        if params:
            return self.marzpay.request('/transactions/export', data=params)
        return self.marzpay.request('/transactions/export')

