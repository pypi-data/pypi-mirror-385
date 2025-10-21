"""
General utilities for MarzPay Python SDK
"""

import uuid
import random
import string
import re
from typing import Dict, Any, Optional


class GeneralUtils:
    """
    General utility functions
    """

    @staticmethod
    def generate_reference() -> str:
        """
        Generate a unique reference string
        
        Returns:
            Unique reference string
            
        Example:
            >>> ref = GeneralUtils.generate_reference()
            >>> len(ref)
            32
        """
        return str(uuid.uuid4()).replace('-', '')

    @staticmethod
    def generate_reference_with_prefix(prefix: str = 'MARZ') -> str:
        """
        Generate a unique reference with custom prefix
        
        Args:
            prefix: Prefix for the reference
            
        Returns:
            Unique reference with prefix
            
        Example:
            >>> ref = GeneralUtils.generate_reference_with_prefix('PAY')
            >>> ref.startswith('PAY_')
            True
        """
        reference = GeneralUtils.generate_reference()
        return f"{prefix}_{reference}"

    @staticmethod
    def format_amount(amount: float, currency: str = 'UGX') -> Dict[str, Any]:
        """
        Format amount for display
        
        Args:
            amount: Amount to format
            currency: Currency code
            
        Returns:
            Formatted amount dictionary
            
        Example:
            >>> GeneralUtils.format_amount(1000.50, 'UGX')
            {'formatted': '1,000.50', 'raw': 1000.50, 'currency': 'UGX'}
        """
        return {
            'formatted': f"{amount:,.2f}",
            'raw': amount,
            'currency': currency
        }

    @staticmethod
    def cents_to_amount(cents: int) -> float:
        """
        Convert cents to amount
        
        Args:
            cents: Amount in cents
            
        Returns:
            Amount in main currency unit
            
        Example:
            >>> GeneralUtils.cents_to_amount(1000)
            10.0
        """
        return cents / 100

    @staticmethod
    def amount_to_cents(amount: float) -> int:
        """
        Convert amount to cents
        
        Args:
            amount: Amount in main currency unit
            
        Returns:
            Amount in cents
            
        Example:
            >>> GeneralUtils.amount_to_cents(10.50)
            1050
        """
        return int(amount * 100)

    @staticmethod
    def format_currency(amount: float, currency: str = 'UGX') -> str:
        """
        Format currency amount
        
        Args:
            amount: Amount to format
            currency: Currency code
            
        Returns:
            Formatted currency string
            
        Example:
            >>> GeneralUtils.format_currency(1000, 'UGX')
            'UGX 1,000.00'
        """
        return f"{currency} {amount:,.2f}"

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Check if email is valid
        
        Args:
            email: Email to validate
            
        Returns:
            True if email is valid
            
        Example:
            >>> GeneralUtils.is_valid_email('test@example.com')
            True
            >>> GeneralUtils.is_valid_email('invalid-email')
            False
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """
        Sanitize input string
        
        Args:
            input_string: String to sanitize
            
        Returns:
            Sanitized string
        """
        return input_string.strip()

    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """
        Generate random string
        
        Args:
            length: Length of random string
            
        Returns:
            Random string
            
        Example:
            >>> random_str = GeneralUtils.generate_random_string(8)
            >>> len(random_str)
            8
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def build_query_string(params: Dict[str, Any]) -> str:
        """
        Build query string from parameters
        
        Args:
            params: Parameters dictionary
            
        Returns:
            Query string
            
        Example:
            >>> params = {'page': 1, 'limit': 10}
            >>> GeneralUtils.build_query_string(params)
            'page=1&limit=10'
        """
        return '&'.join([f"{k}={v}" for k, v in params.items() if v is not None])

    @staticmethod
    def parse_query_string(query_string: str) -> Dict[str, str]:
        """
        Parse query string to dictionary
        
        Args:
            query_string: Query string to parse
            
        Returns:
            Dictionary of parameters
        """
        params = {}
        for pair in query_string.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key] = value
        return params

    @staticmethod
    def deep_merge_dict(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries
        
        Args:
            dict1: First dictionary
            dict2: Second dictionary
            
        Returns:
            Merged dictionary
        """
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = GeneralUtils.deep_merge_dict(result[key], value)
            else:
                result[key] = value
        return result

    @staticmethod
    def remove_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove None values from dictionary
        
        Args:
            data: Dictionary to clean
            
        Returns:
            Dictionary without None values
        """
        return {k: v for k, v in data.items() if v is not None}

    @staticmethod
    def truncate_string(text: str, max_length: int, suffix: str = '...') -> str:
        """
        Truncate string to maximum length
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated
            
        Returns:
            Truncated string
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def format_json(data: Dict[str, Any]) -> str:
        """
        Format data as JSON string
        
        Args:
            data: Data to format
            
        Returns:
            JSON string
        """
        import json
        return json.dumps(data, indent=2, sort_keys=True)

