from rest_framework import serializers
from legal_ai.models import LegalDocument

class LegalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = "__all__"