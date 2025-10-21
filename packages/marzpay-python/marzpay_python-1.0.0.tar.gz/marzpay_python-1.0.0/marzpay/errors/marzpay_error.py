"""
MarzPay custom error class
"""

from typing import Dict, Any, Optional


class MarzPayError(Exception):
    """
    MarzPay Custom Error Class
    
    Extends the standard Exception class to provide additional context
    for MarzPay-specific errors including error codes and HTTP status.
    
    Example:
        ```python
        try:
            client.collections.collect_money(invalid_params)
        except MarzPayError as e:
            print(f"Error Code: {e.code}")
            print(f"HTTP Status: {e.status}")
            print(f"Message: {e.message}")
        ```
    """

    def __init__(
        self,
        message: str = "",
        code: str = "UNKNOWN_ERROR",
        status: int = 0,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Create a new MarzPayError
        
        Args:
            message: Error message
            code: Error code for programmatic handling
            status: HTTP status code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.details = details or {}

    @classmethod
    def from_response(cls, response_data: Dict[str, Any], status_code: int) -> "MarzPayError":
        """
        Create exception from API response
        
        Args:
            response_data: API response data
            status_code: HTTP status code
            
        Returns:
            MarzPayError instance
        """
        message = response_data.get("message", "API request failed")
        code = response_data.get("code", "API_ERROR")
        details = response_data.get("details", {})
        
        return cls(message, code, status_code, details)

    @classmethod
    def network_error(cls, message: str = "Network request failed") -> "MarzPayError":
        """
        Create network error exception
        
        Args:
            message: Network error message
            
        Returns:
            MarzPayError instance
        """
        return cls(message, "NETWORK_ERROR", 0)

    @classmethod
    def validation_error(
        cls, message: str, details: Optional[Dict[str, Any]] = None
    ) -> "MarzPayError":
        """
        Create validation error exception
        
        Args:
            message: Validation error message
            details: Validation details
            
        Returns:
            MarzPayError instance
        """
        return cls(message, "VALIDATION_ERROR", 400, details)

    @classmethod
    def authentication_error(
        cls, message: str = "Authentication failed"
    ) -> "MarzPayError":
        """
        Create authentication error exception
        
        Args:
            message: Authentication error message
            
        Returns:
            MarzPayError instance
        """
        return cls(message, "AUTHENTICATION_ERROR", 401)

    @classmethod
    def authorization_error(
        cls, message: str = "Authorization failed"
    ) -> "MarzPayError":
        """
        Create authorization error exception
        
        Args:
            message: Authorization error message
            
        Returns:
            MarzPayError instance
        """
        return cls(message, "AUTHORIZATION_ERROR", 403)

    @classmethod
    def not_found_error(
        cls, message: str = "Resource not found"
    ) -> "MarzPayError":
        """
        Create not found error exception
        
        Args:
            message: Not found error message
            
        Returns:
            MarzPayError instance
        """
        return cls(message, "NOT_FOUND_ERROR", 404)

    @classmethod
    def rate_limit_error(
        cls, message: str = "Rate limit exceeded"
    ) -> "MarzPayError":
        """
        Create rate limit error exception
        
        Args:
            message: Rate limit error message
            
        Returns:
            MarzPayError instance
        """
        return cls(message, "RATE_LIMIT_ERROR", 429)

    @classmethod
    def server_error(
        cls, message: str = "Internal server error"
    ) -> "MarzPayError":
        """
        Create server error exception
        
        Args:
            message: Server error message
            
        Returns:
            MarzPayError instance
        """
        return cls(message, "SERVER_ERROR", 500)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary
        
        Returns:
            Exception as dictionary
        """
        return {
            "message": self.message,
            "code": self.code,
            "status": self.status,
            "details": self.details,
        }

    def __str__(self) -> str:
        """String representation of the error"""
        return f"MarzPayError({self.code}): {self.message}"

    def __repr__(self) -> str:
        """Representation of the error"""
        return f"MarzPayError(message='{self.message}', code='{self.code}', status={self.status})"


