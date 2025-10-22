"""
Core AuthKit client for OAuth 2.0 authentication
"""

from typing import Dict, List, Optional, Any
from urllib.parse import urlencode, urljoin, urlparse
import requests
import logging
import warnings

from .exceptions import AuthKitError, AuthenticationError, APIError, InvalidTokenError

# Set up logging for security events
logger = logging.getLogger(__name__)


class AuthKitClient:
    """
    Client for interacting with OMAM AuthKit OAuth 2.0 provider.

    Example:
        >>> client = AuthKitClient(
        ...     client_id="your-client-id",
        ...     client_secret="your-client-secret",
        ...     authkit_url="https://auth.yourdomain.com"
        ... )
        >>> auth_url = client.get_authorization_url(
        ...     redirect_uri="http://localhost:8000/callback",
        ...     scopes=["read", "write"]
        ... )
        >>> # After user authorizes, exchange code for tokens
        >>> tokens = client.exchange_code_for_tokens(
        ...     code="authorization_code",
        ...     redirect_uri="http://localhost:8000/callback"
        ... )
        >>> # Get user information
        >>> user_info = client.get_user_info(tokens["access_token"])
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authkit_url: str,
        timeout: int = 30,
        retry_attempts: int = 3,
        allow_http: bool = False,
    ):
        """
        Initialize the AuthKit client.

        Args:
            client_id: OAuth 2.0 client ID
            client_secret: OAuth 2.0 client secret
            authkit_url: Base URL of the AuthKit instance (must be HTTPS in production)
            timeout: Request timeout in seconds (default: 30)
            retry_attempts: Number of retry attempts for failed requests (default: 3)
            allow_http: Allow HTTP URLs (insecure, only for development) (default: False)

        Raises:
            ValueError: If authkit_url is invalid or uses HTTP without allow_http=True
        """
        # Validate and sanitize the AuthKit URL
        self.authkit_url = self._validate_url(authkit_url, allow_http)
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self.retry_attempts = retry_attempts

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "omam-authkit-python-sdk/0.1.0"})

    def _validate_url(self, url: str, allow_http: bool = False) -> str:
        """
        Validate and sanitize the AuthKit URL.

        Args:
            url: URL to validate
            allow_http: Whether to allow HTTP URLs

        Returns:
            Validated and sanitized URL

        Raises:
            ValueError: If URL is invalid
        """
        url = url.rstrip("/")
        parsed = urlparse(url)

        # Check if scheme is present
        if not parsed.scheme:
            raise ValueError(
                "Invalid authkit_url: URL must include scheme (https:// or http://)"
            )

        # Check if scheme is valid
        if parsed.scheme not in ("http", "https"):
            raise ValueError(
                f"Invalid authkit_url scheme: {parsed.scheme}. "
                "Only 'http' and 'https' are supported."
            )

        # Enforce HTTPS in production
        if parsed.scheme == "http":
            if not allow_http:
                raise ValueError(
                    "HTTP URLs are not allowed for security reasons. "
                    "Use HTTPS in production, or set allow_http=True for development only."
                )
            else:
                warnings.warn(
                    "Using HTTP is insecure and should only be used in development. "
                    "Credentials and tokens will be sent in plaintext!",
                    category=UserWarning,
                    stacklevel=3
                )
                logger.warning(f"Using insecure HTTP URL: {url}")

        # Check if hostname is present
        if not parsed.netloc:
            raise ValueError("Invalid authkit_url: URL must include hostname")

        return url

    def get_authorization_url(
        self,
        redirect_uri: str,
        scopes: Optional[List[str]] = None,
        state: Optional[str] = None,
    ) -> str:
        """
        Generate the authorization URL for the OAuth 2.0 flow.

        Args:
            redirect_uri: Callback URL after authorization
            scopes: List of permission scopes (default: ["read"])
            state: State parameter for CSRF protection

        Returns:
            Authorization URL to redirect the user to
        """
        if scopes is None:
            scopes = ["read"]

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
        }

        if state:
            params["state"] = state

        auth_endpoint = urljoin(self.authkit_url, "/oauth/authorize/")
        return f"{auth_endpoint}?{urlencode(params)}"

    def exchange_code_for_tokens(
        self, code: str, redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.

        Args:
            code: Authorization code from the callback
            redirect_uri: Same redirect URI used in authorization request

        Returns:
            Dictionary containing:
                - access_token: Access token for API requests
                - refresh_token: Refresh token for obtaining new access tokens
                - token_type: Token type (usually "Bearer")
                - expires_in: Token expiration time in seconds
                - scope: Granted scopes

        Raises:
            AuthenticationError: If token exchange fails
            APIError: If API request fails
        """
        token_endpoint = urljoin(self.authkit_url, "/oauth/token/")

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            response = self._session.post(
                token_endpoint, data=data, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Log the detailed error for debugging
            logger.error(
                f"Token exchange failed with status {e.response.status_code}: "
                f"{e.response.text[:200]}"
            )
            if e.response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed. Please check your credentials."
                )
            elif e.response.status_code == 400:
                raise AuthenticationError(
                    "Invalid authorization code or redirect URI."
                )
            else:
                raise APIError(
                    f"Token exchange failed with status {e.response.status_code}",
                    status_code=e.response.status_code,
                )
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise APIError("Request failed. Please try again.")

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token using a refresh token.

        Args:
            refresh_token: Refresh token from previous token exchange

        Returns:
            Dictionary containing new tokens (same structure as exchange_code_for_tokens)

        Raises:
            AuthenticationError: If token refresh fails
            APIError: If API request fails
        """
        token_endpoint = urljoin(self.authkit_url, "/oauth/token/")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            response = self._session.post(
                token_endpoint, data=data, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Token refresh failed with status {e.response.status_code}: "
                f"{e.response.text[:200]}"
            )
            if e.response.status_code == 401:
                raise AuthenticationError(
                    "Token refresh failed. The refresh token may be expired or invalid."
                )
            else:
                raise APIError(
                    f"Token refresh failed with status {e.response.status_code}",
                    status_code=e.response.status_code,
                )
        except requests.exceptions.RequestException as e:
            logger.error(f"Token refresh request failed: {str(e)}")
            raise APIError("Token refresh request failed. Please try again.")

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information using an access token.

        Args:
            access_token: Valid access token

        Returns:
            Dictionary containing user information:
                - id: User UUID
                - email: User email address
                - first_name: User's first name
                - last_name: User's last name
                - email_verified: Email verification status
                - created_at: Account creation timestamp

        Raises:
            InvalidTokenError: If token is invalid or expired
            APIError: If API request fails
        """
        userinfo_endpoint = urljoin(self.authkit_url, "/api/auth/userinfo/")

        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = self._session.get(
                userinfo_endpoint, headers=headers, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Get user info failed with status {e.response.status_code}")
            if e.response.status_code == 401:
                raise InvalidTokenError("Access token is invalid or expired")
            else:
                raise APIError(
                    f"Failed to get user info with status {e.response.status_code}",
                    status_code=e.response.status_code,
                )
        except requests.exceptions.RequestException as e:
            logger.error(f"Get user info request failed: {str(e)}")
            raise APIError("Request failed. Please try again.")

    def revoke_token(self, token: str) -> None:
        """
        Revoke an access or refresh token.

        Args:
            token: Token to revoke

        Raises:
            APIError: If revocation fails
        """
        revoke_endpoint = urljoin(self.authkit_url, "/oauth/revoke_token/")

        data = {
            "token": token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            response = self._session.post(
                revoke_endpoint, data=data, timeout=self.timeout
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Token revocation failed: {str(e)}")

    def introspect_token(self, token: str) -> Dict[str, Any]:
        """
        Introspect a token to get its metadata.

        Args:
            token: Token to introspect

        Returns:
            Dictionary containing token metadata:
                - active: Whether the token is active
                - scope: Token scopes
                - client_id: Client ID
                - username: User identifier
                - exp: Expiration timestamp

        Raises:
            APIError: If introspection fails
        """
        introspect_endpoint = urljoin(self.authkit_url, "/oauth/introspect/")

        data = {
            "token": token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            response = self._session.post(
                introspect_endpoint, data=data, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Token introspection failed: {str(e)}")

    def register_user(
        self,
        email: str,
        password: str,
        password_confirm: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a new user account.

        Args:
            email: User email address
            password: User password
            password_confirm: Password confirmation
            first_name: User's first name (optional)
            last_name: User's last name (optional)

        Returns:
            Dictionary containing user information

        Raises:
            APIError: If registration fails
        """
        register_endpoint = urljoin(self.authkit_url, "/api/auth/register/")

        data = {
            "email": email,
            "password": password,
            "password_confirm": password_confirm,
        }

        if first_name:
            data["first_name"] = first_name
        if last_name:
            data["last_name"] = last_name

        try:
            response = self._session.post(
                register_endpoint, json=data, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"User registration failed with status {e.response.status_code}"
            )
            if e.response.status_code == 400:
                raise APIError(
                    "Registration failed. Please check your input and try again.",
                    status_code=e.response.status_code,
                )
            else:
                raise APIError(
                    f"User registration failed with status {e.response.status_code}",
                    status_code=e.response.status_code,
                )
        except requests.exceptions.RequestException as e:
            logger.error(f"Registration request failed: {str(e)}")
            raise APIError("Registration request failed. Please try again.")

    def close(self) -> None:
        """Close the HTTP session."""
        self._session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
