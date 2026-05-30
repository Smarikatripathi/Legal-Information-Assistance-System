from django.db import models
from django.conf import settings

class LegalDocument(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    document_type = models.CharField(
        max_length=100,
        choices=[
            ("constitution", "Constitution"),
            ("civil_code", "Civil Code"),
            ("criminal_code", "Criminal Code"),
            ("act", "Act"),
            ("regulation", "Regulation"),
        ]
    )

    file = models.FileField(upload_to="legal_docs/")
    published_year = models.IntegerField(null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class LegalChunk(models.Model):
    doc = models.ForeignKey(LegalDocument, on_delete=models.CASCADE)
    text = models.TextField()

    # structured metadata (VERY IMPORTANT for legal system)
    part = models.CharField(max_length=255, null=True, blank=True)
    chapter = models.CharField(max_length=255, null=True, blank=True)
    section = models.CharField(max_length=255, null=True, blank=True)
    dhara = models.CharField(max_length=255, null=True, blank=True)

    embedding_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.doc.title}"
    
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("lawyer", "Lawyer"),
        ("admin", "Admin"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.user.username    