import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class VectorSearch:
    def __init__(self):
        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.index = None
        self.chunks = []

    def build_index(self, chunks):
        self.chunks = chunks

        embeddings = self.model.encode(
            chunks,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings.astype("float32"))

    def search(self, query, top_k=3):
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        scores, indices = self.index.search(
            query_embedding.astype("float32"),
            top_k
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            results.append({
                "score": float(score),
                "text": self.chunks[index]
            })

        return results