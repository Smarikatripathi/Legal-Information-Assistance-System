# Generated migration for source metadata fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("legal_ai", "0004_alter_legalchunk_options_alter_legaldocument_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="legaldocument",
            name="act_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="legaldocument",
            name="last_updated",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="legaldocument",
            name="source_type",
            field=models.CharField(
                choices=[("pdf", "PDF Upload"), ("website", "Website")],
                default="pdf",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="legaldocument",
            name="source_url",
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name="legaldocument",
            name="file",
            field=models.FileField(blank=True, null=True, upload_to="legal_docs/"),
        ),
    ]
