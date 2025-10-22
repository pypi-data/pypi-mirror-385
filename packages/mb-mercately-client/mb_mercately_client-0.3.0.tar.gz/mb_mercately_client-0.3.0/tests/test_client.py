"""Tests for the synchronous Mercately client."""

import json
import os
import pytest
import responses
from unittest.mock import patch, MagicMock

from mb_mercately_client import MercatelyClient
from mb_mercately_client.exceptions import (
    ConfigurationError,
    CustomerNotFoundError,
    InvalidPhoneNumberError,
    MercatelyAPIError,
    MercatelyAuthenticationError,
    MercatelyConnectionError,
    MercatelyTimeoutError,
    TemplateNotFoundError,
)
from mb_mercately_client.models import TemplateResponse, HealthResponse


class TestMercatelyClientInit:
    """Test client initialization and configuration."""

    def test_init_with_explicit_params(self):
        """Test initialization with explicit parameters."""
        client = MercatelyClient(
            service_url="https://api.example.com",
            auth_token="test-token"
        )
        assert client._config.service_url == "https://api.example.com"
        assert client._config.auth_token == "test-token"
        assert client._config.timeout == 30

    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        with patch.dict(os.environ, {
            'MERCATELY_SERVICE_URL': 'https://env.example.com',
            'MERCATELY_SERVICE_TOKEN': 'env-token'
        }):
            client = MercatelyClient()
            assert client._config.service_url == "https://env.example.com"
            assert client._config.auth_token == "env-token"

    @patch('mb_mercately_client.client.MercatelyClient._get_django_config')
    def test_init_with_django_settings(self, mock_django_config):
        """Test initialization with Django settings."""
        mock_django_config.return_value = {
            'SERVICE_URL': 'https://django.example.com',
            'AUTH_TOKEN': 'django-token',
            'TIMEOUT': 60
        }
        client = MercatelyClient()
        assert client._config.service_url == "https://django.example.com"
        assert client._config.auth_token == "django-token"
        assert client._config.timeout == 60

    def test_init_missing_service_url(self):
        """Test initialization fails with missing service URL."""
        with pytest.raises(ConfigurationError) as exc_info:
            MercatelyClient(auth_token="test-token")
        assert "service_url is required" in str(exc_info.value)

    def test_init_missing_auth_token(self):
        """Test initialization fails with missing auth token."""
        with pytest.raises(ConfigurationError) as exc_info:
            MercatelyClient(service_url="https://api.example.com")
        assert "auth_token is required" in str(exc_info.value)

    def test_init_invalid_service_url(self):
        """Test initialization fails with invalid service URL."""
        with pytest.raises(ConfigurationError) as exc_info:
            MercatelyClient(
                service_url="invalid-url",
                auth_token="test-token"
            )
        assert "Invalid configuration" in str(exc_info.value)


class TestMercatelyClientSendTemplate:
    """Test send_template method."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return MercatelyClient(
            service_url="https://api.example.com",
            auth_token="test-token"
        )

    @responses.activate
    def test_send_template_success(self, client):
        """Test successful template sending."""
        responses.add(
            responses.POST,
            "https://api.example.com/whatsapp/template",
            json={
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
            },
            status=200
        )

        response = client.send_template(
            phone="+1234567890",
            template_id="welcome",
            template_params=["John", "Doe"]
        )

        assert isinstance(response, TemplateResponse)
        assert response.status == "success"
        assert response.message_id == "msg_123"
        assert response.info.info.status == "submitted"
        assert response.get_message_identifier() == "msg_123"

    @responses.activate
    def test_send_template_with_media_url(self, client):
        """Test successful template sending with media URL."""
        responses.add(
            responses.POST,
            "https://api.example.com/whatsapp/template",
            json={
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
            },
            status=200
        )

        response = client.send_template(
            phone="+1234567890",
            template_id="welcome_media",
            template_params=["John"],
            media_url="https://i.ibb.co/example/image.jpg"
        )

        assert isinstance(response, TemplateResponse)
        assert response.status == "success"
        assert response.message_id == "msg_456"

        # Verify the request included media_url
        assert len(responses.calls) == 1
        request_body = json.loads(responses.calls[0].request.body)
        assert request_body["media_url"] == "https://i.ibb.co/example/image.jpg"

    @responses.activate
    def test_send_template_with_tags(self, client):
        """Test successful template sending with tags."""
        responses.add(
            responses.POST,
            "https://api.example.com/whatsapp/template",
            json={
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
            },
            status=200
        )

        response = client.send_template(
            phone="+1234567890",
            template_id="welcome_vip",
            template_params=["John"],
            tags=[{"name": "Inquilino", "value": True}, {"name": "Premium"}]
        )

        assert isinstance(response, TemplateResponse)
        assert response.status == "success"
        assert response.message_id == "msg_789"

        # Verify the request included tags
        assert len(responses.calls) == 1
        request_body = json.loads(responses.calls[0].request.body)
        assert "tags" in request_body
        assert len(request_body["tags"]) == 2
        assert request_body["tags"][0]["name"] == "Inquilino"
        assert request_body["tags"][0]["value"] is True
        assert request_body["tags"][1]["name"] == "Premium"
        assert request_body["tags"][1]["value"] is True  # Default value

    @responses.activate
    def test_send_template_invalid_phone(self, client):
        """Test sending template with invalid phone number."""
        with pytest.raises(InvalidPhoneNumberError):
            client.send_template(
                phone="1234567890",  # Missing +
                template_id="welcome"
            )

    @responses.activate
    def test_send_template_auth_error(self, client):
        """Test sending template with authentication error."""
        responses.add(
            responses.POST,
            "https://api.example.com/whatsapp/template",
            json={"detail": "Invalid token"},
            status=401
        )

        with pytest.raises(MercatelyAuthenticationError):
            client.send_template(
                phone="+1234567890",
                template_id="welcome"
            )

    @responses.activate
    def test_send_template_not_found(self, client):
        """Test sending template that doesn't exist."""
        responses.add(
            responses.POST,
            "https://api.example.com/whatsapp/template",
            json={"detail": "Template not found"},
            status=404
        )

        with pytest.raises(TemplateNotFoundError):
            client.send_template(
                phone="+1234567890",
                template_id="nonexistent"
            )

    @responses.activate
    def test_send_template_server_error(self, client):
        """Test sending template with server error."""
        responses.add(
            responses.POST,
            "https://api.example.com/whatsapp/template",
            json={"detail": "Internal server error"},
            status=500
        )

        with pytest.raises(MercatelyAPIError) as exc_info:
            client.send_template(
                phone="+1234567890",
                template_id="welcome"
            )
        assert exc_info.value.status_code == 500


class TestMercatelyClientGetTemplates:
    """Test get_templates method."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return MercatelyClient(
            service_url="https://api.example.com",
            auth_token="test-token"
        )

    @responses.activate
    def test_get_templates_success(self, client):
        """Test successful template retrieval."""
        responses.add(
            responses.GET,
            "https://api.example.com/templates",
            json={
                "templates": [
                    {
                        "id": "template_1",
                        "name": "Welcome Template",
                        "internal_id": "welcome_template"
                    },
                    {
                        "id": "template_2",
                        "name": "Order Confirmation",
                        "internal_id": "order_confirmed"
                    }
                ]
            },
            status=200
        )

        templates = client.get_templates()
        assert len(templates) == 2
        assert templates[0].id == "template_1"
        assert templates[0].name == "Welcome Template"
        assert templates[1].internal_id == "order_confirmed"


class TestMercatelyClientHealthCheck:
    """Test health_check method."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return MercatelyClient(
            service_url="https://api.example.com",
            auth_token="test-token"
        )

    @responses.activate
    def test_health_check_success(self, client):
        """Test successful health check."""
        responses.add(
            responses.GET,
            "https://api.example.com/health",
            json={
                "status": "healthy",
                "timestamp": "2023-01-01T00:00:00Z"
            },
            status=200
        )

        health = client.health_check()
        assert isinstance(health, HealthResponse)
        assert health.status == "healthy"
        assert health.timestamp == "2023-01-01T00:00:00Z"


class TestMercatelyClientRetryLogic:
    """Test retry logic for failed requests."""

    @pytest.fixture
    def client(self):
        """Create a test client with retry configuration."""
        return MercatelyClient(
            service_url="https://api.example.com",
            auth_token="test-token",
            retry_attempts=2,
            retry_delay=0.1  # Short delay for tests
        )

    @responses.activate
    def test_retry_on_connection_error(self, client):
        """Test retry logic on connection errors."""
        # First call fails with connection error
        responses.add(
            responses.POST,
            "https://api.example.com/whatsapp/template",
            body=responses.ConnectionError("Connection failed")
        )
        # Second call succeeds
        responses.add(
            responses.POST,
            "https://api.example.com/whatsapp/template",
            json={
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
            },
            status=200
        )

        response = client.send_template(
            phone="+1234567890",
            template_id="welcome"
        )
        assert response.message_id == "msg_123"

    @responses.activate
    def test_no_retry_on_client_error(self, client):
        """Test that client errors (4xx) are not retried."""
        responses.add(
            responses.POST,
            "https://api.example.com/whatsapp/template",
            json={"detail": "Bad request"},
            status=400
        )

        with pytest.raises(MercatelyAPIError):
            client.send_template(
                phone="+1234567890",
                template_id="welcome"
            )

        # Should only have made one request
        assert len(responses.calls) == 1


class TestMercatelyClientMasking:
    """Test phone number masking for privacy."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return MercatelyClient(
            service_url="https://api.example.com",
            auth_token="test-token"
        )

    def test_mask_phone_number(self, client):
        """Test phone number masking."""
        assert client._mask_phone_number("+1234567890") == "+12***890"
        assert client._mask_phone_number("+12345") == "+12345"  # 5 chars not masked (<=6)
        assert client._mask_phone_number("+123456") == "+12***456"  # 7 chars get masked
        assert client._mask_phone_number("+1234567") == "+12***567"  # 7 chars get masked