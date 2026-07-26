from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db import transaction

from legal_information_assistance_system.legal_ai.models import LegalChunk


class Command(BaseCommand):
    help = 'Fix duplicate chunk_id values by making them unique'

    def handle(self, *args, **options):
        # Find chunks with duplicate (doc_id, chunk_id) combinations
        duplicates = LegalChunk.objects.values('doc_id', 'chunk_id').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if not duplicates:
            self.stdout.write(self.style.SUCCESS('No duplicate chunk_id values found.'))
            return
        
        self.stdout.write(self.style.WARNING(f'Found {duplicates.count()} duplicate chunk_id combinations.'))
        self.stdout.write('Fixing duplicates...')
        
        total_fixed = 0
        
        with transaction.atomic():
            for dup in duplicates:
                doc_id = dup['doc_id']
                chunk_id = dup['chunk_id']
                count = dup['count']
                
                # Get all chunks with this duplicate combination
                chunks = LegalChunk.objects.filter(doc_id=doc_id, chunk_id=chunk_id).order_by('id')
                
                # Keep the first one as-is, update the rest
                first_chunk = chunks.first()
                remaining_chunks = chunks[1:]
                
                for i, chunk in enumerate(remaining_chunks, start=1):
                    # Create a unique chunk_id by adding a suffix
                    new_chunk_id = f"{chunk_id}-dup-{i}"
                    chunk.chunk_id = new_chunk_id
                    chunk.save(update_fields=['chunk_id'])
                    total_fixed += 1
        
        self.stdout.write(self.style.SUCCESS(f'Fixed {total_fixed} duplicate chunk_id values.'))
        
        # Verify no duplicates remain
        remaining_duplicates = LegalChunk.objects.values('doc_id', 'chunk_id').annotate(
            count=Count('id')
        ).filter(count__gt=1).count()
        
        if remaining_duplicates == 0:
            self.stdout.write(self.style.SUCCESS('All duplicates resolved. Unique constraint can now be applied.'))
        else:
            self.stdout.write(self.style.ERROR(f'{remaining_duplicates} duplicates still remain.'))
