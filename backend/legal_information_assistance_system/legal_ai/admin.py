from __future__ import annotations

from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
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

from legal_information_assistance_system.legal_ai.services.ingestion import (
    process_document,
)

from legal_information_assistance_system.legal_ai.services.notifications import (
    notification_service,
)

from legal_information_assistance_system.legal_ai.services.retrieval import (
    rebuild_faiss_index,
    search,
)

from legal_information_assistance_system.legal_ai.storage.vector_db import (
    FAISSService,
)


# ============================================================
# HELPER
# ============================================================

def _badge(text: str, kind: str) -> str:
    return format_html(
        '<span class="badge bg-{}">{}</span>',
        kind,
        text,
    )


# ============================================================
# LEGAL DOCUMENT
# ============================================================

class LegalChunkInline(admin.TabularInline):
    model = LegalChunk
    extra = 0
    fields = (
        "chunk_index",
        "title",
        "part",
        "chapter",
        "section",
        "article",
        "embedding_id",
    )
    readonly_fields = fields
    can_delete = False
    max_num = 15
    show_change_link = True


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):

    change_list_template = (
        "admin/legal_ai/legaldocument/change_list.html"
    )

    change_form_template = (
        "admin/legal_ai/legaldocument/change_form.html"
    )

    list_display = (
        "title",
        "document_type",
        "source_type",
        "processing_badge",
        "chunk_count",
        "faiss_badge",
        "uploaded_at",
        "action_links",
    )

    list_filter = (
        "source_type",
        "document_type",
        "processing_status",
    )

    search_fields = (
        "title",
        "source_url",
        "act_name",
        "description",
    )

    actions = (
        "reprocess_documents",
        "retry_failed_documents",
        "delete_with_chunks",
    )

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
        (
            None,
            {
                "fields": (
                    "title",
                    "act_name",
                    "description",
                    "document_type",
                    "source_type",
                    "source_url",
                    "file",
                    "published_year",
                    "last_updated",
                )
            },
        ),
        (
            "Pipeline Status",
            {
                "fields": (
                    "processing_status",
                    "processing_error",
                    "pdf_filename_display",
                    "extraction_status_display",
                    "cleaning_status_display",
                    "chunk_count",
                    "embedding_status_display",
                    "index_status_display",
                    "pipeline_progress_display",
                    "pipeline_steps",
                )
            },
        ),
        (
            "Extracted Content",
            {
                "classes": ("collapse",),
                "fields": (
                    "extracted_text",
                    "cleaned_text",
                    "page_count",
                ),
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()

        custom = [
            path(
                "<int:document_id>/preview/",
                self.admin_site.admin_view(
                    self.preview_view
                ),
                name="legal_ai_legaldocument_preview",
            ),
            path(
                "<int:document_id>/download/",
                self.admin_site.admin_view(
                    self.download_view
                ),
                name="legal_ai_legaldocument_download",
            ),
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

        return _badge(
            obj.get_processing_status_display(),
            mapping.get(
                obj.processing_status,
                "secondary",
            ),
        )

    @admin.display(description="FAISS")
    def faiss_badge(self, obj):

        indexed = bool(
            obj.pipeline_steps.get(
                "stored_in_faiss"
            )
        )

        return _badge(
            "Indexed" if indexed else "Not Indexed",
            "success" if indexed else "secondary",
        )

    @admin.display(description="Actions")
    def action_links(self, obj):

        return format_html(
            '<div class="d-flex gap-2 flex-wrap">'
            '<a class="btn btn-sm btn-outline-primary" href="{}">'
            '<i class="fa-solid fa-eye"></i> View'
            "</a>"
            '<a class="btn btn-sm btn-outline-secondary" href="{}">'
            '<i class="fa-solid fa-file-pdf"></i> PDF Preview'
            "</a>"
            '<a class="btn btn-sm btn-outline-success" href="{}">'
            '<i class="fa-solid fa-download"></i> Download'
            "</a>"
            "</div>",
            reverse(
                "admin:legal_ai_legaldocument_change",
                args=[obj.pk],
            ),
            reverse(
                "admin:legal_ai_legaldocument_preview",
                args=[obj.pk],
            ),
            reverse(
                "admin:legal_ai_legaldocument_download",
                args=[obj.pk],
            ),
        )

    @admin.display(description="PDF File")
    def pdf_filename_display(self, obj):

        return (
            obj.file.name
            if obj.file
            else "—"
        )

    @admin.display(description="Extraction")
    def extraction_status_display(self, obj):

        if not obj.file:
            return "—"

        return (
            "✓ Done"
            if obj.pipeline_steps.get("text_extracted")
            else "Pending"
        )

    @admin.display(description="Cleaning")
    def cleaning_status_display(self, obj):

        return (
            "✓ Done"
            if obj.pipeline_steps.get("text_cleaned")
            else "Pending"
        )

    @admin.display(description="Embeddings")
    def embedding_status_display(self, obj):

        return (
            "✓ Done"
            if obj.pipeline_steps.get(
                "embeddings_generated"
            )
            else "Pending"
        )

    @admin.display(description="FAISS Index")
    def index_status_display(self, obj):

        return (
            "✓ Indexed"
            if obj.pipeline_steps.get(
                "stored_in_faiss"
            )
            else "Pending"
        )

    @admin.display(description="Pipeline Progress")
    def pipeline_progress_display(self, obj):

        progress = obj.pipeline_progress

        return mark_safe(
            "<br>".join(
                f"{'✓' if value else '✕'} "
                f"{label.replace('_', ' ').title()}"
                for label, value in progress.items()
            )
        )

    @admin.action(description="Reprocess selected documents")
    def reprocess_documents(
        self,
        request,
        queryset,
    ):

        ok = 0
        failed = 0

        for doc in queryset:

            result = (
                process_document(
                    doc.id,
                    rebuild_faiss=False,
                )
                if doc.file
                else {"status": "failed"}
            )

            if result.get("status") == "success":
                ok += 1
            else:
                failed += 1

        rebuild_faiss_index()

        self.message_user(
            request,
            (
                f"Reprocessed: {ok} success, "
                f"{failed} failed. FAISS rebuilt."
            ),
            messages.INFO,
        )

    @admin.action(description="Retry failed documents")
    def retry_failed_documents(
        self,
        request,
        queryset,
    ):

        self.reprocess_documents(
            request,
            queryset.filter(
                processing_status="failed"
            ),
        )

    @admin.action(
        description="Delete selected documents and chunks"
    )
    def delete_with_chunks(
        self,
        request,
        queryset,
    ):

        count = queryset.count()

        queryset.delete()

        rebuild_faiss_index()

        self.message_user(
            request,
            (
                f"Deleted {count} document(s) "
                f"and rebuilt FAISS."
            ),
            messages.WARNING,
        )

    def preview_view(
        self,
        request,
        document_id,
    ):

        document = get_object_or_404(
            LegalDocument,
            pk=document_id,
        )

        return TemplateResponse(
            request,
            "admin/legal_ai/legaldocument/pdf_preview.html",
            {
                "document": document,
                "title": (
                    f"PDF Preview - "
                    f"{document.title}"
                ),
            },
        )

    def download_view(
        self,
        request,
        document_id,
    ):

        document = get_object_or_404(
            LegalDocument,
            pk=document_id,
        )

        if not document.file:

            self.message_user(
                request,
                "PDF file is not available "
                "for this document.",
                messages.ERROR,
            )

            return TemplateResponse(
                request,
                "admin/legal_ai/legaldocument/pdf_preview.html",
                {
                    "document": document,
                    "title": (
                        f"PDF Preview - "
                        f"{document.title}"
                    ),
                    "pdf_missing": True,
                },
                status=404,
            )

        return redirect(document.file.url)


# ============================================================
# LEGAL CHUNK
# ============================================================

@admin.register(LegalChunk)
class LegalChunkAdmin(admin.ModelAdmin):

    list_display = (
        "doc",
        "title_preview",
        "section",
        "article",
        "chunk_index",
        "embedding_status",
        "view_actions",
    )

    list_filter = (
        "doc__source_type",
        "doc",
        "chunk_type",
    )

    search_fields = (
        "text",
        "title",
        "section",
        "article",
        "dhara",
    )

    list_per_page = 25

    @admin.display(description="Title")
    def title_preview(self, obj):

        max_length = 80

        title = (
            obj.title
            or obj.text[:max_length]
        )

        title_clean = title.replace(
            "\n",
            " ",
        )

        if len(title_clean) > max_length:

            return format_html(
                '<span title="{}">{}</span>',
                title,
                title_clean[:max_length] + "...",
            )

        return title_clean

    @admin.display(description="Embedding")
    def embedding_status(self, obj):

        if obj.embedding_id:
            return _badge(
                "Indexed",
                "success",
            )

        return _badge(
            "Not Indexed",
            "secondary",
        )

    @admin.display(description="Actions")
    def view_actions(self, obj):

        return format_html(
            '<div class="d-flex gap-2">'
            '<a class="btn btn-sm btn-outline-primary" '
            'href="{}" title="View">'
            '<i class="fa-solid fa-eye"></i>'
            "</a>"
            '<a class="btn btn-sm btn-outline-secondary" '
            'href="{}" title="Edit">'
            '<i class="fa-solid fa-pen"></i>'
            "</a>"
            "</div>",
            reverse(
                "admin:legal_ai_legalchunk_change",
                args=[obj.pk],
            ),
            reverse(
                "admin:legal_ai_legalchunk_change",
                args=[obj.pk],
            ),
        )


# ============================================================
# EMBEDDING CONFIG
# ============================================================

@admin.register(EmbeddingConfig)
class EmbeddingConfigAdmin(admin.ModelAdmin):

    list_display = (
        "model_name",
        "dimension",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )


# ============================================================
# QUERY HISTORY
# ============================================================

@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "query_preview",
        "confidence_score",
        "response_time_ms",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "query",
        "answer",
    )

    @admin.display(description="Query")
    def query_preview(self, obj):

        return obj.query[:80]


# ============================================================
# CONVERSATIONS
# ============================================================

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "title",
        "updated_at",
    )

    search_fields = (
        "title",
        "user__email",
    )


# ============================================================
# MESSAGES
# ============================================================

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "conversation",
        "role",
        "content_preview",
        "created_at",
    )

    list_filter = (
        "role",
    )

    @admin.display(description="Content")
    def content_preview(self, obj):

        return obj.content[:80]
    
    
    # ============================================================
# KNOWLEDGE GAPS
# ============================================================

@admin.register(KnowledgeGap)
class KnowledgeGapAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "query_preview",
        "status",
        "detected_language",
        "user",
        "created_at",
    )

    list_filter = (
        "status",
        "detected_language",
        "created_at",
    )

    search_fields = (
        "query",
        "normalized_query",
        "admin_notes",
    )

    readonly_fields = (
        "query",
        "normalized_query",
        "detected_language",
        "query_intent",
        "retrieval_results",
        "relevance_scores",
        "top_chunks",
        "created_at",
        "updated_at",
    )

    actions = (
        "mark_under_review",
        "mark_resolved",
        "require_document",
    )

    @admin.display(description="Query")
    def query_preview(self, obj):
        return obj.query[:80]

    @admin.action(description="Mark as under review")
    def mark_under_review(self, request, queryset):
        count = queryset.update(
            status="under_review"
        )

        self.message_user(
            request,
            f"Marked {count} gap(s) as under review.",
        )

    @admin.action(description="Mark as resolved")
    def mark_resolved(self, request, queryset):
        count = queryset.update(
            status="resolved",
            resolved_at=timezone.now(),
        )

        self.message_user(
            request,
            f"Marked {count} gap(s) as resolved.",
        )

    @admin.action(description="Mark document required")
    def require_document(self, request, queryset):
        count = queryset.update(
            status="document_required",
            document_required=True,
        )

        self.message_user(
            request,
            f"Marked {count} gap(s) as requiring documents.",
        )


# ============================================================
# CLARIFICATION REQUESTS
# ============================================================

@admin.register(ClarificationRequest)
class ClarificationRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "conversation",
        "original_query_preview",
        "status",
        "clarity_score",
        "created_at",
    )

    list_filter = (
        "status",
        "detected_language",
        "created_at",
    )

    search_fields = (
        "original_query",
        "clarification_question",
        "user_response",
    )

    readonly_fields = (
        "original_query",
        "clarification_question",
        "unknown_terms",
        "ambiguity_detected",
        "clarity_score",
        "detected_language",
        "created_at",
    )

    @admin.display(description="Original Query")
    def original_query_preview(self, obj):
        return obj.original_query[:60]


# ============================================================
# ADMIN NOTIFICATIONS
# ============================================================

@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "notification_type",
        "severity_display",
        "status",
        "created_at",
    )

    list_filter = (
        "notification_type",
        "severity",
        "status",
    )

    search_fields = (
        "title",
        "message",
    )

    readonly_fields = (
        "notification_type",
        "severity",
        "title",
        "message",
        "knowledge_gap",
        "legal_document",
        "metadata",
        "created_at",
        "read_at",
    )

    actions = (
        "mark_as_read",
        "mark_all_as_read",
        "dismiss_selected",
    )

    @admin.display(description="Severity")
    def severity_display(self, obj):

        colors = {
            "low": "success",
            "medium": "info",
            "high": "warning",
            "critical": "danger",
        }

        return _badge(
            obj.severity.upper(),
            colors.get(
                obj.severity,
                "secondary",
            ),
        )

    @admin.action(description="Mark as read")
    def mark_as_read(self, request, queryset):

        count = 0

        for notification in queryset:

            notification_service.mark_as_read(
                notification.id
            )

            count += 1

        self.message_user(
            request,
            f"{count} notification(s) marked as read.",
        )

    @admin.action(description="Mark all as read")
    def mark_all_as_read(self, request, queryset):

        count = (
            notification_service
            .mark_all_as_read()
        )

        self.message_user(
            request,
            f"{count} unread notification(s) marked as read.",
        )

    @admin.action(description="Dismiss selected")
    def dismiss_selected(self, request, queryset):

        count = 0

        for notification in queryset:

            notification_service.dismiss_notification(
                notification.id
            )

            count += 1

        self.message_user(
            request,
            f"{count} notification(s) dismissed.",
        )
        
    # ============================================================
# DASHBOARD DATA
# ============================================================

def _system_stats():
    """
    Collect all statistics needed by the main admin dashboard.

    This combines:
    - Ingestion statistics
    - RAG / FAISS statistics
    - Query analytics
    - Conversation statistics
    - Knowledge gap statistics
    - Notification statistics
    - Document statistics
    """

    # --------------------------------------------------------
    # FAISS information
    # --------------------------------------------------------
    try:
        faiss_info = FAISSService().inspect_index()
    except Exception:
        faiss_info = {
            "status": "unavailable",
            "total_vectors": 0,
            "dimension": "—",
            "index_file_size_bytes": 0,
            "last_rebuild": "Never",
        }

    # --------------------------------------------------------
    # Active embedding configuration
    # --------------------------------------------------------
    embedding = (
        EmbeddingConfig.objects
        .filter(is_active=True)
        .first()
    )

    # --------------------------------------------------------
    # Document statistics
    # --------------------------------------------------------
    total_documents = LegalDocument.objects.count()

    total_pdfs = LegalDocument.objects.filter(
        source_type="pdf"
    ).count()

    documents_waiting = LegalDocument.objects.filter(
        processing_status="pending"
    ).count()

    documents_processing = LegalDocument.objects.filter(
        processing_status__in=[
            "extracting",
            "cleaning",
            "chunking",
            "embedding",
            "indexing",
        ]
    ).count()

    documents_failed = LegalDocument.objects.filter(
        processing_status="failed"
    ).count()

    documents_completed = LegalDocument.objects.filter(
        processing_status="completed"
    ).count()

    # --------------------------------------------------------
    # Knowledge gaps
    # --------------------------------------------------------
    knowledge_gaps = KnowledgeGap.objects.count()

    unresolved_gaps = KnowledgeGap.objects.filter(
        status__in=[
            "new",
            "under_review",
            "document_required",
        ]
    ).count()

    # --------------------------------------------------------
    # Notifications
    # --------------------------------------------------------
    unread_notifications = AdminNotification.objects.filter(
        status="unread"
    ).count()

    high_priority_notifications = AdminNotification.objects.filter(
        status="unread",
        severity__in=[
            "high",
            "critical",
        ],
    ).count()

    # --------------------------------------------------------
    # Query analytics
    # --------------------------------------------------------
    total_queries = QueryHistory.objects.count()

    avg_confidence = (
        QueryHistory.objects.aggregate(
            value=Avg("confidence_score")
        )["value"]
        or 0
    )

    avg_response_time = (
        QueryHistory.objects.aggregate(
            value=Avg("response_time_ms")
        )["value"]
        or 0
    )

    # --------------------------------------------------------
    # Conversation statistics
    # --------------------------------------------------------
    total_conversations = Conversation.objects.count()

    # --------------------------------------------------------
    # Clarification statistics
    # --------------------------------------------------------
    pending_clarifications = ClarificationRequest.objects.filter(
        status="pending"
    ).count()

    total_clarifications = ClarificationRequest.objects.count()

    # --------------------------------------------------------
    # Document distribution
    # --------------------------------------------------------
    documents_by_type = list(
        LegalDocument.objects
        .values("document_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # --------------------------------------------------------
    # Most represented documents
    # --------------------------------------------------------
    top_documents = list(
        LegalChunk.objects
        .values("doc__title")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    # --------------------------------------------------------
    # Recent documents
    # --------------------------------------------------------
    recent_documents = (
        LegalDocument.objects
        .order_by("-uploaded_at")[:10]
    )

    # --------------------------------------------------------
    # Recent notifications
    # --------------------------------------------------------
    recent_notifications = (
        AdminNotification.objects
        .order_by("-created_at")[:8]
    )

    # --------------------------------------------------------
    # Recent knowledge gaps
    # --------------------------------------------------------
    recent_knowledge_gaps = (
        KnowledgeGap.objects
        .order_by("-created_at")[:8]
    )

    # --------------------------------------------------------
    # Return everything to dashboard
    # --------------------------------------------------------
    return {
        # Documents
        "total_documents": total_documents,
        "total_pdfs": total_pdfs,
        "documents_waiting": documents_waiting,
        "documents_processing": documents_processing,
        "documents_failed": documents_failed,
        "documents_completed": documents_completed,

        # RAG / FAISS
        "total_chunks": LegalChunk.objects.count(),
        "total_embeddings": faiss_info.get(
            "total_vectors",
            0,
        ),
        "embedding_model": (
            embedding.model_name
            if embedding
            else "Not configured"
        ),
        "embedding_dimension": (
            embedding.dimension
            if embedding
            else faiss_info.get(
                "dimension",
                "—",
            )
        ),
        "faiss_status": faiss_info.get(
            "status",
            "unknown",
        ),
        "index_size_bytes": faiss_info.get(
            "index_file_size_bytes",
            0,
        ),
        "last_rebuild": faiss_info.get(
            "last_rebuild",
            "Never",
        ),

        # Queries
        "total_queries": total_queries,
        "avg_confidence": avg_confidence,
        "avg_response_time": avg_response_time,

        # Conversations
        "total_conversations": total_conversations,

        # Knowledge gaps
        "knowledge_gaps": knowledge_gaps,
        "unresolved_gaps": unresolved_gaps,

        # Clarifications
        "total_clarifications": total_clarifications,
        "pending_clarifications": pending_clarifications,

        # Notifications
        "unread_notifications": unread_notifications,
        "high_priority_notifications": high_priority_notifications,

        # Charts / breakdowns
        "documents_by_type": documents_by_type,
        "top_documents": top_documents,

        # Recent activity
        "recent_documents": recent_documents,
        "recent_notifications": recent_notifications,
        "recent_knowledge_gaps": recent_knowledge_gaps,
    }


# ============================================================
# MAIN ADMIN DASHBOARD
# ============================================================

def dashboard_view(request):
    """
    Main Legal AI admin dashboard.

    This is the custom /admin/ dashboard.

    The normal Django/Jazzmin sidebar is preserved by providing:
        - admin.site.each_context(request)
        - admin.site.get_app_list(request)

    Therefore the sidebar remains visible on the dashboard
    exactly like it is on normal admin change-list/change-form pages.
    """

    # --------------------------------------------------------
    # Get dashboard statistics
    # --------------------------------------------------------

    stats = _system_stats()

    # --------------------------------------------------------
    # Handle dashboard actions
    # --------------------------------------------------------

    if request.method == "POST":

        action = request.POST.get("action")

        # ----------------------------------------------------
        # Rebuild FAISS index
        # ----------------------------------------------------

        if action == "rebuild_faiss":

            try:

                rebuild_faiss_index()

                messages.success(
                    request,
                    "FAISS index rebuilt successfully.",
                )

            except Exception as exc:

                messages.error(
                    request,
                    f"Failed to rebuild FAISS index: {exc}",
                )

        # ----------------------------------------------------
        # Retry failed documents
        # ----------------------------------------------------

        elif action == "retry_failed":

            failed_documents = LegalDocument.objects.filter(
                processing_status="failed"
            )

            success_count = 0
            failed_count = 0

            for document in failed_documents:

                if not document.file:

                    failed_count += 1
                    continue

                try:

                    result = process_document(
                        document.id,
                        rebuild_faiss=False,
                    )

                    if result.get("status") == "success":

                        success_count += 1

                    else:

                        failed_count += 1

                except Exception:

                    failed_count += 1

            # ------------------------------------------------
            # Rebuild FAISS after processing
            # ------------------------------------------------

            try:

                rebuild_faiss_index()

            except Exception:

                pass

            messages.success(
                request,
                (
                    f"Retry completed: "
                    f"{success_count} succeeded, "
                    f"{failed_count} failed. "
                    f"FAISS index rebuilt."
                ),
            )

        # ----------------------------------------------------
        # Mark all notifications as read
        # ----------------------------------------------------

        elif action == "mark_notifications_read":

            count = notification_service.mark_all_as_read()

            messages.success(
                request,
                f"{count} notification(s) marked as read.",
            )

        # ----------------------------------------------------
        # Unknown action
        # ----------------------------------------------------

        elif action:

            messages.warning(
                request,
                "Unknown dashboard action.",
            )

        # ----------------------------------------------------
        # Refresh statistics after action
        # ----------------------------------------------------

        stats = _system_stats()

    # ========================================================
    # ADMIN SIDEBAR
    # ========================================================
    #
    # This is the important part.
    #
    # Normally Django's admin index provides these values
    # automatically. Since we replaced admin.site.index with
    # our own dashboard_view, we must provide them ourselves.
    #
    # `each_context()` provides the normal admin context.
    #
    # `get_app_list()` provides:
    #     Users
    #     Groups
    #     Account
    #     Social Accounts
    #     Legal AI
    #     Sites
    #     etc.
    #
    # Jazzmin uses this information to build the sidebar.
    # ========================================================

    app_list = admin.site.get_app_list(request)

    admin_context = admin.site.each_context(request)

    # --------------------------------------------------------
    # Add our dashboard data to the normal admin context
    # --------------------------------------------------------

    admin_context.update(
        {
            "app_list": app_list,

            "stats": stats,

            "title": "Legal Assist Dashboard",

            # Helpful for templates/Jazzmin
            "has_permission": True,

            # Used by some admin templates to identify
            # the current application/page.
            "is_popup": False,
            "is_nav_sidebar_enabled": True,
        }
    )

    # --------------------------------------------------------
    # Render dashboard
    # --------------------------------------------------------

    return TemplateResponse(
        request,
        "admin/dashboard.html",
        admin_context,
    )
# ============================================================
# RETRIEVAL DEBUGGER
# ============================================================

def retrieval_debugger_view(request):
    """
    Debug FAISS / RAG retrieval results.

    This is a custom Django admin utility page.
    It keeps the normal Jazzmin sidebar and admin layout.
    """

    results = []
    query = ""

    # --------------------------------------------------------
    # Handle retrieval search
    # --------------------------------------------------------

    if request.method == "POST":

        query = request.POST.get(
            "query",
            "",
        ).strip()

        if query:

            results = search(
                query,
                top_k=10,
                min_score=0.0,
            )

    # --------------------------------------------------------
    # FAISS information
    # --------------------------------------------------------

    try:

        faiss_info = FAISSService().inspect_index()

    except Exception:

        faiss_info = {
            "status": "unavailable",
            "total_vectors": 0,
            "dimension": "—",
        }

    # --------------------------------------------------------
    # NORMAL ADMIN CONTEXT
    # --------------------------------------------------------
    #
    # This is important.
    #
    # It gives Jazzmin:
    # - Sidebar
    # - Applications
    # - User menu
    # - Navigation
    # - Admin branding
    # - Messages
    # - Other normal admin context
    # --------------------------------------------------------

    app_list = admin.site.get_app_list(request)

    admin_context = admin.site.each_context(request)

    # --------------------------------------------------------
    # Add retrieval debugger data
    # --------------------------------------------------------

    admin_context.update(
        {
            "app_list": app_list,

            "query": query,

            "results": results,

            "faiss_info": faiss_info,

            "title": "Retrieval Debugger",

            "has_permission": True,

            "is_popup": False,

            "is_nav_sidebar_enabled": True,
        }
    )

    # --------------------------------------------------------
    # Render
    # --------------------------------------------------------

    return TemplateResponse(
        request,
        "admin/legal_ai/retrieval_debugger.html",
        admin_context,
    )
    # ============================================================
# NOTIFICATION ENDPOINT
# ============================================================

@admin.site.admin_view
def mark_all_notifications_read(request):

    if request.user.is_staff:

        count = notification_service.mark_all_as_read()

        return JsonResponse(
            {
                "success": True,
                "count": count,
            }
        )

    return JsonResponse(
        {
            "success": False,
            "error": "Unauthorized",
        },
        status=403,
    )
    
# ============================================================
# REPLACE DEFAULT ADMIN INDEX
# ============================================================

admin.site.index = dashboard_view
