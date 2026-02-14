from typing import List
import openai
import config


class Embedder:
    def embed(self, texts: List[str]) -> List[List[float]]:
        response = openai.embeddings.create(
            model=config.EMBEDDING_MODEL,
            input=texts
        )
        return [item.embedding for item in response.data]
