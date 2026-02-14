#/root/whatspush/airflow-infra/dags/scriptsmsg/models/embedder.py
from sentence_transformers import SentenceTransformer
import torch
import numpy as np

class MessageEmbedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading model '{model_name}' on {self.device}...")
        self.model = SentenceTransformer(model_name, device=self.device)

    def generate_embeddings(self, texts):
        """Generates normalized float32 embeddings for a list of strings."""
        if not texts:
            return None
        
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embeddings.astype("float32")