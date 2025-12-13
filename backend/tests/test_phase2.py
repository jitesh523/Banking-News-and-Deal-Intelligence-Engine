#!/usr/bin/env python3
"""
Test script for Phase 2: NLP Processing Pipeline
Run this to test the NLP services.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.nlp_pipeline import NLPPipeline
from app.services.storage import StorageService
from app.core.database import Database
from app.core.logging import setup_logging
from loguru import logger


async def test_nlp_pipeline():
    """Test the complete NLP pipeline."""
    
    # Setup logging
    setup_logging()
    logger.info("=" * 60)
    logger.info("Testing NLP Processing Pipeline")
    logger.info("=" * 60)
    
    try:
        # Connect to database
        logger.info("\n1. Connecting to MongoDB...")
        await Database.connect_db()
        logger.success("✓ Database connected")
        
        # Initialize storage service
        logger.info("\n2. Fetching articles from database...")
        storage = StorageService()
        await storage.initialize()
        
        # Get some articles
        articles = await storage.get_recent_articles(limit=20)
        
        if not articles:
            logger.warning("No articles found in database. Please run Phase 1 data collection first.")
            await Database.close_db()
            return
        
        logger.success(f"✓ Fetched {len(articles)} articles")
        
        # Initialize NLP pipeline
        logger.info("\n3. Initializing NLP Pipeline...")
        logger.info("   This may take a minute to download models...")
        nlp_pipeline = NLPPipeline()
        logger.success("✓ NLP Pipeline initialized")
        
        # Process a single article (demo)
        logger.info("\n4. Processing sample article...")
        sample_article = articles[0]
        logger.info(f"   Title: {sample_article.title[:80]}...")
        
        result = nlp_pipeline.process_article(sample_article)
        
        logger.info("\n" + "=" * 60)
        logger.info("SAMPLE ARTICLE ANALYSIS:")
        logger.info("=" * 60)
        logger.info(f"\n📰 Title: {sample_article.title}")
        logger.info(f"📅 Published: {sample_article.published_date}")
        logger.info(f"📍 Source: {sample_article.source}")
        
        logger.info(f"\n🏢 Companies Detected: {len(result['entities']['companies'])}")
        for company in result['entities']['companies'][:5]:
            logger.info(f"   - {company}")
        
        logger.info(f"\n👤 People Detected: {len(result['entities']['people'])}")
        for person in result['entities']['people'][:5]:
            logger.info(f"   - {person}")
        
        logger.info(f"\n💰 Amounts Detected: {len(result['entities']['amounts'])}")
        for amount in result['entities']['amounts'][:5]:
            logger.info(f"   - {amount}")
        
        logger.info(f"\n😊 Sentiment: {result['sentiment']['label'].upper()}")
        logger.info(f"   Score: {result['sentiment']['score']:.3f}")
        logger.info(f"   Confidence: {result['sentiment']['confidence']:.3f}")
        
        logger.info(f"\n🔑 Top Keywords:")
        for kw in result['keywords'][:10]:
            logger.info(f"   - {kw['keyword']} (score: {kw['score']:.3f})")
        
        # Process batch with topic modeling
        logger.info("\n5. Processing batch with topic modeling...")
        logger.info(f"   Processing {len(articles)} articles...")
        
        batch_results = nlp_pipeline.process_articles_batch(
            articles,
            train_topics=True
        )
        
        logger.info(f"\n✓ Processed {len(batch_results)} articles")
        
        # Show topic summary
        logger.info("\n6. Topic Model Summary:")
        topics = nlp_pipeline.get_topic_summary()
        
        if topics:
            logger.info(f"\n📊 Discovered {len(topics)} topics:")
            for topic in topics[:5]:
                logger.info(f"\n   Topic {topic['topic_id']}: {topic['label']}")
                logger.info(f"   Top words: {', '.join([w['word'] for w in topic['words'][:5]])}")
        
        # Statistics
        logger.info("\n" + "=" * 60)
        logger.info("PROCESSING STATISTICS:")
        logger.info("=" * 60)
        
        total_companies = sum(len(r['entities']['companies']) for r in batch_results)
        total_people = sum(len(r['entities']['people']) for r in batch_results)
        total_amounts = sum(len(r['entities']['amounts']) for r in batch_results)
        
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for r in batch_results:
            sentiment_counts[r['sentiment']['label']] += 1
        
        logger.info(f"Total articles processed: {len(batch_results)}")
        logger.info(f"Total companies extracted: {total_companies}")
        logger.info(f"Total people extracted: {total_people}")
        logger.info(f"Total amounts extracted: {total_amounts}")
        logger.info(f"\nSentiment Distribution:")
        logger.info(f"  Positive: {sentiment_counts['positive']}")
        logger.info(f"  Negative: {sentiment_counts['negative']}")
        logger.info(f"  Neutral: {sentiment_counts['neutral']}")
        logger.info("=" * 60)
        
        logger.success("\n✓ NLP Pipeline test PASSED!")
        
        # Close database
        await Database.close_db()
        
    except Exception as e:
        logger.error(f"\n✗ NLP Pipeline test FAILED: {e}")
        import traceback
        traceback.print_exc()
        await Database.close_db()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_nlp_pipeline())
