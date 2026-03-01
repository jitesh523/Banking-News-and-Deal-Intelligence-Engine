"""
Data export API — download deals, companies, and articles as CSV or JSON files.
"""

import csv
import io
import json
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

router = APIRouter(prefix="/api/v1/export", tags=["export"])

# Set by main.py on startup
analytics_engine = None


def set_analytics_engine(engine):
    """Set the analytics engine instance."""
    global analytics_engine
    analytics_engine = engine


def _csv_response(rows: list[dict], filename: str) -> StreamingResponse:
    """Convert a list of dicts to a downloadable CSV response."""
    if not rows:
        output = io.StringIO("No data available\n")
    else:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _json_response(rows: list[dict], filename: str) -> StreamingResponse:
    """Return a list of dicts as a downloadable JSON file."""
    content = json.dumps(rows, indent=2, default=str)
    return StreamingResponse(
        io.StringIO(content),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/deals", summary="Export detected deals")
async def export_deals(
    fmt: str = Query("json", alias="format", description="Export format: json or csv"),
    days: int = Query(90, ge=1, le=365, description="Number of days to include"),
):
    """
    Download all tracked deals as CSV or JSON.

    - **format**: `json` (default) or `csv`
    - **days**: How many days of history to include (max 365)
    """
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")

        insights = analytics_engine.get_deal_insights(days_back=days)
        deals = []

        # Flatten volume trend data into exportable rows
        vol = insights.get("volume_trend", {})
        type_dist = insights.get("type_distribution", {})

        for deal_type, count in type_dist.items():
            deals.append({"deal_type": deal_type, "count": count, "period_days": days})

        if not deals:
            deals = [{"message": "No deals found", "period_days": days}]

        filename = f"deals_export_{days}d"
        if fmt.lower() == "csv":
            return _csv_response(deals, f"{filename}.csv")
        return _json_response(deals, f"{filename}.json")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting deals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies", summary="Export company data")
async def export_companies(
    fmt: str = Query("json", alias="format", description="Export format: json or csv"),
    limit: int = Query(100, ge=1, le=500, description="Maximum companies to export"),
):
    """
    Download company data as CSV or JSON.

    - **format**: `json` (default) or `csv`
    - **limit**: Maximum number of companies (max 500)
    """
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")

        companies = analytics_engine.relationship_mapper.get_top_companies(
            top_n=limit, metric="mentions"
        )

        if not companies:
            companies = [{"message": "No company data available"}]

        filename = f"companies_export_top{limit}"
        if fmt.lower() == "csv":
            return _csv_response(companies, f"{filename}.csv")
        return _json_response(companies, f"{filename}.json")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/articles", summary="Export articles")
async def export_articles(
    fmt: str = Query("json", alias="format", description="Export format: json or csv"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum articles to export"),
):
    """
    Download articles as CSV or JSON.

    - **format**: `json` (default) or `csv`
    - **limit**: Maximum articles (max 1000)
    """
    try:
        from app.services.storage import StorageService

        storage = StorageService()
        await storage.initialize()
        articles = await storage.get_recent_articles(limit=limit)

        rows = []
        for a in articles:
            rows.append({
                "article_id": a.article_id,
                "title": a.title,
                "source": a.source,
                "author": a.author or "",
                "published_date": str(a.published_date),
                "url": str(a.url),
                "sentiment_label": (a.sentiment or {}).get("label", ""),
                "sentiment_score": (a.sentiment or {}).get("score", ""),
                "keywords": ", ".join(a.keywords or []),
            })

        if not rows:
            rows = [{"message": "No articles available"}]

        filename = f"articles_export_{limit}"
        if fmt.lower() == "csv":
            return _csv_response(rows, f"{filename}.csv")
        return _json_response(rows, f"{filename}.json")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))
