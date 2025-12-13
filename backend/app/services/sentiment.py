from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
from typing import Dict, Any, Optional
from loguru import logger


class SentimentAnalyzer:
    """Service for financial sentiment analysis using FinBERT."""
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize sentiment analyzer.
        
        Args:
            model_name: HuggingFace model to use (default: FinBERT)
        """
        try:
            logger.info(f"Loading sentiment model: {model_name}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Create pipeline
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("Sentiment model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading sentiment model: {e}")
            raise
    
    def analyze_sentiment(self, text: str, max_length: int = 512) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Input text
            max_length: Maximum token length
            
        Returns:
            Sentiment analysis results
        """
        try:
            # Truncate text if too long
            tokens = self.tokenizer.encode(text, truncation=True, max_length=max_length)
            truncated_text = self.tokenizer.decode(tokens, skip_special_tokens=True)
            
            # Get sentiment
            result = self.sentiment_pipeline(truncated_text)[0]
            
            # Map labels to standardized format
            label_map = {
                'positive': 'positive',
                'negative': 'negative',
                'neutral': 'neutral',
                'POSITIVE': 'positive',
                'NEGATIVE': 'negative',
                'NEUTRAL': 'neutral'
            }
            
            sentiment_label = label_map.get(result['label'], result['label'].lower())
            
            # Convert to numeric score (-1 to 1)
            score_map = {
                'positive': result['score'],
                'negative': -result['score'],
                'neutral': 0
            }
            
            numeric_score = score_map.get(sentiment_label, 0)
            
            return {
                'label': sentiment_label,
                'score': numeric_score,
                'confidence': result['score'],
                'raw_label': result['label']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                'label': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def analyze_entity_sentiment(
        self,
        text: str,
        entity: str
    ) -> Dict[str, Any]:
        """
        Analyze sentiment towards a specific entity.
        
        Args:
            text: Full text
            entity: Entity to analyze sentiment for
            
        Returns:
            Entity-specific sentiment
        """
        try:
            # Find sentences containing the entity
            sentences = text.split('.')
            relevant_sentences = [s for s in sentences if entity.lower() in s.lower()]
            
            if not relevant_sentences:
                return {
                    'entity': entity,
                    'label': 'neutral',
                    'score': 0.0,
                    'confidence': 0.0,
                    'sentence_count': 0
                }
            
            # Analyze sentiment of relevant sentences
            sentiments = []
            for sentence in relevant_sentences:
                if sentence.strip():
                    sent_result = self.analyze_sentiment(sentence.strip())
                    sentiments.append(sent_result)
            
            # Aggregate sentiments
            if sentiments:
                avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
                avg_confidence = sum(s['confidence'] for s in sentiments) / len(sentiments)
                
                # Determine overall label
                if avg_score > 0.1:
                    label = 'positive'
                elif avg_score < -0.1:
                    label = 'negative'
                else:
                    label = 'neutral'
                
                return {
                    'entity': entity,
                    'label': label,
                    'score': avg_score,
                    'confidence': avg_confidence,
                    'sentence_count': len(relevant_sentences)
                }
            
            return {
                'entity': entity,
                'label': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'sentence_count': 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing entity sentiment: {e}")
            return {
                'entity': entity,
                'label': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def batch_analyze(self, texts: list) -> list:
        """
        Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts
            
        Returns:
            List of sentiment results
        """
        results = []
        for text in texts:
            results.append(self.analyze_sentiment(text))
        return results
