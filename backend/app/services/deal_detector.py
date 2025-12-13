import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
from app.models.article import Deal


class DealDetector:
    """Service for detecting and classifying banking deals from text."""
    
    def __init__(self):
        """Initialize deal detector with patterns."""
        
        # Deal type patterns
        self.deal_patterns = {
            'merger': [
                r'merger\s+(?:with|between)',
                r'merging\s+with',
                r'merged\s+with',
                r'to\s+merge\s+with'
            ],
            'acquisition': [
                r'acquir(?:e|ed|ing|ition)\s+(?:of|by)',
                r'bought\s+(?:by|for)',
                r'purchased\s+(?:by|for)',
                r'takeover\s+(?:of|by)',
                r'buying\s+(?:out)?'
            ],
            'ipo': [
                r'initial\s+public\s+offering',
                r'\bIPO\b',
                r'going\s+public',
                r'public\s+listing',
                r'stock\s+market\s+debut'
            ],
            'loan': [
                r'loan\s+(?:of|for|agreement)',
                r'credit\s+facility',
                r'lending\s+(?:to|for)',
                r'borrowed\s+(?:from)?',
                r'financing\s+(?:of|for)'
            ],
            'partnership': [
                r'partnership\s+(?:with|between)',
                r'partnering\s+with',
                r'joint\s+venture',
                r'strategic\s+alliance',
                r'collaboration\s+(?:with|between)'
            ],
            'investment': [
                r'invest(?:ed|ing|ment)\s+(?:in|of)',
                r'funding\s+(?:of|for)',
                r'capital\s+injection',
                r'raised\s+\$',
                r'secured\s+funding'
            ]
        }
        
        # Amount patterns
        self.amount_patterns = [
            r'\$\s*(\d+(?:\.\d+)?)\s*(billion|million|trillion|bn|mn)',
            r'(\d+(?:\.\d+)?)\s*(billion|million|trillion)\s+dollars',
            r'€\s*(\d+(?:\.\d+)?)\s*(billion|million|trillion)',
            r'£\s*(\d+(?:\.\d+)?)\s*(billion|million|trillion)'
        ]
        
        # Company indicators
        self.company_indicators = [
            'bank', 'group', 'corp', 'inc', 'ltd', 'llc', 'plc',
            'holdings', 'capital', 'financial', 'partners'
        ]
    
    def detect_deals(self, text: str, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Detect deals from text and entities.
        
        Args:
            text: Article text
            entities: Extracted entities (companies, amounts, etc.)
            
        Returns:
            List of detected deals
        """
        deals = []
        text_lower = text.lower()
        
        # Detect deal types
        detected_types = []
        for deal_type, patterns in self.deal_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected_types.append(deal_type)
                    break
        
        if not detected_types:
            return deals
        
        # Extract deal amounts
        amounts = self._extract_amounts(text)
        
        # Get companies involved
        companies = entities.get('companies', [])
        
        # Create deal records
        for deal_type in detected_types:
            deal = {
                'deal_type': deal_type,
                'companies_involved': companies[:5],  # Top 5 companies
                'deal_amount': amounts[0] if amounts else None,
                'confidence': self._calculate_confidence(text_lower, deal_type, companies, amounts),
                'detected_from_text': True
            }
            deals.append(deal)
        
        return deals
    
    def _extract_amounts(self, text: str) -> List[float]:
        """
        Extract monetary amounts from text.
        
        Args:
            text: Input text
            
        Returns:
            List of amounts in USD (normalized)
        """
        amounts = []
        
        for pattern in self.amount_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match.group(1))
                    unit = match.group(2).lower()
                    
                    # Convert to USD
                    multipliers = {
                        'billion': 1_000_000_000,
                        'bn': 1_000_000_000,
                        'million': 1_000_000,
                        'mn': 1_000_000,
                        'trillion': 1_000_000_000_000
                    }
                    
                    amount_usd = value * multipliers.get(unit, 1)
                    amounts.append(amount_usd)
                    
                except (ValueError, IndexError):
                    continue
        
        return sorted(amounts, reverse=True)
    
    def _calculate_confidence(
        self,
        text: str,
        deal_type: str,
        companies: List[str],
        amounts: List[float]
    ) -> float:
        """
        Calculate confidence score for deal detection.
        
        Args:
            text: Article text
            deal_type: Type of deal
            companies: Companies involved
            amounts: Deal amounts
            
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence
        
        # Boost if multiple companies mentioned
        if len(companies) >= 2:
            confidence += 0.2
        
        # Boost if amount is specified
        if amounts:
            confidence += 0.2
        
        # Boost if deal type appears multiple times
        pattern_count = sum(
            len(re.findall(pattern, text))
            for pattern in self.deal_patterns.get(deal_type, [])
        )
        if pattern_count > 1:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def classify_deal_significance(self, deal_amount: Optional[float]) -> str:
        """
        Classify deal significance based on amount.
        
        Args:
            deal_amount: Deal amount in USD
            
        Returns:
            Significance level
        """
        if not deal_amount:
            return 'unknown'
        
        if deal_amount >= 10_000_000_000:  # $10B+
            return 'mega'
        elif deal_amount >= 1_000_000_000:  # $1B+
            return 'major'
        elif deal_amount >= 100_000_000:  # $100M+
            return 'significant'
        elif deal_amount >= 10_000_000:  # $10M+
            return 'moderate'
        else:
            return 'minor'
    
    def create_deal_record(
        self,
        article_id: str,
        deal_info: Dict[str, Any],
        announcement_date: datetime
    ) -> Deal:
        """
        Create a Deal model instance.
        
        Args:
            article_id: Source article ID
            deal_info: Deal information
            announcement_date: Deal announcement date
            
        Returns:
            Deal instance
        """
        # Generate deal ID
        deal_id = f"deal_{article_id}_{deal_info['deal_type']}"
        
        deal = Deal(
            deal_id=deal_id,
            deal_type=deal_info['deal_type'],
            companies_involved=deal_info['companies_involved'],
            deal_amount=deal_info.get('deal_amount'),
            announcement_date=announcement_date,
            status='announced',
            related_articles=[article_id]
        )
        
        return deal
    
    def extract_deal_context(self, text: str, deal_type: str) -> Dict[str, Any]:
        """
        Extract contextual information about the deal.
        
        Args:
            text: Article text
            deal_type: Type of deal
            
        Returns:
            Contextual information
        """
        context = {
            'deal_type': deal_type,
            'rationale': [],
            'expected_completion': None,
            'regulatory_status': None
        }
        
        # Extract rationale keywords
        rationale_keywords = [
            'synergy', 'expansion', 'growth', 'market share',
            'consolidation', 'efficiency', 'cost savings',
            'strategic', 'competitive advantage'
        ]
        
        text_lower = text.lower()
        for keyword in rationale_keywords:
            if keyword in text_lower:
                context['rationale'].append(keyword)
        
        # Check for regulatory mentions
        if re.search(r'regulatory\s+approval|awaiting\s+approval|pending\s+approval', text_lower):
            context['regulatory_status'] = 'pending'
        elif re.search(r'approved\s+by|cleared\s+by', text_lower):
            context['regulatory_status'] = 'approved'
        
        return context
