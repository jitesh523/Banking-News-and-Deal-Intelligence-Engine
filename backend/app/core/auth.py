"""
API Key authentication dependency for protected endpoints.

Usage:
    from app.core.auth import require_api_key

    @router.post("/protected", dependencies=[Depends(require_api_key)])
    async def protected_endpoint():
        ...

Configure API keys via the API_KEYS environment variable (comma-separated).
If API_KEYS is empty, authentication is disabled (development mode).
"""

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Parse configured keys from comma-separated env var
_valid_keys: set[str] = set()
if hasattr(settings, "api_keys") and settings.api_keys:
    _valid_keys = {k.strip() for k in settings.api_keys.split(",") if k.strip()}


async def require_api_key(api_key: str = Security(_api_key_header)) -> str:
    """
    FastAPI dependency that enforces API key authentication.

    If no API keys are configured (dev mode), all requests are allowed.
    Otherwise the client must send a valid key in the ``X-API-Key`` header.
    """
    # Dev mode — no keys configured, allow everything
    if not _valid_keys:
        return "dev-mode"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide it via the X-API-Key header.",
        )

    if api_key not in _valid_keys:
        logger.warning(f"Invalid API key attempt: {api_key[:8]}…")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )

    return api_key
