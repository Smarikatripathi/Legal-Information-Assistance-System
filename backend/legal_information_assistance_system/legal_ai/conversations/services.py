"""Conversation service for managing chat conversations and message history."""

from typing import List, Optional
from django.utils import timezone

from legal_information_assistance_system.legal_ai.models import Conversation, Message


class ConversationService:
    """Service for managing conversations and messages."""
    
    @staticmethod
    def create_conversation(user, title: str = "New conversation") -> Conversation:
        """Create a new conversation for a user."""
        return Conversation.objects.create(user=user, title=title)
    
    @staticmethod
    def get_user_conversations(user, search: Optional[str] = None, limit: int = 50) -> List[Conversation]:
        """Get conversations for a user, optionally filtered by search."""
        qs = Conversation.objects.filter(user=user).prefetch_related('messages')
        
        if search:
            qs = qs.filter(
                title__icontains=search
            ).distinct()
        
        return list(qs[:limit])
    
    @staticmethod
    def get_conversation(conversation_id: int, user) -> Optional[Conversation]:
        """Get a specific conversation for a user."""
        return Conversation.objects.filter(id=conversation_id, user=user).prefetch_related('messages').first()
    
    @staticmethod
    def update_conversation(conversation_id: int, user, **kwargs) -> Optional[Conversation]:
        """Update conversation fields (title, is_archived)."""
        conv = Conversation.objects.filter(id=conversation_id, user=user).first()
        if conv:
            for key, value in kwargs.items():
                if hasattr(conv, key):
                    setattr(conv, key, value)
            conv.save()
        return conv
    
    @staticmethod
    def delete_conversation(conversation_id: int, user) -> bool:
        """Delete a conversation."""
        deleted, _ = Conversation.objects.filter(id=conversation_id, user=user).delete()
        return deleted > 0
    
    @staticmethod
    def add_message(conversation: Conversation, role: str, content: str) -> Message:
        """Add a message to a conversation."""
        message = Message.objects.create(
            conversation=conversation,
            role=role,
            content=content,
        )
        # Update conversation timestamp
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=['updated_at'])
        return message
    
    @staticmethod
    def get_conversation_messages(conversation: Conversation) -> List[Message]:
        """Get all messages for a conversation in order."""
        return list(conversation.messages.all().order_by('created_at'))
    
    @staticmethod
    def get_conversation_context(conversation: Conversation, limit: int = 10) -> List[dict]:
        """Get recent conversation context for RAG processing."""
        messages = conversation.messages.all().order_by('-created_at')[:limit]
        return [
            {
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.isoformat(),
            }
            for msg in reversed(messages)
        ]


# Singleton instance
conversation_service = ConversationService()
