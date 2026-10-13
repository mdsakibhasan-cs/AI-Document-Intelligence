import re

from src.logger import get_logger


logger = get_logger(__name__)


class QAEngine:
    """
    Source-grounded question answering engine.

    The engine selects and reformats evidence from retrieved
    document chunks. It does not use an external LLM.

    Supported question intents:
        - objective
        - definition
        - mechanism
        - result
        - limitation / challenge / problem
        - general
    """

    def __init__(self):
        logger.info("QA engine initialized")

    # ---------------------------------------------------------
    # TEXT NORMALIZATION
    # ---------------------------------------------------------

    def _normalize_text(self, text):
        if not text:
            return ""

        text = str(text)

        text = re.sub(r"\bT\s+o\b", "To", text)
        text = re.sub(r"\bA\s+DFEmu\b", "ADFEmu", text)

        text = re.sub(
            r"(?<=[a-z])(?=[A-Z])",
            " ",
            text,
        )

        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    # ---------------------------------------------------------
    # INTENT DETECTION
    # ---------------------------------------------------------

    def _detect_intent(self, question):
        q = question.lower().strip()

        # Problem / challenge / limitation questions must be
        # checked before generic "what does" or "what are"
        # patterns.
        if any(
            phrase in q
            for phrase in [
                "limitation",
                "limitations",
                "future work",
                "future research",
                "research gap",
                "research gaps",
                "challenge",
                "challenges",
                "drawback",
                "drawbacks",
                "what problem does",
                "what problems does",
                "what problem do",
                "what problems do",
                "what challenges does",
                "what challenges do",
                "what problem is",
                "what problems are",
            ]
        ):
            return "limitation"

        # Objective / purpose questions.
        if any(
            phrase in q
            for phrase in [
                "main objective",
                "main objectives",
                "objective",
                "objectives",
                "purpose",
                "aim",
                "aims",
                "goal",
                "goals",
                "what is the paper trying",
                "what does the paper aim",
            ]
        ):
            return "objective"

        # Mechanism / how questions.
        if re.search(
            r"\bhow\b|\bhow does\b|\bhow do\b|\bhow is\b",
            q,
        ):
            return "mechanism"

        # Result / performance questions.
        if any(
            phrase in q
            for phrase in [
                "what results",
                "what result",
                "results did",
                "result did",
                "performance",
                "achievements",
                "achieve",
                "improve",
                "improvement",
                "coverage",
                "success rate",
                "evaluation result",
                "experimental result",
                "main results",
                "key results",
            ]
        ):
            return "result"

        # Definition questions.
        if any(
            phrase in q
            for phrase in [
                "what is adfemu",
                "what does adfemu",
                "what is this",
                "what is the framework",
                "what is the approach",
            ]
        ):
            return "definition"

        return "general"

    # ---------------------------------------------------------
    # TOKENIZATION
    # ---------------------------------------------------------

    def _tokenize(self, text):
        stopwords = {
            "what",
            "is",
            "are",
            "the",
            "a",
            "an",
            "of",
            "to",
            "in",
            "on",
            "for",
            "and",
            "or",
            "does",
            "do",
            "how",
            "did",
            "this",
            "that",
            "document",
            "paper",
            "main",
            "objective",
            "objectives",
            "results",
            "result",
            "achieve",
            "achieved",
            "use",
            "using",
            "used",
            "with",
            "by",
            "from",
            "its",
            "their",
            "it",
            "be",
            "can",
            "will",
            "would",
            "about",
            "which",
            "was",
            "were",
            "has",
            "have",
            "had",
            "does",
            "problem",
            "problems",
            "challenge",
            "challenges",
            "limitation",
            "limitations",
            "main",
        }

        return {
            token
            for token in re.findall(
                r"\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b",
                text.lower(),
            )
            if token not in stopwords
        }

    # ---------------------------------------------------------
    # SENTENCE SPLITTING
    # ---------------------------------------------------------

    def _split_sentences(self, text):
        text = self._normalize_text(text)

        if not text:
            return []

        protected = re.sub(
            r"\b(e\.g|i\.e|etc|Fig|Figs|Sec|Secs|No)\.",
            lambda m: (
                m.group(1).replace(".", "<DOT>")
                + "<END>"
            ),
            text,
            flags=re.IGNORECASE,
        )

        parts = re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9(\[])",
            protected,
        )

        sentences = []

        for part in parts:
            part = part.replace("<DOT>", ".")
            part = part.replace("<END>", ".")
            part = part.strip()

            if len(part) >= 20:
                sentences.append(part)

        return sentences

    # ---------------------------------------------------------
    # QUALITY FILTER
    # ---------------------------------------------------------

    def _is_low_quality_sentence(self, sentence):
        """
        Reject PDF metadata, headers, page numbers and
        obviously weak evidence.
        """

        lower = sentence.lower().strip()

        if len(lower) < 25:
            return True

        # Pure page-number / numeric fragments.
        if re.fullmatch(
            r"[\d\s;:().,\-]+",
            lower,
        ):
            return True

        # Common journal metadata / headers.
        if re.search(
            r"\bcomput mater contin\b",
            lower,
        ):
            return True

        if re.search(
            r"\bvol\.\s*\d+",
            lower,
        ):
            return True

        if re.search(
            r"\bissn\b",
            lower,
        ):
            return True

        # Copyright / publication metadata.
        if "copyright ©" in lower:
            return True

        if (
            "published by" in lower
            and "press" in lower
        ):
            return True

        if "creative commons" in lower:
            return True

        # Keyword metadata.
        if lower.startswith("keywords:"):
            return True

        return False

    # ---------------------------------------------------------
    # FUTURE WORK DETECTION
    # ---------------------------------------------------------

    def _is_future_work(self, text):
        t = text.lower()

        patterns = [
            r"\bfuture work\b",
            r"\bfuture research\b",
            r"\bin future\b",
            r"\bin the future\b",
            r"\bwe plan to\b",
            r"\bwe intend to\b",
            r"\bwe will explore\b",
            r"\bwe will investigate\b",
            r"\bwe will extend\b",
            r"\bremain(s)? to be addressed\b",
            r"\bremains? an open\b",
            r"\bleft for future\b",
        ]

        return any(
            re.search(pattern, t)
            for pattern in patterns
        )

    # ---------------------------------------------------------
    # OBJECTIVE EXTRACTION
    # ---------------------------------------------------------

    def _extract_objective_block(self, search_results):
        combined = "\n".join(
            self._normalize_text(
                result.get("text", "")
            )
            for result in search_results
        )

        if not combined:
            return None

        anchor_patterns = [
            r"to\s+clearly\s+state\s+the\s+objectives\s+of\s+this\s+work,\s*our\s+research\s+aims\s+to\s*:",
            r"the\s+objectives\s+of\s+this\s+work\s+.*?our\s+research\s+aims\s+to\s*:",
            r"our\s+research\s+aims\s+to\s*:",
            r"our\s+main\s+objectives\s+are\s*:",
            r"the\s+main\s+objectives\s+are\s*:",
        ]

        anchor_match = None

        for pattern in anchor_patterns:
            match = re.search(
                pattern,
                combined,
                flags=re.IGNORECASE,
            )

            if match:
                anchor_match = match
                break

        if not anchor_match:
            return None

        tail = combined[anchor_match.end():]

        item_patterns = [
            r"\(?1\)?\s*[:.\-]?\s*(.*?)(?=\s*;?\s*\(?2\)?\s*[:.\-])",
            r"\(?2\)?\s*[:.\-]?\s*(.*?)(?=\s*;?\s*\(?3\)?\s*[:.\-])",
            r"\(?3\)?\s*[:.\-]?\s*(.*?)(?=\s+(?:our\s+contributions|in\s+summary|the\s+remainder|experimental\s+results|we\s+evaluate|we\s+conduct)|$)",
        ]

        items = []

        for pattern in item_patterns:
            match = re.search(
                pattern,
                tail,
                flags=re.IGNORECASE | re.DOTALL,
            )

            if match:
                item = self._clean_answer_text(
                    match.group(1)
                )

                if item:
                    items.append(item)

        if items:
            return "\n".join(
                f"{index}. {item}"
                for index, item in enumerate(
                    items,
                    start=1,
                )
            )

        fallback = tail[:1200]

        fallback = re.split(
            r"\b(?:our contributions|in summary|the remainder)\b",
            fallback,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]

        fallback = self._clean_answer_text(
            fallback
        )

        return fallback or None

    # ---------------------------------------------------------
    # DEFINITION EXTRACTION
    # ---------------------------------------------------------

    def _extract_definition(
        self,
        question,
        search_results,
    ):
        candidates = []

        for result in search_results:
            text = self._normalize_text(
                result.get("text", "")
            )

            for position, sentence in enumerate(
                self._split_sentences(text)
            ):
                lower = sentence.lower()

                if self._is_low_quality_sentence(
                    sentence
                ):
                    continue

                if "adfemu" not in lower:
                    continue

                if self._is_future_work(sentence):
                    continue

                score = 0.0

                if re.search(
                    r"\badfemu\s+is\s+(?:an?|the)\b",
                    lower,
                ):
                    score += 10

                if re.search(
                    r"\bwe\s+propose\s+adfemu\b",
                    lower,
                ):
                    score += 9

                if re.search(
                    r"\bpropose\s+adfemu\b",
                    lower,
                ):
                    score += 8

                if re.search(
                    r"\badfemu,\s+(?:an?|the)\b",
                    lower,
                ):
                    score += 8

                if re.search(
                    r"\badfemu\s+refers\s+to\b",
                    lower,
                ):
                    score += 8

                for cue in [
                    "framework",
                    "approach",
                    "system",
                    "method",
                    "technique",
                    "emulation",
                    "re-hosting",
                ]:
                    if cue in lower:
                        score += 1

                if (
                    "objectives of this work"
                    in lower
                ):
                    score -= 5

                if "research aims to" in lower:
                    score -= 5

                score -= position * 0.01

                if score > 0:
                    candidates.append(
                        {
                            "score": score,
                            "text": sentence,
                        }
                    )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return self._clean_answer_text(
            candidates[0]["text"]
        )

    # ---------------------------------------------------------
    # MECHANISM EXTRACTION
    # ---------------------------------------------------------

    def _extract_mechanism(
        self,
        question,
        search_results,
    ):
        query_terms = self._tokenize(question)

        candidates = []

        mechanism_cues = {
            "leverages",
            "uses",
            "using",
            "guides",
            "guide",
            "infer",
            "infers",
            "inference",
            "generate",
            "generates",
            "generation",
            "configure",
            "configures",
            "automatically",
            "combines",
            "integrates",
            "emulates",
            "emulation",
            "symbolic",
            "execution",
            "llm",
            "language",
            "model",
            "dma",
            "input",
            "path-sensitive",
            "constraints",
            "monitoring",
        }

        result_cues = {
            "achieves",
            "achieved",
            "results",
            "coverage",
            "crashes",
            "success rate",
            "%",
            "compared to",
        }

        for result in search_results:
            raw_text = self._normalize_text(
                result.get("text", "")
            )

            sentences = self._split_sentences(
                raw_text
            )

            chunk_has_adfemu = (
                "adfemu" in raw_text.lower()
            )

            for position, sentence in enumerate(
                sentences
            ):
                lower = sentence.lower()

                if self._is_low_quality_sentence(
                    sentence
                ):
                    continue

                if self._is_future_work(sentence):
                    continue

                score = 0.0

                sentence_terms = self._tokenize(
                    sentence
                )

                overlap = (
                    query_terms & sentence_terms
                )

                score += len(overlap) * 1.5

                mechanism_count = sum(
                    1
                    for cue in mechanism_cues
                    if cue in lower
                )

                score += mechanism_count * 2.0

                if chunk_has_adfemu:
                    score += 1.5

                result_count = sum(
                    1
                    for cue in result_cues
                    if cue in lower
                )

                score -= result_count * 2.0

                if (
                    "research aims to" in lower
                    or "objectives of this work"
                    in lower
                ):
                    score -= 6

                score -= position * 0.02

                if score > 0:
                    candidates.append(
                        {
                            "score": score,
                            "text": sentence,
                        }
                    )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return self._clean_answer_text(
            candidates[0]["text"]
        )

    # ---------------------------------------------------------
    # RESULT EXTRACTION
    # ---------------------------------------------------------

    def _extract_result(
        self,
        question,
        search_results,
    ):
        query_terms = self._tokenize(question)

        candidates = []

        result_cues = [
            "achieves",
            "achieved",
            "achieve",
            "results",
            "experimental results",
            "evaluation",
            "success",
            "coverage",
            "path exploration",
            "crashes",
            "outperformed",
            "improved",
            "improvement",
            "higher",
            "better",
            "compared to",
            "state of the art",
        ]

        for result in search_results:
            raw_text = self._normalize_text(
                result.get("text", "")
            )

            for position, sentence in enumerate(
                self._split_sentences(raw_text)
            ):
                lower = sentence.lower()

                if self._is_low_quality_sentence(
                    sentence
                ):
                    continue

                if self._is_future_work(sentence):
                    continue

                score = 0.0

                sentence_terms = self._tokenize(
                    sentence
                )

                overlap = (
                    query_terms & sentence_terms
                )

                score += len(overlap) * 2.0

                cue_count = sum(
                    1
                    for cue in result_cues
                    if cue in lower
                )

                score += cue_count * 2.0

                if re.search(
                    r"\b\d+(?:\.\d+)?\s*%",
                    sentence,
                ):
                    score += 8

                if re.search(
                    r"\b\d+(?:\.\d+)?\b",
                    sentence,
                ):
                    score += 3

                if (
                    "overall" in lower
                    or "experimental results"
                    in lower
                    or "our experimental results"
                    in lower
                ):
                    score += 3

                if (
                    "research aims to" in lower
                    or "objectives of this work"
                    in lower
                ):
                    score -= 8

                score -= position * 0.01

                if score > 0:
                    candidates.append(
                        {
                            "score": score,
                            "text": sentence,
                        }
                    )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        best = candidates[0]["text"]

        best = re.sub(
            r"\s*(?:as\s+a\s+result|therefore)\s*,?\s*$",
            "",
            best,
            flags=re.IGNORECASE,
        )

        return self._clean_answer_text(best)

    # ---------------------------------------------------------
    # LIMITATION / CHALLENGE / PROBLEM
    # ---------------------------------------------------------

    def _extract_limitation(
        self,
        question,
        search_results,
    ):
        """
        Prefer explicit limitations, challenges and
        problem statements.

        Future-work statements are only preferred when
        the question explicitly asks about future work
        or research gaps.
        """

        question_lower = question.lower()

        query_terms = self._tokenize(question)

        asks_future = any(
            phrase in question_lower
            for phrase in [
                "future work",
                "future research",
                "research gap",
                "research gaps",
            ]
        )

        candidates = []

        explicit_cues = [
            "limitation",
            "limitations",
            "challenge",
            "challenges",
            "drawback",
            "drawbacks",
            "problem",
            "problems",
            "lack",
            "limited",
            "not support",
            "does not support",
            "do not support",
            "does not address",
            "do not address",
            "cannot",
            "unable to",
            "difficult",
            "difficulty",
            "restrict",
            "restricted",
            "hinder",
            "hindering",
            "lack of",
        ]

        for result in search_results:
            text = self._normalize_text(
                result.get("text", "")
            )

            source_score = float(
                result.get("score", 0.0)
            )

            for position, sentence in enumerate(
                self._split_sentences(text)
            ):
                lower = sentence.lower()

                if self._is_low_quality_sentence(
                    sentence
                ):
                    continue

                sentence_terms = self._tokenize(
                    sentence
                )

                overlap = (
                    query_terms & sentence_terms
                )

                score = len(overlap) * 2.0

                explicit_count = sum(
                    1
                    for cue in explicit_cues
                    if cue in lower
                )

                score += explicit_count * 3.0

                # Strong signals for actual challenge /
                # limitation statements.
                if any(
                    phrase in lower
                    for phrase in [
                        "faces challenges",
                        "face challenges",
                        "still faces challenges",
                        "lack adequate support",
                        "greatly restricts",
                        "limits applicability",
                        "limits scalability",
                        "hinders scalability",
                        "requires manual",
                        "labor-intensive",
                        "manual modeling",
                        "manual intervention",
                    ]
                ):
                    score += 6

                # Explicit statements that existing methods
                # cannot handle or adequately support something.
                if re.search(
                    r"\b(existing|current|traditional)\s+"
                    r"(?:methods?|techniques?|frameworks?|approaches?)"
                    r".{0,120}\b"
                    r"(lack|limited|cannot|unable|"
                    r"do not support|does not support|"
                    r"do not address|does not address)\b",
                    lower,
                ):
                    score += 6

                # Future work is useful only when the question
                # explicitly asks for future work / gaps.
                if self._is_future_work(sentence):
                    if asks_future:
                        score += 3
                    else:
                        score -= 7

                # Pure numerical result statements are usually
                # not limitations.
                if re.search(
                    r"\b\d+(?:\.\d+)?\s*%",
                    sentence,
                ):
                    score -= 3

                # Slightly favor retrieved evidence, but do not
                # let retrieval score overpower explicit wording.
                score += source_score * 0.5

                score -= position * 0.01

                if score > 0:
                    candidates.append(
                        {
                            "score": score,
                            "text": sentence,
                        }
                    )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return self._clean_answer_text(
            candidates[0]["text"]
        )

    # ---------------------------------------------------------
    # GENERAL EXTRACTION
    # ---------------------------------------------------------

    def _extract_general(
        self,
        question,
        search_results,
    ):
        query_terms = self._tokenize(question)

        candidates = []

        for result in search_results:
            text = self._normalize_text(
                result.get("text", "")
            )

            source_score = float(
                result.get("score", 0.0)
            )

            for position, sentence in enumerate(
                self._split_sentences(text)
            ):
                lower = sentence.lower()

                if self._is_low_quality_sentence(
                    sentence
                ):
                    continue

                if self._is_future_work(sentence):
                    continue

                sentence_terms = self._tokenize(
                    sentence
                )

                overlap = (
                    query_terms & sentence_terms
                )

                score = (
                    len(overlap) * 2.5
                    + source_score
                )

                score -= position * 0.01

                if score > 0:
                    candidates.append(
                        {
                            "score": score,
                            "text": sentence,
                        }
                    )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return self._clean_answer_text(
            candidates[0]["text"]
        )

    # ---------------------------------------------------------
    # ANSWER CLEANING
    # ---------------------------------------------------------

    def _clean_answer_text(self, text):
        if not text:
            return ""

        text = self._normalize_text(text)

        text = re.sub(r"\s+", " ", text)

        text = re.sub(
            r"\bT\s+o\b",
            "To",
            text,
        )

        text = re.sub(
            r"\bA\s+DFEmu\b",
            "ADFEmu",
            text,
        )

        text = re.sub(
            r"\s+([,.;:!?])",
            r"\1",
            text,
        )

        text = re.sub(
            r"([,.;:!?])(?=[A-Za-z])",
            r"\1 ",
            text,
        )

        return text.strip()

    # ---------------------------------------------------------
    # MAIN ANSWER FUNCTION
    # ---------------------------------------------------------

    def answer_question(
        self,
        question,
        search_results,
    ):
        logger.info(
            "Answering question: %s",
            question,
        )

        if not question or not question.strip():
            return (
                "Please enter a question about the document."
            )

        if not search_results:
            return (
                "I could not find relevant information "
                "in the uploaded document."
            )

        intent = self._detect_intent(question)

        logger.info(
            "Detected QA intent: %s",
            intent,
        )

        if intent == "objective":
            answer = self._extract_objective_block(
                search_results
            )

            if answer:
                return answer

        if intent == "definition":
            answer = self._extract_definition(
                question,
                search_results,
            )

            if answer:
                return answer

        if intent == "mechanism":
            answer = self._extract_mechanism(
                question,
                search_results,
            )

            if answer:
                return answer

        if intent == "result":
            answer = self._extract_result(
                question,
                search_results,
            )

            if answer:
                return answer

        if intent == "limitation":
            answer = self._extract_limitation(
                question,
                search_results,
            )

            if answer:
                return answer

        # General fallback.
        answer = self._extract_general(
            question,
            search_results,
        )

        if answer:
            return answer

        # Final evidence fallback.
        best_result = search_results[0]

        fallback = self._clean_answer_text(
            best_result.get("text", "")
        )

        if fallback:
            sentences = self._split_sentences(
                fallback
            )

            if sentences:
                return sentences[0]

            return fallback[:800]

        return (
            "I could not find a clear answer "
            "in the uploaded document."
        )