import time as _time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import get_settings
from app.core.database import Database
from app.core.logging import setup_logging
from app.core.middleware import RequestTimingMiddleware, RateLimitMiddleware
from app.services.analytics_engine import AnalyticsEngine

# Import API routers
from app.api import news, analytics, companies, alerts, export
from app.api import websocket as ws_api
from app.api import bookmarks as bookmarks_api
from app.api import collection as collection_api
from app.api import summary as summary_api
from app.api import analytics as analytics_api
from app.api import companies as companies_api
from app.api import alerts as alerts_api
from app.services.market_summary import MarketSummaryService

settings = get_settings()

# Global analytics engine
analytics_engine = None

# Track server start time for uptime calculation
_server_start_time = _time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global analytics_engine
    
    # Startup
    setup_logging()
    logger.info("Starting Banking News Engine API")
    
    # Connect to database
    await Database.connect_db()
    
    # Initialize analytics engine
    logger.info("Initializing Analytics Engine...")
    analytics_engine = AnalyticsEngine()
    
    # Set analytics engine in API modules
    analytics_api.set_analytics_engine(analytics_engine)
    companies_api.set_analytics_engine(analytics_engine)
    alerts_api.set_analytics_engine(analytics_engine)
    
    # Set analytics engine for export module
    export.set_analytics_engine(analytics_engine)
    
    # Initialize market summary service
    summary_service = MarketSummaryService(analytics_engine)
    summary_api.set_summary_service(summary_service)
    
    logger.info("API ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Banking News Engine API")
    await Database.close_db()


# Create FastAPI app
app = FastAPI(
    title="Banking News and Deal Intelligence Engine",
    description="NLP-powered financial news analysis and deal intelligence platform",
    version="2.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestTimingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=settings.api_rate_limit, window_seconds=60)

# Include API routers
app.include_router(news.router)
app.include_router(analytics.router)
app.include_router(companies.router)
app.include_router(alerts.router)
app.include_router(export.router)
app.include_router(ws_api.router)
app.include_router(bookmarks_api.router)
app.include_router(collection_api.router)
app.include_router(summary_api.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Banking News and Deal Intelligence Engine API",
        "version": "2.1.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "news": "/api/v1/news",
            "analytics": "/api/v1/analytics",
            "companies": "/api/v1/companies",
            "alerts": "/api/v1/alerts",
            "export": "/api/v1/export",
            "bookmarks": "/api/v1/bookmarks",
            "collection": "/api/v1/collection",
            "summary": "/api/v1/summary",
            "websocket": "/ws/live-feed"
        }
    }


@app.get("/health")
async def health_check():
    """
    Enhanced health check with system diagnostics.
    
    Returns database connectivity, uptime, memory usage, and version info.
    """
    import psutil
    import os
    from datetime import datetime, timezone

    # Check database connectivity
    db_status = "disconnected"
    try:
        if Database.client:
            await Database.client.admin.command("ping")
            db_status = "connected"
    except Exception:
        db_status = "disconnected"

    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / (1024 * 1024)
    uptime = _time.time() - _server_start_time

    overall = "healthy" if db_status == "connected" else "degraded"

    return {
        "status": overall,
        "version": "2.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(uptime, 1),
        "database": db_status,
        "memory_usage_mb": round(memory_mb, 1),
        "environment": settings.environment,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
