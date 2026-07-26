from django.core.management.base import BaseCommand

from legal_information_assistance_system.legal_ai.models import LegalChunk


class Command(BaseCommand):
    help = "Check Civil Code chunks in database"

    def handle(self, *args, **options):
        # Check Civil Code (Nepali) - document ID 64
        chunks = LegalChunk.objects.filter(doc_id=64)
        self.stdout.write(f"Civil Code (Nepali) chunks: {chunks.count()}")
        
        # Show sample chunks
        for c in chunks[:5]:
            self.stdout.write(f"\nChunk {c.pk}:")
            self.stdout.write(f"  Title: {c.title[:50] if c.title else 'No title'}")
            self.stdout.write(f"  Article: {c.article_number}")
            self.stdout.write(f"  Text preview: {c.text[:150]}...")
