import numpy as np
from .vector_db import load_index
from .embedding import model

def search(query, top_k=5):
    index, chunks = load_index()

    query_vec = model.encode([query])
    query_vec = np.array(query_vec)

    distances, indices = index.search(query_vec, top_k)

    results = [chunks[i] for i in indices[0]]

    return results