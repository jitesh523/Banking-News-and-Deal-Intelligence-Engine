import asyncio
from typing import List
from loguru import logger
from app.services.news_api import NewsAPIService
from app.services.web_scraper import WebScraperService
from app.services.storage import StorageService
from app.models.article import Article


class DataCollector:
    """Orchestrates data collection from multiple sources."""
    
    def __init__(self):
        """Initialize data collector with all services."""
        self.news_api = NewsAPIService()
        self.web_scraper = WebScraperService()
        self.storage = StorageService()
    
    async def initialize(self):
        """Initialize async services."""
        await self.storage.initialize()
        logger.info("Data collector initialized")
    
    async def collect_and_store(self, days_back: int = 1) -> dict:
        """
        Collect news from all sources and store in database.
        
        Args:
            days_back: Number of days to look back for news
            
        Returns:
            Dictionary with collection statistics
        """
        logger.info(f"Starting data collection (looking back {days_back} days)")
        
        all_articles: List[Article] = []
        
        # Collect from NewsAPI
        try:
            logger.info("Collecting from NewsAPI...")
            news_api_articles = self.news_api.collect_news(days_back=days_back)
            all_articles.extend(news_api_articles)
            logger.info(f"Collected {len(news_api_articles)} articles from NewsAPI")
        except Exception as e:
            logger.error(f"NewsAPI collection failed: {e}")
        
        # Collect from web scraping
        try:
            logger.info("Collecting from web scraping...")
            scraped_articles = self.web_scraper.collect_from_all_sources()
            all_articles.extend(scraped_articles)
            logger.info(f"Collected {len(scraped_articles)} articles from web scraping")
        except Exception as e:
            logger.error(f"Web scraping failed: {e}")
        
        # Store all articles
        logger.info(f"Storing {len(all_articles)} total articles...")
        storage_stats = await self.storage.store_articles_bulk(all_articles)
        
        # Get total count
        total_count = await self.storage.get_article_count()
        
        result = {
            'collected': len(all_articles),
            'stored': storage_stats['stored'],
            'duplicates': storage_stats['duplicates'],
            'errors': storage_stats['errors'],
            'total_in_db': total_count
        }
        
        logger.info(f"Collection complete: {result}")
        return result
    
    async def run_scheduled_collection(self):
        """Run scheduled data collection (called by scheduler)."""
        try:
            await self.initialize()
            result = await self.collect_and_store(days_back=1)
            logger.info(f"Scheduled collection completed: {result}")
        except Exception as e:
            logger.error(f"Scheduled collection failed: {e}")


async def run_collection_once():
    """Helper function to run collection once."""
    collector = DataCollector()
    await collector.initialize()
    return await collector.collect_and_store(days_back=7)  # Collect last 7 days initially


if __name__ == "__main__":
    # Run collection once for testing
    asyncio.run(run_collection_once())
