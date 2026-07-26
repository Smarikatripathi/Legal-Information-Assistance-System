from django.core.management.base import BaseCommand

from legal_information_assistance_system.legal_ai.models import LegalChunk


class Command(BaseCommand):
    help = "Check which chunks have embeddings"

    def handle(self, *args, **options):
        # Check Civil Code chunks with embeddings
        civil_chunks = LegalChunk.objects.filter(doc_id=64)
        civil_with_emb = civil_chunks.exclude(embedding_id__isnull=True)
        self.stdout.write(f"Civil Code chunks with embeddings: {civil_with_emb.count()}/{civil_chunks.count()}")
        
        # Check Criminal Code chunks with embeddings
        criminal_chunks = LegalChunk.objects.filter(doc_id=62)
        criminal_with_emb = criminal_chunks.exclude(embedding_id__isnull=True)
        self.stdout.write(f"Criminal Code chunks with embeddings: {criminal_with_emb.count()}/{criminal_chunks.count()}")
        
        # Total chunks in database
        total_chunks = LegalChunk.objects.count()
        total_with_emb = LegalChunk.objects.exclude(embedding_id__isnull=True).count()
        self.stdout.write(f"\nTotal chunks with embeddings: {total_with_emb}/{total_chunks}")
