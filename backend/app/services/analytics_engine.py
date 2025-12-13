from typing import List, Dict, Any
from datetime import datetime
from loguru import logger

from app.services.deal_detector import DealDetector
from app.services.relationship_mapper import CompanyRelationshipMapper
from app.services.trend_analyzer import TrendAnalyzer
from app.services.alert_system import AlertSystem, Alert
from app.models.article import Article


class AnalyticsEngine:
    """Orchestrates all analytics services for deal intelligence."""
    
    def __init__(self):
        """Initialize analytics engine with all services."""
        logger.info("Initializing Analytics Engine...")
        
        self.deal_detector = DealDetector()
        self.relationship_mapper = CompanyRelationshipMapper()
        self.trend_analyzer = TrendAnalyzer()
        self.alert_system = AlertSystem()
        
        logger.info("Analytics Engine initialized successfully")
    
    def analyze_article(
        self,
        article: Article,
        nlp_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform analytics on a single article.
        
        Args:
            article: Article to analyze
            nlp_results: NLP processing results
            
        Returns:
            Analytics results
        """
        logger.info(f"Analyzing article: {article.article_id}")
        
        results = {
            'article_id': article.article_id,
            'deals_detected': [],
            'alerts_generated': [],
            'relationships_added': 0
        }
        
        try:
            # 1. Detect deals
            full_text = f"{article.title}. {article.content}"
            deals = self.deal_detector.detect_deals(full_text, nlp_results['entities'])
            results['deals_detected'] = deals
            
            # 2. Process each detected deal
            for deal_info in deals:
                # Add to trend analyzer
                self.trend_analyzer.add_deal_event(
                    date=article.published_date,
                    deal_type=deal_info['deal_type'],
                    deal_amount=deal_info.get('deal_amount'),
                    companies=deal_info.get('companies_involved', [])
                )
                
                # Check for alerts
                alert = self.alert_system.check_mega_deal(
                    deal_amount=deal_info.get('deal_amount'),
                    deal_type=deal_info['deal_type'],
                    companies=deal_info.get('companies_involved', [])
                )
                
                if alert:
                    self.alert_system.add_alert(alert)
                    results['alerts_generated'].append(alert.to_dict())
                
                # Add company relationships
                companies = deal_info.get('companies_involved', [])
                if len(companies) >= 2:
                    for i in range(len(companies)):
                        for j in range(i + 1, len(companies)):
                            self.relationship_mapper.add_relationship(
                                companies[i],
                                companies[j],
                                deal_info['deal_type'],
                                deal_id=f"{article.article_id}_{deal_info['deal_type']}"
                            )
                            results['relationships_added'] += 1
            
            # 3. Track company mentions
            for company in nlp_results['entities'].get('companies', []):
                self.relationship_mapper.add_company_mention(company, article.article_id)
            
            # 4. Track sentiment
            self.trend_analyzer.add_sentiment_event(
                date=article.published_date,
                sentiment_score=nlp_results['sentiment']['score']
            )
            
            # Track entity-level sentiment
            if 'entity_sentiments' in nlp_results:
                for entity_sent in nlp_results['entity_sentiments']:
                    self.trend_analyzer.add_sentiment_event(
                        date=article.published_date,
                        sentiment_score=entity_sent['score'],
                        company=entity_sent['entity']
                    )
            
            logger.success(f"Article analyzed: {len(deals)} deals detected, {results['relationships_added']} relationships added")
            
        except Exception as e:
            logger.error(f"Error analyzing article {article.article_id}: {e}")
            results['error'] = str(e)
        
        return results
    
    def analyze_articles_batch(
        self,
        articles: List[Article],
        nlp_results_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze multiple articles in batch.
        
        Args:
            articles: List of articles
            nlp_results_list: List of NLP results
            
        Returns:
            Batch analytics results
        """
        logger.info(f"Analyzing batch of {len(articles)} articles...")
        
        total_deals = 0
        total_alerts = 0
        total_relationships = 0
        
        for article, nlp_results in zip(articles, nlp_results_list):
            result = self.analyze_article(article, nlp_results)
            total_deals += len(result['deals_detected'])
            total_alerts += len(result['alerts_generated'])
            total_relationships += result['relationships_added']
        
        summary = {
            'articles_analyzed': len(articles),
            'total_deals_detected': total_deals,
            'total_alerts_generated': total_alerts,
            'total_relationships_added': total_relationships
        }
        
        logger.info(f"Batch analysis complete: {summary}")
        
        return summary
    
    def get_deal_insights(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get insights about deals.
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Deal insights
        """
        from datetime import timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        return {
            'volume_trend': self.trend_analyzer.get_deal_volume_trend(start_date, end_date),
            'value_trend': self.trend_analyzer.get_deal_value_trend(start_date, end_date),
            'type_distribution': self.trend_analyzer.get_deal_type_distribution(start_date, end_date),
            'anomalies': self.trend_analyzer.detect_anomalies(metric='volume')
        }
    
    def get_company_insights(
        self,
        company: Optional[str] = None,
        top_n: int = 20
    ) -> Dict[str, Any]:
        """
        Get insights about companies.
        
        Args:
            company: Specific company (optional)
            top_n: Number of top companies
            
        Returns:
            Company insights
        """
        if company:
            return {
                'company': company,
                'network': self.relationship_mapper.get_company_network(company),
                'sentiment_trend': self.trend_analyzer.get_sentiment_trend(company=company)
            }
        else:
            return {
                'top_companies_by_mentions': self.relationship_mapper.get_top_companies(top_n, 'mentions'),
                'top_companies_by_deals': self.relationship_mapper.get_top_companies(top_n, 'deals'),
                'top_companies_by_connections': self.relationship_mapper.get_top_companies(top_n, 'connections'),
                'relationship_summary': self.relationship_mapper.get_relationship_summary()
            }
    
    def get_sentiment_insights(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get sentiment insights.
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Sentiment insights
        """
        from datetime import timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        return {
            'overall_trend': self.trend_analyzer.get_sentiment_trend(start_date, end_date),
            'summary': self.trend_analyzer.get_summary_statistics()
        }
    
    def get_alerts(
        self,
        priority: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get alerts with optional filtering.
        
        Args:
            priority: Filter by priority
            limit: Maximum alerts
            
        Returns:
            List of alerts
        """
        from app.services.alert_system import AlertPriority
        
        priority_enum = None
        if priority:
            priority_enum = AlertPriority[priority.upper()]
        
        return self.alert_system.get_alerts(priority=priority_enum, limit=limit)
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get summary for dashboard display.
        
        Returns:
            Dashboard summary data
        """
        return {
            'deal_summary': self.trend_analyzer.get_summary_statistics(),
            'relationship_summary': self.relationship_mapper.get_relationship_summary(),
            'alert_summary': self.alert_system.get_alert_summary(),
            'top_companies': self.relationship_mapper.get_top_companies(10, 'mentions')
        }
