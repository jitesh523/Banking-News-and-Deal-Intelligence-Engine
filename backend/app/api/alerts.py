from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from loguru import logger

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

# This will be initialized in main.py
analytics_engine = None


def set_analytics_engine(engine):
    """Set the analytics engine instance."""
    global analytics_engine
    analytics_engine = engine


@router.get("/", summary="Get alerts")
async def get_alerts(
    priority: Optional[str] = Query(None, description="Filter by priority: LOW, MEDIUM, HIGH, CRITICAL"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results")
):
    """
    Get alerts with optional filtering.
    
    - **priority**: Filter by priority level
    - **limit**: Maximum results
    """
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")
        
        alerts = analytics_engine.get_alerts(priority=priority, limit=limit)
        
        return {
            "total": len(alerts),
            "priority_filter": priority,
            "alerts": alerts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", summary="Get alert summary")
async def get_alert_summary():
    """Get summary statistics of alerts."""
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")
        
        summary = analytics_engine.alert_system.get_alert_summary()
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
