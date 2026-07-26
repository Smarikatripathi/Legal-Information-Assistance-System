from django.core.management.base import BaseCommand

from legal_information_assistance_system.legal_ai.models import LegalDocument


class Command(BaseCommand):
    help = "Check extracted text for Civil and Criminal Code documents"

    def handle(self, *args, **options):
        # Check Civil Code (Nepali)
        civil_doc = LegalDocument.objects.filter(title__icontains='देवानी संहिता').first()
        if civil_doc:
            self.stdout.write(f"Civil Code (ID {civil_doc.id}):")
            self.stdout.write(f"  Status: {civil_doc.processing_status}")
            self.stdout.write(f"  Chunks: {civil_doc.chunk_count}")
            self.stdout.write(f"  Extracted text length: {len(civil_doc.extracted_text) if civil_doc.extracted_text else 0}")
            if civil_doc.extracted_text:
                self.stdout.write(f"  First 500 chars: {civil_doc.extracted_text[:500]}")
        
        # Check Criminal Code (Nepali)
        criminal_doc = LegalDocument.objects.filter(title__icontains='अपराध संहिता').first()
        if criminal_doc:
            self.stdout.write(f"\nCriminal Code (ID {criminal_doc.id}):")
            self.stdout.write(f"  Status: {criminal_doc.processing_status}")
            self.stdout.write(f"  Chunks: {criminal_doc.chunk_count}")
            self.stdout.write(f"  Extracted text length: {len(criminal_doc.extracted_text) if criminal_doc.extracted_text else 0}")
            if criminal_doc.extracted_text:
                self.stdout.write(f"  First 500 chars: {criminal_doc.extracted_text[:500]}")
