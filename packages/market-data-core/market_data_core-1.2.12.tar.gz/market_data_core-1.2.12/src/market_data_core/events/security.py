"""Security helpers for event bus.

Provides publisher authentication and optional envelope signing.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Protocol


class PublisherAuthenticator(Protocol):
    """Protocol for publisher authentication.
    
    Implementations can check tokens, API keys, JWT, etc.
    """
    
    def authenticate(self, token: str | None) -> bool:
        """Check if publisher is authenticated.
        
        Args:
            token: Authentication token
        
        Returns:
            True if authenticated, False otherwise
        """
        ...


class SimpleTokenAuthenticator:
    """Simple token-based authenticator.
    
    Compares provided token against a secret token.
    NOT cryptographically secure - use for basic dev/test only.
    """
    
    def __init__(self, secret_token: str | None = None):
        """Initialize authenticator.
        
        Args:
            secret_token: Expected token. If None, reads from PUBLISHER_TOKEN env var.
        """
        self.secret_token = secret_token or os.getenv("PUBLISHER_TOKEN")
        self.enabled = bool(self.secret_token)
    
    def authenticate(self, token: str | None) -> bool:
        """Check if token matches secret token.
        
        Args:
            token: Token to verify
        
        Returns:
            True if token matches or auth is disabled
        """
        if not self.enabled:
            return True  # Auth disabled
        
        if not token:
            return False  # No token provided
        
        return token == self.secret_token


class NoOpAuthenticator:
    """No-op authenticator (always allows)."""
    
    def authenticate(self, token: str | None) -> bool:
        return True


def sign_envelope(payload: bytes, secret: str) -> str:
    """Sign an envelope payload using HMAC-SHA256.
    
    Args:
        payload: Envelope payload (JSON bytes)
        secret: Signing secret
    
    Returns:
        Hex-encoded signature
    
    Example:
        >>> payload = b'{"event": "feedback"}'
        >>> signature = sign_envelope(payload, "secret123")
        >>> # Add signature to envelope.meta.headers["signature"]
    """
    return hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify an envelope signature.
    
    Args:
        payload: Envelope payload (JSON bytes)
        signature: Signature to verify
        secret: Signing secret
    
    Returns:
        True if signature is valid
    
    Example:
        >>> payload = b'{"event": "feedback"}'
        >>> signature = sign_envelope(payload, "secret123")
        >>> assert verify_signature(payload, signature, "secret123")
    """
    expected = sign_envelope(payload, secret)
    return hmac.compare_digest(signature, expected)

