import re
import string
from typing import List, Dict, Any
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from loguru import logger

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)


class TextPreprocessor:
    """Service for preprocessing text data."""
    
    def __init__(self):
        """Initialize text preprocessor."""
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Financial terms to preserve (don't remove as stopwords)
        self.financial_terms = {
            'bank', 'banking', 'merger', 'acquisition', 'deal', 'ipo',
            'stock', 'share', 'equity', 'debt', 'loan', 'credit',
            'investment', 'finance', 'financial', 'capital', 'market'
        }
        
        # Update stopwords to exclude financial terms
        self.stop_words = self.stop_words - self.financial_terms
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing special characters and extra whitespace.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def remove_punctuation(self, text: str, keep_periods: bool = False) -> str:
        """
        Remove punctuation from text.
        
        Args:
            text: Input text
            keep_periods: Whether to keep periods
            
        Returns:
            Text without punctuation
        """
        if keep_periods:
            # Remove all punctuation except periods
            punctuation = string.punctuation.replace('.', '')
            text = text.translate(str.maketrans('', '', punctuation))
        else:
            text = text.translate(str.maketrans('', '', string.punctuation))
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        return word_tokenize(text.lower())
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from token list.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered tokens
        """
        return [token for token in tokens if token not in self.stop_words]
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """
        Lemmatize tokens.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Lemmatized tokens
        """
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def preprocess(
        self,
        text: str,
        remove_punct: bool = True,
        remove_stops: bool = True,
        lemmatize: bool = True
    ) -> Dict[str, Any]:
        """
        Complete preprocessing pipeline.
        
        Args:
            text: Raw text
            remove_punct: Whether to remove punctuation
            remove_stops: Whether to remove stopwords
            lemmatize: Whether to lemmatize
            
        Returns:
            Dictionary with processed text and tokens
        """
        # Clean text
        cleaned = self.clean_text(text)
        
        # Remove punctuation if requested
        if remove_punct:
            cleaned = self.remove_punctuation(cleaned)
        
        # Tokenize
        tokens = self.tokenize(cleaned)
        
        # Remove stopwords if requested
        if remove_stops:
            tokens = self.remove_stopwords(tokens)
        
        # Lemmatize if requested
        if lemmatize:
            tokens = self.lemmatize(tokens)
        
        # Reconstruct text from tokens
        processed_text = ' '.join(tokens)
        
        return {
            'original': text,
            'cleaned': cleaned,
            'tokens': tokens,
            'processed': processed_text,
            'token_count': len(tokens)
        }
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        return sent_tokenize(text)
    
    def get_word_frequency(self, tokens: List[str]) -> Dict[str, int]:
        """
        Calculate word frequency.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Dictionary of word frequencies
        """
        freq_dist = {}
        for token in tokens:
            freq_dist[token] = freq_dist.get(token, 0) + 1
        
        # Sort by frequency
        return dict(sorted(freq_dist.items(), key=lambda x: x[1], reverse=True))
