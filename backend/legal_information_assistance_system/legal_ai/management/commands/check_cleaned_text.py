from django.core.management.base import BaseCommand

from legal_information_assistance_system.legal_ai.models import LegalDocument


class Command(BaseCommand):
    help = "Check cleaned text for a specific document"

    def handle(self, *args, **options):
        doc = LegalDocument.objects.get(id=64)
        self.stdout.write(f"Document: {doc.title}")
        self.stdout.write(f"Cleaned text length: {len(doc.cleaned_text) if doc.cleaned_text else 0}")
        if doc.cleaned_text:
            self.stdout.write(f"Cleaned text first 500 chars: {doc.cleaned_text[:500]}")
