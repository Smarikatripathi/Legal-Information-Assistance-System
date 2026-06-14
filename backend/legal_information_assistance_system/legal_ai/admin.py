from django.contrib import admin
from django.db.models import Avg, Count
from django.template.response import TemplateResponse

from legal_ai.models import (
    Conversation,
    EmbeddingConfig,
    LegalChunk,
    LegalDocument,
    Message,
    QueryHistory,
)
from legal_ai.services.rag_pipeline import search
from legal_ai.storage.vector_db import FAISSService


class LegalChunkInline(admin.TabularInline):
    model = LegalChunk
    extra = 0
    fields = ("chunk_index", "title", "part", "chapter", "section", "article", "text")
    readonly_fields = fields
    can_delete = False
    max_num = 20
    show_change_link = True


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "document_type",
        "processing_status",
        "page_count",
        "chunk_count",
        "uploaded_at",
    )
    list_filter = ("document_type", "processing_status")
    search_fields = ("title", "description")
    readonly_fields = (
        "extracted_text",
        "cleaned_text",
        "page_count",
        "chunk_count",
        "processing_status",
        "processing_error",
        "pipeline_steps",
        "uploaded_at",
        "pipeline_progress_display",
    )
    inlines = [LegalChunkInline]
    fieldsets = (
        (None, {"fields": ("title", "description", "document_type", "file", "published_year")}),
        ("Processing", {
            "fields": (
                "processing_status",
                "processing_error",
                "page_count",
                "chunk_count",
                "pipeline_progress_display",
                "pipeline_steps",
            ),
        }),
        ("Extracted Content", {
            "classes": ("collapse",),
            "fields": ("extracted_text", "cleaned_text"),
        }),
    )

    @admin.display(description="Pipeline Progress")
    def pipeline_progress_display(self, obj):
        progress = obj.pipeline_progress
        return " | ".join(
            f"{'✓' if v else '✗'} {k.replace('_', ' ').title()}"
            for k, v in progress.items()
        )


@admin.register(LegalChunk)
class LegalChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "doc", "title", "part", "chapter", "section", "article", "chunk_index")
    list_filter = ("doc__document_type", "doc")
    search_fields = ("text", "title", "section", "article", "dhara")
    readonly_fields = ("metadata", "embedding_id")


@admin.register(EmbeddingConfig)
class EmbeddingConfigAdmin(admin.ModelAdmin):
    list_display = ("model_name", "dimension", "is_active", "created_at")
    list_filter = ("is_active",)


@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "query_preview", "confidence_score", "response_time_ms", "created_at")
    list_filter = ("created_at",)
    search_fields = ("query", "answer")
    readonly_fields = ("retrieved_chunks",)

    @admin.display(description="Query")
    def query_preview(self, obj):
        return obj.query[:80]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "updated_at")
    search_fields = ("title", "user__email")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "role", "content_preview", "created_at")
    list_filter = ("role",)

    @admin.display(description="Content")
    def content_preview(self, obj):
        return obj.content[:80]


def retrieval_debugger_view(request):
    """Admin retrieval testing page."""
    results = []
    query = ""
    if request.method == "POST":
        query = request.POST.get("query", "")
        if query:
            results = search(query, top_k=10, min_score=0.0)

    faiss_info = FAISSService().inspect_index()
    return TemplateResponse(
        request,
        "admin/legal_ai/retrieval_debugger.html",
        {"query": query, "results": results, "faiss_info": faiss_info, "title": "Retrieval Debugger"},
    )


def analytics_dashboard_view(request):
    """Admin analytics overview."""
    faiss_info = FAISSService().inspect_index()
    embedding = EmbeddingConfig.objects.filter(is_active=True).first()
    stats = {
        "total_documents": LegalDocument.objects.count(),
        "total_chunks": LegalChunk.objects.count(),
        "total_embeddings": faiss_info.get("total_vectors", 0),
        "total_queries": QueryHistory.objects.count(),
        "total_conversations": Conversation.objects.count(),
        "avg_confidence": QueryHistory.objects.aggregate(v=Avg("confidence_score"))["v"] or 0,
        "avg_response_time": QueryHistory.objects.aggregate(v=Avg("response_time_ms"))["v"] or 0,
        "documents_by_type": list(
            LegalDocument.objects.values("document_type").annotate(count=Count("id"))
        ),
        "top_documents": list(
            LegalChunk.objects.values("doc__title").annotate(count=Count("id")).order_by("-count")[:5]
        ),
        "embedding_model": embedding.model_name if embedding else "Not configured",
        "embedding_dimension": embedding.dimension if embedding else faiss_info.get("dimension", "—"),
        "faiss_status": faiss_info.get("status", "unknown"),
        "index_size_bytes": faiss_info.get("index_file_size_bytes", 0),
        "last_rebuild": faiss_info.get("last_rebuild", "Never"),
    }
    return TemplateResponse(
        request,
        "admin/legal_ai/analytics_dashboard.html",
        {"stats": stats, "title": "RAG Analytics Dashboard"},
    )
