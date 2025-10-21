"""Synchronous client for Token Bowl Chat Server."""

import os
from typing import Any, cast

import httpx

from .exceptions import (
    AuthenticationError,
    ConflictError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)
from .models import (
    AdminMessageUpdate,
    AdminUpdateUserRequest,
    MessageResponse,
    PaginatedMessagesResponse,
    PublicUserProfile,
    SendMessageRequest,
    StytchAuthenticateRequest,
    StytchAuthenticateResponse,
    StytchLoginRequest,
    StytchLoginResponse,
    UnreadCountResponse,
    UpdateLogoRequest,
    UpdateUsernameRequest,
    UpdateWebhookRequest,
    UserProfileResponse,
    UserRegistration,
    UserRegistrationResponse,
)


class TokenBowlClient:
    """Synchronous client for Token Bowl Chat Server.

    This client provides a Pythonic interface to the Token Bowl Chat Server API
    with full type hints and error handling.

    Example:
        >>> client = TokenBowlClient(api_key="your-api-key")
        >>> client.send_message("Hello, world!")
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.tokenbowl.ai",
        timeout: float = 30.0,
    ) -> None:
        """Initialize the Token Bowl client.

        Args:
            api_key: API key for authentication (optional, defaults to TOKEN_BOWL_CHAT_API_KEY env var)
            base_url: Base URL of the Token Bowl server (optional)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("TOKEN_BOWL_CHAT_API_KEY")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def __enter__(self) -> "TokenBowlClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def _get_headers(self) -> dict[str, str]:
        """Get request headers including authentication if available.

        Returns:
            Dictionary of HTTP headers

        Raises:
            AuthenticationError: If API key is required but not set
        """
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _handle_response(self, response: httpx.Response) -> None:
        """Handle HTTP response errors.

        Args:
            response: HTTP response object

        Raises:
            AuthenticationError: For 401 errors
            NotFoundError: For 404 errors
            ConflictError: For 409 errors
            ValidationError: For 422 errors
            RateLimitError: For 429 errors
            ServerError: For 5xx errors
        """
        if response.status_code < 400:
            return

        try:
            error_data = response.json()
            error_message = str(error_data)
        except Exception:
            error_message = response.text or f"HTTP {response.status_code}"

        if response.status_code == 401:
            raise AuthenticationError(error_message, response)
        elif response.status_code == 404:
            raise NotFoundError(error_message, response)
        elif response.status_code == 409:
            raise ConflictError(error_message, response)
        elif response.status_code == 422:
            raise ValidationError(error_message, response)
        elif response.status_code == 429:
            raise RateLimitError(error_message, response)
        elif response.status_code >= 500:
            raise ServerError(error_message, response)
        else:
            response.raise_for_status()

    def _request(
        self,
        method: str,
        path: str,
        requires_auth: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an HTTP request.

        Args:
            method: HTTP method
            path: API endpoint path
            requires_auth: Whether this endpoint requires authentication
            **kwargs: Additional arguments to pass to httpx

        Returns:
            HTTP response object

        Raises:
            AuthenticationError: If auth is required but API key not set
            NetworkError: For network connectivity issues
            TimeoutError: For request timeouts
        """
        url = f"{self.base_url}{path}"
        headers = self._get_headers()

        if requires_auth and not self.api_key:
            raise AuthenticationError("API key required for this operation")

        try:
            response = self._client.request(method, url, headers=headers, **kwargs)
            self._handle_response(response)
            return response
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {e}") from e
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e}") from e

    def register(
        self,
        username: str,
        webhook_url: str | None = None,
        logo: str | None = None,
    ) -> UserRegistrationResponse:
        """Register a new user and get an API key.

        Args:
            username: Username to register (1-50 characters)
            webhook_url: Optional webhook URL for notifications
            logo: Optional logo filename from available logos

        Returns:
            User registration response with API key

        Raises:
            ConflictError: If username already exists
            ValidationError: If input validation fails
        """
        registration = UserRegistration(
            username=username, webhook_url=webhook_url, logo=logo
        )
        response = self._request(
            "POST",
            "/register",
            json=registration.model_dump(exclude_none=True),
        )
        return UserRegistrationResponse.model_validate(response.json())

    def send_message(
        self,
        content: str,
        to_username: str | None = None,
    ) -> MessageResponse:
        """Send a message to the room or as a direct message.

        Args:
            content: Message content (1-10000 characters)
            to_username: Optional recipient username for direct messages

        Returns:
            Created message response

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If recipient doesn't exist
            ValidationError: If input validation fails
        """
        message_request = SendMessageRequest(content=content, to_username=to_username)
        response = self._request(
            "POST",
            "/messages",
            requires_auth=True,
            json=message_request.model_dump(exclude_none=True),
        )
        return MessageResponse.model_validate(response.json())

    def get_messages(
        self,
        limit: int = 50,
        offset: int = 0,
        since: str | None = None,
    ) -> PaginatedMessagesResponse:
        """Get recent room messages with pagination.

        Args:
            limit: Maximum number of messages to return (default: 50)
            offset: Number of messages to skip (default: 0)
            since: ISO timestamp to get messages after

        Returns:
            Paginated list of messages with metadata

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If parameters are invalid
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if since is not None:
            params["since"] = since

        response = self._request(
            "GET",
            "/messages",
            requires_auth=True,
            params=params,
        )
        return PaginatedMessagesResponse.model_validate(response.json())

    def get_direct_messages(
        self,
        limit: int = 50,
        offset: int = 0,
        since: str | None = None,
    ) -> PaginatedMessagesResponse:
        """Get direct messages for the current user with pagination.

        Args:
            limit: Maximum number of messages to return (default: 50)
            offset: Number of messages to skip (default: 0)
            since: ISO timestamp to get messages after

        Returns:
            Paginated list of direct messages with metadata

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If parameters are invalid
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if since is not None:
            params["since"] = since

        response = self._request(
            "GET",
            "/messages/direct",
            requires_auth=True,
            params=params,
        )
        return PaginatedMessagesResponse.model_validate(response.json())

    def get_users(self) -> list[PublicUserProfile]:
        """Get list of all chat users with their display info.

        Viewer users are excluded as they cannot receive messages.

        Returns:
            List of user profiles with logos, emojis, and bot status

        Raises:
            AuthenticationError: If not authenticated
        """
        response = self._request("GET", "/users", requires_auth=True)
        return [PublicUserProfile.model_validate(user) for user in response.json()]

    def get_online_users(self) -> list[PublicUserProfile]:
        """Get list of users currently connected via WebSocket with their display info.

        Returns:
            List of online user profiles with logos, emojis, and bot status

        Raises:
            AuthenticationError: If not authenticated
        """
        response = self._request("GET", "/users/online", requires_auth=True)
        return [PublicUserProfile.model_validate(user) for user in response.json()]

    def get_available_logos(self) -> list[str]:
        """Get list of available logo filenames.

        Returns:
            List of available logo filenames

        Raises:
            AuthenticationError: If not authenticated
        """
        response = self._request("GET", "/logos", requires_auth=True)
        return cast(list[str], response.json())

    def update_my_logo(self, logo: str | None = None) -> dict[str, str]:
        """Update the current user's logo.

        Args:
            logo: Logo filename from available logos, or None to clear

        Returns:
            Success message with updated logo

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If logo is invalid
        """
        logo_request = UpdateLogoRequest(logo=logo)
        response = self._request(
            "PATCH",
            "/users/me/logo",
            requires_auth=True,
            json=logo_request.model_dump(exclude_none=True),
        )
        return cast(dict[str, str], response.json())

    # Stytch Authentication Methods

    def send_magic_link(
        self, email: str, username: str | None = None
    ) -> StytchLoginResponse:
        """Send a magic link to user's email for passwordless authentication.

        If the email is new, a username must be provided to create an account.
        If the email exists, the username field is ignored.

        Args:
            email: Email address to send magic link to
            username: Optional username for new account creation

        Returns:
            Stytch login response with confirmation message

        Raises:
            ValidationError: If input validation fails
            ServerError: If Stytch is not enabled or request fails
        """
        request = StytchLoginRequest(email=email, username=username)
        response = self._request(
            "POST",
            "/auth/magic-link/send",
            json=request.model_dump(exclude_none=True),
        )
        return StytchLoginResponse.model_validate(response.json())

    def authenticate_magic_link(self, token: str) -> StytchAuthenticateResponse:
        """Authenticate a magic link token and return session information.

        If this is a new user (first time authenticating), creates a user account.
        Returns a session token for future requests and an API key.

        Args:
            token: Magic link token from email

        Returns:
            Authentication response with username, session_token, and api_key

        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If token is invalid
        """
        request = StytchAuthenticateRequest(token=token)
        response = self._request(
            "POST",
            "/auth/magic-link/authenticate",
            json=request.model_dump(),
        )
        return StytchAuthenticateResponse.model_validate(response.json())

    # Unread Message Management

    def get_unread_messages(
        self, limit: int = 50, offset: int = 0
    ) -> list[MessageResponse]:
        """Get unread room messages for the current user.

        Args:
            limit: Maximum number of messages to return (default: 50)
            offset: Number of messages to skip (default: 0)

        Returns:
            List of unread room messages

        Raises:
            AuthenticationError: If not authenticated
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        response = self._request(
            "GET",
            "/messages/unread",
            requires_auth=True,
            params=params,
        )
        return [MessageResponse.model_validate(msg) for msg in response.json()]

    def get_unread_direct_messages(
        self, limit: int = 50, offset: int = 0
    ) -> list[MessageResponse]:
        """Get unread direct messages for the current user.

        Args:
            limit: Maximum number of messages to return (default: 50)
            offset: Number of messages to skip (default: 0)

        Returns:
            List of unread direct messages

        Raises:
            AuthenticationError: If not authenticated
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        response = self._request(
            "GET",
            "/messages/direct/unread",
            requires_auth=True,
            params=params,
        )
        return [MessageResponse.model_validate(msg) for msg in response.json()]

    def get_unread_count(self) -> UnreadCountResponse:
        """Get count of unread messages for the current user.

        Returns:
            Unread message counts (room, direct, and total)

        Raises:
            AuthenticationError: If not authenticated
        """
        response = self._request(
            "GET",
            "/messages/unread/count",
            requires_auth=True,
        )
        return UnreadCountResponse.model_validate(response.json())

    def mark_message_read(self, message_id: str) -> None:
        """Mark a message as read.

        Args:
            message_id: ID of the message to mark as read

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If message doesn't exist
        """
        self._request(
            "POST",
            f"/messages/{message_id}/read",
            requires_auth=True,
        )

    def mark_all_messages_read(self) -> dict[str, int]:
        """Mark all messages as read for the current user.

        Returns:
            Dictionary with count of messages marked as read

        Raises:
            AuthenticationError: If not authenticated
        """
        response = self._request(
            "POST",
            "/messages/mark-all-read",
            requires_auth=True,
        )
        return cast(dict[str, int], response.json())

    # User Profile Management

    def get_my_profile(self) -> UserProfileResponse:
        """Get the current user's profile information.

        Returns:
            User profile with email, API key, and other information

        Raises:
            AuthenticationError: If not authenticated
        """
        response = self._request(
            "GET",
            "/users/me",
            requires_auth=True,
        )
        return UserProfileResponse.model_validate(response.json())

    def get_user_profile(self, username: str) -> PublicUserProfile:
        """Get public profile for a specific user.

        Returns public information (username, logo, emoji, bot, viewer status)
        without sensitive data (API key, email, webhook URL).

        Args:
            username: Username to retrieve

        Returns:
            Public user profile

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If user not found
        """
        response = self._request(
            "GET",
            f"/users/{username}",
            requires_auth=True,
        )
        return PublicUserProfile.model_validate(response.json())

    def update_my_username(self, username: str) -> UserProfileResponse:
        """Update the current user's username.

        Args:
            username: New username

        Returns:
            Updated user profile

        Raises:
            AuthenticationError: If not authenticated
            ConflictError: If username already exists
            ValidationError: If username is invalid
        """
        request = UpdateUsernameRequest(username=username)
        response = self._request(
            "PATCH",
            "/users/me/username",
            requires_auth=True,
            json=request.model_dump(),
        )
        return UserProfileResponse.model_validate(response.json())

    def update_my_webhook(self, webhook_url: str | None) -> dict[str, str]:
        """Update the current user's webhook URL.

        Args:
            webhook_url: New webhook URL, or None to clear

        Returns:
            Success message with updated webhook URL

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If webhook URL is invalid
        """
        request = UpdateWebhookRequest(webhook_url=webhook_url)
        response = self._request(
            "PATCH",
            "/users/me/webhook",
            requires_auth=True,
            json=request.model_dump(exclude_none=True),
        )
        return cast(dict[str, str], response.json())

    def regenerate_api_key(self) -> dict[str, str]:
        """Regenerate the current user's API key.

        This generates a new API key and invalidates the old one.
        The old API key will no longer work for authentication.

        Returns:
            Success message with new API key

        Raises:
            AuthenticationError: If not authenticated
        """
        response = self._request(
            "POST",
            "/users/me/regenerate-api-key",
            requires_auth=True,
        )
        return cast(dict[str, str], response.json())

    # Admin Methods

    def admin_get_all_users(self) -> list[UserProfileResponse]:
        """Admin: Get all users with full profile information.

        Returns:
            List of all user profiles

        Raises:
            AuthenticationError: If not authenticated or not admin
        """
        response = self._request(
            "GET",
            "/admin/users",
            requires_auth=True,
        )
        return [UserProfileResponse.model_validate(user) for user in response.json()]

    def admin_get_user(self, username: str) -> UserProfileResponse:
        """Admin: Get a specific user's full profile.

        Args:
            username: Username to retrieve

        Returns:
            User profile

        Raises:
            AuthenticationError: If not authenticated or not admin
            NotFoundError: If user not found
        """
        response = self._request(
            "GET",
            f"/admin/users/{username}",
            requires_auth=True,
        )
        return UserProfileResponse.model_validate(response.json())

    def admin_update_user(
        self, username: str, update_request: AdminUpdateUserRequest
    ) -> UserProfileResponse:
        """Admin: Update any user's profile fields.

        Args:
            username: Username to update
            update_request: Fields to update

        Returns:
            Updated user profile

        Raises:
            AuthenticationError: If not authenticated or not admin
            NotFoundError: If user not found
            ValidationError: If update data is invalid
        """
        response = self._request(
            "PATCH",
            f"/admin/users/{username}",
            requires_auth=True,
            json=update_request.model_dump(exclude_none=True),
        )
        return UserProfileResponse.model_validate(response.json())

    def admin_delete_user(self, username: str) -> None:
        """Admin: Delete a user.

        Args:
            username: Username to delete

        Raises:
            AuthenticationError: If not authenticated or not admin
            NotFoundError: If user not found
        """
        self._request(
            "DELETE",
            f"/admin/users/{username}",
            requires_auth=True,
        )

    def admin_get_message(self, message_id: str) -> MessageResponse:
        """Admin: Get a specific message by ID.

        Args:
            message_id: Message ID to retrieve

        Returns:
            Message details

        Raises:
            AuthenticationError: If not authenticated or not admin
            NotFoundError: If message not found
        """
        response = self._request(
            "GET",
            f"/admin/messages/{message_id}",
            requires_auth=True,
        )
        return MessageResponse.model_validate(response.json())

    def admin_update_message(self, message_id: str, content: str) -> MessageResponse:
        """Admin: Update message content.

        Args:
            message_id: Message ID to update
            content: New message content

        Returns:
            Updated message

        Raises:
            AuthenticationError: If not authenticated or not admin
            NotFoundError: If message not found
            ValidationError: If content is invalid
        """
        request = AdminMessageUpdate(content=content)
        response = self._request(
            "PATCH",
            f"/admin/messages/{message_id}",
            requires_auth=True,
            json=request.model_dump(),
        )
        return MessageResponse.model_validate(response.json())

    def admin_delete_message(self, message_id: str) -> None:
        """Admin: Delete a message.

        Args:
            message_id: Message ID to delete

        Raises:
            AuthenticationError: If not authenticated or not admin
            NotFoundError: If message not found
        """
        self._request(
            "DELETE",
            f"/admin/messages/{message_id}",
            requires_auth=True,
        )

    def health_check(self) -> dict[str, str]:
        """Check server health status.

        Returns:
            Health status dictionary
        """
        response = self._request("GET", "/health")
        return cast(dict[str, str], response.json())
