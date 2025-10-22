"""
Webhook verification and handling
"""

import hmac
import hashlib
import json
from typing import Dict, Any, Optional

from ..exceptions import AuthKitError


class WebhookHandler:
    """
    Handler for AuthKit webhook events with signature verification.

    Example:
        >>> webhook_handler = WebhookHandler(
        ...     secret="your-webhook-secret"
        ... )
        >>> # In your Flask/Django view
        >>> event = webhook_handler.verify_and_parse(request.data)
        >>> if event['type'] == 'user.login':
        ...     print(f"User {event['user_id']} logged in")
    """

    def __init__(self, secret: str):
        """
        Initialize the webhook handler.

        Args:
            secret: Webhook secret for signature verification
        """
        self.secret = secret.encode() if isinstance(secret, str) else secret

    def verify_signature(
        self, payload: bytes, signature: str, timestamp: Optional[str] = None
    ) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Raw webhook payload
            signature: Signature from the webhook header
            timestamp: Optional timestamp from webhook header

        Returns:
            True if signature is valid, False otherwise
        """
        if timestamp:
            # Include timestamp in signature calculation for replay protection
            signed_payload = f"{timestamp}.{payload.decode()}".encode()
        else:
            signed_payload = payload

        expected_signature = hmac.new(
            self.secret, signed_payload, hashlib.sha256
        ).hexdigest()

        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(signature, expected_signature)

    def verify_and_parse(
        self,
        payload: bytes,
        signature: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Verify webhook signature and parse the payload.

        Args:
            payload: Raw webhook payload
            signature: Signature from webhook header (if None, verification is skipped)
            timestamp: Optional timestamp from webhook header

        Returns:
            Parsed webhook event data

        Raises:
            AuthKitError: If signature verification fails or payload is invalid
        """
        # Verify signature if provided
        if signature:
            if not self.verify_signature(payload, signature, timestamp):
                raise AuthKitError("Invalid webhook signature")

        # Parse the payload
        try:
            event = json.loads(payload.decode())
            return event
        except json.JSONDecodeError as e:
            raise AuthKitError(f"Invalid webhook payload: {str(e)}")

    def construct_event(
        self, payload: str, signature: str, timestamp: str
    ) -> Dict[str, Any]:
        """
        Construct and verify a webhook event (Stripe-style API).

        Args:
            payload: Raw webhook payload as string
            signature: Signature from the webhook header
            timestamp: Timestamp from the webhook header

        Returns:
            Parsed and verified webhook event

        Raises:
            AuthKitError: If verification fails
        """
        return self.verify_and_parse(
            payload.encode(), signature=signature, timestamp=timestamp
        )

    @staticmethod
    def get_event_type(event: Dict[str, Any]) -> str:
        """
        Get the event type from a webhook event.

        Args:
            event: Parsed webhook event

        Returns:
            Event type string
        """
        return event.get("type", "unknown")

    @staticmethod
    def get_user_id(event: Dict[str, Any]) -> Optional[str]:
        """
        Get the user ID from a webhook event.

        Args:
            event: Parsed webhook event

        Returns:
            User ID or None if not present
        """
        return event.get("user_id")

    @staticmethod
    def is_user_event(event: Dict[str, Any]) -> bool:
        """
        Check if the event is a user-related event.

        Args:
            event: Parsed webhook event

        Returns:
            True if it's a user event
        """
        event_type = WebhookHandler.get_event_type(event)
        return event_type.startswith("user.")
