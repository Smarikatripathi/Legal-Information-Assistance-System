from .models import LegalDocument
from .services.text_extract import extract_pdf_text
from .services.smart_chunking import smart_chunk
from .services.embedding import create_embeddings


def process_document_embeddings(document_id):
    doc = LegalDocument.objects.get(id=document_id)

    print("Processing:", doc.title)

    # 1. Extract text
    text = extract_pdf_text(doc.file.path)

    # 2. Chunk text
    chunks = smart_chunk(text)

    print("Total chunks:", len(chunks))

    # 3. Embeddings (future use)
    embeddings = create_embeddings(chunks)

    return embeddings