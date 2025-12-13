from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from loguru import logger

router = APIRouter(prefix="/api/v1/companies", tags=["companies"])

# This will be initialized in main.py
analytics_engine = None


def set_analytics_engine(engine):
    """Set the analytics engine instance."""
    global analytics_engine
    analytics_engine = engine


@router.get("/", summary="List companies")
async def list_companies(
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    sort_by: str = Query("mentions", description="Sort by: mentions, deals, connections")
):
    """
    Get list of companies.
    
    - **limit**: Maximum results
    - **sort_by**: Sorting metric (mentions, deals, connections)
    """
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")
        
        companies = analytics_engine.relationship_mapper.get_top_companies(
            top_n=limit,
            metric=sort_by
        )
        
        return {
            "total": len(companies),
            "sort_by": sort_by,
            "companies": companies
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{company_name}", summary="Get company details")
async def get_company(company_name: str):
    """
    Get detailed information about a company.
    
    - **company_name**: Company name
    """
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")
        
        # Get company network
        network = analytics_engine.relationship_mapper.get_company_network(company_name)
        
        if network['total_connections'] == 0 and network['mention_count'] == 0:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Get sentiment trend
        sentiment_trend = analytics_engine.trend_analyzer.get_sentiment_trend(
            company=company_name
        )
        
        return {
            "company": company_name,
            "network": network,
            "sentiment": sentiment_trend
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company {company_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{company_name}/relationships", summary="Get company relationships")
async def get_company_relationships(
    company_name: str,
    depth: int = Query(1, ge=1, le=3, description="Network depth")
):
    """
    Get company relationship network.
    
    - **company_name**: Company name
    - **depth**: Network depth (1-3)
    """
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")
        
        network = analytics_engine.relationship_mapper.get_company_network(
            company_name,
            depth=depth
        )
        
        if network['total_connections'] == 0:
            raise HTTPException(status_code=404, detail="Company not found or no relationships")
        
        return network
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting relationships for {company_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{company_name}/sentiment", summary="Get company sentiment history")
async def get_company_sentiment(
    company_name: str,
    days: int = Query(30, ge=1, le=90, description="Number of days")
):
    """
    Get sentiment history for a company.
    
    - **company_name**: Company name
    - **days**: Number of days to analyze
    """
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")
        
        from datetime import datetime, timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        sentiment_trend = analytics_engine.trend_analyzer.get_sentiment_trend(
            start_date=start_date,
            end_date=end_date,
            company=company_name
        )
        
        return {
            "company": company_name,
            "period_days": days,
            "sentiment": sentiment_trend
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sentiment for {company_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network/graph", summary="Get network graph data")
async def get_network_graph():
    """Get complete network graph data for visualization."""
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")
        
        graph_data = analytics_engine.relationship_mapper.export_graph_data()
        
        return graph_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting network graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))
