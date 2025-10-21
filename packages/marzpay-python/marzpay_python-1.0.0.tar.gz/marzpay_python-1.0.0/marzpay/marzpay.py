"""
Main MarzPay client class
"""

import base64
import json
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .classes.collections import CollectionsAPI
from .classes.disbursements import DisbursementsAPI
from .classes.accounts import AccountsAPI
from .classes.balance import BalanceAPI
from .classes.transactions import TransactionsAPI
from .classes.services import ServicesAPI
from .classes.webhooks import WebhooksAPI
from .classes.phone_verification import PhoneVerificationAPI
from .utils.phone_number_utils import PhoneNumberUtils
from .utils.general_utils import GeneralUtils
from .utils.callback_handler import CallbackHandler
from .errors import MarzPayError


class MarzPay:
    """
    MarzPay Python SDK
    
    Official Python SDK for MarzPay - Mobile Money Payment Platform for Uganda.
    
    Example:
        ```python
        from marzpay import MarzPay
        
        client = MarzPay(
            api_key="your_api_key",
            api_secret="your_api_secret"
        )
        
        # Collect money from customer
        result = client.collections.collect_money(
            amount=5000,
            phone_number="0759983853",
            reference=client.collections.generate_reference(),
            description="Payment for services"
        )
        ```
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://wallet.wearemarz.com/api/v1",
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
    ):
        """
        Initialize MarzPay client
        
        Args:
            api_key: Your MarzPay API key
            api_secret: Your MarzPay API secret
            base_url: API base URL (default: https://wallet.wearemarz.com/api/v1)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries (default: 3)
            backoff_factor: Backoff factor for retries (default: 0.3)
        
        Raises:
            MarzPayError: When API credentials are missing
        """
        if not api_key or not api_secret:
            raise MarzPayError("API credentials are required", "MISSING_CREDENTIALS", 400)

        self.config = {
            "api_key": api_key,
            "api_secret": api_secret,
            "base_url": base_url.rstrip("/"),
            "timeout": timeout,
        }

        # Setup HTTP session with retry strategy
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Initialize API modules
        self.collections = CollectionsAPI(self)
        self.disbursements = DisbursementsAPI(self)
        self.accounts = AccountsAPI(self)
        self.balance = BalanceAPI(self)
        self.transactions = TransactionsAPI(self)
        self.services = ServicesAPI(self)
        self.webhooks = WebhooksAPI(self)
        self.phone_verification = PhoneVerificationAPI(self)

        # Initialize utility modules
        self.phone_utils = PhoneNumberUtils()
        self.utils = GeneralUtils()
        self.callback_handler = CallbackHandler(self)

    def request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request to MarzPay API
        
        Args:
            endpoint: API endpoint (without base URL)
            method: HTTP method (default: GET)
            data: Request body data
            headers: Additional headers
            **kwargs: Additional request arguments
        
        Returns:
            API response data
            
        Raises:
            MarzPayError: When request fails
        """
        url = f"{self.config['base_url']}{endpoint}"
        
        request_headers = {
            "Authorization": self.get_auth_header(),
        }
        
        if headers:
            request_headers.update(headers)

        # Extract content_type before spreading kwargs
        content_type = kwargs.get('content_type', 'json')
        if 'content_type' in kwargs:
            del kwargs['content_type']
        
        request_kwargs = {
            "method": method,
            "url": url,
            "headers": request_headers,
            "timeout": self.config["timeout"],
            **kwargs,
        }

        if data and method.upper() in ["POST", "PUT", "PATCH"]:
            
            if content_type == 'multipart':
                # For multipart form data (like collections and disbursements)
                request_kwargs["data"] = data
                # Don't set Content-Type header, let requests handle it
                if "Content-Type" in request_headers:
                    del request_headers["Content-Type"]
            elif content_type == 'form':
                # For form data
                request_kwargs["data"] = data
                request_headers["Content-Type"] = "application/x-www-form-urlencoded"
            else:
                # Default to JSON
                request_kwargs["json"] = data
                request_headers["Content-Type"] = "application/json"

        try:
            response = self.session.request(**request_kwargs)
            response.raise_for_status()
            
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"message": "Success", "data": response.text}

        except requests.exceptions.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                    message = error_data.get("message", str(e))
                    code = error_data.get("code", "REQUEST_FAILED")
                    status = e.response.status_code
                except json.JSONDecodeError:
                    message = str(e)
                    code = "REQUEST_FAILED"
                    status = e.response.status_code
            else:
                message = str(e)
                code = "NETWORK_ERROR"
                status = 0

            raise MarzPayError(message, code, status)

    def set_credentials(self, api_key: str, api_secret: str) -> None:
        """
        Update API credentials at runtime
        
        Args:
            api_key: New API key
            api_secret: New API secret
            
        Raises:
            MarzPayError: When credentials are missing
        """
        if not api_key or not api_secret:
            raise MarzPayError("Both API key and secret are required", "MISSING_CREDENTIALS", 400)

        self.config["api_key"] = api_key
        self.config["api_secret"] = api_secret

    def get_auth_header(self) -> str:
        """
        Get the current authentication header
        
        Returns:
            Base64 encoded authorization header
        """
        credentials = f"{self.config['api_key']}:{self.config['api_secret']}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

    def get_info(self) -> Dict[str, Any]:
        """
        Get SDK version and information
        
        Returns:
            SDK information dictionary
        """
        return {
            "name": "MarzPay Python SDK",
            "version": "1.0.0",
            "description": "Official Python SDK for MarzPay - Mobile Money Payment Platform for Uganda",
            "base_url": self.config["base_url"],
            "features": [
                "Collections API",
                "Disbursements API",
                "Accounts API",
                "Balance API",
                "Transactions API",
                "Services API",
                "Webhooks API",
                "Phone Verification API",
                "Phone Number Utilities",
                "General Utilities",
                "Error Handling",
                "Async Support",
            ],
        }

    def test_connection(self) -> Dict[str, Any]:
        """
        Test API connection
        
        Returns:
            Connection test result
        """
        try:
            response = self.request("/account")
            return {
                "status": "success",
                "message": "API connection successful",
                "data": {
                    "account_status": response.get("data", {}).get("account", {}).get("status", {}).get("account_status", "unknown"),
                    "business_name": response.get("data", {}).get("account", {}).get("business_name", "unknown"),
                },
            }
        except MarzPayError as e:
            return {
                "status": "error",
                "message": "API connection failed",
                "error": e.message,
                "code": e.code,
            }

    def format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number using utility
        
        Args:
            phone_number: Raw phone number
            
        Returns:
            Formatted phone number
        """
        return self.phone_utils.format_phone_number(phone_number)

    def is_valid_phone_number(self, phone_number: str) -> bool:
        """
        Check if phone number is valid using utility
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if valid
        """
        return self.phone_utils.is_valid_uganda_phone_number(phone_number)

    def generate_reference(self) -> str:
        """
        Generate a unique reference using utility
        
        Returns:
            Unique reference string
        """
        return self.utils.generate_reference()

    def generate_reference_with_prefix(self, prefix: str = 'MARZ') -> str:
        """
        Generate a unique reference with prefix using utility
        
        Args:
            prefix: Prefix for reference
            
        Returns:
            Unique reference with prefix
        """
        return self.utils.generate_reference_with_prefix(prefix)


