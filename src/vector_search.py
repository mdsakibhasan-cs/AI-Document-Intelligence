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
        self.chunks = list(chunks or [])

        if sources is None:
            self.sources = ["Unknown"] * len(self.chunks)
        else:
            self.sources = list(sources)

            if len(self.sources) != len(self.chunks):
                raise ValueError(
                    "sources must have the same length as chunks"
                )

        if not self.chunks:
            self.index = None
            return

        embeddings = self.model.encode(
            self.chunks,
            convert_to_numpy=True,
            normalize_embeddings=True,
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
                text.lower(),
            )
        )

    def _keyword_score(self, query, text):
        query_words = self._tokenize(query)
        text_words = self._tokenize(text)

        if not query_words or not text_words:
            return 0.0

        overlap = query_words & text_words

        return len(overlap) / len(query_words)

    def _expanded_queries(self, query):
        query_lower = query.lower()

        expansions = [query]

        objective_terms = (
            "objective",
            "purpose",
            "goal",
            "aim",
            "aims",
            "designed",
            "focus",
            "focuses",
            "investigates",
            "examines",
            "proposes",
        )

        objective_question = any(
            re.search(
                rf"\b{re.escape(term)}\b",
                query_lower,
            )
            for term in objective_terms
        )

        if objective_question:
            expansions.append(
                f"{query} "
                "purpose objective goal aim "
                "of the paper study work"
            )

        return list(dict.fromkeys(expansions))

    def _retrieve_semantic(self, query, candidate_count):
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        scores, indices = self.index.search(
            query_embedding.astype("float32"),
            candidate_count,
        )

        results = []

        for semantic_score, index in zip(
            scores[0],
            indices[0],
        ):
            if index < 0 or index >= len(self.chunks):
                continue

            results.append(
                {
                    "index": int(index),
                    "semantic_score": float(semantic_score),
                }
            )

        return results

    def search(self, query, top_k=8):
        if self.index is None or not self.chunks:
            return []

        top_k = max(1, int(top_k))

        candidate_count = min(
            max(top_k * 8, 30),
            len(self.chunks),
        )

        candidates = {}

        for expanded_query in self._expanded_queries(query):
            semantic_results = self._retrieve_semantic(
                expanded_query,
                candidate_count,
            )

            for item in semantic_results:
                index = item["index"]
                semantic_score = item["semantic_score"]

                keyword_score = self._keyword_score(
                    expanded_query,
                    self.chunks[index],
                )

                retrieval_score = (
                    0.70 * semantic_score
                    + 0.30 * keyword_score
                )

                existing = candidates.get(index)

                if (
                    existing is None
                    or retrieval_score > existing["score"]
                ):
                    candidates[index] = {
                        "score": retrieval_score,
                        "semantic_score": semantic_score,
                        "keyword_score": keyword_score,
                        "text": self.chunks[index],
                        "source": self.sources[index],
                    }

        results = list(candidates.values())

        results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        return results[:top_k]