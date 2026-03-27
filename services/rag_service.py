from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

chunks_store = []
faiss_index = None


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    # Splitting text into overlapping chunks
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def add_to_index(text: str):
    global faiss_index, chunks_store

    new_chunks = chunk_text(text)
    if not new_chunks:
        return 0

    embeddings = model.encode(new_chunks)
    embeddings = np.array(embeddings).astype("float32")

    if faiss_index is None:
        dimension = embeddings.shape[1]            # 384
        faiss_index = faiss.IndexFlatL2(dimension)

    faiss_index.add(embeddings)
    chunks_store.extend(new_chunks)

    return len(new_chunks)


def search(query: str, top_k: int = 3) -> list:
    global faiss_index, chunks_store

    if faiss_index is None or len(chunks_store) == 0:
        return []

    query_vector = model.encode([query])
    query_vector = np.array(query_vector).astype("float32")

    distances, indices = faiss_index.search(query_vector, top_k)

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(chunks_store):
            results.append(chunks_store[idx])

    return results


def reset_index():
    global faiss_index, chunks_store
    faiss_index = None
    chunks_store = []
