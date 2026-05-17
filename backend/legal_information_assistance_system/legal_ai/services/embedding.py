from sentence_transformers import SentenceTransformer


# Load multilingual embedding model
model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def generate_embeddings(chunks):
    """
    Generate embeddings for chunks
    """

    embeddings = model.encode(
        chunks,
        show_progress_bar=True
    )

    return embeddings