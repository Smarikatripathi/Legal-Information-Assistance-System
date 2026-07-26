from celery import shared_task
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


@shared_task(name="legal_ai.process_document")
def process_document_embeddings(document_id: int) -> dict:
    """Process document embeddings using ingestion service."""
    from legal_information_assistance_system.legal_ai.models import LegalDocument
    from legal_information_assistance_system.legal_ai.services.ingestion import process_document

    document = LegalDocument.objects.filter(id=document_id).first()
    if not document:
        return {"status": "error", "message": "Document not found"}

    return process_document(document.id)


@shared_task(name="legal_ai.crawl_law_commission")
def crawl_law_commission(max_pages: int = 5000) -> dict:
    """Run the Scrapy spider to download PDFs into media/legal_docs/."""
    import os
    from pathlib import Path

    from scraper.spiders.law_commission_spider import LawCommissionSpider

    scraper_dir = Path(__file__).resolve().parents[3] / "scraper"
    original_cwd = os.getcwd()
    try:
        os.chdir(scraper_dir)
        settings = get_project_settings()
        process = CrawlerProcess(settings)
        process.crawl(LawCommissionSpider, max_pages=str(max_pages))
        process.start()
    finally:
        os.chdir(original_cwd)

    return {"status": "completed", "max_pages": max_pages}
