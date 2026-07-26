"""Clarification request handling for ambiguous queries."""

from django.utils import timezone
from typing import Optional, Dict
from dataclasses import dataclass

from legal_information_assistance_system.legal_ai.models import ClarificationRequest, Conversation
from legal_information_assistance_system.legal_ai.understanding.query_analyzer import query_analyzer, QueryAnalysis


@dataclass
class ClarificationResponse:
    """Response when clarification is needed."""
    needs_clarification: bool
    clarification_question: str
    unknown_terms: list
    clarification_id: Optional[int] = None


class ClarificationHandler:
    """Handle clarification requests for unclear queries."""
    
    def __init__(self):
        self.query_analyzer = query_analyzer
    
    def check_clarification_needed(
        self, query: str, conversation_id: int, user_id: int
    ) -> ClarificationResponse:
        """Check if clarification is needed for the query."""
        analysis = self.query_analyzer.analyze(query)
        
        # If query is clear enough, no clarification needed
        if analysis.is_clear:
            return ClarificationResponse(
                needs_clarification=False,
                clarification_question="",
                unknown_terms=[],
            )
        
        # If unknown terms detected, ask for clarification
        if analysis.unknown_terms:
            question = self._generate_clarification_question(query, analysis)
            clarification = self._create_clarification_request(
                conversation_id, query, question, analysis
            )
            
            return ClarificationResponse(
                needs_clarification=True,
                clarification_question=question,
                unknown_terms=analysis.unknown_terms,
                clarification_id=clarification.id if clarification else None,
            )
        
        # If ambiguity detected, ask for clarification
        if analysis.ambiguity_detected:
            question = self._generate_ambiguity_question(query, analysis)
            clarification = self._create_clarification_request(
                conversation_id, query, question, analysis
            )
            
            return ClarificationResponse(
                needs_clarification=True,
                clarification_question=question,
                unknown_terms=[],
                clarification_id=clarification.id if clarification else None,
            )
        
        # Query is clear enough
        return ClarificationResponse(
            needs_clarification=False,
            clarification_question="",
            unknown_terms=[],
        )
    
    def resolve_clarification(
        self, clarification_id: int, user_response: str
    ) -> str:
        """Resolve a clarification request with user's response."""
        try:
            clarification = ClarificationRequest.objects.get(id=clarification_id, status="pending")
            clarification.user_response = user_response
            clarification.status = "resolved"
            clarification.resolved_at = timezone.now()
            clarification.save()
            
            # Combine original query with clarification
            combined_query = f"{clarification.original_query} {user_response}"
            return combined_query
        except ClarificationRequest.DoesNotExist:
            return user_response
    
    def _generate_clarification_question(
        self, query: str, analysis: QueryAnalysis
    ) -> str:
        """Generate a clarification question based on analysis."""
        detected_lang = analysis.legal_entities[0] if analysis.legal_entities else "en"
        
        if analysis.unknown_terms:
            if detected_lang == "ne":
                terms_str = ", ".join(analysis.unknown_terms[:3])
                return f"म केही शब्दहरू बुझ्न सकिनँ: {terms_str}। कृपया यी शब्दहरूको अर्थ स्पष्ट पार्नुहोस्।"
            else:
                terms_str = ", ".join(analysis.unknown_terms[:3])
                return f"I'm not sure what you mean by: {terms_str}. Could you clarify what you're referring to?"
        
        return "Could you please provide more details about your question?"
    
    def _generate_ambiguity_question(
        self, query: str, analysis: QueryAnalysis
    ) -> str:
        """Generate a question to resolve ambiguity."""
        detected_lang = analysis.legal_entities[0] if analysis.legal_entities else "en"
        
        if detected_lang == "ne":
            return "तपाईंको प्रश्न केही अस्पष्ट छ। कृपया थप जानकारी प्रदान गर्नुहोस्।"
        else:
            return "Your question is a bit unclear. Could you provide more specific details?"
    
    def _create_clarification_request(
        self, conversation_id: int, query: str, question: str, analysis: QueryAnalysis
    ) -> Optional[ClarificationRequest]:
        """Create a clarification request record."""
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            clarification = ClarificationRequest.objects.create(
                conversation=conversation,
                original_query=query,
                clarification_question=question,
                unknown_terms=analysis.unknown_terms,
                ambiguity_detected=analysis.ambiguity_detected,
                clarity_score=analysis.clarity_score,
            )
            return clarification
        except Conversation.DoesNotExist:
            return None


# Global instance
clarification_handler = ClarificationHandler()
