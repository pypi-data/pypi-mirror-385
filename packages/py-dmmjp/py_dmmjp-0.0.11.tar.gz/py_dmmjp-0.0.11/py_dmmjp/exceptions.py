"""
Exception classes for the py-dmm library.
"""

from typing import Any, Optional


class DMMError(Exception):
    """Base exception for all py-dmm errors."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        """
        Initialize a DMMError.

        Args:
            message: The error message.
            details: Additional error details.
        """

        super().__init__(message)

        self.message = message
        self.details = details


class DMMAPIError(DMMError):
    """Exception raised for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Any] = None,
    ) -> None:
        """
        Initialize a DMMAPIError.

        Args:
            message: The error message.
            status_code: HTTP status code of the failed request.
            response_data: Raw response data from the API.
        """

        super().__init__(message, response_data)

        self.status_code = status_code
        self.response_data = response_data


class DMMAuthError(DMMError):
    """Exception raised for authentication-related errors."""

    def __init__(self, message: str = "Authentication failed") -> None:
        """
        Initialize a DMMAuthError.

        Args:
            message: The error message.
        """

        super().__init__(message)
