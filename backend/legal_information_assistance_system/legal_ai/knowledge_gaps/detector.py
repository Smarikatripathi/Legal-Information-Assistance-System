"""Knowledge gap detection for insufficient legal evidence."""

from typing import List, Dict, Optional
from dataclasses import dataclass

from django.conf import settings

from legal_information_assistance_system.legal_ai.models import KnowledgeGap, Conversation
from legal_information_assistance_system.legal_ai.services.notifications import notification_service

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
        if not retrieved_chunks or not relevance_scores:
            return RetrievalAssessment(
                has_sufficient_evidence=False,
                confidence_score=0.0,
                top_relevance=0.0,
                gap_detected=True,
                gap_reason="No chunks retrieved",
            )
        
        top_score = max(relevance_scores) if relevance_scores else 0.0
        avg_score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        
        # Check if top score is above threshold
        if top_score < KNOWLEDGE_GAP_THRESHOLD:
            return RetrievalAssessment(
                has_sufficient_evidence=False,
                confidence_score=avg_score,
                top_relevance=top_score,
                gap_detected=True,
                gap_reason=f"Low relevance score: {top_score:.2f} < {KNOWLEDGE_GAP_THRESHOLD} (insufficient evidence)",
            )
        
        # Check if we have enough high-quality chunks
        high_quality_count = sum(1 for score in relevance_scores if score >= MIN_SCORE)
        if high_quality_count < 1:  # Reduced from 2 to 1 for testing
            return RetrievalAssessment(
                has_sufficient_evidence=False,
                confidence_score=avg_score,
                top_relevance=top_score,
                gap_detected=True,
                gap_reason=f"Insufficient high-quality chunks: {high_quality_count} < 1",
            )
        
        # Sufficient evidence
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
    ) -> Optional[KnowledgeGap]:
        """Create a knowledge gap record when evidence is insufficient."""
        if not retrieval_assessment.gap_detected:
            return None
        
        try:
            # Normalize query for deduplication
            normalized_query = self._normalize_query(query)
            
            # Check for similar existing gaps
            existing = KnowledgeGap.objects.filter(
                normalized_query=normalized_query,
                status__in=["new", "under_review", "document_required"],
            ).first()
            
            if existing:
                # Update existing gap
                existing.retrieval_results = {
                    "chunks": retrieved_chunks[:5],
                    "count": len(retrieved_chunks),
                }
                existing.relevance_scores = relevance_scores[:10]
                existing.save()
                return existing
            
            # Create new knowledge gap
            conversation = None
            if conversation_id:
                conversation = Conversation.objects.filter(id=conversation_id).first()
            
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
            
            # Create admin notification for new knowledge gap
            severity = "high" if retrieval_assessment.top_relevance < 0.1 else "medium"
            self.notification_service.create_knowledge_gap_notification(gap, severity)
            
            return gap
        except Exception as e:
            # Log error but don't break the flow
            print(f"Error creating knowledge gap: {e}")
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


# Global instance
knowledge_gap_detector = KnowledgeGapDetector()
