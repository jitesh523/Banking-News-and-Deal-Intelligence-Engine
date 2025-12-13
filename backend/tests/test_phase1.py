#!/usr/bin/env python3
"""
Test script for Phase 1: Data Collection & Storage
Run this to test the data collection pipeline.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.collector import DataCollector
from app.core.database import Database
from app.core.logging import setup_logging
from loguru import logger


async def test_data_collection():
    """Test the complete data collection pipeline."""
    
    # Setup logging
    setup_logging()
    logger.info("=" * 60)
    logger.info("Testing Phase 1: Data Collection & Storage")
    logger.info("=" * 60)
    
    try:
        # Connect to database
        logger.info("\n1. Connecting to MongoDB...")
        await Database.connect_db()
        logger.success("✓ Database connected")
        
        # Initialize collector
        logger.info("\n2. Initializing data collector...")
        collector = DataCollector()
        await collector.initialize()
        logger.success("✓ Data collector initialized")
        
        # Run collection
        logger.info("\n3. Collecting news articles...")
        logger.info("   This may take a minute...")
        result = await collector.collect_and_store(days_back=3)
        
        logger.info("\n" + "=" * 60)
        logger.info("COLLECTION RESULTS:")
        logger.info("=" * 60)
        logger.info(f"Articles collected: {result['collected']}")
        logger.info(f"Articles stored: {result['stored']}")
        logger.info(f"Duplicates skipped: {result['duplicates']}")
        logger.info(f"Errors: {result['errors']}")
        logger.info(f"Total in database: {result['total_in_db']}")
        logger.info("=" * 60)
        
        if result['stored'] > 0:
            logger.success("\n✓ Phase 1 test PASSED - Articles collected and stored successfully!")
        else:
            logger.warning("\n⚠ No new articles stored (may be duplicates or API issues)")
        
        # Close database
        await Database.close_db()
        
    except Exception as e:
        logger.error(f"\n✗ Phase 1 test FAILED: {e}")
        import traceback
        traceback.print_exc()
        await Database.close_db()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_data_collection())
