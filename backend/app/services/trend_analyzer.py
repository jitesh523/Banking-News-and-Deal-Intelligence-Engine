from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from loguru import logger
import numpy as np


class TrendAnalyzer:
    """Service for analyzing trends in deals and sentiment."""
    
    def __init__(self):
        """Initialize trend analyzer."""
        self.deal_timeline = defaultdict(list)
        self.sentiment_timeline = defaultdict(list)
        self.company_timeline = defaultdict(lambda: defaultdict(list))
    
    def add_deal_event(
        self,
        date: datetime,
        deal_type: str,
        deal_amount: Optional[float] = None,
        companies: Optional[List[str]] = None
    ) -> None:
        """
        Add a deal event to the timeline.
        
        Args:
            date: Deal date
            deal_type: Type of deal
            deal_amount: Deal amount
            companies: Companies involved
        """
        date_key = date.strftime('%Y-%m-%d')
        
        self.deal_timeline[date_key].append({
            'type': deal_type,
            'amount': deal_amount,
            'companies': companies or []
        })
    
    def add_sentiment_event(
        self,
        date: datetime,
        sentiment_score: float,
        company: Optional[str] = None
    ) -> None:
        """
        Add a sentiment event to the timeline.
        
        Args:
            date: Event date
            sentiment_score: Sentiment score (-1 to 1)
            company: Company name (if entity-specific)
        """
        date_key = date.strftime('%Y-%m-%d')
        
        self.sentiment_timeline[date_key].append(sentiment_score)
        
        if company:
            self.company_timeline[company][date_key].append(sentiment_score)
    
    def get_deal_volume_trend(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        deal_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get deal volume trend over time.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            deal_type: Filter by deal type
            
        Returns:
            Trend data
        """
        # Filter by date range
        filtered_timeline = self._filter_timeline(
            self.deal_timeline,
            start_date,
            end_date
        )
        
        # Calculate daily volumes
        daily_volumes = {}
        for date_key, deals in filtered_timeline.items():
            if deal_type:
                count = sum(1 for d in deals if d['type'] == deal_type)
            else:
                count = len(deals)
            
            daily_volumes[date_key] = count
        
        # Calculate trend statistics
        volumes = list(daily_volumes.values())
        
        return {
            'timeline': daily_volumes,
            'total_deals': sum(volumes),
            'average_daily': np.mean(volumes) if volumes else 0,
            'peak_day': max(daily_volumes.items(), key=lambda x: x[1])[0] if daily_volumes else None,
            'trend_direction': self._calculate_trend_direction(volumes)
        }
    
    def get_deal_value_trend(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get deal value trend over time.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Value trend data
        """
        filtered_timeline = self._filter_timeline(
            self.deal_timeline,
            start_date,
            end_date
        )
        
        daily_values = {}
        for date_key, deals in filtered_timeline.items():
            total_value = sum(
                d['amount'] for d in deals
                if d['amount'] is not None
            )
            daily_values[date_key] = total_value
        
        values = list(daily_values.values())
        
        return {
            'timeline': daily_values,
            'total_value': sum(values),
            'average_daily_value': np.mean(values) if values else 0,
            'largest_deal_day': max(daily_values.items(), key=lambda x: x[1])[0] if daily_values else None,
            'trend_direction': self._calculate_trend_direction(values)
        }
    
    def get_sentiment_trend(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get sentiment trend over time.
        
        Args:
            start_date: Start date
            end_date: End date
            company: Filter by company
            
        Returns:
            Sentiment trend data
        """
        if company:
            timeline = self.company_timeline.get(company, {})
        else:
            timeline = self.sentiment_timeline
        
        filtered_timeline = self._filter_timeline(
            timeline,
            start_date,
            end_date
        )
        
        daily_sentiment = {}
        for date_key, scores in filtered_timeline.items():
            daily_sentiment[date_key] = np.mean(scores) if scores else 0
        
        scores = list(daily_sentiment.values())
        
        return {
            'timeline': daily_sentiment,
            'average_sentiment': np.mean(scores) if scores else 0,
            'sentiment_volatility': np.std(scores) if scores else 0,
            'most_positive_day': max(daily_sentiment.items(), key=lambda x: x[1])[0] if daily_sentiment else None,
            'most_negative_day': min(daily_sentiment.items(), key=lambda x: x[1])[0] if daily_sentiment else None,
            'trend_direction': self._calculate_trend_direction(scores)
        }
    
    def get_deal_type_distribution(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """
        Get distribution of deal types.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Deal type counts
        """
        filtered_timeline = self._filter_timeline(
            self.deal_timeline,
            start_date,
            end_date
        )
        
        deal_types = []
        for deals in filtered_timeline.values():
            deal_types.extend(d['type'] for d in deals)
        
        return dict(Counter(deal_types))
    
    def detect_anomalies(
        self,
        metric: str = 'volume',
        threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous days based on statistical threshold.
        
        Args:
            metric: Metric to analyze ('volume' or 'value')
            threshold: Standard deviation threshold
            
        Returns:
            List of anomalous days
        """
        if metric == 'volume':
            daily_data = {
                date: len(deals)
                for date, deals in self.deal_timeline.items()
            }
        else:  # value
            daily_data = {
                date: sum(d['amount'] for d in deals if d['amount'])
                for date, deals in self.deal_timeline.items()
            }
        
        if not daily_data:
            return []
        
        values = list(daily_data.values())
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        anomalies = []
        for date, value in daily_data.items():
            z_score = (value - mean_val) / std_val if std_val > 0 else 0
            
            if abs(z_score) > threshold:
                anomalies.append({
                    'date': date,
                    'value': value,
                    'z_score': z_score,
                    'type': 'spike' if z_score > 0 else 'drop'
                })
        
        return sorted(anomalies, key=lambda x: abs(x['z_score']), reverse=True)
    
    def _filter_timeline(
        self,
        timeline: Dict[str, List],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> Dict[str, List]:
        """Filter timeline by date range."""
        if not start_date and not end_date:
            return timeline
        
        filtered = {}
        for date_key, data in timeline.items():
            date = datetime.strptime(date_key, '%Y-%m-%d')
            
            if start_date and date < start_date:
                continue
            if end_date and date > end_date:
                continue
            
            filtered[date_key] = data
        
        return filtered
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """
        Calculate trend direction using linear regression.
        
        Args:
            values: Time series values
            
        Returns:
            Trend direction ('increasing', 'decreasing', 'stable')
        """
        if len(values) < 2:
            return 'stable'
        
        # Simple linear regression
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        # Determine direction
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get overall summary statistics.
        
        Returns:
            Summary statistics
        """
        all_deals = [
            deal
            for deals in self.deal_timeline.values()
            for deal in deals
        ]
        
        all_sentiments = [
            score
            for scores in self.sentiment_timeline.values()
            for score in scores
        ]
        
        return {
            'total_deals': len(all_deals),
            'total_days_tracked': len(self.deal_timeline),
            'average_deals_per_day': len(all_deals) / len(self.deal_timeline) if self.deal_timeline else 0,
            'deal_type_distribution': dict(Counter(d['type'] for d in all_deals)),
            'average_sentiment': np.mean(all_sentiments) if all_sentiments else 0,
            'sentiment_distribution': {
                'positive': sum(1 for s in all_sentiments if s > 0.1),
                'negative': sum(1 for s in all_sentiments if s < -0.1),
                'neutral': sum(1 for s in all_sentiments if -0.1 <= s <= 0.1)
            }
        }
