"""
Market Summary Service — generates daily and weekly intelligence digests.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from loguru import logger


class MarketSummaryService:
    """
    Builds market intelligence summaries from the analytics engine.

    Provides daily and weekly digests that highlight:
    - Top deals by value and volume
    - Biggest sentiment movers
    - Most-mentioned companies
    - Key aggregate metrics
    """

    def __init__(self, analytics_engine):
        self.analytics_engine = analytics_engine

    def generate_daily_summary(self) -> Dict[str, Any]:
        """
        Generate today's market intelligence summary.

        Returns:
            Dictionary with daily market metrics and highlights.
        """
        logger.info("Generating daily market summary")

        # Deals
        deal_insights = self.analytics_engine.get_deal_insights(days_back=1)
        deal_insights_7d = self.analytics_engine.get_deal_insights(days_back=7)

        # Companies
        company_insights = self.analytics_engine.get_company_insights(top_n=10)

        # Sentiment
        sentiment_insights = self.analytics_engine.get_sentiment_insights(days_back=1)
        sentiment_7d = self.analytics_engine.get_sentiment_insights(days_back=7)

        # Alerts
        alerts = self.analytics_engine.get_alerts(limit=5)

        return {
            "report_type": "daily",
            "generated_at": datetime.utcnow().isoformat(),
            "period": "Last 24 hours",
            "highlights": {
                "deals_today": deal_insights.get("volume_trend", {}).get("total_deals", 0),
                "deals_7d": deal_insights_7d.get("volume_trend", {}).get("total_deals", 0),
                "avg_sentiment_today": sentiment_insights.get("overall_trend", {}).get(
                    "average_sentiment", 0
                ),
                "avg_sentiment_7d": sentiment_7d.get("overall_trend", {}).get(
                    "average_sentiment", 0
                ),
            },
            "top_companies": company_insights.get("top_companies_by_mentions", [])[:5],
            "deal_type_breakdown": deal_insights.get("type_distribution", {}),
            "recent_alerts": alerts[:5],
            "anomalies": deal_insights_7d.get("anomalies", [])[:3],
            "relationship_network": company_insights.get("relationship_summary", {}),
        }

    def generate_weekly_digest(self) -> Dict[str, Any]:
        """
        Generate a weekly market intelligence digest.

        Returns:
            Dictionary with aggregated weekly metrics and trends.
        """
        logger.info("Generating weekly market digest")

        deal_insights = self.analytics_engine.get_deal_insights(days_back=7)
        deal_insights_30d = self.analytics_engine.get_deal_insights(days_back=30)
        company_insights = self.analytics_engine.get_company_insights(top_n=20)
        sentiment = self.analytics_engine.get_sentiment_insights(days_back=7)
        alerts = self.analytics_engine.get_alerts(limit=20)

        # Categorise alerts by priority
        alert_breakdown = {}
        for alert in alerts:
            p = alert.get("priority", "UNKNOWN")
            alert_breakdown[p] = alert_breakdown.get(p, 0) + 1

        return {
            "report_type": "weekly",
            "generated_at": datetime.utcnow().isoformat(),
            "period": "Last 7 days",
            "overview": {
                "total_deals_this_week": deal_insights.get("volume_trend", {}).get(
                    "total_deals", 0
                ),
                "total_deals_last_30d": deal_insights_30d.get("volume_trend", {}).get(
                    "total_deals", 0
                ),
                "deal_trend_direction": deal_insights.get("volume_trend", {}).get(
                    "trend_direction", "stable"
                ),
                "avg_daily_deals": deal_insights.get("volume_trend", {}).get(
                    "average_daily", 0
                ),
                "sentiment_avg": sentiment.get("overall_trend", {}).get(
                    "average_sentiment", 0
                ),
                "sentiment_direction": sentiment.get("overall_trend", {}).get(
                    "trend_direction", "stable"
                ),
                "sentiment_volatility": sentiment.get("overall_trend", {}).get(
                    "sentiment_volatility", 0
                ),
            },
            "top_companies_by_mentions": company_insights.get(
                "top_companies_by_mentions", []
            )[:10],
            "top_companies_by_deals": company_insights.get(
                "top_companies_by_deals", []
            )[:10],
            "deal_type_breakdown": deal_insights.get("type_distribution", {}),
            "value_trend": deal_insights.get("value_trend", {}),
            "anomalies_detected": deal_insights.get("anomalies", []),
            "alert_summary": {
                "total": len(alerts),
                "by_priority": alert_breakdown,
            },
            "network_stats": company_insights.get("relationship_summary", {}),
        }
