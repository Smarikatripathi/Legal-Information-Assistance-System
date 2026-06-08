from celery import shared_task

from legal_ai.services.rag_pipeline import process_pdf


@shared_task(name="legal_ai.process_document")
def process_document_embeddings(document_id: int) -> dict:
    return process_pdf(document_id)
