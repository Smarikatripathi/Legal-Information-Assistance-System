"""Knowledge gap detection for insufficient legal evidence."""

from typing import List, Dict, Optional
from dataclasses import dataclass

from django.conf import settings

from legal_information_assistance_system.legal_ai.models import KnowledgeGap, Conversation
from legal_information_assistance_system.legal_ai.services.notifications import notification_service
from legal_information_assistance_system.legal_ai.services.llm import llm

# Configuration values (previously from pipeline.config)
KNOWLEDGE_GAP_THRESHOLD = getattr(settings, "RAG_KNOWLEDGE_GAP_THRESHOLD", 0.65)  # Match retrieval threshold
MIN_SCORE = getattr(settings, "RAG_MIN_SCORE", 0.65)  # Match retrieval threshold


@dataclass
class RetrievalAssessment:
    """Assessment of retrieval quality."""
    has_sufficient_evidence: bool
    confidence_score: float
    top_relevance: float
    gap_detected: bool
    gap_reason: str


class KnowledgeGapDetector:
    """Detect when queries cannot be answered from current knowledge base."""
    
    def __init__(self):
        self.notification_service = notification_service
    
    def assess_retrieval(
        self, query: str, retrieved_chunks: List[Dict], relevance_scores: List[float]
    ) -> RetrievalAssessment:
        """Assess if retrieved chunks provide sufficient evidence."""
        print(f"DEBUG: assess_retrieval called with {len(retrieved_chunks)} chunks")
        print(f"DEBUG: Relevance scores: {relevance_scores}")
        print(f"DEBUG: KNOWLEDGE_GAP_THRESHOLD: {KNOWLEDGE_GAP_THRESHOLD}")
        print(f"DEBUG: MIN_SCORE: {MIN_SCORE}")
        
        if not retrieved_chunks or not relevance_scores:
            print(f"DEBUG: No chunks or scores, returning gap_detected=True")
            return RetrievalAssessment(
                has_sufficient_evidence=False,
                confidence_score=0.0,
                top_relevance=0.0,
                gap_detected=True,
                gap_reason="No chunks retrieved",
            )
        
        top_score = max(relevance_scores) if relevance_scores else 0.0
        avg_score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        print(f"DEBUG: Top score: {top_score}, Avg score: {avg_score}")
        
        # Check if top score is above threshold
        if top_score < KNOWLEDGE_GAP_THRESHOLD:
            print(f"DEBUG: Top score below threshold, gap_detected=True")
            return RetrievalAssessment(
                has_sufficient_evidence=False,
                confidence_score=avg_score,
                top_relevance=top_score,
                gap_detected=True,
                gap_reason=f"Low relevance score: {top_score:.2f} < {KNOWLEDGE_GAP_THRESHOLD} (insufficient evidence)",
            )
        
        # Check if we have enough high-quality chunks
        high_quality_count = sum(1 for score in relevance_scores if score >= MIN_SCORE)
        print(f"DEBUG: High quality chunks count: {high_quality_count}")
        if high_quality_count < 1:  # Reduced from 2 to 1 for testing
            print(f"DEBUG: Insufficient high-quality chunks, gap_detected=True")
            return RetrievalAssessment(
                has_sufficient_evidence=False,
                confidence_score=avg_score,
                top_relevance=top_score,
                gap_detected=True,
                gap_reason=f"Insufficient high-quality chunks: {high_quality_count} < 1",
            )
        
        # Sufficient evidence
        print(f"DEBUG: Sufficient evidence, gap_detected=False")
        return RetrievalAssessment(
            has_sufficient_evidence=True,
            confidence_score=avg_score,
            top_relevance=top_score,
            gap_detected=False,
            gap_reason="",
        )
    
    def create_knowledge_gap(
        self,
        user_id: int,
        conversation_id: Optional[int],
        query: str,
        retrieval_assessment: RetrievalAssessment,
        retrieved_chunks: List[Dict],
        relevance_scores: List[float],
        detected_language: str = "en",
        force_create: bool = False,
    ) -> Optional[KnowledgeGap]:
        """Create a knowledge gap record when evidence is insufficient.
        
        Args:
            force_create: If True, create knowledge gap even if retrieval_assessment.gap_detected is False
                         (used when LLM semantically detects a gap that score-based detector missed)
        """
        print(f"DEBUG: create_knowledge_gap called with gap_detected={retrieval_assessment.gap_detected}, force_create={force_create}")
        if not retrieval_assessment.gap_detected and not force_create:
            print(f"DEBUG: Gap not detected and force_create=False, returning None")
            return None
        
        try:
            # Normalize query for deduplication
            normalized_query = self._normalize_query(query)
            print(f"DEBUG: Normalized query: {normalized_query}")
            
            # Check for similar existing gaps
            existing = KnowledgeGap.objects.filter(
                normalized_query=normalized_query,
                status__in=["new", "under_review", "document_required"],
            ).first()
            
            if existing:
                print(f"DEBUG: Found existing knowledge gap, updating it")
                # Update existing gap
                existing.retrieval_results = {
                    "chunks": retrieved_chunks[:5],
                    "count": len(retrieved_chunks),
                }
                existing.relevance_scores = relevance_scores[:10]
                existing.save()
                print(f"DEBUG: Existing gap updated, NOT creating notification")
                return existing
            
            # Create new knowledge gap
            conversation = None
            if conversation_id:
                conversation = Conversation.objects.filter(id=conversation_id).first()
            
            print(f"DEBUG: Creating new knowledge gap record")
            gap = KnowledgeGap.objects.create(
                user_id=user_id if user_id else None,
                conversation=conversation,
                query=query,
                normalized_query=normalized_query,
                detected_language=detected_language,
                retrieval_results={
                    "chunks": retrieved_chunks[:5],
                    "count": len(retrieved_chunks),
                },
                relevance_scores=relevance_scores[:10],
                top_chunks=retrieved_chunks[:3],
                status="new",
                document_required=retrieval_assessment.top_relevance < 0.1,
            )
            print(f"DEBUG: Knowledge gap created with ID: {gap.id}")
            
            # Create admin notification for new knowledge gap
            severity = "high" if retrieval_assessment.top_relevance < 0.1 else "medium"
            print(f"DEBUG: About to create notification with severity: {severity}")
            print(f"DEBUG: Top relevance: {retrieval_assessment.top_relevance}")
            notification = self.notification_service.create_knowledge_gap_notification(gap, severity)
            print(f"DEBUG: Notification created with ID: {notification.id}")
            
            return gap
        except Exception as e:
            # Log error but don't break the flow
            print(f"ERROR: Error creating knowledge gap: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for deduplication."""
        import re
        # Lowercase
        normalized = query.lower()
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        return normalized
    
    def should_trigger_gap_notification(self, gap: KnowledgeGap) -> bool:
        """Determine if a gap should trigger admin notification."""
        # Notify for new gaps with very low relevance
        if gap.status == "new" and gap.relevance_scores:
            if gap.relevance_scores and max(gap.relevance_scores) < 0.15:
                return True
        
        # Notify for gaps requiring documents
        if gap.document_required and gap.status == "new":
            return True
        
        return False
    
    def semantically_detect_knowledge_gap(self, llm_response: str) -> bool:
        """Use LLM to semantically classify if response indicates a knowledge gap.
        
        This is more robust than phrase matching as it understands the meaning
        regardless of specific wording.
        
        Args:
            llm_response: The LLM's response to the user's question
            
        Returns:
            True if the response indicates information is unavailable, False otherwise
        """
        print(f"DEBUG: Semantic classification of LLM response")
        print(f"DEBUG: Response preview: {llm_response[:200]}...")
        
        classification_prompt = f"""You are a semantic classifier for legal AI responses.

Your job is to determine if the following AI response indicates that the requested information is NOT available in the retrieved legal documents.

Response to classify:
{llm_response}

Return ONLY one word:
- "GAP" if the response indicates information is unavailable, insufficient, or not found
- "OK" if the response provides a valid answer from legal documents

Examples that should return "GAP":
- "The information is not available in the retrieved context."
- "The retrieved context does not contain sufficient information."
- "There is no specific information regarding this topic."
- "The current legal documents do not answer this question."

Examples that should return "OK":
- "According to Article 18, citizens have the right to..."
- "The Constitution provides that..."
- "Section 242 states that..."

Classification:"""

        try:
            classification = llm.generate_from_prompt(classification_prompt, query_language="en")
            classification = classification.strip().upper()
            print(f"DEBUG: Semantic classification result: {classification}")
            
            is_gap = classification == "GAP"
            print(f"DEBUG: Knowledge gap detected semantically: {is_gap}")
            
            return is_gap
        except Exception as e:
            print(f"ERROR: Semantic classification failed: {e}")
            import traceback
            print(traceback.format_exc())
            # Fall back to False (don't trigger notification) on error
            return False


# Global instance
knowledge_gap_detector = KnowledgeGapDetector()
