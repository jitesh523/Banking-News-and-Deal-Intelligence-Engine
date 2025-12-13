from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import get_settings
from app.core.database import Database
from app.core.logging import setup_logging
from app.services.analytics_engine import AnalyticsEngine

# Import API routers
from app.api import news, analytics, companies, alerts
from app.api import analytics as analytics_api
from app.api import companies as companies_api
from app.api import alerts as alerts_api

settings = get_settings()

# Global analytics engine
analytics_engine = None


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
    
    logger.info("API ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Banking News Engine API")
    await Database.close_db()


# Create FastAPI app
app = FastAPI(
    title="Banking News and Deal Intelligence Engine",
    description="NLP-powered financial news analysis and deal intelligence platform",
    version="1.0.0",
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

# Include API routers
app.include_router(news.router)
app.include_router(analytics.router)
app.include_router(companies.router)
app.include_router(alerts.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Banking News and Deal Intelligence Engine API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "news": "/api/v1/news",
            "analytics": "/api/v1/analytics",
            "companies": "/api/v1/companies",
            "alerts": "/api/v1/alerts"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
