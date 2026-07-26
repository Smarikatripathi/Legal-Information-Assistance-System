from django.core.management.base import BaseCommand

from legal_information_assistance_system.legal_ai.services.pdf_loader import extract_pdf_text


class Command(BaseCommand):
    help = "Test PDF extraction with mixed content handling"

    def handle(self, *args, **options):
        text, pages = extract_pdf_text('media/legal_docs/मुलुकी-देवानी-संहिता-ऐन-२०७४_zpq6wk7.pdf')
        self.stdout.write(f'Pages: {pages}')
        self.stdout.write(f'Text length: {len(text)}')
        self.stdout.write(f'First 500 chars: {text[:500]}')
