"""
Management command to generate comprehensive chunking quality and coverage reports.
Run with: python manage.py chunk_quality_report
"""
from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from legal_information_assistance_system.legal_ai.models import LegalDocument, LegalChunk


class Command(BaseCommand):
    help = 'Generate comprehensive chunking quality and coverage reports'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write("LEGAL DOCUMENT CHUNKING - QUALITY & COVERAGE REPORT")
        self.stdout.write("=" * 80)
        
        # Overall statistics
        self.stdout.write("\n## OVERALL STATISTICS")
        total_docs = LegalDocument.objects.filter(file__isnull=False).exclude(file="").count()
        total_chunks = LegalChunk.objects.count()
        from django.db.models import Sum
        total_pages = LegalDocument.objects.aggregate(total=Sum('page_count'))['total'] or 0
        
        self.stdout.write(f"Total Documents: {total_docs}")
        self.stdout.write(f"Total Chunks: {total_chunks}")
        self.stdout.write(f"Total Pages: {total_pages}")
        self.stdout.write(f"Average Chunks per Document: {total_chunks / total_docs:.1f}")
        self.stdout.write(f"Average Pages per Document: {total_pages / total_docs:.1f}")
        
        # Document processing status
        self.stdout.write("\n## DOCUMENT PROCESSING STATUS")
        status_counts = LegalDocument.objects.values('processing_status').annotate(
            count=Count('id')
        ).order_by('processing_status')
        
        for status in status_counts:
            self.stdout.write(f"  {status['processing_status']}: {status['count']}")
        
        # Chunk quality metrics
        self.stdout.write("\n## CHUNK QUALITY METRICS")
        
        # OCR status distribution
        ocr_counts = LegalChunk.objects.values('ocr_status').annotate(
            count=Count('id')
        ).order_by('ocr_status')
        self.stdout.write("\nOCR Status Distribution:")
        for status in ocr_counts:
            percentage = (status['count'] / total_chunks) * 100 if total_chunks > 0 else 0
            self.stdout.write(f"  {status['ocr_status']}: {status['count']} ({percentage:.1f}%)")
        
        # Metadata completeness
        self.stdout.write("\nMetadata Completeness:")
        fields = [
            'chunk_id', 'article_number', 'chapter_number', 'part_number',
            'section_number', 'schedule_number', 'citation_label', 'content_hash'
        ]
        for field in fields:
            filled = LegalChunk.objects.filter(~Q(**{f"{field}__isnull": True})).exclude(**{f"{field}": ""}).count()
            percentage = (filled / total_chunks) * 100 if total_chunks > 0 else 0
            self.stdout.write(f"  {field}: {filled}/{total_chunks} ({percentage:.1f}%)")
        
        # Chunk type distribution
        self.stdout.write("\n## CHUNK TYPE DISTRIBUTION")
        chunk_type_counts = LegalChunk.objects.values('chunk_type').annotate(
            count=Count('id')
        ).order_by('-count')
        for chunk_type in chunk_type_counts:
            percentage = (chunk_type['count'] / total_chunks) * 100 if total_chunks > 0 else 0
            self.stdout.write(f"  {chunk_type['chunk_type']}: {chunk_type['count']} ({percentage:.1f}%)")
        
        # Document type distribution
        self.stdout.write("\n## DOCUMENT TYPE DISTRIBUTION")
        doc_types = LegalDocument.objects.values('document_type').annotate(
            doc_count=Count('id')
        ).order_by('-doc_count')
        for doc_type in doc_types:
            chunks_in_type = LegalChunk.objects.filter(doc__document_type=doc_type['document_type']).count()
            avg_chunks = chunks_in_type / doc_type['doc_count'] if doc_type['doc_count'] > 0 else 0
            self.stdout.write(f"  {doc_type['document_type']}: {doc_type['doc_count']} docs, {chunks_in_type} chunks (avg {avg_chunks:.1f} per doc)")
        
        # Top documents by chunk count
        self.stdout.write("\n## TOP DOCUMENTS BY CHUNK COUNT")
        top_docs = LegalDocument.objects.annotate(
            chunks_count=Count('chunks')
        ).order_by('-chunks_count')[:10]
        for doc in top_docs:
            self.stdout.write(f"  {doc.title}: {doc.chunks_count} chunks ({doc.page_count} pages)")
        
        # Hierarchy tracking
        self.stdout.write("\n## HIERARCHY TRACKING")
        hierarchy_fields = ['part_number', 'chapter_number', 'section_number', 'article_number']
        for field in hierarchy_fields:
            filled = LegalChunk.objects.filter(~Q(**{f"{field}__isnull": True})).exclude(**{f"{field}": ""}).count()
            percentage = (filled / total_chunks) * 100 if total_chunks > 0 else 0
            self.stdout.write(f"  {field}: {filled}/{total_chunks} ({percentage:.1f}%)")
        
        # Language distribution
        self.stdout.write("\n## LANGUAGE DISTRIBUTION")
        lang_counts = LegalChunk.objects.values('language').annotate(
            count=Count('id')
        ).order_by('-count')
        for lang in lang_counts:
            percentage = (lang['count'] / total_chunks) * 100 if total_chunks > 0 else 0
            self.stdout.write(f"  {lang['language']}: {lang['count']} ({percentage:.1f}%)")
        
        # Potential issues
        self.stdout.write("\n## POTENTIAL ISSUES")
        
        # Chunks without article_number
        no_article = LegalChunk.objects.filter(article_number__isnull=True).exclude(article_number="").count()
        if no_article > 0:
            self.stdout.write(f"  ⚠ Chunks without article_number: {no_article}")
        
        # Chunks without citation_label
        no_citation = LegalChunk.objects.filter(citation_label__isnull=True).exclude(citation_label="").count()
        if no_citation > 0:
            self.stdout.write(f"  ⚠ Chunks without citation_label: {no_citation}")
        
        # Chunks without content_hash
        no_hash = LegalChunk.objects.filter(content_hash__isnull=True).exclude(content_hash="").count()
        if no_hash > 0:
            self.stdout.write(f"  ⚠ Chunks without content_hash: {no_hash}")
        
        # Very short chunks (potential OCR issues)
        from django.db.models.functions import Length
        short_chunks = LegalChunk.objects.annotate(text_len=Length('text')).filter(text_len__lt=50).count()
        if short_chunks > 0:
            self.stdout.write(f"  ⚠ Very short chunks (<50 chars): {short_chunks}")
        
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("REPORT COMPLETE")
        self.stdout.write("=" * 80)
