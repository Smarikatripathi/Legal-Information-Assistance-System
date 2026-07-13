from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from legal_information_assistance_system.legal_ai.services.ingestion import ingest_pdfs_from_directory


class Command(BaseCommand):
    help = (
        "Scan media/legal_docs/ for PDFs, import new documents, extract text, "
        "chunk, and rebuild FAISS once at the end."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--directory",
            type=str,
            default="",
            help="Override PDF directory (default: MEDIA_ROOT/legal_docs/).",
        )
        parser.add_argument(
            "--no-faiss",
            action="store_true",
            help="Skip FAISS rebuild after processing.",
        )

    def handle(self, *args, **options):
        directory = options["directory"]
        pdf_dir = Path(directory) if directory else Path(settings.MEDIA_ROOT) / "legal_docs"

        self.stdout.write(f"Scanning {pdf_dir} ...")
        stats = ingest_pdfs_from_directory(pdf_dir, rebuild_faiss=not options["no_faiss"])

        self.stdout.write(f"  PDFs on disk: {stats['total_pdfs_on_disk']}")
        self.stdout.write(self.style.SUCCESS(f"  New imports: {stats['imported']}"))
        self.stdout.write(f"  Skipped (already imported): {stats['skipped']}")
        self.stdout.write(self.style.SUCCESS(f"  Processed: {stats['processed']}"))
        if stats["failed"]:
            self.stdout.write(self.style.ERROR(f"  Failed: {stats['failed']}"))
        if stats["faiss_rebuilt"]:
            self.stdout.write(self.style.SUCCESS("  FAISS index rebuilt."))
        elif not options["no_faiss"]:
            self.stdout.write(self.style.WARNING("  FAISS rebuild skipped (no chunks)."))
