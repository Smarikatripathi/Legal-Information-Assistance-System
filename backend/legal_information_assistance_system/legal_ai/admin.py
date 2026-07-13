from django.contrib import admin, messages

from django.db.models import Avg, Count

from django.template.response import TemplateResponse

from django.utils.safestring import mark_safe



from legal_information_assistance_system.legal_ai.models import (

    Conversation,

    EmbeddingConfig,

    LegalChunk,

    LegalDocument,

    Message,

    QueryHistory,

)

from legal_information_assistance_system.legal_ai.services.ingestion import process_document

from legal_information_assistance_system.legal_ai.services.retrieval import rebuild_faiss_index, search

from legal_information_assistance_system.legal_ai.storage.vector_db import FAISSService





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

    list_display = (

        "id",

        "title",

        "source_type",

        "processing_status",

        "chunk_count",

        "index_status_display",

        "uploaded_at",

    )

    list_filter = ("source_type", "document_type", "processing_status")

    search_fields = ("title", "source_url", "act_name", "description")

    actions = ("reprocess_documents", "retry_failed_documents", "delete_with_chunks")

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

    inlines = [LegalChunkInline]

    fieldsets = (

        (None, {

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

            ),

        }),

        ("Pipeline Status", {

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

            ),

        }),

        ("Extracted Content", {

            "classes": ("collapse",),

            "fields": ("extracted_text", "cleaned_text", "page_count"),

        }),

    )



    @admin.display(description="PDF File")

    def pdf_filename_display(self, obj):

        return obj.file.name if obj.file else "—"



    @admin.display(description="Extraction")

    def extraction_status_display(self, obj):

        return "✓ Done" if obj.pipeline_steps.get("text_extracted") else ("—" if not obj.file else "Pending")



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

        html = "<br>".join(

            f"{'✓' if v else '✗'} {k.replace('_', ' ').title()}"

            for k, v in progress.items()

        )

        return mark_safe(html)



    @admin.action(description="Reprocess selected documents")

    def reprocess_documents(self, request, queryset):

        ok, failed = 0, 0

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

        failed = queryset.filter(processing_status="failed")

        self.reprocess_documents(request, failed)



    @admin.action(description="Delete selected documents and chunks")

    def delete_with_chunks(self, request, queryset):

        count = queryset.count()

        queryset.delete()

        rebuild_faiss_index()

        self.message_user(request, f"Deleted {count} document(s) and rebuilt FAISS.", messages.WARNING)





@admin.register(LegalChunk)

class LegalChunkAdmin(admin.ModelAdmin):

    list_display = ("id", "doc", "title", "section", "article", "chunk_index", "embedding_id")

    list_filter = ("doc__source_type", "doc")

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





def _system_stats():

    faiss_info = FAISSService().inspect_index()

    embedding = EmbeddingConfig.objects.filter(is_active=True).first()

    return {

        "total_documents": LegalDocument.objects.count(),

        "total_pdfs": LegalDocument.objects.filter(source_type="pdf").count(),

        "total_chunks": LegalChunk.objects.count(),

        "total_embeddings": faiss_info.get("total_vectors", 0),

        "total_queries": QueryHistory.objects.count(),

        "documents_waiting": LegalDocument.objects.filter(processing_status="pending").count(),

        "documents_processing": LegalDocument.objects.filter(

            processing_status__in=["extracting", "cleaning", "chunking", "embedding", "indexing"]

        ).count(),

        "documents_failed": LegalDocument.objects.filter(processing_status="failed").count(),

        "documents_completed": LegalDocument.objects.filter(processing_status="completed").count(),

        "embedding_model": embedding.model_name if embedding else "Not configured",

        "embedding_dimension": embedding.dimension if embedding else faiss_info.get("dimension", "—"),

        "faiss_status": faiss_info.get("status", "unknown"),

        "index_size_bytes": faiss_info.get("index_file_size_bytes", 0),

        "last_rebuild": faiss_info.get("last_rebuild", "Never"),

        "recent_documents": LegalDocument.objects.order_by("-uploaded_at")[:10],

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



    return TemplateResponse(

        request,

        "admin/legal_ai/ingestion_dashboard.html",

        {"stats": stats, "title": "Ingestion Pipeline Dashboard"},

    )





def retrieval_debugger_view(request):

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

    stats = _system_stats()

    stats["avg_confidence"] = QueryHistory.objects.aggregate(v=Avg("confidence_score"))["v"] or 0

    stats["avg_response_time"] = QueryHistory.objects.aggregate(v=Avg("response_time_ms"))["v"] or 0

    stats["total_conversations"] = Conversation.objects.count()

    stats["documents_by_type"] = list(

        LegalDocument.objects.values("document_type").annotate(count=Count("id"))

    )

    return TemplateResponse(

        request,

        "admin/legal_ai/analytics_dashboard.html",

        {"stats": stats, "title": "RAG Analytics Dashboard"},

    )


