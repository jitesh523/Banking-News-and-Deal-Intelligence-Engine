from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime, timedelta
from loguru import logger

from app.core.cache import cache

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

# This will be initialized in main.py
analytics_engine = None


def set_analytics_engine(engine):
    """Set the analytics engine instance."""
    global analytics_engine
    analytics_engine = engine


@router.get("/sentiment", summary="Get sentiment trends")
async def get_sentiment_trends(
    days: int = Query(30, ge=1, le=90, description="Number of days to analyze"),
    company: Optional[str] = Query(None, description="Filter by company")
):
    """
    Get sentiment trends over time.
    
    - **days**: Number of days to analyze (1-90)
    - **company**: Optional company filter
    """
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")
        
        insights = analytics_engine.get_sentiment_insights(days_back=days)
        
        if company:
            # Get company-specific sentiment
            from datetime import timedelta
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            company_trend = analytics_engine.trend_analyzer.get_sentiment_trend(
                start_date=start_date,
                end_date=end_date,
                company=company
            )
            
            return {
                "company": company,
                "period_days": days,
                "trend": company_trend
            }
        
        return {
            "period_days": days,
            "insights": insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sentiment trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics", summary="Get topic distribution")
async def get_topics():
    """Get topic distribution from topic modeling."""
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")
        
        # This would require NLP pipeline to be integrated
        return {
            "message": "Topic modeling requires NLP pipeline integration",
            "topics": []
        }
        
    except Exception as e:
        logger.error(f"Error getting topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities", summary="Get entity frequency")
async def get_entity_frequency(
    entity_type: str = Query("companies", description="Type of entity"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results")
):
    """
    Get frequency of entities mentioned.
    
    - **entity_type**: Type of entity (companies, people, locations)
    - **limit**: Maximum results
    """
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")
        
        if entity_type == "companies":
            top_companies = analytics_engine.relationship_mapper.get_top_companies(
                top_n=limit,
                metric='mentions'
            )
            
            return {
                "entity_type": entity_type,
                "total": len(top_companies),
                "entities": top_companies
            }
        
        return {
            "entity_type": entity_type,
            "message": "Entity type not yet implemented",
            "entities": []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity frequency: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deals", summary="Get deal statistics")
async def get_deal_stats(
    days: int = Query(30, ge=1, le=90, description="Number of days to analyze")
):
    """
    Get deal statistics and trends.
    
    - **days**: Number of days to analyze
    """
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")
        
        cache_key = f"deal_stats:{days}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        insights = analytics_engine.get_deal_insights(days_back=days)
        result = {"period_days": days, "insights": insights}
        cache.set(cache_key, result, ttl=180)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deal stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", summary="Get dashboard summary")
async def get_dashboard_summary():
    """Get comprehensive dashboard summary (cached for 2 minutes)."""
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")
        
        cached = cache.get("dashboard_summary")
        if cached is not None:
            return cached

        summary = analytics_engine.get_dashboard_summary()
        cache.set("dashboard_summary", summary, ttl=120)
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

