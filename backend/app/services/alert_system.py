from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from loguru import logger
from enum import Enum


class AlertPriority(Enum):
    """Alert priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AlertType(Enum):
    """Types of alerts."""
    MEGA_DEAL = "mega_deal"
    SENTIMENT_SHIFT = "sentiment_shift"
    UNUSUAL_ACTIVITY = "unusual_activity"
    COMPANY_MENTION_SPIKE = "company_mention_spike"
    DEAL_CLUSTER = "deal_cluster"


class Alert:
    """Alert model."""
    
    def __init__(
        self,
        alert_type: AlertType,
        priority: AlertPriority,
        title: str,
        description: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        self.alert_type = alert_type
        self.priority = priority
        self.title = title
        self.description = description
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
        self.alert_id = f"{alert_type.value}_{int(self.timestamp.timestamp())}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            'alert_id': self.alert_id,
            'type': self.alert_type.value,
            'priority': self.priority.value,
            'title': self.title,
            'description': self.description,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }


class AlertSystem:
    """Service for generating and managing alerts."""
    
    def __init__(self):
        """Initialize alert system."""
        self.alerts = []
        self.alert_rules = {
            'mega_deal_threshold': 10_000_000_000,  # $10B
            'major_deal_threshold': 1_000_000_000,  # $1B
            'sentiment_shift_threshold': 0.5,  # 50% change
            'mention_spike_threshold': 3.0,  # 3x normal
            'deal_cluster_threshold': 5  # 5+ deals in short period
        }
        self.subscribers = []
    
    def check_mega_deal(
        self,
        deal_amount: Optional[float],
        deal_type: str,
        companies: List[str]
    ) -> Optional[Alert]:
        """
        Check if deal qualifies as mega deal alert.
        
        Args:
            deal_amount: Deal amount in USD
            deal_type: Type of deal
            companies: Companies involved
            
        Returns:
            Alert if threshold met
        """
        if not deal_amount:
            return None
        
        if deal_amount >= self.alert_rules['mega_deal_threshold']:
            return Alert(
                alert_type=AlertType.MEGA_DEAL,
                priority=AlertPriority.CRITICAL,
                title=f"Mega {deal_type.title()} Deal Detected",
                description=f"${deal_amount/1e9:.2f}B {deal_type} involving {', '.join(companies[:3])}",
                data={
                    'deal_amount': deal_amount,
                    'deal_type': deal_type,
                    'companies': companies
                }
            )
        elif deal_amount >= self.alert_rules['major_deal_threshold']:
            return Alert(
                alert_type=AlertType.MEGA_DEAL,
                priority=AlertPriority.HIGH,
                title=f"Major {deal_type.title()} Deal Detected",
                description=f"${deal_amount/1e9:.2f}B {deal_type} involving {', '.join(companies[:3])}",
                data={
                    'deal_amount': deal_amount,
                    'deal_type': deal_type,
                    'companies': companies
                }
            )
        
        return None
    
    def check_sentiment_shift(
        self,
        company: str,
        current_sentiment: float,
        previous_sentiment: float
    ) -> Optional[Alert]:
        """
        Check for significant sentiment shift.
        
        Args:
            company: Company name
            current_sentiment: Current sentiment score
            previous_sentiment: Previous sentiment score
            
        Returns:
            Alert if significant shift detected
        """
        if abs(current_sentiment - previous_sentiment) >= self.alert_rules['sentiment_shift_threshold']:
            direction = "improved" if current_sentiment > previous_sentiment else "declined"
            
            return Alert(
                alert_type=AlertType.SENTIMENT_SHIFT,
                priority=AlertPriority.MEDIUM,
                title=f"Sentiment Shift for {company}",
                description=f"Sentiment has {direction} significantly from {previous_sentiment:.2f} to {current_sentiment:.2f}",
                data={
                    'company': company,
                    'current_sentiment': current_sentiment,
                    'previous_sentiment': previous_sentiment,
                    'change': current_sentiment - previous_sentiment
                }
            )
        
        return None
    
    def check_unusual_activity(
        self,
        metric_value: float,
        average_value: float,
        metric_name: str
    ) -> Optional[Alert]:
        """
        Check for unusual activity based on deviation from average.
        
        Args:
            metric_value: Current metric value
            average_value: Historical average
            metric_name: Name of metric
            
        Returns:
            Alert if unusual activity detected
        """
        if average_value == 0:
            return None
        
        ratio = metric_value / average_value
        
        if ratio >= self.alert_rules['mention_spike_threshold']:
            return Alert(
                alert_type=AlertType.UNUSUAL_ACTIVITY,
                priority=AlertPriority.HIGH,
                title=f"Unusual Activity: {metric_name}",
                description=f"{metric_name} is {ratio:.1f}x higher than average ({metric_value:.0f} vs {average_value:.0f})",
                data={
                    'metric_name': metric_name,
                    'current_value': metric_value,
                    'average_value': average_value,
                    'ratio': ratio
                }
            )
        
        return None
    
    def check_company_mention_spike(
        self,
        company: str,
        current_mentions: int,
        average_mentions: float
    ) -> Optional[Alert]:
        """
        Check for spike in company mentions.
        
        Args:
            company: Company name
            current_mentions: Current mention count
            average_mentions: Average mention count
            
        Returns:
            Alert if spike detected
        """
        alert = self.check_unusual_activity(
            current_mentions,
            average_mentions,
            f"{company} mentions"
        )
        
        if alert:
            alert.alert_type = AlertType.COMPANY_MENTION_SPIKE
            alert.data['company'] = company
        
        return alert
    
    def check_deal_cluster(
        self,
        deal_count: int,
        time_period: str,
        deal_type: Optional[str] = None
    ) -> Optional[Alert]:
        """
        Check for cluster of deals in short time period.
        
        Args:
            deal_count: Number of deals
            time_period: Time period description
            deal_type: Type of deals (optional)
            
        Returns:
            Alert if cluster detected
        """
        if deal_count >= self.alert_rules['deal_cluster_threshold']:
            deal_desc = f"{deal_type} " if deal_type else ""
            
            return Alert(
                alert_type=AlertType.DEAL_CLUSTER,
                priority=AlertPriority.MEDIUM,
                title=f"Deal Cluster Detected",
                description=f"{deal_count} {deal_desc}deals in {time_period}",
                data={
                    'deal_count': deal_count,
                    'time_period': time_period,
                    'deal_type': deal_type
                }
            )
        
        return None
    
    def add_alert(self, alert: Alert) -> None:
        """
        Add alert to the system.
        
        Args:
            alert: Alert to add
        """
        self.alerts.append(alert)
        logger.info(f"Alert generated: {alert.title} (Priority: {alert.priority.name})")
        
        # Notify subscribers
        self._notify_subscribers(alert)
    
    def get_alerts(
        self,
        priority: Optional[AlertPriority] = None,
        alert_type: Optional[AlertType] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get alerts with optional filtering.
        
        Args:
            priority: Filter by priority
            alert_type: Filter by type
            limit: Maximum number of alerts
            
        Returns:
            List of alerts
        """
        filtered_alerts = self.alerts
        
        if priority:
            filtered_alerts = [a for a in filtered_alerts if a.priority == priority]
        
        if alert_type:
            filtered_alerts = [a for a in filtered_alerts if a.alert_type == alert_type]
        
        # Sort by timestamp (newest first)
        filtered_alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [alert.to_dict() for alert in filtered_alerts[:limit]]
    
    def subscribe(self, callback: Callable[[Alert], None]) -> None:
        """
        Subscribe to alerts.
        
        Args:
            callback: Function to call when alert is generated
        """
        self.subscribers.append(callback)
    
    def _notify_subscribers(self, alert: Alert) -> None:
        """Notify all subscribers of new alert."""
        for callback in self.subscribers:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
    
    def update_rules(self, rules: Dict[str, Any]) -> None:
        """
        Update alert rules.
        
        Args:
            rules: Dictionary of rule updates
        """
        self.alert_rules.update(rules)
        logger.info(f"Alert rules updated: {rules}")
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """
        Get summary of alerts.
        
        Returns:
            Alert summary statistics
        """
        priority_counts = {p.name: 0 for p in AlertPriority}
        type_counts = {t.value: 0 for t in AlertType}
        
        for alert in self.alerts:
            priority_counts[alert.priority.name] += 1
            type_counts[alert.alert_type.value] += 1
        
        return {
            'total_alerts': len(self.alerts),
            'by_priority': priority_counts,
            'by_type': type_counts,
            'latest_alert': self.alerts[-1].to_dict() if self.alerts else None
        }
