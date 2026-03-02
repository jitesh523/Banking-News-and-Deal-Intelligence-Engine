"""
Article bookmarks API — save, list, and remove favourite articles.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from loguru import logger

from app.core.database import Database

router = APIRouter(prefix="/api/v1/bookmarks", tags=["bookmarks"])


# ---------- Request / Response models ----------

class BookmarkCreate(BaseModel):
    """Request body for creating a bookmark."""
    article_id: str = Field(..., description="ID of the article to bookmark")
    notes: Optional[str] = Field(None, max_length=500, description="Optional user notes")


class BookmarkResponse(BaseModel):
    """Single bookmark entry."""
    article_id: str
    notes: Optional[str] = None
    created_at: datetime


# ---------- Endpoints ----------

@router.post("/", summary="Bookmark an article", status_code=201)
async def create_bookmark(payload: BookmarkCreate):
    """
    Bookmark an article for later reference.

    - **article_id**: The unique article identifier
    - **notes**: Optional personal notes (max 500 chars)
    """
    try:
        db = Database.get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        # Check for duplicate
        existing = await db.bookmarks.find_one({"article_id": payload.article_id})
        if existing:
            raise HTTPException(status_code=409, detail="Article is already bookmarked")

        bookmark = {
            "article_id": payload.article_id,
            "notes": payload.notes,
            "created_at": datetime.utcnow(),
        }
        await db.bookmarks.insert_one(bookmark)
        logger.info(f"Bookmarked article: {payload.article_id}")

        return {"message": "Article bookmarked", "article_id": payload.article_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating bookmark: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", summary="List all bookmarks")
async def list_bookmarks(
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
):
    """
    Retrieve all bookmarked articles, newest first.
    """
    try:
        db = Database.get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        cursor = db.bookmarks.find().sort("created_at", -1).skip(skip).limit(limit)
        bookmarks = []
        async for doc in cursor:
            bookmarks.append(
                {
                    "article_id": doc["article_id"],
                    "notes": doc.get("notes"),
                    "created_at": doc["created_at"].isoformat(),
                }
            )

        total = await db.bookmarks.count_documents({})

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "bookmarks": bookmarks,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing bookmarks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{article_id}", summary="Remove a bookmark")
async def delete_bookmark(article_id: str):
    """
    Remove a previously bookmarked article.

    - **article_id**: The article to un-bookmark
    """
    try:
        db = Database.get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        result = await db.bookmarks.delete_one({"article_id": article_id})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Bookmark not found")

        logger.info(f"Removed bookmark: {article_id}")
        return {"message": "Bookmark removed", "article_id": article_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting bookmark: {e}")
        raise HTTPException(status_code=500, detail=str(e))
