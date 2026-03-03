"""
Text analysis API — on-demand NLP analysis of any text snippet.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from loguru import logger

from app.core.auth import require_api_key
from app.core.cache import cache

router = APIRouter(prefix="/api/v1/analyze", tags=["analyze"])

# Set in main.py on startup
_nlp_pipeline = None


def set_nlp_pipeline(pipeline):
    """Set the NLPPipeline instance."""
    global _nlp_pipeline
    _nlp_pipeline = pipeline


class TextAnalysisRequest(BaseModel):
    """Request body for text analysis."""
    text: str = Field(..., min_length=10, max_length=10000, description="Text to analyze")
    include_keywords: bool = Field(True, description="Include keyword extraction")
    include_entities: bool = Field(True, description="Include named entity recognition")
    include_sentiment: bool = Field(True, description="Include sentiment analysis")


@router.post("/", summary="Analyze a text snippet")
async def analyze_text(payload: TextAnalysisRequest):
    """
    Run NLP analysis on any text snippet on-demand.

    Returns entities, sentiment, and keywords extracted from the provided text.
    Useful for testing the NLP pipeline or analyzing custom content.

    - **text**: Between 10 and 10,000 characters
    - **include_keywords**: Toggle keyword extraction
    - **include_entities**: Toggle NER
    - **include_sentiment**: Toggle sentiment analysis
    """
    try:
        if not _nlp_pipeline:
            raise HTTPException(status_code=503, detail="NLP pipeline not initialized")

        # Check cache
        import hashlib
        cache_key = f"analyze:{hashlib.md5(payload.text[:200].encode()).hexdigest()}"
        cached = cache.get(cache_key)
        if cached is not None:
            cached["from_cache"] = True
            return cached

        results = {"text_length": len(payload.text)}

        full_analysis = _nlp_pipeline.analyze_text_snippet(payload.text)

        if payload.include_entities:
            results["entities"] = full_analysis.get("entities", {})

        if payload.include_sentiment:
            results["sentiment"] = full_analysis.get("sentiment", {})

        if payload.include_keywords:
            results["keywords"] = full_analysis.get("keywords", [])

        results["from_cache"] = False

        # Cache for 5 minutes
        cache.set(cache_key, results, ttl=300)

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats", summary="Get cache statistics")
async def cache_stats():
    """Return current cache statistics."""
    return cache.stats()


@router.post("/cache/clear", summary="Clear analysis cache", dependencies=[Depends(require_api_key)])
async def clear_cache():
    """Clear the analysis cache. Requires API key."""
    count = cache.clear()
    return {"message": f"Cache cleared: {count} entries removed"}
