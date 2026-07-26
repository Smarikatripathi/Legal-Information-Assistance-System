from __future__ import annotations

from django.contrib import admin, messages
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html, mark_safe

from legal_information_assistance_system.legal_ai.models import (
    AdminNotification,
    ClarificationRequest,
    Conversation,
    EmbeddingConfig,
    KnowledgeGap,
    LegalChunk,
    LegalDocument,
    Message,
    QueryHistory,
)
from legal_information_assistance_system.legal_ai.services.ingestion import process_document
from legal_information_assistance_system.legal_ai.services.notifications import notification_service
from legal_information_assistance_system.legal_ai.services.retrieval import rebuild_faiss_index, search
from legal_information_assistance_system.legal_ai.storage.vector_db import FAISSService


def _badge(text: str, kind: str) -> str:
    return format_html('<span class="badge bg-{}">{}</span>', kind, text)


class LegalChunkInline(admin.TabularInline):
    model = LegalChunk
    extra = 0
    fields = ("chunk_index", "title", "part", "chapter", "section", "article", "embedding_id")
    readonly_fields = fields
    can_delete = False
    max_num = 15
    show_change_link = True


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    change_list_template = "admin/legal_ai/legaldocument/change_list.html"
    change_form_template = "admin/legal_ai/legaldocument/change_form.html"
    list_display = ("title", "document_type", "source_type", "processing_badge", "chunk_count", "faiss_badge", "uploaded_at", "action_links")
    list_filter = ("source_type", "document_type", "processing_status")
    search_fields = ("title", "source_url", "act_name", "description")
    actions = ("reprocess_documents", "retry_failed_documents", "delete_with_chunks")
    inlines = [LegalChunkInline]
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
        "extraction_status_display",
        "cleaning_status_display",
        "embedding_status_display",
        "index_status_display",
        "pdf_filename_display",
    )
    fieldsets = (
        (None, {"fields": ("title", "act_name", "description", "document_type", "source_type", "source_url", "file", "published_year", "last_updated")}),
        ("Pipeline Status", {"fields": ("processing_status", "processing_error", "pdf_filename_display", "extraction_status_display", "cleaning_status_display", "chunk_count", "embedding_status_display", "index_status_display", "pipeline_progress_display", "pipeline_steps")}),
        ("Extracted Content", {"classes": ("collapse",), "fields": ("extracted_text", "cleaned_text", "page_count")}),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("<int:document_id>/preview/", self.admin_site.admin_view(self.preview_view), name="legal_ai_legaldocument_preview"),
            path("<int:document_id>/download/", self.admin_site.admin_view(self.download_view), name="legal_ai_legaldocument_download"),
        ]
        return custom + urls

    @admin.display(description="Processing")
    def processing_badge(self, obj):
        mapping = {
            "completed": "success",
            "failed": "danger",
            "pending": "warning",
            "extracting": "info",
            "cleaning": "info",
            "chunking": "info",
            "embedding": "info",
            "indexing": "info",
        }
        return _badge(obj.get_processing_status_display(), mapping.get(obj.processing_status, "secondary"))

    @admin.display(description="FAISS")
    def faiss_badge(self, obj):
        indexed = bool(obj.pipeline_steps.get("stored_in_faiss"))
        return _badge("Indexed" if indexed else "Not Indexed", "success" if indexed else "secondary")

    @admin.display(description="Actions")
    def action_links(self, obj):
        return format_html(
            '<div class="d-flex gap-2 flex-wrap">'
            '<a class="btn btn-sm btn-outline-primary" href="{}"><i class="fa-solid fa-eye"></i> View</a>'
            '<a class="btn btn-sm btn-outline-secondary" href="{}"><i class="fa-solid fa-file-pdf"></i> PDF Preview</a>'
            '<a class="btn btn-sm btn-outline-success" href="{}"><i class="fa-solid fa-download"></i> Download</a>'
            "</div>",
            reverse("admin:legal_ai_legaldocument_change", args=[obj.pk]),
            reverse("admin:legal_ai_legaldocument_preview", args=[obj.pk]),
            reverse("admin:legal_ai_legaldocument_download", args=[obj.pk]),
        )

    @admin.display(description="PDF File")
    def pdf_filename_display(self, obj):
        return obj.file.name if obj.file else "—"

    @admin.display(description="Extraction")
    def extraction_status_display(self, obj):
        if not obj.file:
            return "—"
        return "✓ Done" if obj.pipeline_steps.get("text_extracted") else "Pending"

    @admin.display(description="Cleaning")
    def cleaning_status_display(self, obj):
        return "✓ Done" if obj.pipeline_steps.get("text_cleaned") else "Pending"

    @admin.display(description="Embeddings")
    def embedding_status_display(self, obj):
        return "✓ Done" if obj.pipeline_steps.get("embeddings_generated") else "Pending"

    @admin.display(description="FAISS Index")
    def index_status_display(self, obj):
        return "✓ Indexed" if obj.pipeline_steps.get("stored_in_faiss") else "Pending"

    @admin.display(description="Pipeline Progress")
    def pipeline_progress_display(self, obj):
        progress = obj.pipeline_progress
        return mark_safe(
            "<br>".join(
                f"{'✓' if value else '✕'} {label.replace('_', ' ').title()}"
                for label, value in progress.items()
            )
        )

    @admin.action(description="Reprocess selected documents")
    def reprocess_documents(self, request, queryset):
        ok = failed = 0
        for doc in queryset:
            result = process_document(doc.id, rebuild_faiss=False) if doc.file else {"status": "failed"}
            if result.get("status") == "success":
                ok += 1
            else:
                failed += 1
        rebuild_faiss_index()
        self.message_user(request, f"Reprocessed: {ok} success, {failed} failed. FAISS rebuilt.", messages.INFO)

    @admin.action(description="Retry failed documents")
    def retry_failed_documents(self, request, queryset):
        self.reprocess_documents(request, queryset.filter(processing_status="failed"))

    @admin.action(description="Delete selected documents and chunks")
    def delete_with_chunks(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        rebuild_faiss_index()
        self.message_user(request, f"Deleted {count} document(s) and rebuilt FAISS.", messages.WARNING)

    def preview_view(self, request, document_id):
        document = get_object_or_404(LegalDocument, pk=document_id)
        return TemplateResponse(
            request,
            "admin/legal_ai/legaldocument/pdf_preview.html",
            {"document": document, "title": f"PDF Preview - {document.title}"},
        )

    def download_view(self, request, document_id):
        document = get_object_or_404(LegalDocument, pk=document_id)
        if not document.file:
            self.message_user(request, "PDF file is not available for this document.", messages.ERROR)
            return TemplateResponse(
                request,
                "admin/legal_ai/legaldocument/pdf_preview.html",
                {"document": document, "title": f"PDF Preview - {document.title}", "pdf_missing": True},
                status=404,
            )
        return redirect(document.file.url)


@admin.register(LegalChunk)
class LegalChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "doc", "title_preview", "section", "article", "chunk_index", "embedding_id")
    list_filter = ("doc__source_type", "doc")
    search_fields = ("text", "title", "section", "article", "dhara")

    @admin.display(description="Title")
    def title_preview(self, obj):
        return (obj.title or obj.text[:80]).replace("\n", " ")[:80]


@admin.register(EmbeddingConfig)
class EmbeddingConfigAdmin(admin.ModelAdmin):
    list_display = ("model_name", "dimension", "is_active", "created_at")
    list_filter = ("is_active",)


@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "query_preview", "confidence_score", "response_time_ms", "created_at")
    list_filter = ("created_at",)
    search_fields = ("query", "answer")

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


@admin.register(KnowledgeGap)
class KnowledgeGapAdmin(admin.ModelAdmin):
    list_display = ("id", "query_preview", "status", "detected_language", "user", "created_at")
    list_filter = ("status", "detected_language", "created_at")
    search_fields = ("query", "normalized_query", "admin_notes")
    readonly_fields = ("query", "normalized_query", "detected_language", "query_intent", "retrieval_results", "relevance_scores", "top_chunks", "created_at", "updated_at")
    actions = ("mark_under_review", "mark_resolved", "require_document")

    @admin.display(description="Query")
    def query_preview(self, obj):
        return obj.query[:80]

    @admin.action(description="Mark as under review")
    def mark_under_review(self, request, queryset):
        queryset.update(status="under_review")
        self.message_user(request, f"Marked {queryset.count()} gaps as under review.")

    @admin.action(description="Mark as resolved")
    def mark_resolved(self, request, queryset):
        queryset.update(status="resolved", resolved_at=timezone.now())
        self.message_user(request, f"Marked {queryset.count()} gaps as resolved.")

    @admin.action(description="Mark document required")
    def require_document(self, request, queryset):
        queryset.update(status="document_required", document_required=True)
        self.message_user(request, f"Marked {queryset.count()} gaps as requiring documents.")


@admin.register(ClarificationRequest)
class ClarificationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "original_query_preview", "status", "clarity_score", "created_at")
    list_filter = ("status", "detected_language", "created_at")
    search_fields = ("original_query", "clarification_question", "user_response")
    readonly_fields = ("original_query", "clarification_question", "unknown_terms", "ambiguity_detected", "clarity_score", "detected_language", "created_at")

    @admin.display(description="Original Query")
    def original_query_preview(self, obj):
        return obj.original_query[:60]


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "notification_type", "severity_display", "status", "created_at")
    list_filter = ("notification_type", "severity", "status")
    search_fields = ("title", "message")
    readonly_fields = ("notification_type", "severity", "title", "message", "knowledge_gap", "legal_document", "metadata", "created_at", "read_at")
    actions = ("mark_as_read", "mark_all_as_read", "dismiss_selected")

    @admin.display(description="Severity")
    def severity_display(self, obj):
        colors = {"low": "success", "medium": "info", "high": "warning", "critical": "danger"}
        return _badge(obj.severity.upper(), colors.get(obj.severity, "secondary"))

    @admin.action(description="Mark as read")
    def mark_as_read(self, request, queryset):
        count = 0
        for notification in queryset:
            notification_service.mark_as_read(notification.id)
            count += 1
        self.message_user(request, f"{count} notification(s) marked as read.")

    @admin.action(description="Mark all as read")
    def mark_all_as_read(self, request, queryset):
        count = notification_service.mark_all_as_read()
        self.message_user(request, f"{count} unread notification(s) marked as read.")

    @admin.action(description="Dismiss selected")
    def dismiss_selected(self, request, queryset):
        count = 0
        for notification in queryset:
            notification_service.dismiss_notification(notification.id)
            count += 1
        self.message_user(request, f"{count} notification(s) dismissed.")


@admin.site.admin_view
def mark_all_notifications_read(request):
    if request.user.is_staff:
        count = notification_service.mark_all_as_read()
        return JsonResponse({"success": True, "count": count})
    return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)


def _system_stats():
    faiss_info = FAISSService().inspect_index()
    embedding = EmbeddingConfig.objects.filter(is_active=True).first()
    return {
        "total_documents": LegalDocument.objects.count(),
        "total_pdfs": LegalDocument.objects.filter(source_type="pdf").count(),
        "total_chunks": LegalChunk.objects.count(),
        "total_embeddings": faiss_info.get("total_vectors", 0),
        "total_queries": QueryHistory.objects.count(),
        "total_conversations": Conversation.objects.count(),
        "knowledge_gaps": KnowledgeGap.objects.count(),
        "unresolved_gaps": KnowledgeGap.objects.filter(status__in=["new", "under_review", "document_required"]).count(),
        "unread_notifications": AdminNotification.objects.filter(status="unread").count(),
        "high_priority_notifications": AdminNotification.objects.filter(status="unread", severity__in=["high", "critical"]).count(),
        "documents_waiting": LegalDocument.objects.filter(processing_status="pending").count(),
        "documents_processing": LegalDocument.objects.filter(processing_status__in=["extracting", "cleaning", "chunking", "embedding", "indexing"]).count(),
        "documents_failed": LegalDocument.objects.filter(processing_status="failed").count(),
        "documents_completed": LegalDocument.objects.filter(processing_status="completed").count(),
        "embedding_model": embedding.model_name if embedding else "Not configured",
        "embedding_dimension": embedding.dimension if embedding else faiss_info.get("dimension", "—"),
        "faiss_status": faiss_info.get("status", "unknown"),
        "index_size_bytes": faiss_info.get("index_file_size_bytes", 0),
        "last_rebuild": faiss_info.get("last_rebuild", "Never"),
        "recent_documents": LegalDocument.objects.order_by("-uploaded_at")[:10],
        "recent_notifications": AdminNotification.objects.order_by("-created_at")[:5],
    }


def ingestion_dashboard_view(request):
    stats = _system_stats()
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "rebuild_faiss":
            rebuild_faiss_index()
            messages.success(request, "FAISS index rebuilt from all chunks.")
        elif action == "retry_failed":
            for doc in LegalDocument.objects.filter(processing_status="failed"):
                if doc.file:
                    process_document(doc.id, rebuild_faiss=False)
            rebuild_faiss_index()
            messages.success(request, "Retried all failed documents and rebuilt FAISS.")
        stats = _system_stats()
    return TemplateResponse(request, "admin/legal_ai/ingestion_dashboard.html", {"stats": stats, "title": "Ingestion Pipeline Dashboard"})


def retrieval_debugger_view(request):
    results = []
    query = ""
    if request.method == "POST":
        query = request.POST.get("query", "")
        if query:
            results = search(query, top_k=10, min_score=0.0)
    faiss_info = FAISSService().inspect_index()
    return TemplateResponse(request, "admin/legal_ai/retrieval_debugger.html", {"query": query, "results": results, "faiss_info": faiss_info, "title": "Retrieval Debugger"})


def analytics_dashboard_view(request):
    stats = _system_stats()
    stats["avg_confidence"] = QueryHistory.objects.aggregate(v=Avg("confidence_score"))["v"] or 0
    stats["avg_response_time"] = QueryHistory.objects.aggregate(v=Avg("response_time_ms"))["v"] or 0
    stats["total_conversations"] = Conversation.objects.count()
    stats["total_knowledge_gaps"] = KnowledgeGap.objects.count()
    stats["unresolved_knowledge_gaps"] = KnowledgeGap.objects.filter(status="new").count()
    stats["pending_clarifications"] = ClarificationRequest.objects.filter(status="pending").count()
    stats["documents_by_type"] = list(LegalDocument.objects.values("document_type").annotate(count=Count("id")))
    stats["top_documents"] = list(LegalChunk.objects.values("doc__title").annotate(count=Count("id")).order_by("-count")[:5])
    return TemplateResponse(request, "admin/legal_ai/analytics_dashboard.html", {"stats": stats, "title": "RAG Analytics Dashboard"})
