import faiss
import os
import pickle

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STORE_PATH = os.path.join(BASE_DIR, "storage")

INDEX_PATH = os.path.join(STORE_PATH, "index.faiss")
CHUNKS_PATH = os.path.join(STORE_PATH, "chunks.pkl")

def save_index(index, chunks):
    os.makedirs(STORE_PATH, exist_ok=True)

    faiss.write_index(index, INDEX_PATH)

    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)


def load_index():
    index = faiss.read_index(INDEX_PATH)

    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)

    return index, chunks