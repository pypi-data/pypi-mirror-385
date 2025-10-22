"""Tests for the asynchronous Mercately client."""

import asyncio
import os
import pytest
import pytest_asyncio
import httpx
import respx
from unittest.mock import patch

from mb_mercately_client import AsyncMercatelyClient
from mb_mercately_client.exceptions import (
    ConfigurationError,
    MercatelyAPIError,
    MercatelyAuthenticationError,
    MercatelyTimeoutError,
    TemplateNotFoundError,
)
from mb_mercately_client.models import TemplateResponse, HealthResponse


class TestAsyncMercatelyClientInit:
    """Test async client initialization and configuration."""

    def test_init_with_explicit_params(self):
        """Test initialization with explicit parameters."""
        client = AsyncMercatelyClient(
            service_url="https://api.example.com",
            auth_token="test-token"
        )
        assert client._config.service_url == "https://api.example.com"
        assert client._config.auth_token == "test-token"
        assert client._config.timeout == 30

    def test_init_missing_service_url(self):
        """Test initialization fails with missing service URL."""
        with pytest.raises(ConfigurationError) as exc_info:
            AsyncMercatelyClient(auth_token="test-token")
        assert "service_url is required" in str(exc_info.value)


@pytest.mark.asyncio
class TestAsyncMercatelyClientSendTemplate:
    """Test async send_template method."""

    @pytest_asyncio.fixture
    async def client(self):
        """Create a test async client."""
        client = AsyncMercatelyClient(
            service_url="https://api.example.com",
            auth_token="test-token"
        )
        yield client
        await client.close()

    @respx.mock
    async def test_send_template_success(self, client):
        """Test successful template sending."""
        respx.post("https://api.example.com/whatsapp/template").mock(
            return_value=httpx.Response(200, json={
                "status": "success",
                "message_id": "msg_123",
                "info": {
                    "message": "Ok",
                    "info": {
                        "channel": "whatsapp",
                        "content": {"text": "Test message"},
                        "direction": "outbound",
                        "status": "submitted",
                        "destination": "+1234567890",
                        "country": "US",
                        "created_time": "2023-01-01T00:00:00Z",
                        "error": None
                    }
                },
                "error": None
            })
        )

        response = await client.send_template(
            phone="+1234567890",
            template_id="welcome",
            template_params=["John", "Doe"]
        )

        assert isinstance(response, TemplateResponse)
        assert response.status == "success"
        assert response.message_id == "msg_123"
        assert response.info.info.status == "submitted"

    @respx.mock
    async def test_send_template_with_media_url(self, client):
        """Test successful template sending with media URL."""
        route = respx.post("https://api.example.com/whatsapp/template").mock(
            return_value=httpx.Response(200, json={
                "status": "success",
                "message_id": "msg_456",
                "info": {
                    "message": "Ok",
                    "info": {
                        "channel": "whatsapp",
                        "content": {"text": "Test message with media"},
                        "direction": "outbound",
                        "status": "submitted",
                        "destination": "+1234567890",
                        "country": "US",
                        "created_time": "2023-01-01T00:00:00Z",
                        "error": None
                    }
                },
                "error": None
            })
        )

        response = await client.send_template(
            phone="+1234567890",
            template_id="welcome_media",
            template_params=["John"],
            media_url="https://i.ibb.co/example/image.jpg"
        )

        assert isinstance(response, TemplateResponse)
        assert response.status == "success"
        assert response.message_id == "msg_456"

        # Verify the request included media_url
        assert route.called
        request = route.calls.last.request
        request_json = httpx.QueryParams(request.content.decode()).get("media_url") or eval(request.content.decode())
        assert "https://i.ibb.co/example/image.jpg" in str(request_json)

    @respx.mock
    async def test_send_template_with_tags(self, client):
        """Test successful template sending with tags."""
        import json
        route = respx.post("https://api.example.com/whatsapp/template").mock(
            return_value=httpx.Response(200, json={
                "status": "success",
                "message_id": "msg_789",
                "info": {
                    "message": "Ok",
                    "info": {
                        "channel": "whatsapp",
                        "content": {"text": "Test message with tags"},
                        "direction": "outbound",
                        "status": "submitted",
                        "destination": "+1234567890",
                        "country": "US",
                        "created_time": "2023-01-01T00:00:00Z",
                        "error": None
                    }
                },
                "error": None
            })
        )

        response = await client.send_template(
            phone="+1234567890",
            template_id="welcome_vip",
            template_params=["John"],
            tags=[{"name": "Inquilino", "value": True}, {"name": "Premium"}]
        )

        assert isinstance(response, TemplateResponse)
        assert response.status == "success"
        assert response.message_id == "msg_789"

        # Verify the request included tags
        assert route.called
        request = route.calls.last.request
        request_body = json.loads(request.content.decode())
        assert "tags" in request_body
        assert len(request_body["tags"]) == 2
        assert request_body["tags"][0]["name"] == "Inquilino"
        assert request_body["tags"][0]["value"] is True
        assert request_body["tags"][1]["name"] == "Premium"
        assert request_body["tags"][1]["value"] is True

    @respx.mock
    async def test_send_template_auth_error(self, client):
        """Test sending template with authentication error."""
        respx.post("https://api.example.com/whatsapp/template").mock(
            return_value=httpx.Response(401, json={"detail": "Invalid token"})
        )

        with pytest.raises(MercatelyAuthenticationError):
            await client.send_template(
                phone="+1234567890",
                template_id="welcome"
            )

    @respx.mock
    async def test_send_template_not_found(self, client):
        """Test sending template that doesn't exist."""
        respx.post("https://api.example.com/whatsapp/template").mock(
            return_value=httpx.Response(404, json={"detail": "Template not found"})
        )

        with pytest.raises(TemplateNotFoundError):
            await client.send_template(
                phone="+1234567890",
                template_id="nonexistent"
            )

    @respx.mock
    async def test_send_template_server_error(self, client):
        """Test sending template with server error."""
        respx.post("https://api.example.com/whatsapp/template").mock(
            return_value=httpx.Response(500, json={"detail": "Internal server error"})
        )

        with pytest.raises(MercatelyAPIError) as exc_info:
            await client.send_template(
                phone="+1234567890",
                template_id="welcome"
            )
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
class TestAsyncMercatelyClientGetTemplates:
    """Test async get_templates method."""

    @pytest_asyncio.fixture
    async def client(self):
        """Create a test async client."""
        client = AsyncMercatelyClient(
            service_url="https://api.example.com",
            auth_token="test-token"
        )
        yield client
        await client.close()

    @respx.mock
    async def test_get_templates_success(self, client):
        """Test successful template retrieval."""
        respx.get("https://api.example.com/templates").mock(
            return_value=httpx.Response(200, json={
                "templates": [
                    {
                        "id": "template_1",
                        "name": "Welcome Template",
                        "internal_id": "welcome_template"
                    }
                ]
            })
        )

        templates = await client.get_templates()
        assert len(templates) == 1
        assert templates[0].id == "template_1"
        assert templates[0].name == "Welcome Template"


@pytest.mark.asyncio
class TestAsyncMercatelyClientHealthCheck:
    """Test async health_check method."""

    @pytest_asyncio.fixture
    async def client(self):
        """Create a test async client."""
        client = AsyncMercatelyClient(
            service_url="https://api.example.com",
            auth_token="test-token"
        )
        yield client
        await client.close()

    @respx.mock
    async def test_health_check_success(self, client):
        """Test successful health check."""
        respx.get("https://api.example.com/health").mock(
            return_value=httpx.Response(200, json={
                "status": "healthy",
                "timestamp": "2023-01-01T00:00:00Z"
            })
        )

        health = await client.health_check()
        assert isinstance(health, HealthResponse)
        assert health.status == "healthy"


@pytest.mark.asyncio
class TestAsyncMercatelyClientContextManager:
    """Test async client context manager functionality."""

    @respx.mock
    async def test_context_manager(self):
        """Test using client as async context manager."""
        respx.get("https://api.example.com/health").mock(
            return_value=httpx.Response(200, json={
                "status": "healthy",
                "timestamp": "2023-01-01T00:00:00Z"
            })
        )

        async with AsyncMercatelyClient(
            service_url="https://api.example.com",
            auth_token="test-token"
        ) as client:
            health = await client.health_check()
            assert health.status == "healthy"

        # Client should be closed after context manager exit
        assert client._client is None


@pytest.mark.asyncio
class TestAsyncMercatelyClientRetryLogic:
    """Test retry logic for failed requests."""

    @pytest_asyncio.fixture
    async def client(self):
        """Create a test client with retry configuration."""
        client = AsyncMercatelyClient(
            service_url="https://api.example.com",
            auth_token="test-token",
            retry_attempts=2,
            retry_delay=0.1  # Short delay for tests
        )
        yield client
        await client.close()

    @respx.mock
    async def test_retry_on_connection_error(self, client):
        """Test retry logic on connection errors."""
        # First call fails, second succeeds
        route = respx.post("https://api.example.com/whatsapp/template")
        route.side_effect = [
            httpx.ConnectError("Connection failed"),
            httpx.Response(200, json={
                "status": "success",
                "message_id": "msg_123",
                "info": {
                    "message": "Ok",
                    "info": {
                        "channel": "whatsapp",
                        "content": {"text": "Test message"},
                        "direction": "outbound",
                        "status": "submitted",
                        "destination": "+1234567890",
                        "country": "US",
                        "created_time": "2023-01-01T00:00:00Z",
                        "error": None
                    }
                },
                "error": None
            })
        ]

        response = await client.send_template(
            phone="+1234567890",
            template_id="welcome"
        )
        assert response.message_id == "msg_123"

    @respx.mock
    async def test_no_retry_on_client_error(self, client):
        """Test that client errors (4xx) are not retried."""
        respx.post("https://api.example.com/whatsapp/template").mock(
            return_value=httpx.Response(400, json={"detail": "Bad request"})
        )

        with pytest.raises(MercatelyAPIError):
            await client.send_template(
                phone="+1234567890",
                template_id="welcome"
            )


@pytest.mark.asyncio
class TestAsyncMercatelyClientCustomerOperations:
    """Test async customer operations."""

    @pytest_asyncio.fixture
    async def client(self):
        """Create a test async client."""
        client = AsyncMercatelyClient(
            service_url="https://api.example.com",
            auth_token="test-token"
        )
        yield client
        await client.close()

    @respx.mock
    async def test_create_customer_success(self, client):
        """Test successful customer creation."""
        respx.post("https://api.example.com/customers").mock(
            return_value=httpx.Response(200, json={
                "customer": {
                    "id": "cust_123",
                    "phone_number": "+1234567890",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john@example.com",
                    "created_at": "2023-01-01T00:00:00Z",
                    "metadata": None
                }
            })
        )

        customer = await client.create_customer(
            phone="+1234567890",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )

        assert customer.id == "cust_123"
        assert customer.first_name == "John"
        assert customer.email == "john@example.com"

    @respx.mock
    async def test_get_customer_success(self, client):
        """Test successful customer retrieval."""
        respx.get("https://api.example.com/customers/+1234567890").mock(
            return_value=httpx.Response(200, json={
                "customer": {
                    "id": "cust_123",
                    "phone_number": "+1234567890",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john@example.com",
                    "created_at": "2023-01-01T00:00:00Z",
                    "metadata": None
                }
            })
        )

        customer = await client.get_customer("+1234567890")
        assert customer.id == "cust_123"
        assert customer.phone_number == "+1234567890"