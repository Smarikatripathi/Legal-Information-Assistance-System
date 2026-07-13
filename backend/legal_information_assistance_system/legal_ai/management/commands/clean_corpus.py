from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from legal_information_assistance_system.legal_ai.models import LegalChunk, LegalDocument
from legal_information_assistance_system.legal_ai.services.retrieval import rebuild_faiss_index
from legal_information_assistance_system.legal_ai.storage.vector_db import FAISSService


class Command(BaseCommand):
    help = (
        "Remove old website/HTML documents, delete orphan PDF files on disk, "
        "and rebuild the FAISS index from remaining PDF documents."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-website",
            action="store_true",
            help="Do not delete website-sourced documents.",
        )
        parser.add_argument(
            "--no-faiss",
            action="store_true",
            help="Skip FAISS rebuild after cleanup.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without making changes.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        legal_dir = Path(settings.MEDIA_ROOT) / "legal_docs"

        if not options["keep_website"]:
            website_docs = LegalDocument.objects.filter(source_type="website")
            count = website_docs.count()
            if count:
                if dry_run:
                    self.stdout.write(f"Would delete {count} website documents:")
                    for doc in website_docs:
                        self.stdout.write(f"  - [{doc.id}] {doc.title}")
                else:
                    website_docs.delete()
                    self.stdout.write(self.style.SUCCESS(f"Deleted {count} website documents."))
            else:
                self.stdout.write("No website documents to delete.")

        referenced = {
            Path(name).name
            for name in LegalDocument.objects.exclude(file="").values_list("file", flat=True)
            if name
        }

        if legal_dir.exists():
            orphans = [p for p in legal_dir.glob("*.pdf") if p.name not in referenced]
            if orphans:
                if dry_run:
                    self.stdout.write(f"Would remove {len(orphans)} orphan PDF files:")
                    for path in orphans:
                        self.stdout.write(f"  - {path.name}")
                else:
                    for path in orphans:
                        path.unlink(missing_ok=True)
                    self.stdout.write(self.style.SUCCESS(f"Removed {len(orphans)} orphan PDF files."))
            else:
                self.stdout.write("No orphan PDF files on disk.")

        remaining = LegalDocument.objects.count()
        chunks = LegalChunk.objects.count()
        self.stdout.write(f"Remaining documents: {remaining}, chunks: {chunks}")

        if options["no_faiss"] or dry_run:
            return

        if chunks == 0:
            FAISSService().clear()
            self.stdout.write(self.style.WARNING("No chunks left — cleared FAISS index."))
            return

        if rebuild_faiss_index():
            info = FAISSService().inspect_index()
            self.stdout.write(self.style.SUCCESS(
                f"FAISS rebuilt: {info.get('total_vectors')} vectors."
            ))
        else:
            self.stdout.write(self.style.ERROR("FAISS rebuild failed."))
