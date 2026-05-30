from rest_framework import serializers
from legal_ai.models import LegalDocument


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


class QuerySerializer(serializers.Serializer):
    query = serializers.CharField(max_length=2000)
    top_k = serializers.IntegerField(required=False, min_value=1, max_value=20, default=5)


class LegalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = "__all__"