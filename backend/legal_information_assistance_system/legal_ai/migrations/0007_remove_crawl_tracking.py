# Generated migration — removes unused crawl tracking models.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("legal_ai", "0006_crawlrun_pipelinelog"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PipelineLog",
        ),
        migrations.DeleteModel(
            name="CrawlRun",
        ),
    ]
