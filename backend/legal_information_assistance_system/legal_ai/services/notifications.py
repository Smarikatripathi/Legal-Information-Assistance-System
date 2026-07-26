"""Notification service for admin alerts."""

from typing import Optional, Dict, Any
from django.utils import timezone

from legal_information_assistance_system.legal_ai.models import (
    AdminNotification,
    KnowledgeGap,
    LegalDocument,
)


class NotificationService:
    """Service for creating and managing admin notifications."""
    
    def create_knowledge_gap_notification(
        self,
        knowledge_gap: KnowledgeGap,
        severity: str = "medium"
    ) -> AdminNotification:
        """Create a notification for a new knowledge gap."""
        title = f"New Knowledge Gap: {knowledge_gap.query[:50]}..."
        message = (
            f"A user query could not be answered from the current knowledge base.\n\n"
            f"Query: {knowledge_gap.query}\n"
            f"Language: {knowledge_gap.detected_language}\n"
            f"Relevance Score: {max(knowledge_gap.relevance_scores) if knowledge_gap.relevance_scores else 0:.2f}\n"
            f"Chunks Retrieved: {knowledge_gap.retrieval_results.get('count', 0)}\n\n"
            f"Please review and determine if new documents are needed."
        )
        
        notification = AdminNotification.objects.create(
            notification_type="knowledge_gap",
            severity=severity,
            title=title,
            message=message,
            knowledge_gap=knowledge_gap,
            metadata={
                "query": knowledge_gap.query,
                "normalized_query": knowledge_gap.normalized_query,
                "detected_language": knowledge_gap.detected_language,
                "relevance_scores": knowledge_gap.relevance_scores,
                "chunks_count": knowledge_gap.retrieval_results.get('count', 0),
            }
        )
        return notification
    
    def create_document_failed_notification(
        self,
        document: LegalDocument,
        error_message: str,
        severity: str = "high"
    ) -> AdminNotification:
        """Create a notification for document processing failure."""
        title = f"Document Processing Failed: {document.title[:50]}..."
        message = (
            f"Failed to process document: {document.title}\n\n"
            f"Source: {document.source_url or 'Upload'}\n"
            f"Error: {error_message}\n\n"
            f"Please check the document and try reprocessing."
        )
        
        notification = AdminNotification.objects.create(
            notification_type="document_failed",
            severity=severity,
            title=title,
            message=message,
            legal_document=document,
            metadata={
                "document_id": document.id,
                "document_title": document.title,
                "source_url": document.source_url,
                "error": error_message,
            }
        )
        return notification
    
    def create_index_rebuilt_notification(
        self,
        chunk_count: int,
        model_name: str,
        severity: str = "low"
    ) -> AdminNotification:
        """Create a notification for FAISS index rebuild."""
        title = f"FAISS Index Rebuilt Successfully"
        message = (
            f"The vector index has been rebuilt.\n\n"
            f"Chunks Indexed: {chunk_count}\n"
            f"Embedding Model: {model_name}\n\n"
            f"The system is ready for queries."
        )
        
        notification = AdminNotification.objects.create(
            notification_type="index_rebuilt",
            severity=severity,
            title=title,
            message=message,
            metadata={
                "chunk_count": chunk_count,
                "model_name": model_name,
            }
        )
        return notification
    
    def create_system_alert_notification(
        self,
        title: str,
        message: str,
        severity: str = "high",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AdminNotification:
        """Create a general system alert notification."""
        notification = AdminNotification.objects.create(
            notification_type="system_alert",
            severity=severity,
            title=title,
            message=message,
            metadata=metadata or {}
        )
        return notification
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark a notification as read."""
        try:
            notification = AdminNotification.objects.get(id=notification_id)
            notification.status = "read"
            notification.read_at = timezone.now()
            notification.save()
            return True
        except AdminNotification.DoesNotExist:
            return False
    
    def mark_all_as_read(self) -> int:
        """Mark all unread notifications as read."""
        count = AdminNotification.objects.filter(status="unread").update(
            status="read",
            read_at=timezone.now()
        )
        return count
    
    def dismiss_notification(self, notification_id: int) -> bool:
        """Dismiss a notification."""
        try:
            notification = AdminNotification.objects.get(id=notification_id)
            notification.status = "dismissed"
            notification.read_at = timezone.now()
            notification.save()
            return True
        except AdminNotification.DoesNotExist:
            return False
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications."""
        return AdminNotification.objects.filter(status="unread").count()
    
    def get_high_priority_count(self) -> int:
        """Get count of high/critical priority unread notifications."""
        return AdminNotification.objects.filter(
            status="unread",
            severity__in=["high", "critical"]
        ).count()


# Global instance
notification_service = NotificationService()
