#rag/vector_store.py
import faiss
import json
import os
from typing import List, Dict, Tuple


class VectorStore:
  

    def __init__(
        self,
        index_path: str,
        metadata_path: str
    ):
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found at {index_path}")

        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found at {metadata_path}")

        self.index_path = index_path
        self.metadata_path = metadata_path

        self.index = None
        self.metadata = None

        self._load()

    def _load(self):
       
        self.index = faiss.read_index(self.index_path)

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        """
        if self.index.ntotal != len(self.metadata):
            raise ValueError(
                f"FAISS index size ({self.index.ntotal}) "
                f"!= metadata size ({len(self.metadata)})"
            )
        """

    def search(
        self,
        query_embedding,
        top_k: int = 5
    ) -> List[Dict]:
        

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        scores, indices = self.index.search(query_embedding, top_k)

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            meta = self.metadata[idx]

            results.append({
                "score": float(score),
                "faiss_id": int(idx),
                "chunk_id": meta.get("chunk_id"),
                "question": meta.get("question"),
                "source": meta.get("source", "")
            })

        return results
