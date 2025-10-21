"""
Phone number utilities for Uganda phone numbers
"""

import re
from typing import Optional


class PhoneNumberUtils:
    """
    Utilities for handling Uganda phone numbers
    """

    @staticmethod
    def format_phone_number(phone_number: str) -> str:
        """
        Format phone number to standard Uganda format (+256XXXXXXXXX)
        
        Args:
            phone_number: Raw phone number
            
        Returns:
            Formatted phone number with +256 prefix
            
        Example:
            >>> PhoneNumberUtils.format_phone_number("0759983853")
            "+256759983853"
            >>> PhoneNumberUtils.format_phone_number("+256759983853")
            "+256759983853"
            >>> PhoneNumberUtils.format_phone_number("256759983853")
            "+256759983853"
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

    @staticmethod
    def is_valid_uganda_phone_number(phone_number: str) -> bool:
        """
        Check if phone number is a valid Uganda phone number
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if valid Uganda phone number
            
        Example:
            >>> PhoneNumberUtils.is_valid_uganda_phone_number("0759983853")
            True
            >>> PhoneNumberUtils.is_valid_uganda_phone_number("+256759983853")
            True
            >>> PhoneNumberUtils.is_valid_uganda_phone_number("123456789")
            False
        """
        # Remove any non-digit characters except +
        clean_number = re.sub(r'[^\d+]', '', phone_number)
        
        # Remove + if present
        clean_number = clean_number.replace('+', '')
        
        # Check if it starts with 256 (Uganda country code)
        if not clean_number.startswith('256'):
            # Check if it's a local number starting with 0
            if clean_number.startswith('0') and len(clean_number) == 10:
                return True
            return False
        
        # Check if it's the correct length for Uganda (256 + 9 digits = 12 total)
        if len(clean_number) == 12:
            return True
        
        return False

    @staticmethod
    def normalize_phone_number(phone_number: str, include_plus: bool = True) -> str:
        """
        Normalize phone number to standard format
        
        Args:
            phone_number: Raw phone number
            include_plus: Whether to include + prefix
            
        Returns:
            Normalized phone number
            
        Example:
            >>> PhoneNumberUtils.normalize_phone_number("0759983853")
            "+256759983853"
            >>> PhoneNumberUtils.normalize_phone_number("0759983853", include_plus=False)
            "256759983853"
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
        
        return '+' + phone_number if include_plus else phone_number

