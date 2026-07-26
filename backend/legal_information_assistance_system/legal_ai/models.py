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

    SOURCE_TYPES = [
        ("pdf", "PDF Upload"),
        ("website", "Website"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=100, choices=DOCUMENT_TYPES)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default="pdf")
    source_url = models.URLField(max_length=500, blank=True)
    act_name = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to="legal_docs/", blank=True, null=True)
    published_year = models.IntegerField(null=True, blank=True)
    last_updated = models.DateField(null=True, blank=True)
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

    # Original hierarchy fields (deprecated - use canonical fields below)
    part = models.CharField(max_length=255, blank=True, help_text="Deprecated: Use part_number")
    chapter = models.CharField(max_length=255, blank=True, help_text="Deprecated: Use chapter_number")
    section = models.CharField(max_length=255, blank=True, help_text="Deprecated: Use section_number")
    article = models.CharField(max_length=255, blank=True, help_text="Deprecated: Use article_number")
    clause = models.CharField(max_length=255, blank=True, help_text="Deprecated: Use clause_number")
    dhara = models.CharField(max_length=255, blank=True, help_text="Deprecated: Use section_number or article_number")

    # New advanced metadata fields
    chunk_id = models.CharField(max_length=500, blank=True, null=True)
    document_type = models.CharField(max_length=100, blank=True)
    jurisdiction = models.CharField(max_length=100, default="Nepal")
    language = models.CharField(max_length=10, default="ne")
    
    # Detailed hierarchy
    part_number = models.CharField(max_length=50, blank=True, null=True)
    part_title = models.CharField(max_length=500, blank=True, null=True)
    chapter_number = models.CharField(max_length=50, blank=True, null=True)
    chapter_title = models.CharField(max_length=500, blank=True, null=True)
    section_number = models.CharField(max_length=50, blank=True, null=True)
    section_title = models.CharField(max_length=500, blank=True, null=True)
    article_number = models.CharField(max_length=50, blank=True, null=True)
    article_title = models.CharField(max_length=500, blank=True, null=True)
    subclause_number = models.CharField(max_length=50, blank=True, null=True)
    paragraph_number = models.CharField(max_length=50, blank=True, null=True)
    schedule_number = models.CharField(max_length=50, blank=True, null=True)
    schedule_title = models.CharField(max_length=500, blank=True, null=True)
    annex_number = models.CharField(max_length=50, blank=True, null=True)
    annex_title = models.CharField(max_length=500, blank=True, null=True)
    
    # Chunk classification
    chunk_type = models.CharField(max_length=50, default="provision")
    parent_chunk_id = models.CharField(max_length=500, blank=True, null=True)
    hierarchy_path = models.JSONField(default=list, blank=True)
    
    # Source tracking
    source_page_start = models.PositiveIntegerField(null=True, blank=True)
    source_page_end = models.PositiveIntegerField(null=True, blank=True)
    pdf_page_number = models.PositiveIntegerField(null=True, blank=True)
    
    # OCR and quality
    corrected_text = models.TextField(blank=True)
    contextualized_text = models.TextField(blank=True)
    ocr_status = models.CharField(max_length=20, default="uncertain")
    content_hash = models.CharField(max_length=64, blank=True)
    citation_label = models.CharField(max_length=500, blank=True)
    ocr_corrections = models.JSONField(default=list, blank=True)

    # Legacy fields
    metadata = models.JSONField(default=dict, blank=True)
    chunk_index = models.PositiveIntegerField(default=0)
    embedding_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["doc_id", "chunk_index"]
        indexes = [
            models.Index(fields=["doc", "chunk_index"]),
            models.Index(fields=["section"]),
            models.Index(fields=["article"]),
            models.Index(fields=["chunk_id"]),
            models.Index(fields=["content_hash"]),
            # New indexes for metadata filtering
            models.Index(fields=["doc", "article_number"]),
            models.Index(fields=["doc", "section_number"]),
            models.Index(fields=["document_type"]),
            models.Index(fields=["language"]),
            models.Index(fields=["chunk_type"]),
            models.Index(fields=["ocr_status"]),
            # Composite indexes for common queries
            models.Index(fields=["doc", "article_number", "chunk_index"]),
            models.Index(fields=["doc", "section_number", "chunk_index"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["doc", "chunk_id"],
                name="unique_document_chunk_id",
            )
        ]

    def __str__(self):
        label = self.citation_label or self.section or self.article or self.dhara or self.title or "chunk"
        return f"{self.doc.title} — {label}"

    def to_metadata(self) -> dict:
        source_file = self.doc.file.name if self.doc.file else ""
        base_metadata = {
            "chunk_id": self.chunk_id or self.pk,
            "doc_id": self.doc_id,
            "document_name": self.doc.title,
            "document_title": self.doc.title,
            "document_type": self.document_type or self.doc.document_type,
            "act_name": self.doc.act_name or self.doc.title,
            "source_type": self.doc.source_type,
            "source_url": self.doc.source_url,
            "source_file": source_file,
            "url": self.doc.source_url,
            "year": self.doc.published_year,
            "publication_date": str(self.doc.published_year) if self.doc.published_year else "",
            "last_updated": str(self.doc.last_updated) if self.doc.last_updated else "",
            # Legacy fields
            "part": self.part,
            "chapter": self.chapter,
            "section": self.section,
            "article": self.article,
            "clause": self.clause,
            "dhara": self.dhara,
            "title": self.title,
            "text": self.text,
            # New advanced fields
            "jurisdiction": self.jurisdiction,
            "language": self.language,
            "part_number": self.part_number,
            "part_title": self.part_title,
            "chapter_number": self.chapter_number,
            "chapter_title": self.chapter_title,
            "section_number": self.section_number,
            "section_title": self.section_title,
            "article_number": self.article_number,
            "article_title": self.article_title,
            "subclause_number": self.subclause_number,
            "paragraph_number": self.paragraph_number,
            "schedule_number": self.schedule_number,
            "schedule_title": self.schedule_title,
            "annex_number": self.annex_number,
            "annex_title": self.annex_title,
            "chunk_type": self.chunk_type,
            "parent_chunk_id": self.parent_chunk_id,
            "hierarchy_path": self.hierarchy_path,
            "source_page_start": self.source_page_start,
            "source_page_end": self.source_page_end,
            "pdf_page_number": self.pdf_page_number,
            "corrected_text": self.corrected_text or self.text,
            "contextualized_text": self.contextualized_text,
            "ocr_status": self.ocr_status,
            "content_hash": self.content_hash,
            "citation_label": self.citation_label,
        }
        # Merge with existing metadata, preferring new fields if they exist
        if self.metadata:
            base_metadata.update(self.metadata)
        return base_metadata


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
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "-updated_at"]),
            models.Index(fields=["user", "is_archived"]),
        ]

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
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class SourceReference(models.Model):
    """Track source references for assistant messages."""
    
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="source_references",
    )
    document = models.ForeignKey(
        LegalDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_references",
    )
    chunk = models.ForeignKey(
        LegalChunk,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_references",
    )
    article = models.CharField(max_length=255, blank=True)
    section = models.CharField(max_length=255, blank=True)
    relevance_score = models.FloatField(default=0.0)
    source_url = models.URLField(max_length=500, blank=True)
    
    class Meta:
        ordering = ["-relevance_score"]
        indexes = [
            models.Index(fields=["message"]),
            models.Index(fields=["document"]),
        ]
    
    def __str__(self):
        return f"{self.document.title if self.document else 'Unknown'} - {self.article or self.section or 'Unknown'}"


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


class KnowledgeGap(models.Model):
    """Track legal questions that cannot be answered from current documents."""
    
    STATUS_CHOICES = [
        ("new", "New"),
        ("under_review", "Under Review"),
        ("resolved", "Resolved"),
        ("document_required", "Document Required"),
        ("document_added", "Document Added"),
        ("closed", "Closed"),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="knowledge_gaps",
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="knowledge_gaps",
    )
    query = models.TextField()
    normalized_query = models.TextField(blank=True)
    detected_language = models.CharField(max_length=10, default="en")
    query_intent = models.CharField(max_length=50, blank=True)
    
    # Retrieval information
    retrieval_results = models.JSONField(default=dict, blank=True)
    relevance_scores = models.JSONField(default=list, blank=True)
    top_chunks = models.JSONField(default=list, blank=True)
    
    # Resolution tracking
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="new")
    admin_notes = models.TextField(blank=True)
    resolution = models.TextField(blank=True)
    
    # Document tracking
    document_required = models.BooleanField(default=False)
    document_uploaded = models.BooleanField(default=False)
    knowledge_base_updated = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["detected_language"]),
            models.Index(fields=["created_at"]),
        ]
    
    def __str__(self):
        return f"{self.query[:50]}... ({self.status})"


class ClarificationRequest(models.Model):
    """Track clarification requests for ambiguous queries."""
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("resolved", "Resolved"),
        ("cancelled", "Cancelled"),
    ]
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="clarifications",
    )
    original_query = models.TextField()
    clarification_question = models.TextField()
    user_response = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    
    # Query analysis
    unknown_terms = models.JSONField(default=list, blank=True)
    ambiguity_detected = models.BooleanField(default=False)
    clarity_score = models.FloatField(default=0.0)
    
    # Context
    detected_language = models.CharField(max_length=10, default="en")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["conversation"]),
        ]
    
    def __str__(self):
        return f"{self.original_query[:40]}... → {self.clarification_question[:40]}"


class AdminNotification(models.Model):
    """Admin notifications for knowledge gaps and system events."""
    
    NOTIFICATION_TYPES = [
        ('knowledge_gap', 'Knowledge Gap'),
        ('document_failed', 'Document Processing Failed'),
        ('index_rebuilt', 'Index Rebuilt'),
        ('system_alert', 'System Alert'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('dismissed', 'Dismissed'),
    ]
    
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    knowledge_gap = models.ForeignKey(KnowledgeGap, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    legal_document = models.ForeignKey(LegalDocument, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["severity"]),
            models.Index(fields=["notification_type"]),
        ]
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"
