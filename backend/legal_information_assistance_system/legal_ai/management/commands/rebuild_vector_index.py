from django.core.management.base import BaseCommand

from legal_ai.models import LegalChunk, LegalDocument
from legal_ai.services.rag_pipeline import process_pdf, rebuild_index_from_chunks, sync_vector_store
from legal_ai.storage.vector_db import FAISSService


class Command(BaseCommand):
    help = "Rebuild FAISS vector index from database chunks. Use --clear to wipe stale index first."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear FAISS files before rebuilding.",
        )
        parser.add_argument(
            "--reprocess",
            action="store_true",
            help="Re-run PDF ingestion for all documents before rebuilding.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            FAISSService().clear()
            self.stdout.write(self.style.WARNING("Cleared FAISS index files."))

        if options["reprocess"]:
            docs = LegalDocument.objects.all()
            self.stdout.write(f"Reprocessing {docs.count()} documents...")
            for doc in docs:
                self.stdout.write(f"  Processing: {doc.title}")
                result = process_pdf(doc.id)
                if result.get("status") != "success":
                    self.stdout.write(self.style.ERROR(f"    Failed: {result.get('message')}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"    OK — {result.get('chunk_count')} chunks"))

        sync_vector_store()
        chunk_count = LegalChunk.objects.count()
        if chunk_count == 0:
            self.stdout.write(self.style.WARNING("No chunks in database. Upload PDFs first."))
            return

        ok = rebuild_index_from_chunks()
        if ok:
            info = FAISSService().inspect_index()
            self.stdout.write(self.style.SUCCESS(
                f"Index rebuilt: {info.get('total_vectors')} vectors, dim={info.get('dimension')}"
            ))
        else:
            self.stdout.write(self.style.ERROR("Rebuild failed."))
