from django.db.models import Q
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from legal_information_assistance_system.legal_ai.api.serializers import (
    ConversationSerializer,
    LegalDocumentSerializer,
    LegalDocumentUploadSerializer,
    MessageSerializer,
    QueryHistorySerializer,
    QuerySerializer,
)
from legal_information_assistance_system.legal_ai.models import Conversation, LegalDocument, Message, QueryHistory
from legal_information_assistance_system.legal_ai.services.rag_pipeline import answer_query
from legal_information_assistance_system.legal_ai.tasks import crawl_law_commission, process_document_embeddings


class UploadPDFView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = LegalDocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        document = serializer.save()
        process_document_embeddings.delay(document.id)

        return Response(
            {
                "message": "PDF uploaded. Processing in background.",
                "document_id": document.id,
                "processing_status": "pending",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        docs = LegalDocument.objects.all()
        return Response(LegalDocumentSerializer(docs, many=True).data)


class LegalQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        query = serializer.validated_data["query"]
        top_k = serializer.validated_data.get("top_k", 5)
        conversation_id = serializer.validated_data.get("conversation_id")

        conversation = None
        if conversation_id:
            conversation = Conversation.objects.filter(
                id=conversation_id, user=request.user
            ).first()

        if conversation is None:
            conversation = Conversation.objects.create(
                user=request.user,
                title=query[:80],
            )

        Message.objects.create(conversation=conversation, role="user", content=query)

        response = answer_query(query, top_k=top_k)

        Message.objects.create(conversation=conversation, role="assistant", content=response["answer"])
        conversation.save(update_fields=["updated_at"])

        QueryHistory.objects.create(
            user=request.user,
            conversation=conversation,
            query=query,
            answer=response["answer"],
            retrieved_chunks=response.get("sources", []),
            confidence_score=response.get("confidence_score", 0),
            response_time_ms=response.get("response_time_ms", 0),
        )

        response["conversation_id"] = conversation.id
        return Response(response)


class ConversationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.query_params.get("search", "")
        qs = Conversation.objects.filter(user=request.user)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(messages__content__icontains=search)).distinct()
        return Response(ConversationSerializer(qs[:50], many=True).data)

    def post(self, request):
        title = request.data.get("title", "New conversation")
        conv = Conversation.objects.create(user=request.user, title=title)
        return Response(ConversationSerializer(conv).data, status=status.HTTP_201_CREATED)


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        conv = Conversation.objects.filter(pk=pk, user=request.user).first()
        if not conv:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        messages = conv.messages.all()
        return Response({
            "conversation": ConversationSerializer(conv).data,
            "messages": MessageSerializer(messages, many=True).data,
        })

    def delete(self, request, pk):
        deleted, _ = Conversation.objects.filter(pk=pk, user=request.user).delete()
        if not deleted:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class QueryHistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = QueryHistory.objects.filter(user=request.user)[:100]
        return Response(QueryHistorySerializer(qs, many=True).data)


class CrawlLawCommissionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        max_pages = int(request.data.get("max_pages", 50))
        task = crawl_law_commission.delay(max_pages=max_pages)
        return Response(
            {
                "message": "Law Commission PDF download started. Run ingest_pdfs after crawl completes.",
                "task_id": task.id,
                "max_pages": max_pages,
            },
            status=status.HTTP_202_ACCEPTED,
        )
