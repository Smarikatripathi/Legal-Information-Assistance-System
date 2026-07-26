"""
Query Clarification Service
Handles UNCLEAR queries by asking for clarification
"""

from typing import Dict, Any


class ClarificationService:
    """Provides clarification responses for unclear queries."""
    
    CLARIFICATION_MESSAGES = {
        "en": "Could you please provide more details about your situation? For example, if you're asking about a legal matter, please mention the specific issue (e.g., theft, property dispute, marriage, arrest, etc.) and any relevant context.",
        "ne": "कृपया तपाईंको स्थितिबारे थप विवरण प्रदान गर्नुहोस्। उदाहरणका लागि, यदि तपाईं कानुनी विषयको बारेमा सोध्दै हुनुहुन्छ भने, कृपया विशिष्ट समस्या (जस्तै: चोरी, सम्पत्ति विवाद, विवाह, पक्राउ, आदि) र सम्बन्धित सन्दर्भ उल्लेख गर्नुहोस्।",
        "ne_roman": "Kripaya tapaiko sthitibari thap bibaran pradan garnuhos. Udaharanka lagi, yadi tapai kanuni vishyako barema sodhdai hunuhuncha bhane, kripaya vishista samasya (jastai: chori, sampatti bibad, bibaha, pakrau, aadi) ra sambandhit sandarbh ullikh garnuhos.",
    }
    
    def get_clarification_response(self, language: str) -> Dict[str, Any]:
        """
        Return a clarification response in the appropriate language.
        """
        message = self.CLARIFICATION_MESSAGES.get(language, self.CLARIFICATION_MESSAGES["en"])
        
        return {
            "answer": message,
            "needs_clarification": True,
            "skipped_llm": True,
            "skipped_retrieval": True,
            "language": language,
        }
    
    def is_query_too_short(self, query: str, min_length: int = 10) -> bool:
        """
        Check if query is too short to be meaningful.
        """
        return len(query.strip()) < min_length
    
    def is_query_too_vague(self, query: str) -> bool:
        """
        Check if query is too vague (e.g., single words, yes/no questions without context).
        """
        vague_patterns = [
            r"^(yes|no|maybe|ok|okay|sure|alright|fine|good|bad|better|worse)$",
            r"^(can i|may i|should i|could i|would i|is it|is this|is that)$",
            r"^(के|किन|कसरी|कहाँ|कुन|को|कहिले|कति)$",
            r"^(हो|होइन|होला|हुन्छ|हुनेछ|हुनुहुन्छ|हुनुपर्छ)$",
            r"^(छ|छैन|छन्)$",
            r"^(ठीक|ठीक छ|ठीक छैन)$",
            r"^(राम्रो|राम्रो छ|राम्रो छैन)$",
            r"^(खराब|खराब छ|खराब छैन)$",
        ]
        
        import re
        query_lower = query.lower().strip()
        
        for pattern in vague_patterns:
            if re.match(pattern, query_lower):
                return True
        
        return False


clarification_service = ClarificationService()
