import faiss
import numpy as np
import os
import pickle

INDEX_PATH = "faiss.index"
META_PATH = "faiss_meta.pkl"


# ======================================================
# CREATE OR LOAD INDEX
# ======================================================
def get_index(dimension: int):
    """
    Load existing FAISS index OR create new one
    """

    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
    else:
        index = faiss.IndexFlatL2(dimension)

    return index


# ======================================================
# SAVE INDEX + METADATA
# ======================================================
def save_index(index, metadata):
    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)


# ======================================================
# LOAD INDEX + METADATA
# ======================================================
def load_index():
    if not os.path.exists(INDEX_PATH):
        return None, []

    index = faiss.read_index(INDEX_PATH)

    with open(META_PATH, "rb") as f:
        metadata = pickle.load(f)

    return index, metadata