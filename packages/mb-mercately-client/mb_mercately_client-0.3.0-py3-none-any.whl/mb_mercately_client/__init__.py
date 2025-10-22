"""Mercately WhatsApp API client for Django applications."""

__version__ = "0.3.0"
__author__ = "Multiburó"
__email__ = "gerardo.gornes@multiburo.com.mx"

# Core client classes
from .client import MercatelyClient
from .async_client import AsyncMercatelyClient

# Data models
from .models import (
    ClientConfig,
    Customer,
    CustomerRequest,
    CustomerResponse,
    HealthResponse,
    MessageInfo,
    Tag,
    Template,
    TemplateRequest,
    TemplateResponse,
    TemplatesResponse,
)

# Exceptions
from .exceptions import (
    ConfigurationError,
    CustomerNotFoundError,
    InvalidPhoneNumberError,
    MercatelyAPIError,
    MercatelyAuthenticationError,
    MercatelyClientError,
    MercatelyConnectionError,
    MercatelyTimeoutError,
    RateLimitError,
    TemplateNotFoundError,
    ValidationError,
)

# Public API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",

    # Core clients
    "MercatelyClient",
    "AsyncMercatelyClient",

    # Models
    "ClientConfig",
    "Customer",
    "CustomerRequest",
    "CustomerResponse",
    "HealthResponse",
    "MessageInfo",
    "Tag",
    "Template",
    "TemplateRequest",
    "TemplateResponse",
    "TemplatesResponse",

    # Exceptions
    "ConfigurationError",
    "CustomerNotFoundError",
    "InvalidPhoneNumberError",
    "MercatelyAPIError",
    "MercatelyAuthenticationError",
    "MercatelyClientError",
    "MercatelyConnectionError",
    "MercatelyTimeoutError",
    "RateLimitError",
    "TemplateNotFoundError",
    "ValidationError",
]


def get_version() -> str:
    """Get the package version."""
    return __version__


def get_client(**kwargs) -> MercatelyClient:
    """Get a configured synchronous Mercately client.

    This is a convenience function that creates a MercatelyClient with
    automatic configuration discovery.

    Args:
        **kwargs: Optional arguments to override configuration.

    Returns:
        Configured MercatelyClient instance.

    Example:
        from mercately_client import get_client

        client = get_client()
        response = client.send_template(
            phone="+1234567890",
            template_id="welcome"
        )
    """
    return MercatelyClient(**kwargs)


def get_async_client(**kwargs) -> AsyncMercatelyClient:
    """Get a configured asynchronous Mercately client.

    This is a convenience function that creates an AsyncMercatelyClient with
    automatic configuration discovery.

    Args:
        **kwargs: Optional arguments to override configuration.

    Returns:
        Configured AsyncMercatelyClient instance.

    Example:
        from mercately_client import get_async_client

        async def send_message():
            async with get_async_client() as client:
                response = await client.send_template(
                    phone="+1234567890",
                    template_id="welcome"
                )
    """
    return AsyncMercatelyClient(**kwargs)