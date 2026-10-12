import re


class QAEngine:

    def __init__(self):
        print("QA Engine initialized successfully!")

    def answer_question(self, question, search_results):

        if not search_results:
            return "No relevant information was found in the document."

        # Use the most relevant search results
        text = " ".join(
            result["text"]
            for result in search_results[:3]
        )

        # Split document text into sentences
        sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        # Remove very short sentences
        sentences = [
            sentence.strip()
            for sentence in sentences
            if len(sentence.strip().split()) >= 6
        ]

        # Extract meaningful keywords from the question
        stop_words = {
            "what", "how", "why", "when", "where",
            "which", "does", "do", "did", "is", "are",
            "was", "were", "the", "a", "an", "and",
            "or", "of", "to", "in", "on", "for",
            "with", "by", "from"
        }

        question_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                question.lower()
            )
        )

        question_words -= stop_words

        # Score each sentence
        scored_sentences = []

        for sentence in sentences:

            sentence_words = set(
                re.findall(
                    r"\b[a-zA-Z]{3,}\b",
                    sentence.lower()
                )
            )

            overlap = question_words & sentence_words

            if overlap:
                score = len(overlap)

                # Slight bonus for sentences containing
                # important action words
                action_words = {
                    "handle", "identify", "detect",
                    "infer", "fire", "generate",
                    "execute", "analyze", "model"
                }

                if sentence_words & action_words:
                    score += 1

                scored_sentences.append(
                    (score, sentence)
                )

        # Sort by relevance
        scored_sentences.sort(
            key=lambda x: x[0],
            reverse=True
        )

        if not scored_sentences:
            return search_results[0]["text"][:500]

        # Select the best sentences
        selected = []

        for score, sentence in scored_sentences:

            if sentence not in selected:
                selected.append(sentence)

            if len(selected) == 2:
                break

        # Create concise answer
        answer = " ".join(selected)

        # Clean unnecessary spaces
        answer = re.sub(r"\s+", " ", answer).strip()

        return answer