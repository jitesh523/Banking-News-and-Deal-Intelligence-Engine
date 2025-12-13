import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional, Dict, Any
from loguru import logger
from app.models.article import Article
import hashlib
import time


class WebScraperService:
    """Service for scraping financial news from various sources."""
    
    def __init__(self):
        """Initialize web scraper."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def generate_article_id(self, url: str) -> str:
        """Generate unique article ID from URL."""
        return f"scraped_{hashlib.md5(url.encode()).hexdigest()}"
    
    def scrape_reuters(self, topic: str = 'banking') -> List[Article]:
        """
        Scrape articles from Reuters.
        
        Args:
            topic: Topic to search for
            
        Returns:
            List of Article instances
        """
        articles = []
        
        try:
            # Reuters finance section
            url = f"https://www.reuters.com/finance"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find article containers (this is a simplified example)
                # In production, you'd need to inspect the actual HTML structure
                article_links = soup.find_all('a', {'data-testid': 'Heading'}, limit=5)
                
                for link in article_links:
                    try:
                        article_url = link.get('href')
                        if article_url and not article_url.startswith('http'):
                            article_url = f"https://www.reuters.com{article_url}"
                        
                        title = link.get_text(strip=True)
                        
                        # Create basic article (content would require additional request)
                        article = Article(
                            article_id=self.generate_article_id(article_url),
                            title=title,
                            content=f"Article from Reuters: {title}",  # Placeholder
                            source="Reuters",
                            author=None,
                            published_date=datetime.utcnow(),
                            url=article_url,
                            raw_data={'scraped': True}
                        )
                        
                        articles.append(article)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing Reuters article: {e}")
                        continue
                
                logger.info(f"Scraped {len(articles)} articles from Reuters")
                
        except Exception as e:
            logger.error(f"Error scraping Reuters: {e}")
        
        return articles
    
    def scrape_bloomberg(self) -> List[Article]:
        """
        Scrape articles from Bloomberg.
        Note: Bloomberg has strong anti-scraping measures.
        This is a placeholder for demonstration.
        
        Returns:
            List of Article instances
        """
        articles = []
        
        try:
            # Bloomberg requires authentication and has anti-scraping
            # This is a simplified placeholder
            logger.info("Bloomberg scraping requires authentication - skipping")
            
        except Exception as e:
            logger.error(f"Error scraping Bloomberg: {e}")
        
        return articles
    
    def scrape_generic_rss(self, rss_url: str, source_name: str) -> List[Article]:
        """
        Scrape articles from RSS feed.
        
        Args:
            rss_url: RSS feed URL
            source_name: Name of the source
            
        Returns:
            List of Article instances
        """
        articles = []
        
        try:
            response = self.session.get(rss_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item', limit=10)
                
                for item in items:
                    try:
                        title = item.find('title').get_text(strip=True)
                        link = item.find('link').get_text(strip=True)
                        description = item.find('description')
                        pub_date = item.find('pubDate')
                        
                        # Parse date
                        published_date = datetime.utcnow()
                        if pub_date:
                            try:
                                from dateutil import parser
                                published_date = parser.parse(pub_date.get_text(strip=True))
                            except:
                                pass
                        
                        article = Article(
                            article_id=self.generate_article_id(link),
                            title=title,
                            content=description.get_text(strip=True) if description else title,
                            source=source_name,
                            author=None,
                            published_date=published_date,
                            url=link,
                            raw_data={'rss': True}
                        )
                        
                        articles.append(article)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing RSS item: {e}")
                        continue
                
                logger.info(f"Scraped {len(articles)} articles from {source_name} RSS")
                
        except Exception as e:
            logger.error(f"Error scraping RSS feed {rss_url}: {e}")
        
        return articles
    
    def collect_from_all_sources(self) -> List[Article]:
        """
        Collect articles from all configured sources.
        
        Returns:
            List of Article instances
        """
        all_articles = []
        
        # Scrape Reuters
        all_articles.extend(self.scrape_reuters())
        time.sleep(2)  # Be respectful with rate limiting
        
        # Add more sources as needed
        # all_articles.extend(self.scrape_bloomberg())
        
        # Example RSS feeds
        rss_feeds = [
            ('https://www.ft.com/rss/home', 'Financial Times'),
            ('https://feeds.reuters.com/reuters/businessNews', 'Reuters Business'),
        ]
        
        for rss_url, source_name in rss_feeds:
            try:
                all_articles.extend(self.scrape_generic_rss(rss_url, source_name))
                time.sleep(2)  # Rate limiting
            except Exception as e:
                logger.error(f"Error with {source_name}: {e}")
        
        logger.info(f"Total articles collected from web scraping: {len(all_articles)}")
        return all_articles
