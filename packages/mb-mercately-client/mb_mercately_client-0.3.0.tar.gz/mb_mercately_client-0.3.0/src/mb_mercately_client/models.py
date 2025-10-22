"""Pydantic models for Mercately API requests and responses."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class Tag(BaseModel):
    """Tag model for customer categorization."""

    name: str = Field(..., description="Tag name")
    value: bool = Field(default=True, description="Tag value (typically true)")


class TemplateRequest(BaseModel):
    """Request model for sending WhatsApp template messages."""

    phone_number: str = Field(..., description="Phone number with country code (e.g., +5213312296362)")
    template_id: str = Field(..., description="Template identifier")
    template_params: List[str] = Field(default_factory=list, description="Template parameters in order")
    auto_create_customer: bool = Field(default=True, description="Whether to create customer if not exists")
    media_url: Optional[str] = Field(None, description="URL of media to include with the template message")
    tags: Optional[List[Tag]] = Field(None, description="Tags to apply to the customer")
    first_name: Optional[str] = Field(None, description="Customer first name (used when auto-creating customer)")
    last_name: Optional[str] = Field(None, description="Customer last name (used when auto-creating customer)")
    email: Optional[str] = Field(None, description="Customer email (used when auto-creating customer)")

    @field_validator('phone_number')
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number format."""
        if not v.startswith('+'):
            raise ValueError('Phone number must start with + and include country code')
        if len(v) < 10:
            raise ValueError('Phone number too short')
        return v


class MessageContent(BaseModel):
    """Content of the message."""

    text: str = Field(..., description="Message text content")


class MessageInfoDetails(BaseModel):
    """Detailed information about the sent message."""

    channel: str = Field(..., description="Channel used (e.g., 'whatsapp')")
    content: MessageContent = Field(..., description="Message content")
    direction: str = Field(..., description="Message direction (e.g., 'outbound')")
    status: str = Field(..., description="Message status (e.g., 'submitted')")
    destination: str = Field(..., description="Destination phone number")
    country: str = Field(..., description="Country code")
    created_time: str = Field(..., description="Message creation timestamp")
    error: Optional[str] = Field(None, description="Error message if any")


class MessageInfo(BaseModel):
    """Information about a sent message."""

    message: str = Field(..., description="Response message")
    info: MessageInfoDetails = Field(..., description="Detailed message information")


class TemplateResponse(BaseModel):
    """Response model for template message sending."""

    status: str = Field(..., description="Request status")
    message_id: Optional[str] = Field(None, description="Unique message identifier (may be null)")
    info: MessageInfo = Field(..., description="Additional message information")
    error: Optional[str] = Field(None, description="Error message if any")

    def get_message_identifier(self) -> str:
        """Get a message identifier, using created_time as fallback if message_id is null."""
        return self.message_id or self.info.info.created_time

    def get_message_status(self) -> str:
        """Get the message status from the detailed info."""
        return self.info.info.status

    def get_destination(self) -> str:
        """Get the destination phone number."""
        return self.info.info.destination


class Template(BaseModel):
    """Template information model."""

    id: str = Field(..., description="Template ID")
    name: str = Field(..., description="Template display name")
    internal_id: str = Field(..., description="Internal template identifier")


class TemplatesResponse(BaseModel):
    """Response model for getting available templates."""

    templates: List[Template] = Field(..., description="List of available templates")


class CustomerRequest(BaseModel):
    """Request model for creating customers."""

    phone_number: str = Field(..., description="Phone number with country code")
    first_name: Optional[str] = Field(None, description="Customer first name")
    last_name: Optional[str] = Field(None, description="Customer last name")
    email: Optional[str] = Field(None, description="Customer email")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional customer metadata")
    tags: Optional[List[Tag]] = Field(None, description="Tags to apply to the customer")

    @field_validator('phone_number')
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number format."""
        if not v.startswith('+'):
            raise ValueError('Phone number must start with + and include country code')
        if len(v) < 10:
            raise ValueError('Phone number too short')
        return v


class Customer(BaseModel):
    """Customer information model."""

    id: str = Field(..., description="Customer ID")
    phone_number: str = Field(..., description="Customer phone number")
    first_name: Optional[str] = Field(None, description="Customer first name")
    last_name: Optional[str] = Field(None, description="Customer last name")
    email: Optional[str] = Field(None, description="Customer email")
    created_at: str = Field(..., description="Customer creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional customer metadata")


class CustomerResponse(BaseModel):
    """Response model for customer operations."""

    customer: Customer = Field(..., description="Customer information")


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Health check timestamp")


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    status_code: Optional[int] = Field(None, description="HTTP status code")


class ClientConfig(BaseModel):
    """Configuration model for Mercately client."""

    service_url: str = Field(..., description="Base URL of the Mercately service")
    auth_token: str = Field(..., description="Authentication token")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    retry_delay: float = Field(default=1.0, description="Base delay between retries in seconds")
    max_retry_delay: float = Field(default=60.0, description="Maximum delay between retries")

    @field_validator('service_url')
    def validate_service_url(cls, v: str) -> str:
        """Validate service URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Service URL must start with http:// or https://')
        return v.rstrip('/')

    @field_validator('timeout')
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout value."""
        if v <= 0:
            raise ValueError('Timeout must be positive')
        return v

    @field_validator('retry_attempts')
    def validate_retry_attempts(cls, v: int) -> int:
        """Validate retry attempts value."""
        if v < 0:
            raise ValueError('Retry attempts cannot be negative')
        return v