from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any, Tuple
import re
from collections import Counter
from loguru import logger


class KeywordExtractor:
    """Service for extracting keywords from text."""
    
    def __init__(self):
        """Initialize keyword extractor."""
        self.tfidf_vectorizer = None
        
        # Financial domain keywords (higher weight)
        self.domain_keywords = {
            'merger', 'acquisition', 'deal', 'ipo', 'takeover', 'buyout',
            'bank', 'banking', 'financial', 'investment', 'capital',
            'stock', 'share', 'equity', 'debt', 'loan', 'credit',
            'revenue', 'profit', 'earnings', 'valuation', 'market',
            'partnership', 'alliance', 'joint venture', 'financing'
        }
    
    def extract_tfidf_keywords(
        self,
        documents: List[str],
        top_n: int = 10,
        max_features: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Extract keywords using TF-IDF.
        
        Args:
            documents: List of documents
            top_n: Number of top keywords to extract per document
            max_features: Maximum number of features
            
        Returns:
            List of keyword dictionaries for each document
        """
        try:
            # Initialize TF-IDF vectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=max_features,
                stop_words='english',
                ngram_range=(1, 2),  # Unigrams and bigrams
                min_df=1,
                max_df=0.8
            )
            
            # Fit and transform
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Extract keywords for each document
            all_keywords = []
            for doc_idx in range(len(documents)):
                # Get TF-IDF scores for this document
                doc_tfidf = tfidf_matrix[doc_idx].toarray()[0]
                
                # Get top keywords
                top_indices = doc_tfidf.argsort()[-top_n:][::-1]
                
                keywords = []
                for idx in top_indices:
                    if doc_tfidf[idx] > 0:
                        keyword = feature_names[idx]
                        score = float(doc_tfidf[idx])
                        
                        # Boost score if it's a domain keyword
                        if keyword.lower() in self.domain_keywords:
                            score *= 1.5
                        
                        keywords.append({
                            'keyword': keyword,
                            'score': score,
                            'method': 'tfidf'
                        })
                
                # Re-sort after boosting
                keywords.sort(key=lambda x: x['score'], reverse=True)
                all_keywords.append(keywords[:top_n])
            
            return all_keywords
            
        except Exception as e:
            logger.error(f"Error extracting TF-IDF keywords: {e}")
            return [[] for _ in documents]
    
    def extract_rake_keywords(
        self,
        text: str,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Extract keywords using RAKE (Rapid Automatic Keyword Extraction).
        
        Args:
            text: Input text
            top_n: Number of top keywords
            
        Returns:
            List of keywords with scores
        """
        try:
            # Split into sentences
            sentences = re.split(r'[.!?]', text.lower())
            
            # Define stop words and delimiters
            stop_words = set([
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
                'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was',
                'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do',
                'does', 'did', 'will', 'would', 'should', 'could', 'may',
                'might', 'must', 'can', 'this', 'that', 'these', 'those'
            ])
            
            # Extract phrases
            phrases = []
            for sentence in sentences:
                # Remove punctuation except spaces
                sentence = re.sub(r'[^\w\s]', ' ', sentence)
                
                # Split by stop words
                words = sentence.split()
                phrase = []
                
                for word in words:
                    if word not in stop_words and len(word) > 2:
                        phrase.append(word)
                    else:
                        if phrase:
                            phrases.append(' '.join(phrase))
                            phrase = []
                
                if phrase:
                    phrases.append(' '.join(phrase))
            
            # Calculate word scores
            word_freq = Counter()
            word_degree = Counter()
            
            for phrase in phrases:
                words = phrase.split()
                degree = len(words) - 1
                
                for word in words:
                    word_freq[word] += 1
                    word_degree[word] += degree
            
            # Calculate word scores (degree/frequency)
            word_scores = {}
            for word in word_freq:
                word_scores[word] = word_degree[word] / word_freq[word]
            
            # Calculate phrase scores
            phrase_scores = {}
            for phrase in phrases:
                words = phrase.split()
                score = sum(word_scores.get(word, 0) for word in words)
                phrase_scores[phrase] = score
            
            # Get top phrases
            sorted_phrases = sorted(
                phrase_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            keywords = []
            for phrase, score in sorted_phrases[:top_n]:
                # Boost if domain keyword
                boost = 1.5 if any(kw in phrase for kw in self.domain_keywords) else 1.0
                
                keywords.append({
                    'keyword': phrase,
                    'score': float(score * boost),
                    'method': 'rake'
                })
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting RAKE keywords: {e}")
            return []
    
    def extract_financial_terms(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract financial-specific terms and metrics.
        
        Args:
            text: Input text
            
        Returns:
            List of financial terms found
        """
        financial_terms = []
        text_lower = text.lower()
        
        # Financial metrics patterns
        patterns = {
            'deal_value': r'\$?\d+(?:\.\d+)?\s*(?:billion|million|trillion|bn|mn)',
            'percentage': r'\d+(?:\.\d+)?%',
            'stock_price': r'\$\d+(?:\.\d+)?',
            'year': r'\b20\d{2}\b'
        }
        
        for term_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                financial_terms.append({
                    'term': match,
                    'type': term_type,
                    'method': 'pattern_matching'
                })
        
        # Domain keywords
        for keyword in self.domain_keywords:
            if keyword in text_lower:
                count = text_lower.count(keyword)
                financial_terms.append({
                    'term': keyword,
                    'type': 'domain_keyword',
                    'count': count,
                    'method': 'domain_matching'
                })
        
        return financial_terms
    
    def extract_combined_keywords(
        self,
        text: str,
        top_n: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Extract keywords using multiple methods and combine results.
        
        Args:
            text: Input text
            top_n: Number of top keywords
            
        Returns:
            Combined list of keywords
        """
        # Extract using RAKE
        rake_keywords = self.extract_rake_keywords(text, top_n=top_n)
        
        # Extract financial terms
        financial_terms = self.extract_financial_terms(text)
        
        # Combine and deduplicate
        all_keywords = {}
        
        for kw in rake_keywords:
            all_keywords[kw['keyword']] = kw
        
        for term in financial_terms:
            if term['term'] not in all_keywords:
                all_keywords[term['term']] = {
                    'keyword': term['term'],
                    'score': term.get('count', 1) * 2.0,  # Higher weight for financial terms
                    'method': term['method'],
                    'type': term.get('type', 'financial')
                }
        
        # Sort by score
        combined = sorted(
            all_keywords.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        return combined[:top_n]
