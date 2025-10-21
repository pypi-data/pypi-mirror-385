class ClientError(Exception):
    """Base exception for kc-ohlc client."""

class AuthError(ClientError):
    """Raised when API key is missing or unauthorized."""

class APIError(ClientError):
    """Raised for non-2xx API responses."""
