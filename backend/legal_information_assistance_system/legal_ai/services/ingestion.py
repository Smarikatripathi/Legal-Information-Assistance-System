from pathlib import Path
from typing import Any, Dict, List

from django.conf import settings
from django.db import transaction

from legal_information_assistance_system.legal_ai.models import LegalChunk, LegalDocument
from legal_information_assistance_system.legal_ai.services.chunking import LegalChunker
from legal_information_assistance_system.legal_ai.services.pdf_loader import extract_pdf_text
from legal_information_assistance_system.legal_ai.services.retrieval import rebuild_faiss_index
from legal_information_assistance_system.legal_ai.services.text_cleaning import clean_text

_chunker = LegalChunker(max_words=300, overlap=50)
LEGAL_DOCS_DIR = Path(settings.MEDIA_ROOT) / "legal_docs"


def _update_pipeline_step(document: LegalDocument, step: str, value: bool = True) -> None:
    steps = dict(document.pipeline_steps or {})
    steps[step] = value
    document.pipeline_steps = steps
    document.save(update_fields=["pipeline_steps"])


def _guess_document_type(filename: str) -> str:
    lower = filename.lower()
    if "constitution" in lower or "samvidhan" in lower:
        return "constitution"
    if any(k in lower for k in ("court", "judgment", "decision", "nijamit")):
        return "court_decision"
    if "regulation" in lower or "niyam" in lower:
        return "regulation"
    if "rule" in lower:
        return "act"
    if "criminal" in lower:
        return "criminal_code"
    if "civil" in lower:
        return "civil_code"
    return "act"


def _title_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    return stem.replace("-", " ").replace("_", " ").strip() or filename


def is_pdf_imported(filename: str) -> bool:
    """Return True if a LegalDocument already references this PDF filename."""
    relative = f"legal_docs/{filename}"
    return LegalDocument.objects.filter(file=relative).exists()


def get_imported_filenames() -> set[str]:
    return {
        Path(name).name
        for name in LegalDocument.objects.exclude(file="").values_list("file", flat=True)
        if name
    }


def register_pdf_document(pdf_path: Path) -> LegalDocument | None:
    """Create a LegalDocument for a PDF on disk. Returns None if already imported."""
    filename = pdf_path.name
    if is_pdf_imported(filename):
        return None

    relative = f"legal_docs/{filename}"
    doc = LegalDocument(
        title=_title_from_filename(filename),
        document_type=_guess_document_type(filename),
        source_type="pdf",
        file=relative,
        processing_status="pending",
    )
    doc.save()
    _update_pipeline_step(doc, "pdf_uploaded")
    return doc


def process_document(document_id: int, *, rebuild_faiss: bool = False) -> Dict[str, Any]:
    """
    Extract text, clean, chunk, and store chunks for one document.
    FAISS rebuild is optional and should be deferred during batch ingestion.
    """
    document = LegalDocument.objects.get(id=document_id)
    document.processing_status = "extracting"
    document.processing_error = ""
    document.save(update_fields=["processing_status", "processing_error"])

    try:
        if not document.file:
            raise ValueError("Document has no PDF file attached.")

        file_path = Path(settings.MEDIA_ROOT) / document.file.name
        if not file_path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        raw_text, page_count = extract_pdf_text(str(file_path))
        document.extracted_text = raw_text
        document.page_count = page_count
        document.processing_status = "cleaning"
        document.save(update_fields=["extracted_text", "page_count", "processing_status"])
        _update_pipeline_step(document, "text_extracted")

        cleaned = clean_text(raw_text)
        document.cleaned_text = cleaned
        document.processing_status = "chunking"
        document.save(update_fields=["cleaned_text", "processing_status"])
        _update_pipeline_step(document, "text_cleaned")

        chunks_data = _chunker.chunk(cleaned, document_name=document.title)
        if not chunks_data:
            raise ValueError("No valid legal sections found in PDF.")

        document.processing_status = "embedding"
        document.save(update_fields=["processing_status"])

        with transaction.atomic():
            LegalChunk.objects.filter(doc=document).delete()
            LegalChunk.objects.bulk_create([
                LegalChunk(
                    doc=document,
                    text=data["text"],
                    title=data.get("title", ""),
                    part=data.get("part", ""),
                    chapter=data.get("chapter", ""),
                    section=data.get("section", ""),
                    article=data.get("article", ""),
                    clause=data.get("clause", ""),
                    dhara=data.get("dhara", ""),
                    metadata=data.get("metadata", {}),
                    chunk_index=data.get("chunk_index", 0),
                )
                for data in chunks_data
            ])

        _update_pipeline_step(document, "chunks_created")
        _update_pipeline_step(document, "metadata_generated")
        _update_pipeline_step(document, "embeddings_generated")

        chunk_count = len(chunks_data)
        document.chunk_count = chunk_count
        document.processing_status = "completed"
        document.save(update_fields=["chunk_count", "processing_status"])

        if rebuild_faiss:
            rebuild_faiss_index()
            _update_pipeline_step(document, "stored_in_faiss")

        return {"status": "success", "chunk_count": chunk_count, "page_count": page_count}

    except Exception as exc:
        document.processing_status = "failed"
        document.processing_error = str(exc)
        document.save(update_fields=["processing_status", "processing_error"])
        return {"status": "failed", "message": str(exc)}


def discover_pdfs(directory: Path | None = None) -> List[Path]:
    """Return sorted PDF paths from the legal docs directory."""
    root = directory or LEGAL_DOCS_DIR
    if not root.exists():
        root.mkdir(parents=True, exist_ok=True)
        return []
    return sorted(p for p in root.glob("*.pdf") if p.is_file())


def ingest_pdfs_from_directory(
    directory: Path | None = None,
    *,
    rebuild_faiss: bool = True,
) -> Dict[str, Any]:
    """
    Scan media/legal_docs/, import new PDFs, process all pending docs,
    then rebuild FAISS once at the end.
    """
    pdf_paths = discover_pdfs(directory)
    imported = skipped = processed = failed = 0

    for pdf_path in pdf_paths:
        if is_pdf_imported(pdf_path.name):
            skipped += 1
            continue
        doc = register_pdf_document(pdf_path)
        if doc:
            imported += 1

    pending_docs = LegalDocument.objects.filter(
        processing_status__in=["pending", "failed"],
        file__isnull=False,
    ).exclude(file="")

    for doc in pending_docs:
        result = process_document(doc.id, rebuild_faiss=False)
        if result.get("status") == "success":
            processed += 1
        else:
            failed += 1

    faiss_built = False
    if rebuild_faiss and LegalChunk.objects.exists():
        faiss_built = rebuild_faiss_index()
        if faiss_built:
            for doc in LegalDocument.objects.filter(processing_status="completed"):
                steps = dict(doc.pipeline_steps or {})
                steps["stored_in_faiss"] = True
                doc.pipeline_steps = steps
                doc.save(update_fields=["pipeline_steps"])

    return {
        "total_pdfs_on_disk": len(pdf_paths),
        "imported": imported,
        "skipped": skipped,
        "processed": processed,
        "failed": failed,
        "faiss_rebuilt": faiss_built,
    }


# Backward-compatible alias used by upload API and admin
process_pdf = process_document
