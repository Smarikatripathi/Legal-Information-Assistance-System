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
    SourceReferenceSerializer,
)
from legal_information_assistance_system.legal_ai.models import (
    Conversation,
    LegalDocument,
    Message,
    QueryHistory,
    SourceReference,
)
from legal_information_assistance_system.legal_ai.services.rag import answer_query
from legal_information_assistance_system.legal_ai.services.llm import correct_typos
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
        try:
            serializer = QuerySerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            query = serializer.validated_data["query"]
            # Correct common typos (e.g., "atq" -> "atm")
            corrected_query = correct_typos(query)
            top_k = serializer.validated_data.get("top_k", 5)
            conversation_id = serializer.validated_data.get("conversation_id")

            # Get or create conversation
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

            # Save user message
            Message.objects.create(
                conversation=conversation,
                role="user",
                content=query,
            )

            # Use simplified RAG pipeline
            response = answer_query(
                query=corrected_query,
                top_k=top_k,
                conversation_id=conversation.id,
                user_id=request.user.id,
            )

            # Handle out-of-scope queries
            if response.get("out_of_scope"):
                Message.objects.create(
                    conversation=conversation,
                    role="assistant",
                    content=response["answer"],
                )
                response["conversation_id"] = conversation.id
                return Response(response)

            # Save assistant response for normal answers
            Message.objects.create(
                conversation=conversation,
                role="assistant",
                content=response["answer"],
            )

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
        
        except Exception as e:
            import traceback
            print(f"Error in LegalQueryView: {e}")
            print(traceback.format_exc())
            return Response(
                {"error": "An error occurred while processing your query. Please try again.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.query_params.get("search", "")
        conversations = Conversation.objects.filter(user=request.user)
        if search:
            conversations = conversations.filter(title__icontains=search)
        conversations = conversations.order_by('-updated_at')[:50]
        return Response(ConversationSerializer(conversations, many=True).data)

    def post(self, request):
        title = request.data.get("title", "New conversation")
        conv = Conversation.objects.create(user=request.user, title=title)
        return Response(ConversationSerializer(conv).data, status=status.HTTP_201_CREATED)


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        conv = Conversation.objects.filter(id=pk, user=request.user).first()
        if not conv:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        messages = conv.messages.all().order_by('created_at')
        return Response({
            "conversation": ConversationSerializer(conv).data,
            "messages": MessageSerializer(messages, many=True).data,
        })

    def patch(self, request, pk):
        conv = Conversation.objects.filter(id=pk, user=request.user).first()
        if not conv:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if 'title' in request.data:
            conv.title = request.data['title']
        if 'is_archived' in request.data:
            conv.is_archived = request.data['is_archived']
        
        conv.save()
        return Response(ConversationSerializer(conv).data)

    def delete(self, request, pk):
        conv = Conversation.objects.filter(id=pk, user=request.user).first()
        if not conv:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        conv.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class QueryHistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = QueryHistory.objects.filter(user=request.user).select_related('conversation').prefetch_related('conversation__messages')[:100]
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
