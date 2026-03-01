"""
Custom middleware for request tracking, timing, and rate limiting.
"""

import time
import uuid
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds request timing and unique request ID tracking.
    
    Headers added to every response:
        - X-Request-ID: Unique identifier for the request
        - X-Process-Time: Time taken to process the request (seconds)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        # Attach request_id to request state for use in logging
        request.state.request_id = request_id

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        logger.debug(
            f"[{request_id[:8]}] {request.method} {request.url.path} "
            f"→ {response.status_code} ({process_time:.3f}s)"
        )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter per client IP.
    
    Limits each IP to `max_requests` within a sliding `window_seconds` window.
    Health and docs endpoints are exempt from rate limiting.
    """

    EXEMPT_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old entries and add current
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if t > window_start
        ]
        self._requests[client_ip].append(now)

        remaining = self.max_requests - len(self._requests[client_ip])

        if remaining < 0:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return Response(
                content='{"detail": "Rate limit exceeded. Please try again later."}',
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(remaining, 0))
        return response
