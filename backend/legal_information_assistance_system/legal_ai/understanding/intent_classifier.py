"""Intent classification for legal queries."""

import re
from typing import Optional


class IntentClassifier:
    """Classify the intent/type of legal questions."""
    
    INTENT_PATTERNS = {
        "yes_no": [
            r'^(के|can|is|are|do|does|will|would|shall|should|may|might)',
            r'\?$',
            r'(हो|होइन|छ|छैन)',
        ],
        "how_to": [
            r'^(कसरी|how|how do|how to|process|procedure|steps|way)',
            r'(गर्न|register|apply|file|obtain|get|process)',
            r'(प्रक्रिया|तरिका)',
        ],
        "definition": [
            r'^(के हो|what is|define|definition|meaning)',
            r'(को अर्थ|means|के भन्ने)',
            r'(explain|व्याख्या)',
        ],
        "why": [
            r'^(किन|why|reason|cause)',
            r'(reject|denied|failed|refused)',
            r'(कारण)',
        ],
        "comparison": [
            r'^(difference|compare|vs|versus)',
            r'(फरक|भिन्नता)',
        ],
        "rights": [
            r'^(rights|right|अधिकार)',
            r'(entitled|पाउनु)',
        ],
        "obligations": [
            r'^(obligation|duty|responsibility|must|should)',
            r'(दायित्व|जिम्मेवार)',
        ],
        "penalty": [
            r'^(penalty|punishment|fine|imprisonment|jail)',
            r'(दण्ड|सजाय|कारावास)',
        ],
    }
    
    def classify(self, query: str) -> str:
        """Classify the intent of the query."""
        query_lower = query.lower()
        
        scores = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    score += 1
            if score > 0:
                scores[intent] = score
        
        if not scores:
            return "general"
        
        # Return intent with highest score
        return max(scores, key=scores.get)
    
    def get_template_for_intent(self, intent: str) -> str:
        """Get the appropriate answer template for the intent."""
        templates = {
            "yes_no": "direct_answer",
            "how_to": "step_by_step",
            "definition": "definition",
            "why": "explanation",
            "comparison": "comparison",
            "rights": "rights",
            "obligations": "obligations",
            "penalty": "penalty",
            "general": "general",
        }
        return templates.get(intent, "general")


# Global instance
intent_classifier = IntentClassifier()
