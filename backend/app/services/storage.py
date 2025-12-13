from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger
from app.core.database import Database
from app.models.article import Article
from pymongo.errors import DuplicateKeyError


class StorageService:
    """Service for storing and retrieving articles from MongoDB."""
    
    def __init__(self):
        """Initialize storage service."""
        self.db = None
    
    async def initialize(self):
        """Initialize database connection."""
        self.db = Database.get_database()
    
    async def store_article(self, article: Article) -> bool:
        """
        Store a single article in the database.
        
        Args:
            article: Article instance to store
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            article_dict = article.model_dump(by_alias=True, exclude={'id'})
            
            # Try to insert
            result = await self.db.articles.insert_one(article_dict)
            
            if result.inserted_id:
                logger.debug(f"Stored article: {article.article_id}")
                return True
            
            return False
            
        except DuplicateKeyError:
            logger.debug(f"Article already exists: {article.article_id}")
            return False
        except Exception as e:
            logger.error(f"Error storing article {article.article_id}: {e}")
            return False
    
    async def store_articles_bulk(self, articles: List[Article]) -> Dict[str, int]:
        """
        Store multiple articles in bulk.
        
        Args:
            articles: List of Article instances
            
        Returns:
            Dictionary with counts of stored and duplicate articles
        """
        stored_count = 0
        duplicate_count = 0
        error_count = 0
        
        for article in articles:
            success = await self.store_article(article)
            if success:
                stored_count += 1
            elif success is False:
                duplicate_count += 1
            else:
                error_count += 1
        
        logger.info(
            f"Bulk storage complete: {stored_count} stored, "
            f"{duplicate_count} duplicates, {error_count} errors"
        )
        
        return {
            'stored': stored_count,
            'duplicates': duplicate_count,
            'errors': error_count,
            'total': len(articles)
        }
    
    async def get_article_by_id(self, article_id: str) -> Optional[Article]:
        """
        Retrieve article by ID.
        
        Args:
            article_id: Unique article identifier
            
        Returns:
            Article instance or None
        """
        try:
            article_data = await self.db.articles.find_one({'article_id': article_id})
            
            if article_data:
                return Article(**article_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving article {article_id}: {e}")
            return None
    
    async def get_recent_articles(self, limit: int = 50, skip: int = 0) -> List[Article]:
        """
        Get recent articles.
        
        Args:
            limit: Maximum number of articles to return
            skip: Number of articles to skip
            
        Returns:
            List of Article instances
        """
        try:
            cursor = self.db.articles.find().sort('published_date', -1).skip(skip).limit(limit)
            articles = []
            
            async for article_data in cursor:
                articles.append(Article(**article_data))
            
            return articles
            
        except Exception as e:
            logger.error(f"Error retrieving recent articles: {e}")
            return []
    
    async def search_articles(
        self,
        query: Optional[str] = None,
        source: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Article]:
        """
        Search articles with filters.
        
        Args:
            query: Text search query
            source: Filter by source
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum results
            
        Returns:
            List of Article instances
        """
        try:
            filter_dict = {}
            
            if query:
                filter_dict['$text'] = {'$search': query}
            
            if source:
                filter_dict['source'] = source
            
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter['$gte'] = start_date
                if end_date:
                    date_filter['$lte'] = end_date
                filter_dict['published_date'] = date_filter
            
            cursor = self.db.articles.find(filter_dict).sort('published_date', -1).limit(limit)
            articles = []
            
            async for article_data in cursor:
                articles.append(Article(**article_data))
            
            logger.info(f"Search returned {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return []
    
    async def get_article_count(self) -> int:
        """
        Get total number of articles in database.
        
        Returns:
            Article count
        """
        try:
            count = await self.db.articles.count_documents({})
            return count
        except Exception as e:
            logger.error(f"Error counting articles: {e}")
            return 0
