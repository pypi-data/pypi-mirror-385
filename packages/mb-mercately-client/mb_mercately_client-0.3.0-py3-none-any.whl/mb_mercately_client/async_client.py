"""Asynchronous Mercately WhatsApp API client."""

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional, Union

import httpx
from pydantic import ValidationError

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
)
from .models import (
    ClientConfig,
    Customer,
    CustomerRequest,
    CustomerResponse,
    HealthResponse,
    Template,
    TemplateRequest,
    TemplateResponse,
    TemplatesResponse,
)

logger = logging.getLogger(__name__)


class AsyncMercatelyClient:
    """Asynchronous client for Mercately WhatsApp API."""

    def __init__(
        self,
        service_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        max_retry_delay: float = 60.0,
    ) -> None:
        """Initialize the async Mercately client.

        Args:
            service_url: Base URL of the Mercately service. If not provided, will attempt
                to discover from Django settings or environment variables.
            auth_token: Authentication token. If not provided, will attempt to discover
                from Django settings or environment variables.
            timeout: Request timeout in seconds.
            retry_attempts: Number of retry attempts for failed requests.
            retry_delay: Base delay between retries in seconds.
            max_retry_delay: Maximum delay between retries in seconds.

        Raises:
            ConfigurationError: If required configuration is missing.
        """
        self._config = self._build_config(
            service_url=service_url,
            auth_token=auth_token,
            timeout=timeout,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay,
            max_retry_delay=max_retry_delay,
        )
        self._client: Optional[httpx.AsyncClient] = None

    def _build_config(
        self,
        service_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        max_retry_delay: float = 60.0,
    ) -> ClientConfig:
        """Build client configuration from various sources."""
        # Try to get from Django settings first
        django_config = self._get_django_config()

        # Build final config with precedence: explicit params > Django settings > env vars
        final_service_url = (
            service_url
            or django_config.get("SERVICE_URL")
            or os.getenv("MERCATELY_SERVICE_URL")
        )
        final_auth_token = (
            auth_token
            or django_config.get("AUTH_TOKEN")
            or os.getenv("MERCATELY_SERVICE_TOKEN")
        )

        if not final_service_url:
            raise ConfigurationError("service_url is required", missing_config="service_url")
        if not final_auth_token:
            raise ConfigurationError("auth_token is required", missing_config="auth_token")

        # Override defaults with Django settings if available
        final_timeout = django_config.get("TIMEOUT", timeout)
        final_retry_attempts = django_config.get("RETRY_ATTEMPTS", retry_attempts)
        final_retry_delay = django_config.get("RETRY_DELAY", retry_delay)

        try:
            return ClientConfig(
                service_url=final_service_url,
                auth_token=final_auth_token,
                timeout=final_timeout,
                retry_attempts=final_retry_attempts,
                retry_delay=final_retry_delay,
                max_retry_delay=max_retry_delay,
            )
        except ValidationError as e:
            raise ConfigurationError(f"Invalid configuration: {e}")

    def _get_django_config(self) -> Dict[str, Any]:
        """Attempt to get configuration from Django settings."""
        try:
            from django.conf import settings
            return getattr(settings, "MERCATELY_CLIENT", {})
        except (ImportError, AttributeError):
            return {}

    async def _get_client(self, require_auth: bool = True) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "mb-mercately-client/0.2.0",
            }
            if require_auth:
                headers["Authorization"] = f"Bearer {self._config.auth_token}"

            self._client = httpx.AsyncClient(
                timeout=self._config.timeout,
                headers=headers,
            )

        return self._client

    def _mask_phone_number(self, phone: str) -> str:
        """Mask phone number for logging (show first 3 and last 3 digits)."""
        if len(phone) <= 6:
            return phone
        return f"{phone[:3]}***{phone[-3:]}"

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
    ) -> Dict[str, Any]:
        """Make an HTTP request with retry logic."""
        url = f"{self._config.service_url}{endpoint}"

        for attempt in range(self._config.retry_attempts + 1):
            try:
                start_time = time.time()
                client = await self._get_client(require_auth=require_auth)

                response = await client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                )

                response_time = int((time.time() - start_time) * 1000)

                # Log successful requests
                logger.info(
                    f"{method} {endpoint} completed",
                    extra={
                        "status_code": response.status_code,
                        "response_time_ms": response_time,
                        "attempt": attempt + 1,
                    },
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise MercatelyAuthenticationError("Invalid authentication token")
                elif response.status_code == 404:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("detail", "Resource not found")
                    if "template" in endpoint.lower():
                        # Extract template_id from error or data
                        template_id = (data or {}).get("template_id", "unknown")
                        raise TemplateNotFoundError(template_id)
                    elif "customer" in endpoint.lower():
                        # Extract phone from URL or data
                        phone = endpoint.split("/")[-1] if "/" in endpoint else "unknown"
                        raise CustomerNotFoundError(phone)
                    else:
                        raise MercatelyAPIError(error_msg, response.status_code)
                elif response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    retry_after_int = int(retry_after) if retry_after else None
                    raise RateLimitError(retry_after=retry_after_int)
                else:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("detail", f"HTTP {response.status_code}")
                    raise MercatelyAPIError(
                        error_msg,
                        response.status_code,
                        response_data=error_data,
                    )

            except httpx.TimeoutException:
                if attempt == self._config.retry_attempts:
                    logger.error(f"Request timed out after {self._config.retry_attempts + 1} attempts")
                    raise MercatelyTimeoutError(timeout=self._config.timeout)

            except httpx.ConnectError as e:
                if attempt == self._config.retry_attempts:
                    logger.error(f"Connection failed after {self._config.retry_attempts + 1} attempts")
                    raise MercatelyConnectionError("Failed to connect to Mercately service", e)

            except (MercatelyAPIError, MercatelyAuthenticationError) as e:
                # Don't retry client errors (4xx)
                logger.error(f"API error: {e}")
                raise

            except Exception as e:
                if attempt == self._config.retry_attempts:
                    logger.error(f"Unexpected error after {self._config.retry_attempts + 1} attempts: {e}")
                    raise MercatelyClientError(f"Unexpected error: {e}")

            # Calculate delay for next retry
            if attempt < self._config.retry_attempts:
                delay = min(
                    self._config.retry_delay * (2 ** attempt),
                    self._config.max_retry_delay
                )
                logger.warning(f"Request failed, retrying in {delay}s (attempt {attempt + 1})")
                await asyncio.sleep(delay)

        raise MercatelyClientError("Max retries exceeded")

    async def send_template(
        self,
        phone: str,
        template_id: str,
        template_params: Optional[List[str]] = None,
        auto_create_customer: bool = True,
        media_url: Optional[str] = None,
        tags: Optional[List[Dict[str, Any]]] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> TemplateResponse:
        """Send a WhatsApp template message.

        Args:
            phone: Phone number with country code (e.g., '+1234567890').
            template_id: Template identifier.
            template_params: Template parameters in order.
            auto_create_customer: Whether to create customer if not exists.
            media_url: URL of media to include with the template message.
            tags: List of tags to apply to the customer (e.g., [{"name": "Inquilino", "value": True}]).
            first_name: Customer first name (used when auto-creating customer).
            last_name: Customer last name (used when auto-creating customer).
            email: Customer email (used when auto-creating customer).

        Returns:
            TemplateResponse with message details.

        Raises:
            InvalidPhoneNumberError: If phone number format is invalid.
            TemplateNotFoundError: If template is not found.
            MercatelyAPIError: If API request fails.
        """
        # Convert tag dicts to Tag objects if provided
        tag_objects = None
        if tags:
            from .models import Tag
            tag_objects = [Tag(**tag) if isinstance(tag, dict) else tag for tag in tags]

        try:
            request_data = TemplateRequest(
                phone_number=phone,
                template_id=template_id,
                template_params=template_params or [],
                auto_create_customer=auto_create_customer,
                media_url=media_url,
                tags=tag_objects,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
        except ValidationError as e:
            # Convert validation errors to our custom exceptions
            if "phone_number" in str(e):
                raise InvalidPhoneNumberError(phone)
            raise MercatelyClientError(f"Validation error: {e}")

        masked_phone = self._mask_phone_number(phone)
        logger.info(
            f"Sending template message",
            extra={
                "phone": masked_phone,
                "template_id": template_id,
                "params_count": len(template_params or []),
                "has_media": media_url is not None,
            },
        )

        response_data = await self._make_request(
            method="POST",
            endpoint="/whatsapp/template",
            data=request_data.model_dump(exclude_none=True),
        )

        try:
            response = TemplateResponse(**response_data)

            # Use the created_time from the detailed info as a fallback identifier
            message_identifier = response.message_id or response.info.info.created_time

            logger.info(
                f"Template sent successfully",
                extra={
                    "phone": masked_phone,
                    "template_id": template_id,
                    "message_id": response.message_id,
                    "message_status": response.info.info.status,
                    "created_time": response.info.info.created_time,
                },
            )
            return response
        except ValidationError as e:
            logger.error(f"Response validation failed. Raw response: {response_data}")
            raise MercatelyClientError(f"Invalid response format: {e}")

    async def get_templates(self) -> List[Template]:
        """Get available WhatsApp templates.

        Returns:
            List of available templates.

        Raises:
            MercatelyAPIError: If API request fails.
        """
        logger.info("Fetching available templates")

        response_data = await self._make_request(
            method="GET",
            endpoint="/templates",
        )

        try:
            response = TemplatesResponse(**response_data)
            logger.info(f"Retrieved {len(response.templates)} templates")
            return response.templates
        except ValidationError as e:
            raise MercatelyClientError(f"Invalid response format: {e}")

    async def create_customer(
        self,
        phone: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[Dict[str, Any]]] = None,
    ) -> Customer:
        """Create a new customer.

        Args:
            phone: Phone number with country code.
            first_name: Customer first name.
            last_name: Customer last name.
            email: Customer email.
            metadata: Additional customer metadata.
            tags: List of tags to apply to the customer (e.g., [{"name": "Inquilino", "value": True}]).

        Returns:
            Created customer information.

        Raises:
            InvalidPhoneNumberError: If phone number format is invalid.
            MercatelyAPIError: If API request fails.
        """
        # Convert tag dicts to Tag objects if provided
        tag_objects = None
        if tags:
            from .models import Tag
            tag_objects = [Tag(**tag) if isinstance(tag, dict) else tag for tag in tags]

        try:
            request_data = CustomerRequest(
                phone_number=phone,
                first_name=first_name,
                last_name=last_name,
                email=email,
                metadata=metadata,
                tags=tag_objects,
            )
        except ValidationError as e:
            if "phone_number" in str(e):
                raise InvalidPhoneNumberError(phone)
            raise MercatelyClientError(f"Validation error: {e}")

        masked_phone = self._mask_phone_number(phone)
        logger.info(f"Creating customer", extra={"phone": masked_phone})

        response_data = await self._make_request(
            method="POST",
            endpoint="/customers",
            data=request_data.model_dump(exclude_none=True),
        )

        try:
            response = CustomerResponse(**response_data)
            logger.info(f"Customer created", extra={"phone": masked_phone, "customer_id": response.customer.id})
            return response.customer
        except ValidationError as e:
            raise MercatelyClientError(f"Invalid response format: {e}")

    async def get_customer(self, phone: str) -> Customer:
        """Get customer by phone number.

        Args:
            phone: Phone number with country code.

        Returns:
            Customer information.

        Raises:
            CustomerNotFoundError: If customer is not found.
            MercatelyAPIError: If API request fails.
        """
        masked_phone = self._mask_phone_number(phone)
        logger.info(f"Getting customer", extra={"phone": masked_phone})

        response_data = await self._make_request(
            method="GET",
            endpoint=f"/customers/{phone}",
        )

        try:
            response = CustomerResponse(**response_data)
            logger.info(f"Customer retrieved", extra={"phone": masked_phone, "customer_id": response.customer.id})
            return response.customer
        except ValidationError as e:
            raise MercatelyClientError(f"Invalid response format: {e}")

    async def health_check(self) -> HealthResponse:
        """Check service health.

        Returns:
            Health status information.

        Raises:
            MercatelyConnectionError: If unable to connect to service.
        """
        logger.info("Performing health check")

        response_data = await self._make_request(
            method="GET",
            endpoint="/health",
            require_auth=False,
        )

        try:
            response = HealthResponse(**response_data)
            logger.info(f"Health check completed", extra={"status": response.status})
            return response
        except ValidationError as e:
            raise MercatelyClientError(f"Invalid response format: {e}")

    async def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "AsyncMercatelyClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()