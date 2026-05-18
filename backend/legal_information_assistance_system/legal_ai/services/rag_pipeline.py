import numpy as np
from legal_ai.storage.vector_db import load_index, save_index
from legal_ai.services.embedding import embedding_model
from legal_ai.services.pdf_loader import extract_pdf
from legal_ai.services.text_cleaning import clean_text, chunk_text


# =====================================================
# 1. INGESTION PIPELINE
# =====================================================
def ingest_document(doc_id, file_path):

    # 1. Extract
    text = extract_pdf(file_path)

    # 2. Clean
    text = clean_text(text)

    # 3. Chunk
    chunks = chunk_text(text)

    if not chunks:
        return {"status": "failed"}

    # 4. Embeddings
    embeddings = embedding_model.embed(chunks)

    dimension = embeddings.shape[1]

    # 5. Load FAISS
    index, metadata = load_index(dimension)

    # 6. Add vectors
    index.add(embeddings)

    # 7. Store metadata (VERY IMPORTANT alignment)
    for i, chunk in enumerate(chunks):
        metadata.append({
            "doc_id": doc_id,
            "chunk_text": chunk,
            "chunk_index": i
        })

    save_index(index, metadata)

    return {
        "status": "success",
        "chunks": len(chunks)
    }


# =====================================================
# 2. QUERY PIPELINE
# =====================================================
def ask_question(query, top_k=5):

    # 1. Load FAISS
    index, metadata = load_index()

    if len(metadata) == 0:
        return "No documents found."

    # 2. Embed query
    query_vector = embedding_model.embed_query(query).reshape(1, -1)

    # 3. Search FAISS
    D, I = index.search(query_vector, top_k)

    context_chunks = []

    for idx in I[0]:
        if idx < len(metadata):
            context_chunks.append(metadata[idx]["chunk_text"])

    context = "\n\n".join(context_chunks)

    # 4. Generate answer using LLM
    answer = generate_answer(query, context)

    return {
        "query": query,
        "answer": answer,
        "sources": context_chunks
    }


# =====================================================
# 3. LLM GENERATION (OPENAI / OLLAMA READY)
# =====================================================
def generate_answer(query, context):

    prompt = f"""
You are a legal assistant AI for Nepal law system.

Use ONLY the context below.

Context:
{context}

Question:
{query}

Answer in simple legal explanation:
"""

    # ----------------------------
    # OPTION 1: OpenAI (recommended)
    # ----------------------------
    # return openai.chat.completions.create(...)

    # ----------------------------
    # OPTION 2: Ollama (LOCAL)
    # ----------------------------
    # return ollama.generate(...)

    return prompt