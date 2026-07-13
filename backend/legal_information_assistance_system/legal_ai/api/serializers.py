from rest_framework import serializers

from legal_information_assistance_system.legal_ai.models import Conversation, LegalDocument, Message, QueryHistory


class LegalDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = [
            "title",
            "description",
            "document_type",
            "file",
            "published_year",
        ]


class LegalDocumentSerializer(serializers.ModelSerializer):
    pipeline_progress = serializers.ReadOnlyField()

    class Meta:
        model = LegalDocument
        fields = [
            "id",
            "title",
            "description",
            "document_type",
            "published_year",
            "uploaded_at",
            "page_count",
            "chunk_count",
            "processing_status",
            "pipeline_progress",
        ]


class QuerySerializer(serializers.Serializer):
    query = serializers.CharField(max_length=2000)
    top_k = serializers.IntegerField(required=False, min_value=1, max_value=20, default=5)
    conversation_id = serializers.IntegerField(required=False, allow_null=True)


class ConversationSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "title", "created_at", "updated_at", "message_count"]
        read_only_fields = ["created_at", "updated_at"]

    def get_message_count(self, obj):
        return obj.messages.count()


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "created_at"]
        read_only_fields = ["created_at"]


class QueryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryHistory
        fields = [
            "id",
            "query",
            "answer",
            "sources",
            "confidence_score",
            "response_time_ms",
            "created_at",
        ]

    sources = serializers.SerializerMethodField()

    def get_sources(self, obj):
        return obj.retrieved_chunks
