from rest_framework.views import APIView
from rest_framework.response import Response

from legal_ai.models import LegalDocument
from legal_ai.api.serializers import LegalDocumentSerializer

from legal_ai.services.rag_pipeline import generate_answer, process_pdf, search


# ------------------------
# PDF UPLOAD API
# ------------------------
class UploadPDFView(APIView):

    def post(self, request):
        serializer = LegalDocumentSerializer(data=request.data)

        if serializer.is_valid():
            doc = serializer.save()

            process_pdf(doc.id, doc.file.path)

            return Response({
                "message": "PDF uploaded & processed successfully"
            })

        return Response(serializer.errors, status=400)


# ------------------------
# LEGAL QUERY API
# ------------------------
class LegalQueryView(APIView):

    def post(self, request):
        query = request.data.get("query")

        chunks = search(query)

        context = "\n\n".join([c.text for c in chunks])

        # later replace this with LLM
        answer = generate_answer(query, context)

        return Response({
            "query": query,
            "context": context,
            "answer": answer,
            "sources": [c.id for c in chunks]
        })