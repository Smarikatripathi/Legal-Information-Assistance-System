"""Knowledge gap detection and tracking for legal RAG system."""

from legal_information_assistance_system.legal_ai.knowledge_gaps.detector import knowledge_gap_detector
from legal_information_assistance_system.legal_ai.knowledge_gaps.services import KnowledgeGapsService

__all__ = ["knowledge_gap_detector", "KnowledgeGapsService"]
