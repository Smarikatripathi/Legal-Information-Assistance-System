"""Topic classification for legal queries."""

import re
from typing import Optional, List


class TopicClassifier:
    """Classify the legal topic/domain of queries."""
    
    TOPIC_KEYWORDS = {
        "marriage": [
            "विवाह", "marriage", "wedding", "दम्पत्ती", "spouse", "divorce", 
            "सम्बन्ध विच्छेद", "separation", "annulment", "dowry", "दहेज",
        ],
        "citizenship": [
            "नागरिकता", "citizenship", "passport", "राहदानी", "nationality",
            "naturalization", "by descent", "by birth",
        ],
        "employment": [
            "रोजगारी", "employment", "job", "कामदार", "worker", "salary", "तलब",
            "wage", "labor", "श्रम", "workplace", "termination", "firing", "बर्खास्त",
        ],
        "property": [
            "जग्गा", "land", "property", "सम्पत्ती", "house", "घर", "real estate",
            "ownership", "transfer", "registration", "दर्ता",
        ],
        "crime": [
            "अपराध", "crime", "theft", "चोरी", "murder", "हत्या", "fraud",
            "assault", "robbery", "offense", "criminal", "फौजदारी",
        ],
        "court": [
            "अदालत", "court", "case", "मुद्दा", "petition", "निवेदन", "litigation",
            "lawsuit", "judgment", "verdict", "निर्णय", "appeal", "अपील",
        ],
        "business": [
            "business", "company", "कम्पनी", "firm", "enterprise", "registration",
            "incorporation", "partnership", "share", "शेयर",
        ],
        "family": [
            "family", "परिवार", "child", "बालक", "custody", "adoption",
            "दत्तक", "inheritance", "उत्तराधिकार",
        ],
        "contract": [
            "contract", "agreement", "सम्झौता", "breach", "violation", "terms",
            "conditions", "obligation", "दायित्व",
        ],
        "tax": [
            "tax", "कर", "revenue", "राजस्व", "income tax", "vat", "भ्याट",
        ],
        "consumer": [
            "consumer", "उपभोक्ता", "rights", "protection", "complaint", "गुनासो",
            "refund", "warranty",
        ],
        "environment": [
            "environment", "पर्यावरण", "pollution", "प्रदूषण", "conservation",
            "protection", "संरक्षण",
        ],
    }
    
    # Document type to topic mapping
    DOCUMENT_TYPE_TOPICS = {
        "constitution": ["citizenship", "rights", "court"],
        "civil_code": ["marriage", "property", "family", "contract", "business"],
        "criminal_code": ["crime", "court"],
        "act": ["employment", "tax", "consumer", "environment"],
        "regulation": ["business", "tax", "environment"],
    }
    
    def __init__(self):
        pass
    
    def classify(self, query: str) -> str:
        """Classify the legal topic of the query."""
        query_lower = query.lower()
        
        scores = {}
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    score += 1
            if score > 0:
                scores[topic] = score
        
        if not scores:
            return "other"
        
        # Return topic with highest score
        return max(scores, key=scores.get)
    
    def get_relevant_document_types(self, topic: str) -> List[str]:
        """Get document types relevant to a topic."""
        relevant_types = []
        for doc_type, topics in self.DOCUMENT_TYPE_TOPICS.items():
            if topic in topics:
                relevant_types.append(doc_type)
        return relevant_types
    
    def classify_with_confidence(self, query: str) -> tuple[str, float]:
        """Classify topic with confidence score."""
        query_lower = query.lower()
        
        scores = {}
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    score += 1
            if score > 0:
                scores[topic] = score
        
        if not scores:
            return "other", 0.0
        
        max_topic = max(scores, key=scores.get)
        max_score = scores[max_topic]
        
        # Normalize confidence (0.0 to 1.0)
        confidence = min(max_score / 3.0, 1.0)
        
        return max_topic, confidence


# Global instance
topic_classifier = TopicClassifier()
