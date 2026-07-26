"""
Management command to re-process all legal documents with the new AdvancedLegalChunker.
Run with: python manage.py reprocess_documents
"""
from django.core.management.base import BaseCommand

from legal_information_assistance_system.legal_ai.models import LegalDocument
from legal_information_assistance_system.legal_ai.services.ingestion import process_document
from legal_information_assistance_system.legal_ai.services.retrieval import rebuild_faiss_index


class Command(BaseCommand):
    help = 'Re-process all legal documents with the new AdvancedLegalChunker'

    def handle(self, *args, **options):
        documents = LegalDocument.objects.filter(file__isnull=False).exclude(file="")
        
        self.stdout.write(f"Found {documents.count()} documents to re-process")
        self.stdout.write("=" * 60)
        
        success_count = 0
        failed_count = 0
        failed_docs = []
        
        for doc in documents:
            self.stdout.write(f"\nProcessing: {doc.title} (ID: {doc.id})")
            result = process_document(doc.id, rebuild_faiss=False)
            
            if result.get("status") == "success":
                chunk_count = result.get("chunk_count", 0)
                page_count = result.get("page_count", 0)
                self.stdout.write(f"  ✓ Success - {chunk_count} chunks from {page_count} pages")
                success_count += 1
            else:
                error_msg = result.get("message", "Unknown error")
                self.stdout.write(f"  ✗ Failed: {error_msg}")
                failed_count += 1
                failed_docs.append((doc.title, error_msg))
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"SUMMARY:")
        self.stdout.write(f"  Total documents: {documents.count()}")
        self.stdout.write(f"  Successful: {success_count}")
        self.stdout.write(f"  Failed: {failed_count}")
        
        if failed_docs:
            self.stdout.write(f"\nFailed documents:")
            for title, error in failed_docs:
                self.stdout.write(f"  - {title}: {error}")
        
        # Rebuild FAISS index after all documents are processed
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Rebuilding FAISS index...")
        faiss_result = rebuild_faiss_index()
        if faiss_result:
            self.stdout.write("  ✓ FAISS index rebuilt successfully")
        else:
            self.stdout.write("  ✗ FAISS index rebuild failed")
        
        self.stdout.write("\nRe-processing complete!")
