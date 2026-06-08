# Generated migration for RAG system upgrade

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("legal_ai", "0002_legalchunk_delete_documentchunk"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="legaldocument",
            name="chunk_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="legaldocument",
            name="cleaned_text",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="legaldocument",
            name="extracted_text",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="legaldocument",
            name="page_count",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="legaldocument",
            name="pipeline_steps",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="legaldocument",
            name="processing_error",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="legaldocument",
            name="processing_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("extracting", "Extracting Text"),
                    ("cleaning", "Cleaning Text"),
                    ("chunking", "Creating Chunks"),
                    ("embedding", "Generating Embeddings"),
                    ("indexing", "Indexing Vectors"),
                    ("completed", "Completed"),
                    ("failed", "Failed"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="legalchunk",
            name="article",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="legalchunk",
            name="chunk_index",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="legalchunk",
            name="clause",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="legalchunk",
            name="metadata",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="legalchunk",
            name="title",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name="legaldocument",
            name="document_type",
            field=models.CharField(
                choices=[
                    ("constitution", "Constitution"),
                    ("civil_code", "National Civil Code"),
                    ("criminal_code", "Criminal Code"),
                    ("act", "Act"),
                    ("regulation", "Regulation"),
                    ("court_decision", "Court Decision"),
                ],
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="legalchunk",
            name="part",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="legalchunk",
            name="chapter",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="legalchunk",
            name="section",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="legalchunk",
            name="dhara",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.CreateModel(
            name="EmbeddingConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("model_name", models.CharField(max_length=255)),
                ("dimension", models.PositiveIntegerField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Conversation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(default="New conversation", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="conversations", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("user", "User"), ("assistant", "Assistant")], max_length=20)),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("conversation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="legal_ai.conversation")),
            ],
            options={"ordering": ["created_at"]},
        ),
        migrations.CreateModel(
            name="QueryHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("query", models.TextField()),
                ("answer", models.TextField()),
                ("retrieved_chunks", models.JSONField(blank=True, default=list)),
                ("confidence_score", models.FloatField(default=0.0)),
                ("response_time_ms", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("conversation", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="queries", to="legal_ai.conversation")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="query_history", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"], "verbose_name_plural": "Query histories"},
        ),
        migrations.DeleteModel(
            name="UserProfile",
        ),
        migrations.AddIndex(
            model_name="legalchunk",
            index=models.Index(fields=["doc", "chunk_index"], name="legal_ai_le_doc_id_idx"),
        ),
        migrations.AddIndex(
            model_name="legalchunk",
            index=models.Index(fields=["section"], name="legal_ai_le_section_idx"),
        ),
        migrations.AddIndex(
            model_name="legalchunk",
            index=models.Index(fields=["article"], name="legal_ai_le_article_idx"),
        ),
    ]
