import json
from rag.embedder import Embedder
from rag.vector_store import VectorStore
import config

PROCESSED_PATH = "data/processed/cloudpos_chunks.json"
INDEX_PATH = "data/embeddings/faiss_index.bin"


def main():
    with open(PROCESSED_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [item["text"] for item in chunks]

    embedder = Embedder()
    embeddings = embedder.embed(texts)

    vector_store = VectorStore(
        dim=len(embeddings[0]),
        index_path=INDEX_PATH
    )

    vector_store.add(embeddings)
    vector_store.save()

    print(f" FAISS index built with {len(embeddings)} vectors.")


if __name__ == "__main__":
    main()
