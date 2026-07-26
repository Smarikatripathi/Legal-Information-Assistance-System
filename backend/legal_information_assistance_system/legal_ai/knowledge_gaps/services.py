"""Knowledge Gaps Service - Manages knowledge gap detection and tracking."""

from typing import List, Optional, Dict
from dataclasses import dataclass

from legal_information_assistance_system.legal_ai.models import KnowledgeGap
from legal_information_assistance_system.legal_ai.knowledge_gaps.detector import knowledge_gap_detector, RetrievalAssessment


@dataclass
class KnowledgeGapAssessment:
    """Assessment of knowledge gap for a query."""
    gap_detected: bool
    gap_reason: str
    confidence_score: float
    top_relevance: float
    avg_relevance: float


class KnowledgeGapsService:
    """Service for managing knowledge gaps."""
    
    def __init__(self):
        self.detector = knowledge_gap_detector
    
    def assess_retrieval(
        self,
        query: str,
        retrieved_chunks: List[Dict],
        relevance_scores: List[float],
    ) -> KnowledgeGapAssessment:
        """Assess if there's a knowledge gap based on retrieval results.
        
        Args:
            query: The user's query
            retrieved_chunks: Retrieved document chunks
            relevance_scores: Relevance scores for chunks
            
        Returns:
            KnowledgeGapAssessment with gap information
        """
        assessment = self.detector.assess_retrieval(query, retrieved_chunks, relevance_scores)
        
        return KnowledgeGapAssessment(
            gap_detected=assessment.gap_detected,
            gap_reason=assessment.gap_reason,
            confidence_score=assessment.confidence_score,
            top_relevance=assessment.top_relevance,
            avg_relevance=assessment.avg_relevance,
        )
    
    def create_knowledge_gap(
        self,
        user_id: Optional[int],
        conversation_id: Optional[int],
        query: str,
        retrieval_assessment: KnowledgeGapAssessment,
        retrieved_chunks: List[Dict],
        relevance_scores: List[float],
        detected_language: str = 'en',
    ) -> KnowledgeGap:
        """Create a knowledge gap record.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            query: The query that caused the gap
            retrieval_assessment: Assessment of the gap
            retrieved_chunks: Retrieved chunks
            relevance_scores: Relevance scores
            detected_language: Detected language
            
        Returns:
            KnowledgeGap instance
        """
        # Convert to RetrievalAssessment format for detector
        from legal_information_assistance_system.legal_ai.knowledge_gaps.detector import RetrievalAssessment
        detector_assessment = RetrievalAssessment(
            gap_detected=retrieval_assessment.gap_detected,
            gap_reason=retrieval_assessment.gap_reason,
            confidence_score=retrieval_assessment.confidence_score,
            top_relevance=retrieval_assessment.top_relevance,
            avg_relevance=retrieval_assessment.avg_relevance,
        )
        
        return self.detector.create_knowledge_gap(
            user_id=user_id,
            conversation_id=conversation_id,
            query=query,
            retrieval_assessment=detector_assessment,
            retrieved_chunks=retrieved_chunks,
            relevance_scores=relevance_scores,
            detected_language=detected_language,
        )
    
    def list_knowledge_gaps(
        self,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[KnowledgeGap]:
        """List knowledge gaps, optionally filtered.
        
        Args:
            user_id: Optional user filter
            status: Optional status filter
            limit: Maximum results
            
        Returns:
            List of KnowledgeGap instances
        """
        qs = KnowledgeGap.objects.all()
        if user_id:
            qs = qs.filter(user_id=user_id)
        if status:
            qs = qs.filter(status=status)
        return list(qs[:limit])
    
    def update_knowledge_gap(
        self,
        gap_id: int,
        status: Optional[str] = None,
        resolution: Optional[str] = None,
        admin_notes: Optional[str] = None,
    ) -> Optional[KnowledgeGap]:
        """Update a knowledge gap record.
        
        Args:
            gap_id: Knowledge gap ID
            status: New status
            resolution: Resolution text
            admin_notes: Admin notes
            
        Returns:
            Updated KnowledgeGap or None
        """
        gap = KnowledgeGap.objects.filter(id=gap_id).first()
        if gap:
            if status:
                gap.status = status
            if resolution:
                gap.resolution = resolution
            if admin_notes:
                gap.admin_notes = admin_notes
            gap.save()
        return gap


# Global instance
knowledge_gaps_service = KnowledgeGapsService()
