"""
Custom HTTPException subclasses used across the API for consistent,
debuggable error responses.

Each exception carries a sensible default status code and detail message
so endpoints can raise them without repeating boilerplate, while still
allowing callers to override the message with request-specific context.
"""
from fastapi import HTTPException, status


class InvalidSymbolError(HTTPException):
    """Raised when a trading symbol is not in the supported symbol set."""

    def __init__(self, symbol: str, supported: list[str] | None = None):
        detail = f"Symbol '{symbol}' is not supported."
        if supported:
            detail += f" Supported symbols: {sorted(supported)}"
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ValidationError(HTTPException):
    """Raised for general request validation failures that aren't caught by Pydantic."""

    def __init__(self, detail: str = "Invalid request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class AuthenticationError(HTTPException):
    """Raised when authentication fails (bad credentials, invalid/expired token)."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Raised when an authenticated user doesn't have permission for an action."""

    def __init__(self, detail: str = "You do not have permission to perform this action"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ResourceNotFoundError(HTTPException):
    """Raised when a requested resource does not exist."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictError(HTTPException):
    """Raised when a request conflicts with existing state (e.g. duplicate resource)."""

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UpstreamServiceError(HTTPException):
    """Raised when an upstream dependency (e.g. Binance) fails and no fallback is available."""

    def __init__(self, detail: str = "Upstream service temporarily unavailable"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)
