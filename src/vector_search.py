import re

import faiss
from sentence_transformers import SentenceTransformer


class VectorSearch:
    def __init__(self):
        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        self.index = None
        self.chunks = []
        self.sources = []

    def build_index(self, chunks, sources=None):
        self.chunks = chunks

        if sources is None:
            self.sources = ["Unknown"] * len(chunks)
        else:
            self.sources = sources

        if not chunks:
            self.index = None
            return

        embeddings = self.model.encode(
            chunks,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(
            embeddings.astype("float32")
        )

    def _tokenize(self, text):
        return set(
            re.findall(
                r"\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b",
                text.lower()
            )
        )

    def _keyword_score(self, query, text):
        query_words = self._tokenize(query)
        text_words = self._tokenize(text)

        if not query_words or not text_words:
            return 0.0

        overlap = query_words & text_words

        return len(overlap) / len(query_words)

    def search(self, query, top_k=8):
        if self.index is None or not self.chunks:
            return []

        candidate_count = min(
            max(top_k * 5, 20),
            len(self.chunks)
        )

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        scores, indices = self.index.search(
            query_embedding.astype("float32"),
            candidate_count
        )

        candidates = []

        for semantic_score, index in zip(
            scores[0],
            indices[0]
        ):
            if index < 0 or index >= len(self.chunks):
                continue

            chunk = self.chunks[index]

            keyword_score = self._keyword_score(
                query,
                chunk
            )

            combined_score = (
                0.70 * float(semantic_score)
                + 0.30 * keyword_score
            )

            candidates.append({
                "score": combined_score,
                "semantic_score": float(semantic_score),
                "keyword_score": keyword_score,
                "text": chunk,
                "source": self.sources[index]
            })

        candidates.sort(
            key=lambda result: result["score"],
            reverse=True
        )

        return candidates[:top_k]