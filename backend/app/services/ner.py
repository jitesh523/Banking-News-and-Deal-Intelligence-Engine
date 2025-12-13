import spacy
from typing import List, Dict, Any, Optional
from loguru import logger
import re


class NERService:
    """Service for Named Entity Recognition using spaCy."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize NER service.
        
        Args:
            model_name: spaCy model to use
        """
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.warning(f"Model {model_name} not found. Downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", model_name])
            self.nlp = spacy.load(model_name)
        
        # Banking-specific patterns
        self.banking_patterns = {
            'deal_types': [
                'merger', 'acquisition', 'M&A', 'IPO', 'takeover',
                'buyout', 'partnership', 'joint venture', 'alliance',
                'loan', 'credit facility', 'financing', 'investment'
            ],
            'financial_terms': [
                'billion', 'million', 'trillion', 'USD', 'EUR', 'GBP',
                'shares', 'stock', 'equity', 'debt', 'capital'
            ]
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of entity types and their values
        """
        doc = self.nlp(text)
        
        entities = {
            'companies': [],
            'people': [],
            'locations': [],
            'amounts': [],
            'dates': [],
            'organizations': [],
            'other': []
        }
        
        for ent in doc.ents:
            entity_info = {
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            }
            
            # Categorize entities
            if ent.label_ == 'ORG':
                # Check if it's a company (contains banking/financial keywords)
                if self._is_company(ent.text):
                    entities['companies'].append(entity_info)
                else:
                    entities['organizations'].append(entity_info)
            
            elif ent.label_ == 'PERSON':
                entities['people'].append(entity_info)
            
            elif ent.label_ in ['GPE', 'LOC']:
                entities['locations'].append(entity_info)
            
            elif ent.label_ == 'MONEY':
                entities['amounts'].append(entity_info)
            
            elif ent.label_ == 'DATE':
                entities['dates'].append(entity_info)
            
            else:
                entities['other'].append(entity_info)
        
        # Extract additional financial amounts using regex
        amounts = self._extract_financial_amounts(text)
        entities['amounts'].extend(amounts)
        
        # Remove duplicates
        for key in entities:
            entities[key] = self._remove_duplicate_entities(entities[key])
        
        return entities
    
    def _is_company(self, text: str) -> bool:
        """
        Check if entity is likely a company.
        
        Args:
            text: Entity text
            
        Returns:
            True if likely a company
        """
        company_indicators = [
            'bank', 'group', 'corp', 'inc', 'ltd', 'llc', 'plc',
            'holdings', 'capital', 'financial', 'investment',
            'securities', 'partners', 'advisors'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in company_indicators)
    
    def _extract_financial_amounts(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract financial amounts using regex patterns.
        
        Args:
            text: Input text
            
        Returns:
            List of amount entities
        """
        amounts = []
        
        # Pattern for amounts like "$5 billion", "€2.5 million", etc.
        pattern = r'[\$€£¥]?\s*\d+(?:\.\d+)?\s*(?:billion|million|trillion|bn|mn|tn)'
        
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            amounts.append({
                'text': match.group(),
                'label': 'MONEY',
                'start': match.start(),
                'end': match.end()
            })
        
        return amounts
    
    def _remove_duplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate entities based on text.
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Deduplicated list
        """
        seen = set()
        unique_entities = []
        
        for entity in entities:
            if entity['text'] not in seen:
                seen.add(entity['text'])
                unique_entities.append(entity)
        
        return unique_entities
    
    def extract_relationships(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract relationships between entities (basic implementation).
        
        Args:
            text: Input text
            
        Returns:
            List of relationship tuples
        """
        doc = self.nlp(text)
        relationships = []
        
        # Simple pattern: COMPANY verb COMPANY
        for token in doc:
            if token.pos_ == 'VERB':
                # Look for subjects and objects
                subjects = [child for child in token.children if child.dep_ == 'nsubj']
                objects = [child for child in token.children if child.dep_ == 'dobj']
                
                for subj in subjects:
                    for obj in objects:
                        if subj.ent_type_ == 'ORG' and obj.ent_type_ == 'ORG':
                            relationships.append({
                                'subject': subj.text,
                                'verb': token.text,
                                'object': obj.text,
                                'type': 'action'
                            })
        
        return relationships
    
    def get_entity_summary(self, entities: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
        """
        Get summary counts of entities.
        
        Args:
            entities: Entity dictionary
            
        Returns:
            Count summary
        """
        return {
            entity_type: len(entity_list)
            for entity_type, entity_list in entities.items()
        }
