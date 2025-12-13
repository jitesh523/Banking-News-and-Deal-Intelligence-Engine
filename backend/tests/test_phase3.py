#!/usr/bin/env python3
"""
Test script for Phase 3: Deal Intelligence & Analytics
Run this to test the analytics services.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.nlp_pipeline import NLPPipeline
from app.services.analytics_engine import AnalyticsEngine
from app.services.storage import StorageService
from app.core.database import Database
from app.core.logging import setup_logging
from loguru import logger


async def test_analytics():
    """Test the complete analytics pipeline."""
    
    # Setup logging
    setup_logging()
    logger.info("=" * 60)
    logger.info("Testing Deal Intelligence & Analytics")
    logger.info("=" * 60)
    
    try:
        # Connect to database
        logger.info("\n1. Connecting to MongoDB...")
        await Database.connect_db()
        logger.success("✓ Database connected")
        
        # Initialize services
        logger.info("\n2. Fetching articles from database...")
        storage = StorageService()
        await storage.initialize()
        
        articles = await storage.get_recent_articles(limit=30)
        
        if not articles:
            logger.warning("No articles found. Please run Phase 1 and 2 first.")
            await Database.close_db()
            return
        
        logger.success(f"✓ Fetched {len(articles)} articles")
        
        # Initialize NLP pipeline
        logger.info("\n3. Initializing NLP Pipeline...")
        nlp_pipeline = NLPPipeline()
        logger.success("✓ NLP Pipeline initialized")
        
        # Initialize Analytics Engine
        logger.info("\n4. Initializing Analytics Engine...")
        analytics_engine = AnalyticsEngine()
        logger.success("✓ Analytics Engine initialized")
        
        # Process articles with NLP
        logger.info("\n5. Processing articles with NLP...")
        nlp_results = nlp_pipeline.process_articles_batch(articles, train_topics=False)
        logger.success(f"✓ Processed {len(nlp_results)} articles")
        
        # Analyze with analytics engine
        logger.info("\n6. Running analytics on articles...")
        analytics_summary = analytics_engine.analyze_articles_batch(articles, nlp_results)
        
        logger.info("\n" + "=" * 60)
        logger.info("ANALYTICS SUMMARY:")
        logger.info("=" * 60)
        logger.info(f"Articles analyzed: {analytics_summary['articles_analyzed']}")
        logger.info(f"Deals detected: {analytics_summary['total_deals_detected']}")
        logger.info(f"Alerts generated: {analytics_summary['total_alerts_generated']}")
        logger.info(f"Relationships mapped: {analytics_summary['total_relationships_added']}")
        
        # Get deal insights
        logger.info("\n7. Generating deal insights...")
        deal_insights = analytics_engine.get_deal_insights(days_back=30)
        
        logger.info("\n📊 Deal Insights:")
        logger.info(f"Total deals: {deal_insights['volume_trend']['total_deals']}")
        logger.info(f"Average daily deals: {deal_insights['volume_trend']['average_daily']:.1f}")
        logger.info(f"Trend direction: {deal_insights['volume_trend']['trend_direction']}")
        
        if deal_insights['type_distribution']:
            logger.info(f"\nDeal Type Distribution:")
            for deal_type, count in deal_insights['type_distribution'].items():
                logger.info(f"  {deal_type}: {count}")
        
        if deal_insights['anomalies']:
            logger.info(f"\n⚠️  Anomalies detected: {len(deal_insights['anomalies'])}")
            for anomaly in deal_insights['anomalies'][:3]:
                logger.info(f"  {anomaly['date']}: {anomaly['type']} (z-score: {anomaly['z_score']:.2f})")
        
        # Get company insights
        logger.info("\n8. Generating company insights...")
        company_insights = analytics_engine.get_company_insights()
        
        logger.info("\n🏢 Top Companies by Mentions:")
        for i, company in enumerate(company_insights['top_companies_by_mentions'][:10], 1):
            logger.info(f"  {i}. {company['company']} ({company['mention_count']} mentions, {company['deal_count']} deals)")
        
        rel_summary = company_insights['relationship_summary']
        logger.info(f"\n🔗 Relationship Network:")
        logger.info(f"  Total companies: {rel_summary['total_companies']}")
        logger.info(f"  Total relationships: {rel_summary['total_relationships']}")
        logger.info(f"  Average connections: {rel_summary['average_connections']:.1f}")
        if rel_summary['most_connected_company']:
            logger.info(f"  Most connected: {rel_summary['most_connected_company']}")
        
        # Get sentiment insights
        logger.info("\n9. Generating sentiment insights...")
        sentiment_insights = analytics_engine.get_sentiment_insights(days_back=30)
        
        logger.info(f"\n😊 Sentiment Analysis:")
        logger.info(f"  Average sentiment: {sentiment_insights['overall_trend']['average_sentiment']:.3f}")
        logger.info(f"  Trend direction: {sentiment_insights['overall_trend']['trend_direction']}")
        logger.info(f"  Volatility: {sentiment_insights['overall_trend']['sentiment_volatility']:.3f}")
        
        sent_dist = sentiment_insights['summary']['sentiment_distribution']
        logger.info(f"\n  Distribution:")
        logger.info(f"    Positive: {sent_dist['positive']}")
        logger.info(f"    Neutral: {sent_dist['neutral']}")
        logger.info(f"    Negative: {sent_dist['negative']}")
        
        # Get alerts
        logger.info("\n10. Checking alerts...")
        alerts = analytics_engine.get_alerts(limit=10)
        
        if alerts:
            logger.info(f"\n🚨 Alerts Generated ({len(alerts)}):")
            for alert in alerts[:5]:
                logger.info(f"  [{alert['priority']}] {alert['title']}")
                logger.info(f"    {alert['description']}")
        else:
            logger.info("\n  No alerts generated")
        
        # Dashboard summary
        logger.info("\n11. Generating dashboard summary...")
        dashboard = analytics_engine.get_dashboard_summary()
        
        logger.info("\n" + "=" * 60)
        logger.info("DASHBOARD SUMMARY:")
        logger.info("=" * 60)
        logger.info(f"Total deals tracked: {dashboard['deal_summary']['total_deals']}")
        logger.info(f"Companies in network: {dashboard['relationship_summary']['total_companies']}")
        logger.info(f"Total alerts: {dashboard['alert_summary']['total_alerts']}")
        logger.info("=" * 60)
        
        logger.success("\n✓ Analytics test PASSED!")
        
        # Close database
        await Database.close_db()
        
    except Exception as e:
        logger.error(f"\n✗ Analytics test FAILED: {e}")
        import traceback
        traceback.print_exc()
        await Database.close_db()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_analytics())
