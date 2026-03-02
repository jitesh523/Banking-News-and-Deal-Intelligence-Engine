"""
On-demand data collection API — trigger collection, view history, check status.
"""

import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from loguru import logger

from app.core.database import Database

router = APIRouter(prefix="/api/v1/collection", tags=["collection"])

# Simple in-memory state for the current run
_current_run = {
    "running": False,
    "started_at": None,
    "progress": None,
}


async def _run_collection(days_back: int):
    """Execute the data collection pipeline as a background task."""
    global _current_run
    _current_run["running"] = True
    _current_run["started_at"] = datetime.utcnow().isoformat()
    _current_run["progress"] = "Initializing collector…"

    db = Database.get_database()
    result = {"collected": 0, "stored": 0, "duplicates": 0, "errors": 0}

    try:
        from app.services.collector import DataCollector

        collector = DataCollector()
        await collector.initialize()

        _current_run["progress"] = "Collecting articles…"
        result = await collector.collect_and_store(days_back=days_back)

        # Persist run to history
        if db is not None:
            await db.collection_history.insert_one(
                {
                    "started_at": _current_run["started_at"],
                    "completed_at": datetime.utcnow().isoformat(),
                    "days_back": days_back,
                    "status": "success",
                    **result,
                }
            )
        logger.info(f"Collection run completed: {result}")

    except Exception as e:
        logger.error(f"Collection run failed: {e}")
        if db is not None:
            await db.collection_history.insert_one(
                {
                    "started_at": _current_run["started_at"],
                    "completed_at": datetime.utcnow().isoformat(),
                    "days_back": days_back,
                    "status": "failed",
                    "error": str(e),
                }
            )
    finally:
        _current_run["running"] = False
        _current_run["progress"] = None


@router.post("/trigger", summary="Trigger data collection")
async def trigger_collection(
    background_tasks: BackgroundTasks,
    days_back: int = Query(3, ge=1, le=30, description="Days of news to collect"),
):
    """
    Start an on-demand data collection run in the background.

    - **days_back**: How many days of history to fetch (1-30)

    Returns immediately; use ``/status`` to check progress.
    """
    if _current_run["running"]:
        raise HTTPException(status_code=409, detail="A collection run is already in progress")

    background_tasks.add_task(_run_collection, days_back)
    logger.info(f"Collection triggered for {days_back} days back")

    return {
        "message": "Collection started",
        "days_back": days_back,
        "check_status": "/api/v1/collection/status",
    }


@router.get("/status", summary="Check collection status")
async def collection_status():
    """Check whether a collection run is currently active."""
    return {
        "running": _current_run["running"],
        "started_at": _current_run["started_at"],
        "progress": _current_run["progress"],
    }


@router.get("/history", summary="View collection history")
async def collection_history(
    limit: int = Query(20, ge=1, le=100, description="Maximum records"),
):
    """
    View past collection runs with statistics.
    """
    try:
        db = Database.get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        cursor = db.collection_history.find().sort("started_at", -1).limit(limit)
        runs = []
        async for doc in cursor:
            doc.pop("_id", None)
            runs.append(doc)

        return {"total": len(runs), "runs": runs}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching collection history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
