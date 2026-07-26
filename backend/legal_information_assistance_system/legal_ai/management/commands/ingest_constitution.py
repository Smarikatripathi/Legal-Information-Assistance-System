from django.core.management.base import BaseCommand
from legal_information_assistance_system.legal_ai.models import LegalDocument, LegalChunk
from legal_information_assistance_system.legal_ai.services.chunking_v2 import AdvancedLegalChunker
from legal_information_assistance_system.legal_ai.services.retrieval import rebuild_faiss_index
from django.db import transaction


class Command(BaseCommand):
    help = 'Ingest constitution part 2 chunks and rebuild FAISS index'

    def handle(self, *args, **options):
        doc = LegalDocument.objects.get(id=87)
        text = doc.cleaned_text
        chunker = AdvancedLegalChunker(
            document_id=doc.id,
            document_name=doc.title,
            document_type=doc.document_type
        )
        chunks_metadata = chunker.chunk(text)
        self.stdout.write(f'Chunks created: {len(chunks_metadata)}')

        with transaction.atomic():
            LegalChunk.objects.filter(doc=doc).delete()
            LegalChunk.objects.bulk_create([
                LegalChunk(
                    doc=doc,
                    text=meta.corrected_text or meta.source_text,
                    title=meta.article_title or "",
                    part=meta.part_number or "",
                    chapter=meta.chapter_number or "",
                    section=meta.section_number or "",
                    article=meta.article_number or "",
                    clause=meta.clause_number or "",
                    dhara=meta.section_number or meta.article_number or "",
                    chunk_id=meta.chunk_id,
                    document_type=meta.document_type,
                    jurisdiction=meta.jurisdiction,
                    language=meta.language,
                    part_number=meta.part_number or "",
                    part_title=meta.part_title,
                    chapter_number=meta.chapter_number or "",
                    chapter_title=meta.chapter_title,
                    section_number=meta.section_number or "",
                    section_title=meta.section_title,
                    article_number=meta.article_number or "",
                    article_title=meta.article_title,
                    subclause_number=meta.subclause_number,
                    paragraph_number=meta.paragraph_number,
                    schedule_number=meta.schedule_number,
                    schedule_title=meta.schedule_title,
                    annex_number=meta.annex_number,
                    annex_title=meta.annex_title,
                    chunk_type=meta.chunk_type,
                    parent_chunk_id=meta.parent_chunk_id,
                    hierarchy_path=meta.hierarchy_path,
                    source_page_start=meta.source_page_start,
                    source_page_end=meta.source_page_end,
                    pdf_page_number=meta.pdf_page_number,
                    corrected_text=meta.corrected_text,
                    contextualized_text=meta.contextualized_text,
                    ocr_status=meta.ocr_status,
                    content_hash=meta.content_hash,
                    citation_label=meta.citation_label,
                    ocr_corrections=[
                        {
                            "original": c.original,
                            "corrected": c.corrected,
                            "confidence": c.confidence,
                            "rule_id": c.rule_id,
                        }
                        for c in meta.ocr_corrections
                    ],
                    metadata={},
                    chunk_index=i
                )
                for i, meta in enumerate(chunks_metadata)
            ])

        doc.chunk_count = len(chunks_metadata)
        doc.save(update_fields=['chunk_count'])
        self.stdout.write('Chunks saved')

        rebuild_faiss_index()
        self.stdout.write(self.style.SUCCESS('FAISS index rebuilt'))
