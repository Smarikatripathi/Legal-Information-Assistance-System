from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from legal_ai.api.serializers import LegalDocumentUploadSerializer, QuerySerializer
from legal_ai.services.rag_pipeline import answer_query, process_pdf


# ------------------------
# PDF UPLOAD API
# ------------------------
class UploadPDFView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = LegalDocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        document = serializer.save()
        result = process_pdf(document.id)

        if result.get("status") != "success":
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                "message": "PDF uploaded and indexed successfully.",
                "document_id": document.id,
                "chunk_count": result.get("chunk_count", 0),
            },
            status=status.HTTP_201_CREATED,
        )


# ------------------------
# LEGAL QUERY API
# ------------------------
class LegalQueryView(APIView):

    def post(self, request):
        serializer = QuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        query = serializer.validated_data["query"]
        top_k = serializer.validated_data.get("top_k", 5)

        response = answer_query(query, top_k=top_k)
        return Response(response)


