"""Data models for Token Bowl Chat Client.

This module contains all the Pydantic models that correspond to the
OpenAPI schema definitions for the Token Bowl Chat Server API.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class MessageType(str, Enum):
    """Type of message."""

    ROOM = "room"
    DIRECT = "direct"
    SYSTEM = "system"


class UserRegistration(BaseModel):
    """Request model for user registration."""

    username: str = Field(..., min_length=1, max_length=50)
    webhook_url: str | None = Field(None, min_length=1, max_length=2083)
    logo: str | None = None
    viewer: bool = False
    admin: bool = False
    bot: bool = False
    emoji: str | None = None

    @field_validator("webhook_url")
    @classmethod
    def validate_webhook_url(cls, v: str | None) -> str | None:
        """Validate webhook URL format."""
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("webhook_url must be a valid HTTP(S) URL")
        return v


class UserRegistrationResponse(BaseModel):
    """Response model for user registration."""

    username: str
    api_key: str
    webhook_url: str | None = Field(None, min_length=1, max_length=2083)
    logo: str | None = None
    viewer: bool = False
    admin: bool = False
    bot: bool = False
    emoji: str | None = None


class SendMessageRequest(BaseModel):
    """Request model for sending a message."""

    content: str = Field(..., min_length=1, max_length=10000)
    to_username: str | None = Field(None, min_length=1, max_length=50)


class MessageResponse(BaseModel):
    """Response model for messages."""

    id: str
    from_username: str
    from_user_logo: str | None = None
    from_user_emoji: str | None = None
    from_user_bot: bool = False
    to_username: str | None
    content: str
    message_type: MessageType
    timestamp: str

    @property
    def timestamp_dt(self) -> datetime:
        """Parse timestamp string to datetime object."""
        return datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))


class PaginationMetadata(BaseModel):
    """Pagination metadata for message lists."""

    total: int
    offset: int
    limit: int
    has_more: bool


class PaginatedMessagesResponse(BaseModel):
    """Paginated response for messages."""

    messages: list[MessageResponse]
    pagination: PaginationMetadata


class ValidationError(BaseModel):
    """Validation error details."""

    loc: list[str | int]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    """HTTP validation error response."""

    detail: list[ValidationError]


class UpdateLogoRequest(BaseModel):
    """Request model for updating user logo."""

    logo: str | None = None


class UpdateWebhookRequest(BaseModel):
    """Request model for updating user webhook URL."""

    webhook_url: str | None = Field(None, min_length=1, max_length=2083)

    @field_validator("webhook_url")
    @classmethod
    def validate_webhook_url(cls, v: str | None) -> str | None:
        """Validate webhook URL format."""
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("webhook_url must be a valid HTTP(S) URL")
        return v


class UpdateUsernameRequest(BaseModel):
    """Request model for updating username."""

    username: str = Field(..., min_length=1, max_length=50)


class UnreadCountResponse(BaseModel):
    """Response model for unread message counts."""

    unread_room_messages: int
    unread_direct_messages: int
    total_unread: int


class UserProfileResponse(BaseModel):
    """Response model for user profile."""

    username: str
    email: str | None = None
    api_key: str
    webhook_url: str | None = Field(None, min_length=1, max_length=2083)
    logo: str | None = None
    viewer: bool = False
    admin: bool = False
    bot: bool = False
    emoji: str | None = None
    created_at: str


class PublicUserProfile(BaseModel):
    """Public user profile (no sensitive information)."""

    username: str
    logo: str | None = None
    emoji: str | None = None
    bot: bool = False
    viewer: bool = False


class StytchLoginRequest(BaseModel):
    """Request model for Stytch magic link login/signup."""

    email: str = Field(..., min_length=3, max_length=255)
    username: str | None = Field(None, min_length=1, max_length=50)


class StytchLoginResponse(BaseModel):
    """Response model for Stytch magic link send."""

    message: str
    email: str


class StytchAuthenticateRequest(BaseModel):
    """Request model for Stytch magic link authentication."""

    token: str = Field(..., min_length=1)


class StytchAuthenticateResponse(BaseModel):
    """Response model for Stytch authentication."""

    username: str
    session_token: str
    api_key: str


class AdminUpdateUserRequest(BaseModel):
    """Admin request model for updating any user's profile."""

    email: str | None = None
    webhook_url: str | None = Field(None, min_length=1, max_length=2083)
    logo: str | None = None
    viewer: bool | None = None
    admin: bool | None = None
    bot: bool | None = None
    emoji: str | None = None

    @field_validator("webhook_url")
    @classmethod
    def validate_webhook_url(cls, v: str | None) -> str | None:
        """Validate webhook URL format."""
        if v is not None and v != "" and not v.startswith(("http://", "https://")):
            raise ValueError("webhook_url must be a valid HTTP(S) URL")
        return v


class AdminMessageUpdate(BaseModel):
    """Admin request model for updating message content."""

    content: str = Field(..., min_length=1, max_length=10000)
