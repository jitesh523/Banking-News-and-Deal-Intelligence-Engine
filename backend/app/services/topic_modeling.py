from gensim import corpora, models
from gensim.models import LdaModel, CoherenceModel
from typing import List, Dict, Any, Optional
from loguru import logger
import numpy as np


class TopicModeler:
    """Service for topic modeling using LDA (Latent Dirichlet Allocation)."""
    
    def __init__(self, num_topics: int = 10, passes: int = 15, iterations: int = 400):
        """
        Initialize topic modeler.
        
        Args:
            num_topics: Number of topics to extract
            passes: Number of passes through the corpus
            iterations: Number of iterations
        """
        self.num_topics = num_topics
        self.passes = passes
        self.iterations = iterations
        self.dictionary = None
        self.corpus = None
        self.lda_model = None
        self.topic_labels = {}
    
    def prepare_corpus(self, documents: List[List[str]]) -> None:
        """
        Prepare corpus for topic modeling.
        
        Args:
            documents: List of tokenized documents
        """
        # Create dictionary
        self.dictionary = corpora.Dictionary(documents)
        
        # Filter extremes
        self.dictionary.filter_extremes(no_below=2, no_above=0.5)
        
        # Create corpus (bag of words)
        self.corpus = [self.dictionary.doc2bow(doc) for doc in documents]
        
        logger.info(f"Corpus prepared: {len(documents)} documents, {len(self.dictionary)} unique tokens")
    
    def train_model(self, documents: List[List[str]]) -> None:
        """
        Train LDA model.
        
        Args:
            documents: List of tokenized documents
        """
        # Prepare corpus
        self.prepare_corpus(documents)
        
        # Train LDA model
        logger.info(f"Training LDA model with {self.num_topics} topics...")
        
        self.lda_model = LdaModel(
            corpus=self.corpus,
            id2word=self.dictionary,
            num_topics=self.num_topics,
            random_state=42,
            passes=self.passes,
            iterations=self.iterations,
            alpha='auto',
            per_word_topics=True
        )
        
        logger.info("LDA model training complete")
        
        # Auto-label topics
        self._auto_label_topics()
    
    def _auto_label_topics(self) -> None:
        """Automatically generate labels for topics based on top words."""
        for topic_id in range(self.num_topics):
            # Get top words for topic
            top_words = self.lda_model.show_topic(topic_id, topn=3)
            
            # Create label from top 3 words
            label = '_'.join([word for word, _ in top_words])
            self.topic_labels[topic_id] = label
    
    def get_document_topics(self, document: List[str], threshold: float = 0.1) -> List[Dict[str, Any]]:
        """
        Get topics for a document.
        
        Args:
            document: Tokenized document
            threshold: Minimum probability threshold
            
        Returns:
            List of topics with probabilities
        """
        if not self.lda_model or not self.dictionary:
            logger.warning("Model not trained. Call train_model first.")
            return []
        
        # Convert document to bag of words
        bow = self.dictionary.doc2bow(document)
        
        # Get topic distribution
        topic_dist = self.lda_model.get_document_topics(bow)
        
        # Filter by threshold and format
        topics = []
        for topic_id, prob in topic_dist:
            if prob >= threshold:
                topics.append({
                    'topic_id': topic_id,
                    'probability': float(prob),
                    'label': self.topic_labels.get(topic_id, f'topic_{topic_id}'),
                    'top_words': [word for word, _ in self.lda_model.show_topic(topic_id, topn=5)]
                })
        
        # Sort by probability
        topics.sort(key=lambda x: x['probability'], reverse=True)
        
        return topics
    
    def get_all_topics(self, num_words: int = 10) -> List[Dict[str, Any]]:
        """
        Get all topics with their top words.
        
        Args:
            num_words: Number of top words per topic
            
        Returns:
            List of topic information
        """
        if not self.lda_model:
            return []
        
        topics = []
        for topic_id in range(self.num_topics):
            top_words = self.lda_model.show_topic(topic_id, topn=num_words)
            
            topics.append({
                'topic_id': topic_id,
                'label': self.topic_labels.get(topic_id, f'topic_{topic_id}'),
                'words': [
                    {'word': word, 'weight': float(weight)}
                    for word, weight in top_words
                ]
            })
        
        return topics
    
    def calculate_coherence(self, documents: List[List[str]]) -> float:
        """
        Calculate coherence score for the model.
        
        Args:
            documents: Tokenized documents
            
        Returns:
            Coherence score
        """
        if not self.lda_model:
            return 0.0
        
        coherence_model = CoherenceModel(
            model=self.lda_model,
            texts=documents,
            dictionary=self.dictionary,
            coherence='c_v'
        )
        
        coherence_score = coherence_model.get_coherence()
        logger.info(f"Coherence score: {coherence_score:.4f}")
        
        return coherence_score
    
    def get_topic_distribution(self) -> Dict[int, float]:
        """
        Get overall topic distribution across corpus.
        
        Returns:
            Dictionary of topic distributions
        """
        if not self.corpus or not self.lda_model:
            return {}
        
        # Calculate average topic distribution
        topic_sums = np.zeros(self.num_topics)
        
        for doc_bow in self.corpus:
            doc_topics = self.lda_model.get_document_topics(doc_bow)
            for topic_id, prob in doc_topics:
                topic_sums[topic_id] += prob
        
        # Normalize
        topic_dist = topic_sums / len(self.corpus)
        
        return {i: float(prob) for i, prob in enumerate(topic_dist)}
    
    def find_similar_documents(
        self,
        document: List[str],
        all_documents: List[List[str]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find documents similar to the given document based on topic distribution.
        
        Args:
            document: Query document (tokenized)
            all_documents: All documents (tokenized)
            top_n: Number of similar documents to return
            
        Returns:
            List of similar documents with similarity scores
        """
        if not self.lda_model or not self.dictionary:
            return []
        
        # Get topic distribution for query document
        query_bow = self.dictionary.doc2bow(document)
        query_topics = dict(self.lda_model.get_document_topics(query_bow))
        
        # Calculate similarity with all documents
        similarities = []
        for idx, doc in enumerate(all_documents):
            doc_bow = self.dictionary.doc2bow(doc)
            doc_topics = dict(self.lda_model.get_document_topics(doc_bow))
            
            # Calculate cosine similarity between topic distributions
            similarity = self._calculate_topic_similarity(query_topics, doc_topics)
            similarities.append({
                'index': idx,
                'similarity': similarity
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_n]
    
    def _calculate_topic_similarity(
        self,
        topics1: Dict[int, float],
        topics2: Dict[int, float]
    ) -> float:
        """Calculate cosine similarity between two topic distributions."""
        # Get all topic IDs
        all_topics = set(topics1.keys()) | set(topics2.keys())
        
        # Create vectors
        vec1 = np.array([topics1.get(t, 0.0) for t in all_topics])
        vec2 = np.array([topics2.get(t, 0.0) for t in all_topics])
        
        # Calculate cosine similarity
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)
