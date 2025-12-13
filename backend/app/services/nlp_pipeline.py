from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from app.services.text_preprocessing import TextPreprocessor
from app.services.ner import NERService
from app.services.sentiment import SentimentAnalyzer
from app.services.topic_modeling import TopicModeler
from app.services.keyword_extraction import KeywordExtractor
from app.models.article import Article


class NLPPipeline:
    """Orchestrates all NLP processing services."""
    
    def __init__(self):
        """Initialize NLP pipeline with all services."""
        logger.info("Initializing NLP Pipeline...")
        
        self.preprocessor = TextPreprocessor()
        self.ner_service = NERService()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_modeler = TopicModeler(num_topics=10)
        self.keyword_extractor = KeywordExtractor()
        
        self.is_topic_model_trained = False
        
        logger.info("NLP Pipeline initialized successfully")
    
    def process_article(
        self,
        article: Article,
        extract_topics: bool = False
    ) -> Dict[str, Any]:
        """
        Process a single article through the NLP pipeline.
        
        Args:
            article: Article to process
            extract_topics: Whether to extract topics (requires trained model)
            
        Returns:
            Dictionary with all NLP results
        """
        logger.info(f"Processing article: {article.article_id}")
        
        results = {
            'article_id': article.article_id,
            'processing_date': datetime.utcnow(),
            'entities': {},
            'sentiment': {},
            'topics': [],
            'keywords': []
        }
        
        try:
            # Combine title and content
            full_text = f"{article.title}. {article.content}"
            
            # 1. Text Preprocessing
            logger.debug("Preprocessing text...")
            preprocessed = self.preprocessor.preprocess(
                full_text,
                remove_punct=False,  # Keep punctuation for NER
                remove_stops=True,
                lemmatize=True
            )
            
            # 2. Named Entity Recognition
            logger.debug("Extracting entities...")
            entities = self.ner_service.extract_entities(full_text)
            results['entities'] = {
                'companies': [e['text'] for e in entities['companies']],
                'people': [e['text'] for e in entities['people']],
                'locations': [e['text'] for e in entities['locations']],
                'amounts': [e['text'] for e in entities['amounts']],
                'dates': [e['text'] for e in entities['dates']]
            }
            
            # 3. Sentiment Analysis
            logger.debug("Analyzing sentiment...")
            sentiment = self.sentiment_analyzer.analyze_sentiment(full_text)
            results['sentiment'] = {
                'label': sentiment['label'],
                'score': sentiment['score'],
                'confidence': sentiment['confidence']
            }
            
            # Entity-level sentiment for companies
            if entities['companies']:
                entity_sentiments = []
                for company in entities['companies'][:5]:  # Top 5 companies
                    entity_sent = self.sentiment_analyzer.analyze_entity_sentiment(
                        full_text,
                        company['text']
                    )
                    entity_sentiments.append(entity_sent)
                
                results['entity_sentiments'] = entity_sentiments
            
            # 4. Topic Modeling (if model is trained)
            if extract_topics and self.is_topic_model_trained:
                logger.debug("Extracting topics...")
                topics = self.topic_modeler.get_document_topics(
                    preprocessed['tokens'],
                    threshold=0.1
                )
                results['topics'] = [
                    {
                        'label': t['label'],
                        'probability': t['probability'],
                        'top_words': t['top_words']
                    }
                    for t in topics
                ]
            
            # 5. Keyword Extraction
            logger.debug("Extracting keywords...")
            keywords = self.keyword_extractor.extract_combined_keywords(
                full_text,
                top_n=10
            )
            results['keywords'] = [
                {
                    'keyword': kw['keyword'],
                    'score': kw['score']
                }
                for kw in keywords
            ]
            
            logger.success(f"Article processed successfully: {article.article_id}")
            
        except Exception as e:
            logger.error(f"Error processing article {article.article_id}: {e}")
            results['error'] = str(e)
        
        return results
    
    def process_articles_batch(
        self,
        articles: List[Article],
        train_topics: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Process multiple articles in batch.
        
        Args:
            articles: List of articles to process
            train_topics: Whether to train topic model
            
        Returns:
            List of processing results
        """
        logger.info(f"Processing batch of {len(articles)} articles...")
        
        results = []
        
        # First pass: Process all articles (except topics)
        for article in articles:
            result = self.process_article(article, extract_topics=False)
            results.append(result)
        
        # Train topic model if requested
        if train_topics and len(articles) >= 10:  # Need minimum documents
            logger.info("Training topic model...")
            try:
                # Prepare documents for topic modeling
                documents = []
                for article in articles:
                    full_text = f"{article.title}. {article.content}"
                    preprocessed = self.preprocessor.preprocess(full_text)
                    documents.append(preprocessed['tokens'])
                
                # Train model
                self.topic_modeler.train_model(documents)
                self.is_topic_model_trained = True
                
                # Second pass: Add topics to results
                for i, article in enumerate(articles):
                    full_text = f"{article.title}. {article.content}"
                    preprocessed = self.preprocessor.preprocess(full_text)
                    
                    topics = self.topic_modeler.get_document_topics(
                        preprocessed['tokens'],
                        threshold=0.1
                    )
                    
                    results[i]['topics'] = [
                        {
                            'label': t['label'],
                            'probability': t['probability'],
                            'top_words': t['top_words']
                        }
                        for t in topics
                    ]
                
                logger.success("Topic model trained and topics extracted")
                
            except Exception as e:
                logger.error(f"Error training topic model: {e}")
        
        logger.info(f"Batch processing complete: {len(results)} articles processed")
        
        return results
    
    def get_topic_summary(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get summary of all topics.
        
        Returns:
            List of topics with their top words
        """
        if not self.is_topic_model_trained:
            logger.warning("Topic model not trained yet")
            return None
        
        return self.topic_modeler.get_all_topics(num_words=10)
    
    def analyze_text_snippet(self, text: str) -> Dict[str, Any]:
        """
        Quick analysis of a text snippet (for testing/demo).
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis results
        """
        results = {}
        
        # Entities
        entities = self.ner_service.extract_entities(text)
        results['entities'] = entities
        
        # Sentiment
        sentiment = self.sentiment_analyzer.analyze_sentiment(text)
        results['sentiment'] = sentiment
        
        # Keywords
        keywords = self.keyword_extractor.extract_combined_keywords(text, top_n=10)
        results['keywords'] = keywords
        
        return results
