from django.core.management.base import BaseCommand

from legal_information_assistance_system.legal_ai.services.nepali_font_converter import (
    is_unicode_text,
    is_legacy_font,
    convert_legacy_to_unicode,
)


class Command(BaseCommand):
    help = "Test font detection and conversion on Civil Code text"

    def handle(self, *args, **options):
        from legal_information_assistance_system.legal_ai.models import LegalDocument
        
        doc = LegalDocument.objects.get(id=64)
        sample_text = doc.extracted_text[:1000] if doc.extracted_text else ""
        
        self.stdout.write(f"Sample text: {sample_text}")
        self.stdout.write(f"\nIs Unicode: {is_unicode_text(sample_text)}")
        self.stdout.write(f"Is Legacy Font: {is_legacy_font(sample_text)}")
        
        if is_legacy_font(sample_text):
            converted = convert_legacy_to_unicode(sample_text)
            self.stdout.write(f"\nConverted text: {converted[:500]}")
