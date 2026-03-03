"""
Article tags & categories API — user-defined tagging for articles.
"""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from loguru import logger

from app.core.database import Database

router = APIRouter(prefix="/api/v1/tags", tags=["tags"])


# ---------- Models ----------

class TagCreate(BaseModel):
    """Create a new tag."""
    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    color: str = Field("#1976d2", max_length=7, description="Hex color code")


class TagArticle(BaseModel):
    """Assign a tag to an article."""
    article_id: str = Field(..., description="Article to tag")
    tag_name: str = Field(..., description="Tag name to assign")


# ---------- Tag CRUD ----------

@router.post("/", summary="Create a tag", status_code=201)
async def create_tag(payload: TagCreate):
    """Create a new reusable tag."""
    try:
        db = Database.get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        existing = await db.tags.find_one({"name": payload.name.lower()})
        if existing:
            raise HTTPException(status_code=409, detail="Tag already exists")

        tag = {
            "name": payload.name.lower(),
            "color": payload.color,
            "created_at": datetime.utcnow(),
            "article_count": 0,
        }
        await db.tags.insert_one(tag)
        logger.info(f"Created tag: {payload.name}")
        return {"message": "Tag created", "tag": payload.name.lower()}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", summary="List all tags")
async def list_tags():
    """Get all available tags."""
    try:
        db = Database.get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        cursor = db.tags.find().sort("name", 1)
        tags = []
        async for doc in cursor:
            tags.append({
                "name": doc["name"],
                "color": doc.get("color", "#1976d2"),
                "article_count": doc.get("article_count", 0),
            })

        return {"total": len(tags), "tags": tags}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{tag_name}", summary="Delete a tag")
async def delete_tag(tag_name: str):
    """Delete a tag and remove it from all articles."""
    try:
        db = Database.get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        result = await db.tags.delete_one({"name": tag_name.lower()})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Tag not found")

        # Remove tag from all article_tags entries
        await db.article_tags.delete_many({"tag_name": tag_name.lower()})

        return {"message": f"Tag '{tag_name}' deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Article-Tag Assignments ----------

@router.post("/assign", summary="Tag an article")
async def assign_tag(payload: TagArticle):
    """Assign a tag to an article."""
    try:
        db = Database.get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        # Verify tag exists
        tag = await db.tags.find_one({"name": payload.tag_name.lower()})
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        # Check duplicate
        existing = await db.article_tags.find_one({
            "article_id": payload.article_id,
            "tag_name": payload.tag_name.lower(),
        })
        if existing:
            raise HTTPException(status_code=409, detail="Article already has this tag")

        await db.article_tags.insert_one({
            "article_id": payload.article_id,
            "tag_name": payload.tag_name.lower(),
            "assigned_at": datetime.utcnow(),
        })

        # Increment tag count
        await db.tags.update_one(
            {"name": payload.tag_name.lower()},
            {"$inc": {"article_count": 1}},
        )

        return {"message": "Tag assigned", "article_id": payload.article_id, "tag": payload.tag_name}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/article/{article_id}", summary="Get tags for an article")
async def get_article_tags(article_id: str):
    """Get all tags assigned to a specific article."""
    try:
        db = Database.get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        cursor = db.article_tags.find({"article_id": article_id})
        tags = []
        async for doc in cursor:
            tags.append(doc["tag_name"])

        return {"article_id": article_id, "tags": tags}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting article tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))
