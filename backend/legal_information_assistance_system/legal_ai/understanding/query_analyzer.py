"""Query analysis for clarity, unknown terms, and ambiguity detection."""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

from legal_information_assistance_system.legal_ai.services.language import language_service


@dataclass
class QueryAnalysis:
    """Result of query analysis."""
    is_clear: bool
    clarity_score: float
    unknown_terms: List[str]
    ambiguity_detected: bool
    legal_entities: List[str]
    section_numbers: List[str]
    article_numbers: List[str]
    confidence: float


class QueryAnalyzer:
    """Analyze queries for clarity, unknown terms, and legal entities."""
    
    # Common unknown terms that should trigger clarification
    UNKNOWN_TERM_PATTERNS = [
        r'\b[a-z]{3,5}\b',  # Short unclear terms like "atqr"
    ]
    
    # Common English words to exclude from unknown term detection
    COMMON_ENGLISH_WORDS = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 
        'our', 'out', 'has', 'have', 'been', 'what', 'when', 'where', 'who', 'why', 'how', 'this', 'that', 
        'with', 'from', 'they', 'will', 'more', 'some', 'time', 'very', 'your', 'about', 'would', 'which',
        'their', 'said', 'each', 'she', 'does', 'into', 'through', 'when', 'there', 'could', 'than', 'then',
        'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our',
        'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most'
    }
    
    # Legal entity patterns
    LEGAL_ENTITY_PATTERNS = [
        r'(Constitution|संविधान)',
        r'(Civil Code|देवानी संहिता)',
        r'(Criminal Code|फौजदारी संहिता)',
        r'(Labor Act|श्रम ऐन)',
        r'(Court|अदालत)',
        r'(Supreme Court|सर्वोच्च अदालत)',
    ]
    
    # Section/article patterns
    SECTION_PATTERNS = [
        r'(Section|दफा|धारा)\s*\d+',
        r'(Article|अनुच्छेद)\s*\d+',
    ]
    
    # Ambiguity indicators
    AMBIGUITY_INDICATORS = [
        'maybe', 'perhaps', 'possibly', 'might be',
        'सायद', 'हुन सक्छ', 'होला',
    ]
    
    def __init__(self):
        self.language_service = language_service
    
    def analyze(self, query: str) -> QueryAnalysis:
        """Perform comprehensive query analysis."""
        detected_lang = self.language_service.detect_language(query)
        
        # Detect unknown terms
        unknown_terms = self._detect_unknown_terms(query, detected_lang)
        
        # Detect legal entities
        legal_entities = self._detect_legal_entities(query)
        
        # Detect section/article numbers
        section_numbers = self._detect_section_numbers(query)
        article_numbers = self._detect_article_numbers(query)
        
        # Detect ambiguity
        ambiguity_detected = self._detect_ambiguity(query, detected_lang)
        
        # Calculate clarity score
        clarity_score = self._calculate_clarity_score(
            query, unknown_terms, ambiguity_detected, legal_entities
        )
        
        # Determine if query is clear enough
        is_clear = clarity_score >= 0.6 and len(unknown_terms) == 0
        
        # Overall confidence
        confidence = self._calculate_confidence(
            clarity_score, len(legal_entities), len(section_numbers) + len(article_numbers)
        )
        
        return QueryAnalysis(
            is_clear=is_clear,
            clarity_score=clarity_score,
            unknown_terms=unknown_terms,
            ambiguity_detected=ambiguity_detected,
            legal_entities=legal_entities,
            section_numbers=section_numbers,
            article_numbers=article_numbers,
            confidence=confidence,
        )
    
    def _detect_unknown_terms(self, query: str, language: str) -> List[str]:
        """Detect potentially unknown or unclear terms."""
        unknown_terms = []
        
        # For English: check for short, uncommon terms
        if language == 'en':
            words = re.findall(r'\b[a-z]+\b', query.lower())
            for word in words:
                # Skip common words
                if word in self.COMMON_ENGLISH_WORDS:
                    continue
                # Flag very short uncommon words (like "atqr")
                if len(word) <= 5 and word not in ['gold', 'bag', 'stole', 'theft', 'money', 'land', 'house']:
                    unknown_terms.append(word)
        
        # For Nepali: check for unclear terms
        elif language == 'ne':
            # Check for very short Devanagari words that might be unclear
            words = re.findall(r'[\u0900-\u097F]+', query)
            for word in words:
                if len(word) <= 2:  # Very short Nepali words might be unclear
                    unknown_terms.append(word)
        
        return unknown_terms
    
    def _detect_legal_entities(self, query: str) -> List[str]:
        """Detect legal document names and entities."""
        entities = []
        for pattern in self.LEGAL_ENTITY_PATTERNS:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities.extend(matches)
        return list(set(entities))
    
    def _detect_section_numbers(self, query: str) -> List[str]:
        """Detect section/dhara references."""
        sections = []
        pattern = r'(Section|दफा|धारा)\s*(\d+)'
        matches = re.findall(pattern, query, re.IGNORECASE)
        for match in matches:
            sections.append(f"{match[0]} {match[1]}")
        return sections
    
    def _detect_article_numbers(self, query: str) -> List[str]:
        """Detect article references."""
        articles = []
        pattern = r'(Article|अनुच्छेद)\s*(\d+)'
        matches = re.findall(pattern, query, re.IGNORECASE)
        for match in matches:
            articles.append(f"{match[0]} {match[1]}")
        return articles
    
    def _detect_ambiguity(self, query: str, language: str) -> bool:
        """Detect ambiguous language in query."""
        query_lower = query.lower()
        for indicator in self.AMBIGUITY_INDICATORS:
            if indicator in query_lower:
                return True
        return False
    
    def _calculate_clarity_score(
        self, query: str, unknown_terms: List[str], ambiguity: bool, entities: List[str]
    ) -> float:
        """Calculate overall clarity score (0.0 to 1.0)."""
        score = 1.0
        
        # Penalize unknown terms heavily
        score -= len(unknown_terms) * 0.3
        
        # Penalize ambiguity
        if ambiguity:
            score -= 0.2
        
        # Boost if legal entities are present
        if entities:
            score += min(len(entities) * 0.1, 0.2)
        
        # Boost if query is long enough (more context)
        if len(query.split()) >= 5:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _calculate_confidence(
        self, clarity_score: float, entity_count: int, reference_count: int
    ) -> float:
        """Calculate overall confidence in analysis."""
        confidence = clarity_score * 0.6
        confidence += min(entity_count * 0.1, 0.2)
        confidence += min(reference_count * 0.1, 0.2)
        return min(1.0, confidence)


# Global instance
query_analyzer = QueryAnalyzer()
