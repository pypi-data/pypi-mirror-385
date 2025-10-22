"""Custom exceptions for Mercately client."""

from typing import Any, Dict, Optional


class MercatelyClientError(Exception):
    """Base exception for all Mercately client errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (details: {self.details})"
        return self.message


class MercatelyAPIError(MercatelyClientError):
    """Exception raised for API-specific errors from the Mercately service."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_data: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ) -> None:
        super().__init__(message, {"status_code": status_code, "error_code": error_code})
        self.status_code = status_code
        self.response_data = response_data or {}
        self.error_code = error_code

    def __str__(self) -> str:
        return f"API Error {self.status_code}: {self.message}"


class MercatelyTimeoutError(MercatelyClientError):
    """Exception raised when a request times out."""

    def __init__(self, message: str = "Request timed out", timeout: Optional[float] = None) -> None:
        super().__init__(message, {"timeout": timeout})
        self.timeout = timeout


class MercatelyAuthenticationError(MercatelyAPIError):
    """Exception raised for authentication-related errors."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, status_code=401, error_code="AUTHENTICATION_ERROR")


class MercatelyConnectionError(MercatelyClientError):
    """Exception raised for connection-related errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None) -> None:
        super().__init__(message, {"original_error": str(original_error) if original_error else None})
        self.original_error = original_error


class InvalidPhoneNumberError(MercatelyClientError):
    """Exception raised for invalid phone number format."""

    def __init__(self, phone_number: str, message: str = "Invalid phone number format") -> None:
        super().__init__(f"{message}: {phone_number}", {"phone_number": phone_number})
        self.phone_number = phone_number


class TemplateNotFoundError(MercatelyAPIError):
    """Exception raised when a template is not found."""

    def __init__(self, template_id: str) -> None:
        super().__init__(
            f"Template not found: {template_id}",
            status_code=404,
            error_code="TEMPLATE_NOT_FOUND",
        )
        self.template_id = template_id


class CustomerNotFoundError(MercatelyAPIError):
    """Exception raised when a customer is not found."""

    def __init__(self, phone_number: str) -> None:
        super().__init__(
            f"Customer not found: {phone_number}",
            status_code=404,
            error_code="CUSTOMER_NOT_FOUND",
        )
        self.phone_number = phone_number


class RateLimitError(MercatelyAPIError):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None) -> None:
        super().__init__(message, status_code=429, error_code="RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after
        if retry_after:
            self.details["retry_after"] = retry_after


class ConfigurationError(MercatelyClientError):
    """Exception raised for configuration-related errors."""

    def __init__(self, message: str, missing_config: Optional[str] = None) -> None:
        super().__init__(message, {"missing_config": missing_config})
        self.missing_config = missing_config


class ValidationError(MercatelyClientError):
    """Exception raised for data validation errors."""

    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None) -> None:
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        super().__init__(message, details)
        self.field = field
        self.value = value