from django.conf import settings
from django.db import models


class LegalDocument(models.Model):
    DOCUMENT_TYPES = [
        ("constitution", "Constitution"),
        ("civil_code", "National Civil Code"),
        ("criminal_code", "Criminal Code"),
        ("act", "Act"),
        ("regulation", "Regulation"),
        ("court_decision", "Court Decision"),
    ]

    PROCESSING_STATUSES = [
        ("pending", "Pending"),
        ("extracting", "Extracting Text"),
        ("cleaning", "Cleaning Text"),
        ("chunking", "Creating Chunks"),
        ("embedding", "Generating Embeddings"),
        ("indexing", "Indexing Vectors"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=100, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to="legal_docs/")
    published_year = models.IntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    extracted_text = models.TextField(blank=True)
    cleaned_text = models.TextField(blank=True)
    page_count = models.PositiveIntegerField(null=True, blank=True)
    chunk_count = models.PositiveIntegerField(default=0)
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUSES,
        default="pending",
    )
    processing_error = models.TextField(blank=True)
    pipeline_steps = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title

    @property
    def pipeline_progress(self) -> dict:
        steps = [
            "pdf_uploaded",
            "text_extracted",
            "text_cleaned",
            "chunks_created",
            "metadata_generated",
            "embeddings_generated",
            "stored_in_faiss",
        ]
        return {step: bool(self.pipeline_steps.get(step)) for step in steps}


class LegalChunk(models.Model):
    doc = models.ForeignKey(LegalDocument, on_delete=models.CASCADE, related_name="chunks")
    text = models.TextField()
    title = models.CharField(max_length=500, blank=True)

    part = models.CharField(max_length=255, blank=True)
    chapter = models.CharField(max_length=255, blank=True)
    section = models.CharField(max_length=255, blank=True)
    article = models.CharField(max_length=255, blank=True)
    clause = models.CharField(max_length=255, blank=True)
    dhara = models.CharField(max_length=255, blank=True)

    metadata = models.JSONField(default=dict, blank=True)
    chunk_index = models.PositiveIntegerField(default=0)
    embedding_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["doc_id", "chunk_index"]
        indexes = [
            models.Index(fields=["doc", "chunk_index"]),
            models.Index(fields=["section"]),
            models.Index(fields=["article"]),
        ]

    def __str__(self):
        label = self.section or self.article or self.dhara or self.title or "chunk"
        return f"{self.doc.title} — {label}"

    def to_metadata(self) -> dict:
        return {
            "chunk_id": self.pk,
            "doc_id": self.doc_id,
            "document_name": self.doc.title,
            "document_type": self.doc.document_type,
            "source_file": self.doc.file.name,
            "year": self.doc.published_year,
            "part": self.part,
            "chapter": self.chapter,
            "section": self.section,
            "article": self.article,
            "clause": self.clause,
            "dhara": self.dhara,
            "title": self.title,
            "text": self.text,
            **self.metadata,
        }


class EmbeddingConfig(models.Model):
    model_name = models.CharField(max_length=255)
    dimension = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.model_name} ({self.dimension}d)"


class Conversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    title = models.CharField(max_length=255, default="New conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class Message(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class QueryHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="query_history",
        null=True,
        blank=True,
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="queries",
    )
    query = models.TextField()
    answer = models.TextField()
    retrieved_chunks = models.JSONField(default=list, blank=True)
    confidence_score = models.FloatField(default=0.0)
    response_time_ms = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Query histories"

    def __str__(self):
        return self.query[:80]
