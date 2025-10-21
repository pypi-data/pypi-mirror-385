"""
Collections API - Money collection from customers via mobile money
"""

import re
import uuid
from typing import Dict, Any, Optional

from ..errors import MarzPayError


class CollectionsAPI:
    """
    Collections API - Money collection from customers via mobile money
    
    This class handles all collection-related operations including:
    - Initiating money collections
    - Retrieving collection details
    - Getting available collection services
    
    Example:
        ```python
        client = MarzPay(config)
        
        # Collect money from customer
        result = client.collections.collect_money(
            amount=5000,
            phone_number="0759983853",
            reference="550e8400-e29b-41d4-a716-446655440000",
            description="Payment for services"
        )
        ```
    """

    def __init__(self, client):
        """Initialize CollectionsAPI with MarzPay client"""
        self.client = client

    def collect_money(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect money from a customer via mobile money
        
        Args:
            params: Parameters for collecting money
                - phone_number (str): Customer phone number
                - amount (int): Amount to collect
                - country (str): Country code (default: UG)
                - description (str): Payment description
                - reference (str): Unique reference (optional, auto-generated if not provided)
                - callback_url (str): Webhook callback URL (optional)
        
        Returns:
            API response with transaction details
            
        Raises:
            MarzPayError: When request fails or validation fails
        """
        self._validate_collect_money_params(params)

        # Generate a valid UUID if no reference provided
        reference = params.get('reference') or self._generate_uuid()
        
        payload = {
            'amount': str(params['amount']),  # API expects string
            'phone_number': self._format_phone_number(params['phone_number']),
            'reference': reference,
            'description': params.get('description', 'Payment for services'),
            'callback_url': params.get('callback_url'),
            'country': params.get('country', 'UG'),
        }

        return self.client.request('/collect-money', method='POST', data=payload, content_type='multipart')

    def get_collection_details(self, uuid: str) -> Dict[str, Any]:
        """
        Get collection details by UUID
        
        Args:
            uuid: Collection UUID
            
        Returns:
            API response with collection details
        """
        return self.client.request(f'/collect-money/{uuid}')

    def get_collection(self, collection_id: str) -> Dict[str, Any]:
        """
        Alias for get_collection_details for backward compatibility
        
        Args:
            collection_id: Collection ID
            
        Returns:
            Collection details
        """
        return self.get_collection_details(collection_id)

    def get_collections(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get all collections with optional filters
        
        Args:
            page: Page number
            limit: Items per page
            status: Filter by status
            from_date: Filter from date (YYYY-MM-DD)
            to_date: Filter to date (YYYY-MM-DD)
            
        Returns:
            Collections list
        """
        filters = {}
        
        if page is not None:
            filters["page"] = page
        if limit is not None:
            filters["limit"] = limit
        if status is not None:
            filters["status"] = status
        if from_date is not None:
            filters["from_date"] = from_date
        if to_date is not None:
            filters["to_date"] = to_date

        endpoint = "/collections"
        if filters:
            query_params = "&".join([f"{k}={v}" for k, v in filters.items()])
            endpoint += f"?{query_params}"

        return self.client.request(endpoint)

    def get_services(self) -> Dict[str, Any]:
        """
        Get available collection services
        
        Returns:
            API response with available services
        """
        return self.client.request('/collect-money/services')

    def generate_reference(self) -> str:
        """
        Generate a unique reference for collections
        
        Returns:
            UUID4 reference string
        """
        return str(uuid.uuid4())

    def _validate_collect_money_params(self, params: Dict[str, Any]) -> None:
        """
        Validate collect money parameters
        
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

    def _generate_uuid(self) -> str:
        """
        Generate a valid UUID v4
        
        Returns:
            UUID v4 string
        """
        return str(uuid.uuid4())

    def _format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number for Uganda (ensure + prefix)
        
        Args:
            phone_number: Raw phone number
            
        Returns:
            Formatted phone number with + prefix
        """
        # Remove any non-digit characters except +
        phone_number = re.sub(r'[^\d+]', '', phone_number)
        
        # Remove + if present
        phone_number = phone_number.replace('+', '')
        
        # Add country code if not present
        if not phone_number.startswith('256'):
            if phone_number.startswith('0'):
                phone_number = '256' + phone_number[1:]
            else:
                phone_number = '256' + phone_number
        
        return '+' + phone_number


