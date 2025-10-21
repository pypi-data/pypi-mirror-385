"""
Services API class for service operations
"""

from typing import Dict, Any
from ..errors import MarzPayError


class ServicesAPI:
    """
    Services API for service operations
    """

    def __init__(self, marzpay_client):
        """
        Initialize Services API
        
        Args:
            marzpay_client: MarzPay client instance
        """
        self.marzpay = marzpay_client

    def get_services(self) -> Dict[str, Any]:
        """
        Get all available services
        
        Returns:
            API response with available services
        """
        return self.marzpay.request('/services')

    def get_service(self, service_id: str) -> Dict[str, Any]:
        """
        Get specific service details
        
        Args:
            service_id: Service ID
            
        Returns:
            API response with service details
        """
        return self.marzpay.request(f'/services/{service_id}')

    def get_service_providers(self, country: str = None) -> Dict[str, Any]:
        """
        Get service providers
        
        Args:
            country: Optional country code filter
            
        Returns:
            API response with service providers
        """
        if country:
            return self.marzpay.request(f'/services/providers?country={country}')
        return self.marzpay.request('/services/providers')

    def get_service_categories(self) -> Dict[str, Any]:
        """
        Get service categories
        
        Returns:
            API response with service categories
        """
        return self.marzpay.request('/services/categories')
