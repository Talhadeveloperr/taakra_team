# rag/retriever.py
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from rag.vector_store import VectorStore
import os

class Retriever:
    

    def __init__(
        self,
        vector_index_path: str,
        metadata_path: str,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        # Load FAISS vector store
        if not os.path.exists(vector_index_path):
            raise FileNotFoundError(f"FAISS index not found at {vector_index_path}")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found at {metadata_path}")

        self.vector_store = VectorStore(index_path=vector_index_path, metadata_path=metadata_path)

        # Load embedding model
        self.embedder = SentenceTransformer(model_name)

    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        
        if not query:
            return []

        # Embed the query
        query_embedding = self.embedder.encode(query, normalize_embeddings=True)

        # Search FAISS
        results = self.vector_store.search(query_embedding=query_embedding, top_k=top_k)
        return results



if __name__ == "__main__":
    
    vector_path = os.path.join("scriptsmsg", "embeddings", "faiss_index.bin")
    metadata_path = os.path.join("scriptsmsg", "processed", "chunks.json") 

    try:
        retriever = Retriever(vector_index_path=vector_path, metadata_path=metadata_path)
        
        query = "how many messages are there in the system?"
        top_chunks = retriever.retrieve(query, top_k=3)

        print(f"\n Results for: {query}")
        for chunk in top_chunks:
            print(f"- [Score: {chunk.get('score'):.4f}] {chunk.get('question')}")
    except Exception as e:
        print(f" Error: {e}")