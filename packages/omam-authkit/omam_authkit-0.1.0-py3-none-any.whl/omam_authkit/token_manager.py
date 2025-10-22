"""
Token management utilities for handling token refresh and validation
"""

import time
from typing import Dict, Any, Optional
from collections import OrderedDict
import jwt
from datetime import datetime, timedelta

from .client import AuthKitClient
from .exceptions import TokenExpiredError, InvalidTokenError


class TokenManager:
    """
    Manages OAuth 2.0 tokens with automatic refresh capabilities.

    Example:
        >>> token_manager = TokenManager(
        ...     client_id="your-client-id",
        ...     client_secret="your-client-secret",
        ...     authkit_url="https://auth.yourdomain.com"
        ... )
        >>> # Get valid access token (auto-refreshes if needed)
        >>> access_token = token_manager.get_valid_token(refresh_token)
        >>> # Check if token is expired
        >>> is_expired = token_manager.is_token_expired(access_token)
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authkit_url: str,
        timeout: int = 30,
        cache_max_size: int = 1000,
        cache_ttl: int = 3600,
    ):
        """
        Initialize the token manager.

        Args:
            client_id: OAuth 2.0 client ID
            client_secret: OAuth 2.0 client secret
            authkit_url: Base URL of the AuthKit instance
            timeout: Request timeout in seconds
            cache_max_size: Maximum number of entries in token cache (default: 1000)
            cache_ttl: Time-to-live for cache entries in seconds (default: 3600)
        """
        self.client = AuthKitClient(
            client_id=client_id,
            client_secret=client_secret,
            authkit_url=authkit_url,
            timeout=timeout,
        )
        self._token_cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._cache_max_size = cache_max_size
        self._cache_ttl = cache_ttl

    def _cache_get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if key not in self._token_cache:
            return None

        entry = self._token_cache[key]
        timestamp = entry.get("_cached_at", 0)

        # Check if entry has expired based on TTL
        if time.time() - timestamp > self._cache_ttl:
            # Remove expired entry
            del self._token_cache[key]
            return None

        # Move to end (LRU)
        self._token_cache.move_to_end(key)
        return entry.get("value")

    def _cache_put(self, key: str, value: Dict[str, Any]) -> None:
        """
        Put value in cache with LRU eviction.

        Args:
            key: Cache key
            value: Value to cache
        """
        # Remove oldest entry if cache is full
        if len(self._token_cache) >= self._cache_max_size:
            self._token_cache.popitem(last=False)  # Remove oldest (FIFO/LRU)

        # Add new entry with timestamp
        self._token_cache[key] = {
            "value": value,
            "_cached_at": time.time()
        }

    def get_valid_token(
        self, refresh_token: str, force_refresh: bool = False
    ) -> str:
        """
        Get a valid access token, refreshing if necessary.

        Args:
            refresh_token: Refresh token to use for obtaining new access token
            force_refresh: Force refresh even if cached token is valid

        Returns:
            Valid access token

        Raises:
            TokenExpiredError: If refresh token is expired
            InvalidTokenError: If refresh token is invalid
        """
        # Check cache first
        if not force_refresh:
            cached = self._cache_get(refresh_token)
            if cached and not self.is_token_expired(cached["access_token"]):
                return cached["access_token"]

        # Refresh the token
        try:
            tokens = self.client.refresh_access_token(refresh_token)
            self._cache_put(refresh_token, tokens)
            return tokens["access_token"]
        except Exception as e:
            raise TokenExpiredError(f"Failed to refresh token: {str(e)}")

    def is_token_expired(
        self, access_token: str, buffer_seconds: int = 60
    ) -> bool:
        """
        Check if an access token is expired.

        Args:
            access_token: Access token to check
            buffer_seconds: Consider token expired this many seconds before actual expiry

        Returns:
            True if token is expired, False otherwise
        """
        try:
            # Decode without verification (we just need to check expiry)
            decoded = jwt.decode(
                access_token, options={"verify_signature": False}
            )

            if "exp" not in decoded:
                # If no expiry, assume it's valid
                return False

            expiry_time = decoded["exp"]
            current_time = time.time()

            return current_time >= (expiry_time - buffer_seconds)
        except jwt.DecodeError:
            # If we can't decode, assume it's invalid/expired
            return True

    def get_token_expiry(self, access_token: str) -> Optional[datetime]:
        """
        Get the expiry time of an access token.

        Args:
            access_token: Access token to check

        Returns:
            Expiry datetime or None if no expiry is set
        """
        try:
            decoded = jwt.decode(
                access_token, options={"verify_signature": False}
            )

            if "exp" in decoded:
                return datetime.fromtimestamp(decoded["exp"])

            return None
        except jwt.DecodeError:
            return None

    def validate_token(self, access_token: str) -> Dict[str, Any]:
        """
        Validate a token and get its metadata using introspection.

        Args:
            access_token: Token to validate

        Returns:
            Token metadata from introspection endpoint

        Raises:
            InvalidTokenError: If token is invalid
        """
        result = self.client.introspect_token(access_token)

        if not result.get("active", False):
            raise InvalidTokenError("Token is not active")

        return result

    def clear_cache(self) -> None:
        """Clear the token cache."""
        self._token_cache.clear()

    def close(self) -> None:
        """Close the underlying client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
