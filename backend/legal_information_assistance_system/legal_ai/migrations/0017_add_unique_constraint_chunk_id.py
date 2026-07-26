# Generated manually to add unique constraint after fixing duplicates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legal_ai', '0016_legalchunk_ocr_corrections_alter_legalchunk_article_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='legalchunk',
            constraint=models.UniqueConstraint(fields=('doc', 'chunk_id'), name='unique_document_chunk_id'),
        ),
    ]
