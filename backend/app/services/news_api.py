from newsapi import NewsApiClient
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger
from app.core.config import get_settings
from app.models.article import Article
import hashlib

settings = get_settings()


class NewsAPIService:
    """Service for collecting news from NewsAPI."""
    
    def __init__(self):
        """Initialize NewsAPI client."""
        self.client = NewsApiClient(api_key=settings.news_api_key)
        self.sources = [
            'bloomberg',
            'financial-times',
            'the-wall-street-journal',
            'reuters',
            'cnbc',
            'business-insider'
        ]
        self.keywords = [
            'banking',
            'merger',
            'acquisition',
            'M&A',
            'IPO',
            'deal',
            'investment banking',
            'financial services',
            'bank loan',
            'corporate finance'
        ]
    
    def generate_article_id(self, url: str, published_date: str) -> str:
        """Generate unique article ID from URL and date."""
        unique_string = f"{url}_{published_date}"
        return f"newsapi_{hashlib.md5(unique_string.encode()).hexdigest()}"
    
    def fetch_top_headlines(self, query: Optional[str] = None, days_back: int = 1) -> List[Dict[str, Any]]:
        """
        Fetch top headlines from NewsAPI.
        
        Args:
            query: Search query (default: banking-related keywords)
            days_back: Number of days to look back
            
        Returns:
            List of article dictionaries
        """
        try:
            articles = []
            
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)
            
            # Search for each keyword
            for keyword in self.keywords[:3]:  # Limit to avoid rate limits
                try:
                    response = self.client.get_everything(
                        q=query or keyword,
                        language='en',
                        sort_by='publishedAt',
                        from_param=from_date.strftime('%Y-%m-%d'),
                        to=to_date.strftime('%Y-%m-%d'),
                        page_size=10
                    )
                    
                    if response['status'] == 'ok':
                        articles.extend(response['articles'])
                        logger.info(f"Fetched {len(response['articles'])} articles for keyword: {keyword}")
                    
                except Exception as e:
                    logger.error(f"Error fetching articles for keyword '{keyword}': {e}")
                    continue
            
            logger.info(f"Total articles fetched: {len(articles)}")
            return articles
            
        except Exception as e:
            logger.error(f"Error in fetch_top_headlines: {e}")
            return []
    
    def parse_article(self, article_data: Dict[str, Any]) -> Optional[Article]:
        """
        Parse NewsAPI article data into Article model.
        
        Args:
            article_data: Raw article data from NewsAPI
            
        Returns:
            Article model instance or None if parsing fails
        """
        try:
            # Skip articles without content
            if not article_data.get('content') or article_data.get('content') == '[Removed]':
                return None
            
            # Parse published date
            published_date = datetime.fromisoformat(
                article_data['publishedAt'].replace('Z', '+00:00')
            )
            
            # Generate unique article ID
            article_id = self.generate_article_id(
                article_data['url'],
                article_data['publishedAt']
            )
            
            # Create Article instance
            article = Article(
                article_id=article_id,
                title=article_data.get('title', 'No Title'),
                content=article_data.get('content', ''),
                source=article_data.get('source', {}).get('name', 'Unknown'),
                author=article_data.get('author'),
                published_date=published_date,
                url=article_data['url'],
                raw_data=article_data
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return None
    
    def collect_news(self, query: Optional[str] = None, days_back: int = 1) -> List[Article]:
        """
        Collect and parse news articles.
        
        Args:
            query: Search query
            days_back: Number of days to look back
            
        Returns:
            List of Article instances
        """
        raw_articles = self.fetch_top_headlines(query, days_back)
        
        parsed_articles = []
        for raw_article in raw_articles:
            article = self.parse_article(raw_article)
            if article:
                parsed_articles.append(article)
        
        logger.info(f"Successfully parsed {len(parsed_articles)} articles")
        return parsed_articles
