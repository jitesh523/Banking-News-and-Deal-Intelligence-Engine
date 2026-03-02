"""
Market summary API — daily and weekly intelligence digests.
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

router = APIRouter(prefix="/api/v1/summary", tags=["summary"])

# Set in main.py on startup
_summary_service = None


def set_summary_service(service):
    """Set the MarketSummaryService instance."""
    global _summary_service
    _summary_service = service


@router.get("/daily", summary="Get daily market summary")
async def daily_summary():
    """
    Generate today's market intelligence summary.

    Includes top deals, sentiment metrics, most-mentioned companies,
    recent alerts, and detected anomalies.
    """
    try:
        if not _summary_service:
            raise HTTPException(status_code=503, detail="Summary service not initialized")

        return _summary_service.generate_daily_summary()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating daily summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weekly", summary="Get weekly market digest")
async def weekly_digest():
    """
    Generate a weekly market intelligence digest.

    Aggregated metrics covering deals, sentiment trends, company rankings,
    alert breakdown, and network statistics over the past 7 days.
    """
    try:
        if not _summary_service:
            raise HTTPException(status_code=503, detail="Summary service not initialized")

        return _summary_service.generate_weekly_digest()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating weekly digest: {e}")
        raise HTTPException(status_code=500, detail=str(e))
