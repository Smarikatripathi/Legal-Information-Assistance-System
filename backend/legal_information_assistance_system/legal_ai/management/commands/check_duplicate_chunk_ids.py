from django.core.management.base import BaseCommand
from django.db.models import Count

from legal_information_assistance_system.legal_ai.models import LegalChunk


class Command(BaseCommand):
    help = 'Check for duplicate chunk_id values within documents'

    def handle(self, *args, **options):
        # Find chunks with duplicate (doc_id, chunk_id) combinations
        duplicates = LegalChunk.objects.values('doc_id', 'chunk_id').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if not duplicates:
            self.stdout.write(self.style.SUCCESS('No duplicate chunk_id values found.'))
            return
        
        self.stdout.write(self.style.WARNING(f'Found {duplicates.count()} duplicate chunk_id combinations:'))
        
        for dup in duplicates:
            doc_id = dup['doc_id']
            chunk_id = dup['chunk_id']
            count = dup['count']
            
            self.stdout.write(f'  Document ID {doc_id}, Chunk ID "{chunk_id}": {count} duplicates')
            
            # Show the actual chunk IDs
            chunks = LegalChunk.objects.filter(doc_id=doc_id, chunk_id=chunk_id)
            for chunk in chunks:
                self.stdout.write(f'    - Chunk ID: {chunk.id}, Article: {chunk.article_number}, Section: {chunk.section_number}')
        
        self.stdout.write(self.style.ERROR('Please fix duplicates before applying the unique constraint migration.'))
