"""
Global error handler — structured JSON error responses with dev-mode stack traces.
"""

import traceback
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all exception handler that returns consistent JSON error responses.

    In development mode, includes the full stack trace for debugging.
    """
    error_id = f"ERR-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    logger.error(
        f"[{error_id}] Unhandled exception on {request.method} {request.url.path}: {exc}"
    )

    body = {
        "success": False,
        "error": {
            "id": error_id,
            "type": type(exc).__name__,
            "message": str(exc),
            "path": str(request.url.path),
            "method": request.method,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Include traceback in development
    if settings.environment == "development":
        body["error"]["traceback"] = traceback.format_exception(
            type(exc), exc, exc.__traceback__
        )

    return JSONResponse(status_code=500, content=body)


def register_error_handlers(app: FastAPI) -> None:
    """Register the global error handler on the FastAPI app."""
    app.add_exception_handler(Exception, global_exception_handler)
