"""Conversation context management for multi-turn legal queries."""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from legal_information_assistance_system.legal_ai.models import Conversation, Message


@dataclass
class ConversationContext:
    """Context from conversation history."""
    conversation_id: int
    user_id: int
    messages: List[Dict]
    last_query: Optional[str]
    last_response: Optional[str]
    query_count: int
    language: str


class ConversationManager:
    """Manage conversation context for clarification and multi-turn queries."""
    
    def __init__(self):
        pass
    
    def get_context(self, conversation_id: int, user_id: int) -> Optional[ConversationContext]:
        """Get conversation context for a given conversation."""
        try:
            conversation = Conversation.objects.get(id=conversation_id, user_id=user_id)
            messages = conversation.messages.all().order_by('created_at')
            
            message_list = []
            for msg in messages:
                message_list.append({
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat(),
                })
            
            last_user_msg = messages.filter(role='user').last()
            last_assistant_msg = messages.filter(role='assistant').last()
            
            # Detect language from last user message
            language = 'en'
            if last_user_msg:
                from legal_information_assistance_system.legal_ai.services.language import language_service
                language = language_service.detect_language(last_user_msg.content)
            
            return ConversationContext(
                conversation_id=conversation.id,
                user_id=user_id,
                messages=message_list,
                last_query=last_user_msg.content if last_user_msg else None,
                last_response=last_assistant_msg.content if last_assistant_msg else None,
                query_count=messages.filter(role='user').count(),
                language=language,
            )
        except Conversation.DoesNotExist:
            return None
    
    def combine_query_with_context(
        self, current_query: str, context: ConversationContext
    ) -> str:
        """Combine current query with conversation context."""
        if not context.last_query or context.query_count < 2:
            return current_query
        
        # If this is a clarification response, combine with original query
        if self._is_clarification_response(current_query, context):
            combined = f"{context.last_query} {current_query}"
            return combined
        
        # Otherwise, return current query as-is
        return current_query
    
    def _is_clarification_response(self, query: str, context: ConversationContext) -> bool:
        """Check if current query is a clarification response."""
        if not context.last_response:
            return False
        
        # Check if last assistant message was asking for clarification
        clarification_indicators = [
            "clarify", "what do you mean", "could you specify",
            "स्पष्ट", "के भन्नुहुन्छ", "बताउनुहोस्",
            "unclear", "not sure",
        ]
        
        last_response_lower = context.last_response.lower()
        for indicator in clarification_indicators:
            if indicator in last_response_lower:
                return True
        
        return False
    
    def get_conversation_summary(self, conversation_id: int, user_id: int) -> str:
        """Generate a summary of the conversation for context."""
        context = self.get_context(conversation_id, user_id)
        if not context:
            return ""
        
        if context.query_count <= 1:
            return ""
        
        # Get recent queries (last 3)
        recent_messages = context.messages[-6:] if len(context.messages) > 6 else context.messages
        
        summary_parts = []
        for msg in recent_messages:
            if msg['role'] == 'user':
                summary_parts.append(f"User: {msg['content']}")
        
        return " | ".join(summary_parts)
    
    def should_continue_conversation(self, context: ConversationContext) -> bool:
        """Determine if conversation should continue (has relevant context)."""
        if context.query_count < 2:
            return False
        
        # Check if recent messages are related
        if len(context.messages) >= 4:
            last_two_user = [m for m in context.messages[-4:] if m['role'] == 'user']
            if len(last_two_user) >= 2:
                # Simple check: if last query is very short, it might be clarification
                if len(last_two_user[-1]['content'].split()) <= 3:
                    return True
        
        return False


# Global instance
conversation_manager = ConversationManager()
