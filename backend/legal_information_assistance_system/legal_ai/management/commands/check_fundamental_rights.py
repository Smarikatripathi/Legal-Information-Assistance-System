from django.core.management.base import BaseCommand

from legal_information_assistance_system.legal_ai.models import LegalChunk


class Command(BaseCommand):
    help = "Check fundamental rights chunks in Nepali Constitution"

    def handle(self, *args, **options):
        # Fundamental rights are typically in Articles 16-46
        fr_articles = ['16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46']
        
        chunks = LegalChunk.objects.filter(
            doc_id=88,
            article_number__in=fr_articles
        )
        
        self.stdout.write(f"Fundamental rights chunks: {chunks.count()}")
        
        for c in chunks[:15]:
            title = c.article_title[:50] if c.article_title else "No title"
            self.stdout.write(f"Article {c.article_number}: {title}")
