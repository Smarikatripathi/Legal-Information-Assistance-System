"""Language Service - Detects and handles query language."""

from typing import Optional


class LanguageService:
    """Service for detecting and handling query language."""
    
    # Common Nepali words for language detection
    NEPALI_WORDS = [
        'के', 'कसरी', 'किन', 'कहिले', 'कता', 'को', 'कुन',
        'छ', 'हो', 'थियो', 'हुनेछ', 'छैन',
        'म', 'तिमी', 'उहाँ', 'हामी', 'तपाईं',
        'यो', 'त्यो', 'यी', 'ती',
        'गर्नु', 'गर्ने', 'गरेको',
        'छु', 'छौ', 'छन्',
        'जानु', 'आउनु', 'लाग्नु',
        'कानून', 'न्याय', 'अदालत', 'अधिकार',
    ]
    
    def __init__(self):
        self.nepali_word_set = set(self.NEPALI_WORDS)
    
    def detect_language(self, text: str) -> str:
        """Detect the language of a text (English or Nepali).
        
        Args:
            text: The text to analyze
            
        Returns:
            'ne' for Nepali, 'en' for English
        """
        if not text:
            return 'en'
        
        # Check for Devanagari script (Nepali)
        if any('\u0900' <= char <= '\u097F' for char in text):
            return 'ne'
        
        # Check for Nepali words
        words = text.lower().split()
        nepali_count = sum(1 for word in words if word in self.nepali_word_set)
        
        # If more than 20% of words are Nepali, classify as Nepali
        if len(words) > 0 and nepali_count / len(words) > 0.2:
            return 'ne'
        
        return 'en'
    
    def get_response_language(self, query_language: str) -> str:
        """Get the language for the response (same as query)."""
        return query_language


# Global instance
language_service = LanguageService()
