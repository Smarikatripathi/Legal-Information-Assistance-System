from django.core.management.base import BaseCommand

from legal_information_assistance_system.legal_ai.models import LegalDocument


class Command(BaseCommand):
    help = "Check English Civil and Criminal Code documents"

    def handle(self, *args, **options):
        # Check Civil Code (English)
        civil_doc = LegalDocument.objects.get(id=2)
        self.stdout.write(f"Civil Code (ID 2): {civil_doc.title}")
        self.stdout.write(f"  File: {civil_doc.file.name}")
        self.stdout.write(f"  Status: {civil_doc.processing_status}")
        self.stdout.write(f"  Chunks: {civil_doc.chunk_count}")
        self.stdout.write(f"  Extracted text length: {len(civil_doc.extracted_text) if civil_doc.extracted_text else 0}")
        if civil_doc.extracted_text:
            self.stdout.write(f"  First 300 chars: {civil_doc.extracted_text[:300]}")
        
        # Check Criminal Code (English)
        criminal_doc = LegalDocument.objects.get(id=3)
        self.stdout.write(f"\nCriminal Code (ID 3): {criminal_doc.title}")
        self.stdout.write(f"  File: {criminal_doc.file.name}")
        self.stdout.write(f"  Status: {criminal_doc.processing_status}")
        self.stdout.write(f"  Chunks: {criminal_doc.chunk_count}")
        self.stdout.write(f"  Extracted text length: {len(criminal_doc.extracted_text) if criminal_doc.extracted_text else 0}")
        if criminal_doc.extracted_text:
            self.stdout.write(f"  First 300 chars: {criminal_doc.extracted_text[:300]}")
