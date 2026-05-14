from django.contrib import admin
from .models import LegalDocument, DocumentChunk
from .tasks import process_document_embeddings
import threading

@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "document_type", "published_year", "uploaded_at")
    list_filter = ("document_type", "published_year")
    search_fields = ("title", "description")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # run only on new upload
        if not change:
            threading.Thread(
                target=process_document_embeddings,
                args=(obj.id,)
            ).start()

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("document", "chunk_index")
    search_fields = ("content",)

    readonly_fields = ("embedding_id",)            