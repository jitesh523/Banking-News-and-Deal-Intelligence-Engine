from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime, timedelta
from loguru import logger

from app.services.storage import StorageService
from app.models.article import Article
from app.core.responses import PaginatedResponse

router = APIRouter(prefix="/api/v1/news", tags=["news"])
storage = StorageService()


@router.on_event("startup")
async def startup():
    """Initialize storage service."""
    await storage.initialize()


@router.get("/", summary="List all news articles")
async def list_articles(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    source: Optional[str] = Query(None, description="Filter by source"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get paginated list of news articles with optional filtering.

    - **page**: Page number (1-indexed)
    - **per_page**: Items per page (1-100)
    - **source**: Filter by news source
    - **start_date**: Filter articles from this date
    - **end_date**: Filter articles until this date
    """
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        # Fetch a generous limit to count total
        all_articles = await storage.search_articles(
            source=source,
            start_date=start_dt,
            end_date=end_dt,
            limit=1000
        )

        total = len(all_articles)
        skip = (page - 1) * per_page
        page_articles = all_articles[skip : skip + per_page]

        return PaginatedResponse.create(
            items=[a.model_dump(exclude={"raw_data"}) for a in page_articles],
            total=total,
            page=page,
            per_page=per_page,
        )

    except Exception as e:
        logger.error(f"Error listing articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{article_id}", summary="Get specific article")
async def get_article(article_id: str):
    """
    Get a specific article by ID.

    - **article_id**: Unique article identifier
    """
    try:
        article = await storage.get_article_by_id(article_id)

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        return article.model_dump()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting article {article_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/", summary="Search articles")
async def search_articles(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Search articles by text query with pagination.

    - **q**: Search query (searches title and content)
    - **page**: Page number
    - **per_page**: Items per page
    """
    try:
        all_articles = await storage.search_articles(query=q, limit=500)
        total = len(all_articles)
        skip = (page - 1) * per_page
        page_articles = all_articles[skip : skip + per_page]

        return PaginatedResponse.create(
            items=[a.model_dump(exclude={"raw_data"}) for a in page_articles],
            total=total,
            page=page,
            per_page=per_page,
        )
        
    except Exception as e:
        logger.error(f"Error searching articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending/", summary="Get trending news")
async def get_trending(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    limit: int = Query(20, ge=1, le=50, description="Maximum results")
):
    """
    Get trending news articles from recent days.
    
    - **days**: Number of days to look back (1-30)
    - **limit**: Maximum results
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        articles = await storage.search_articles(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return {
            "period_days": days,
            "total": len(articles),
            "articles": [article.model_dump(exclude={'raw_data'}) for article in articles]
        }
        
    except Exception as e:
        logger.error(f"Error getting trending articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/", summary="Get news statistics")
async def get_news_stats():
    """Get overall news statistics."""
    try:
        total_count = await storage.get_article_count()
        
        # Get recent articles to calculate stats
        recent_articles = await storage.get_recent_articles(limit=100)
        
        # Calculate source distribution
        source_counts = {}
        for article in recent_articles:
            source_counts[article.source] = source_counts.get(article.source, 0) + 1
        
        return {
            "total_articles": total_count,
            "recent_sample_size": len(recent_articles),
            "sources": source_counts
        }
        
    except Exception as e:
        logger.error(f"Error getting news stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
