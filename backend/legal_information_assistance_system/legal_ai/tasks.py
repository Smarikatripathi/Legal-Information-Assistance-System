from celery import shared_task

from .services.rag_pipeline import process_pdf


@shared_task(bind=True)
def process_document_embeddings(self, document_id: int) -> dict:
    result = process_pdf(document_id)
    if result.get("status") != "success":
        raise RuntimeError(f"Document ingestion failed: {result}")
    return result
