"""
Company comparison API — side-by-side comparison of two companies.
"""

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.core.cache import cache

router = APIRouter(prefix="/api/v1/compare", tags=["compare"])

# Set in main.py on startup
_analytics_engine = None


def set_analytics_engine(engine):
    global _analytics_engine
    _analytics_engine = engine


@router.get("/companies", summary="Compare two companies")
async def compare_companies(
    company_a: str = Query(..., min_length=1, description="First company name"),
    company_b: str = Query(..., min_length=1, description="Second company name"),
):
    """
    Side-by-side comparison of two companies.

    Returns mentions, deal involvement, sentiment, relationships,
    and network centrality for each company.

    - **company_a**: First company name
    - **company_b**: Second company name
    """
    try:
        if not _analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics engine not initialized")

        cache_key = f"compare:{sorted([company_a.lower(), company_b.lower()])}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        mapper = _analytics_engine.relationship_mapper

        def _company_stats(name: str) -> dict:
            """Extract stats for a single company."""
            mentions = mapper.company_mentions.get(name, 0)
            deals = mapper.company_deals.get(name, [])
            sentiment = mapper.company_sentiments.get(name, [])

            avg_sentiment = 0.0
            if sentiment:
                avg_sentiment = round(sum(sentiment) / len(sentiment), 3)

            # Network info
            neighbors = []
            if mapper.graph.has_node(name):
                neighbors = list(mapper.graph.neighbors(name))

            return {
                "company": name,
                "mention_count": mentions,
                "deal_count": len(deals),
                "deal_types": list(set(deals)),
                "average_sentiment": avg_sentiment,
                "sentiment_data_points": len(sentiment),
                "connections": neighbors[:15],
                "connection_count": len(neighbors),
            }

        stats_a = _company_stats(company_a)
        stats_b = _company_stats(company_b)

        # Shared connections
        connections_a = set(stats_a["connections"])
        connections_b = set(stats_b["connections"])
        shared = list(connections_a & connections_b)

        # Direct relationship
        direct_relationship = mapper.graph.has_edge(company_a, company_b)

        result = {
            "company_a": stats_a,
            "company_b": stats_b,
            "comparison": {
                "shared_connections": shared,
                "shared_connection_count": len(shared),
                "direct_relationship": direct_relationship,
                "mention_leader": company_a if stats_a["mention_count"] >= stats_b["mention_count"] else company_b,
                "deal_leader": company_a if stats_a["deal_count"] >= stats_b["deal_count"] else company_b,
                "sentiment_leader": company_a if stats_a["average_sentiment"] >= stats_b["average_sentiment"] else company_b,
            },
        }

        cache.set(cache_key, result, ttl=120)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))
