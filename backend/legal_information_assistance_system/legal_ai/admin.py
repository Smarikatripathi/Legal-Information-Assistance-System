from django.contrib import admin
from .models import LegalDocument, LegalChunk


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "uploaded_at")


@admin.register(LegalChunk)
class LegalChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "doc", "dhara")