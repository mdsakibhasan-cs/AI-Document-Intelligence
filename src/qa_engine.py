import re
from typing import Dict, List, Tuple


class QAEngine:
    """
    Source-grounded extractive QA engine.

    The engine selects answers from retrieved document text.
    It does not invent unsupported facts.
    """

    # =========================================================
    # BASIC LANGUAGE CONFIGURATION
    # =========================================================

    STOPWORDS = {
        "a", "an", "the",
        "is", "are", "was", "were",
        "be", "been", "being",

        "do", "does", "did", "doing",

        "how", "what", "why", "when",
        "where", "which", "who",
        "whom", "whose",

        "can", "could", "would",
        "should", "may", "might",
        "will", "shall",

        "of", "to", "for", "in",
        "on", "at", "by", "with",
        "from", "into", "through",

        "and", "or", "but", "as",
        "that", "this", "these",
        "those",

        "it", "its",
        "they", "them", "their",
        "he", "she",
        "we", "our",
        "you", "your",

        "about", "than", "then",

        "main", "major", "key",
        "primary", "important",

        "problem", "issue", "challenge",
        "objective", "purpose", "goal",

        "result", "results",
        "finding", "findings",

        "method", "system",
        "approach", "paper",

        "use", "uses", "used", "using",
        "handle", "handles", "handled",
    }

    QUESTION_WORDS = {
        "what", "how", "why", "when",
        "where", "which", "who",
        "whom", "whose",
        "does", "do", "did",
        "can", "could", "would",
        "should", "may", "might",
        "will", "is", "are",
        "was", "were",
    }

    GENERIC_TERMS = {
        "address",
        "addresses",
        "addressed",

        "problem",
        "issue",
        "challenge",

        "work",
        "works",
        "working",

        "handle",
        "handles",
        "handled",

        "use",
        "uses",
        "used",
        "using",

        "method",
        "approach",
        "system",
        "paper",

        "main",
        "major",
        "key",
        "primary",

        "objective",
        "purpose",
        "goal",

        "result",
        "results",
        "finding",
        "findings",
    }

    # =========================================================
    # COMPARISON / NEGATIVE LANGUAGE
    # =========================================================

    COMPARISON_PHRASES = (
        "compared to",
        "compared with",
        "in comparison",
        "in contrast",
        "unlike",
        "whereas",

        "other samples",
        "other approaches",
        "other methods",
        "other systems",
        "other techniques",
        "other tools",

        "orthogonal challenge",


        "does not address",
        "does not support",
        "does not handle",

        "cannot address",
        "cannot support",
        "cannot handle",
    )

    # =========================================================
    # PROBLEM CUES
    # =========================================================

    PROBLEM_CUES = (
        "major issue",
        "major problem",
        "key problem",
        "main problem",

        "critical issue",
        "critical problem",

        "challenge",
        "problem of",
        "problem with",

        "difficulty",
        "difficult",

        "remains unresolved",
        "unresolved",
        "remains a challenge",

        "incorrectly",
        "incorrect",
        "wrong",

        "imprecise",
        "inaccurate",

        "crash",
        "crashes",

        "get stuck",
        "stuck",

        "hang",
        "hangs",

        "halt",
        "halts",

        "reset",
        "resets",

        "infinite loop",

        "cannot determine",
        "unable to determine",

        "randomly triggered",
        "wrong interrupts",
    )

    STRONG_PROBLEM_PATTERNS = (
        "major issue",
        "major problem",
        "key problem",
        "critical issue",
        "critical problem",

        "remains unresolved",
        "challenge remains",

        "challenge of accurately",
        "problem of accurately",

        "proper mechanism",

        "interrupt triggering problem",
        "interrupt handling problem",
        "triggering interrupts problem",
    )

    # =========================================================
    # MECHANISM CUES
    # =========================================================

    MECHANISM_CUES = (
        "uses",
        "using",

        "utilizes",
        "utilises",

        "via",
        "through",
        "based on",

        "handles",
        "handle",

        "triggers",
        "trigger",
        "firing",

        "mechanism",
        "algorithm",
        "architecture",
        "framework",

        "monitors",
        "monitor",

        "detects",
        "detect",

        "identifies",
        "identify",

        "models",
        "model",

        "analyzes",
        "analyze",

        "selects",
        "select",

        "adapts",
        "adaptive",

        "automatically",

        "determines",
        "determine",

        "tracks",
        "track",

        "checks",
        "check",
    )

    # =========================================================
    # OBJECTIVE CUES
    # =========================================================

    OBJECTIVE_CUES = (
        "aims to",
        "aim to",
        "aimed to",

        "our goal",
        "goal is",

        "purpose is",
        "objective is",

        "designed to",

        "we propose",
        "we introduce",
        "we present",

        "we develop",
        "we developed",

        "to address",
        "to tackle",
        "to solve",

        "focuses on",
        "focus on",

        "intended to",
    )

    # =========================================================
    # RESULT CUES
    # =========================================================

    RESULT_CUES = (
        "we found",
        "we discovered",
        "found that",
        "discovered that",

        "results show",
        "results indicate",
        "our results",

        "achieved",
        "achieves",

        "outperforms",

        "improves",
        "improved",

        "higher",
        "lower",

        "coverage",

        "vulnerabilities",
        "vulnerability",

        "evaluated",
        "evaluation",

        "experiment",
        "experiments",

        "successfully",

        "detected",
        "identified",

        "revealed",
        "demonstrated",

        "shows",
        "showed",
    )

    # =========================================================
    # LIMITATION CUES
    # =========================================================

    LIMITATION_CUES = (
        "limitation",
        "limitations",

        "future work",
        "future research",

        "does not support",
        "does not handle",
        "does not address",

        "cannot support",
        "cannot handle",
        "cannot address",

        "cannot fully",

        "could not",

        "unable to",
        "unable",

        "drawback",
        "shortcoming",

        "not supported",
        "not addressed",
        "not covered",

        "remains a challenge",
        "still challenging",
    )

    # =========================================================
    # INIT
    # =========================================================

    def __init__(self):
        pass

    # =========================================================
    # TEXT NORMALIZATION
    # =========================================================

    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""

        text = str(text)

        replacements = {
            "\u00ad": "",
            "\r\n": "\n",
            "\r": "\n",

            "interruptdriven": "interrupt-driven",
            "interrupt driven": "interrupt-driven",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        # Repair words split across PDF line breaks:
        # interrupt-\ntriggering -> interrupt-triggering
        text = re.sub(
            r"([A-Za-z])-\s*\n\s*([A-Za-z])",
            r"\1-\2",
            text
        )

        # Remaining newlines become spaces.
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def _clean_answer_text(self, text: str) -> str:
        if not text:
            return ""

        text = self._normalize_text(text)

        # Only punctuation spacing is changed.
        # No numbers or technical content are removed.
        text = re.sub(
            r"\s+([,.;:!?])",
            r"\1",
            text
        )

        text = re.sub(
            r"([(\[])\s+",
            r"\1",
            text
        )

        text = re.sub(
            r"\s+([)\]])",
            r"\1",
            text
        )

        return text.strip()

    # =========================================================
    # SENTENCE SPLITTING
    # =========================================================

    def _split_sentences(self, text: str) -> List[str]:
        """
        Research-paper-aware sentence splitting.

        Protects:
        - e.g.
        - i.e.
        - etc.
        - Fig.
        - Eq.
        - initials
        - decimal numbers

        so that they do not accidentally become sentence
        boundaries.
        """

        text = self._normalize_text(text)

        if not text:
            return []

        # -----------------------------------------------------
        # Protect common abbreviations
        # -----------------------------------------------------

        protected = {
            "e.g.": "__EG__",
            "i.e.": "__IE__",
            "etc.": "__ETC__",

            "Fig.": "__FIG__",
            "Figs.": "__FIGS__",

            "Eq.": "__EQ__",
            "Eqs.": "__EQS__",

            "Dr.": "__DR__",
            "Mr.": "__MR__",
            "Mrs.": "__MRS__",
        }

        for old, new in protected.items():
            text = text.replace(old, new)

        # -----------------------------------------------------
        # Protect decimal points
        # -----------------------------------------------------

        text = re.sub(
            r"(?<=\d)\.(?=\d)",
            "__DECIMAL__",
            text
        )

        # -----------------------------------------------------
        # Protect initials
        # Example:
        # A. B. Smith
        # -----------------------------------------------------

        text = re.sub(
            r"\b([A-Z])\.(?=\s+[A-Z])",
            r"\1__INITIAL__",
            text
        )

        # -----------------------------------------------------
        # Sentence boundary
        # -----------------------------------------------------

        parts = re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9])",
            text
        )

        # -----------------------------------------------------
        # Restore protected content
        # -----------------------------------------------------

        restored = {
            "__EG__": "e.g.",
            "__IE__": "i.e.",
            "__ETC__": "etc.",

            "__FIG__": "Fig.",
            "__FIGS__": "Figs.",

            "__EQ__": "Eq.",
            "__EQS__": "Eqs.",

            "__DR__": "Dr.",
            "__MR__": "Mr.",
            "__MRS__": "Mrs.",

            "__DECIMAL__": ".",
            "__INITIAL__": ".",
        }

        sentences = []

        for part in parts:

            for old, new in restored.items():
                part = part.replace(
                    old,
                    new
                )

            part = self._clean_answer_text(
                part
            )

            if len(part) < 20:
                continue

            if self._is_bad_sentence(
                part
            ):
                continue

            sentences.append(part)

        return sentences

    # =========================================================
    # TOKENIZATION
    # =========================================================

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(
            r"[A-Za-z][A-Za-z0-9_-]*",
            text.lower()
        )

    def _important_tokens(
        self,
        text: str
    ) -> set:

        return {
            token
            for token in self._tokenize(text)
            if token not in self.STOPWORDS
            and len(token) > 2
        }

    # =========================================================
    # QUESTION ENTITIES
    # =========================================================

    def _extract_question_entities(
        self,
        question: str
    ) -> List[str]:

        if not question:
            return []

        entities = []

        # -----------------------------------------------------
        # CamelCase / mixed-case technical names
        # Example: AidFuzzer
        # -----------------------------------------------------

        entities.extend(
            re.findall(
                r"\b[A-Z][A-Za-z0-9]*"
                r"[A-Z][A-Za-z0-9_-]*\b",
                question
            )
        )

        # -----------------------------------------------------
        # Acronyms
        # Example: AIM, LLM, HIL
        # -----------------------------------------------------

        entities.extend(
            re.findall(
                r"\b[A-Z]{2,}[0-9]*\b",
                question
            )
        )

        # -----------------------------------------------------
        # Other capitalized names
        # -----------------------------------------------------

        for token in re.findall(
            r"\b[A-Z][A-Za-z0-9_-]{2,}\b",
            question
        ):

            lower = token.lower()

            if lower in self.QUESTION_WORDS:
                continue

            if lower in self.GENERIC_TERMS:
                continue

            entities.append(token)

        # -----------------------------------------------------
        # Remove duplicates
        # -----------------------------------------------------

        unique = []

        for entity in entities:

            lower = entity.lower()

            if lower in self.QUESTION_WORDS:
                continue

            if lower in self.GENERIC_TERMS:
                continue

            if not any(
                lower == existing.lower()
                for existing in unique
            ):
                unique.append(entity)

        return unique

    # =========================================================
    # QUESTION TOPIC TOKENS
    # =========================================================

    def _question_focus_tokens(
        self,
        question: str
    ) -> set:

        tokens = self._important_tokens(
            question
        )

        return tokens - self.GENERIC_TERMS

    # =========================================================
    # INTENT DETECTION
    # =========================================================

    def _detect_intent(
        self,
        question: str
    ) -> str:

        q = self._normalize_text(
            question
        ).lower()

        # -----------------------------------------------------
        # Addressed problem
        # -----------------------------------------------------

        if re.search(
            r"\bwhat\s+problem\b|"
            r"\bwhat\s+issue\b|"
            r"\bwhich\s+problem\b|"
            r"\bwhat\s+challenge\b|"
            r"\bproblem\s+does\b|"
            r"\bissue\s+does\b|"
            r"\bchallenge\s+does\b",
            q
        ):
            return "addressed_problem"

        # -----------------------------------------------------
        # Limitations
        # -----------------------------------------------------

        if re.search(
            r"\bwhat\s+are\s+the\s+limitations?\b|"
            r"\bwhat\s+limitations?\b|"
            r"\bwhat\s+are\s+the\s+drawbacks?\b|"
            r"\bwhat\s+are\s+the\s+weaknesses?\b|"
            r"\bwhat\s+gaps?\b|"
            r"\bwhat\s+research\s+gaps?\b",
            q
        ):
            return "limitation"

        # -----------------------------------------------------
        # Objective
        # -----------------------------------------------------

        if re.search(
            r"\bmain\s+objective\b|"
            r"\bprimary\s+objective\b|"
            r"\bobjective\s+of\b|"
            r"\bpurpose\s+of\b|"
            r"\bgoal\s+of\b|"
            r"\bwhat\s+does\s+.+\s+aim\b|"
            r"\bwhat\s+is\s+the\s+purpose\b|"
            r"\bwhat\s+is\s+the\s+main\s+goal\b",
            q
        ):
            return "objective"

        # -----------------------------------------------------
        # Results
        # -----------------------------------------------------

        if re.search(
            r"\bmain\s+results?\b|"
            r"\bkey\s+results?\b|"
            r"\bwhat\s+did\s+.+\s+find\b|"
            r"\bwhat\s+were\s+the\s+results?\b|"
            r"\bfindings?\b|"
            r"\bachievements?\b|"
            r"\bwhat\s+was\s+achieved\b",
            q
        ):
            return "result"

        # -----------------------------------------------------
        # Mechanism
        # -----------------------------------------------------

        if re.search(
            r"^\s*how\s+",
            q
        ) or re.search(
            r"\bhow\s+does\b|"
            r"\bhow\s+do\b|"
            r"\bhow\s+is\b|"
            r"\bhow\s+are\b|"
            r"\bmechanism\b|"
            r"\bprocess\b",
            q
        ):
            return "mechanism"

        # -----------------------------------------------------
        # Definition
        # -----------------------------------------------------

        if re.search(
            r"^\s*what\s+is\b|"
            r"^\s*what\s+are\b",
            q
        ):
            return "definition"

        return "general"

    # =========================================================
    # QUALITY FILTERS
    # =========================================================

    def _is_bad_sentence(
        self,
        sentence: str
    ) -> bool:

        if not sentence:
            return True

        sentence = sentence.strip()

        if len(sentence) < 20:
            return True

        if re.fullmatch(
            r"[\d\s.,:;()\-]+",
            sentence
        ):
            return True

        lower = sentence.lower()

        if lower.startswith(
            "references"
        ):
            return True

        if lower.startswith(
            "acknowledgment"
        ):
            return True

        if lower.startswith(
            "acknowledgements"
        ):
            return True

        return False

    def _is_comparison_sentence(
        self,
        sentence: str
    ) -> bool:

        lower = sentence.lower()

        return any(
            phrase in lower
            for phrase in self.COMPARISON_PHRASES
        )

    def _is_limitation_sentence(
        self,
        sentence: str
    ) -> bool:

        lower = sentence.lower()

        return any(
            phrase in lower
            for phrase in self.LIMITATION_CUES
        )

    def _contains_entity(
        self,
        sentence: str,
        entities: List[str]
    ) -> bool:

        if not entities:
            return False

        lower = sentence.lower()

        return any(
            entity.lower() in lower
            for entity in entities
        )

    # =========================================================
    # CANDIDATE COLLECTION
    # =========================================================

    def _collect_candidates(
        self,
        question: str,
        search_results: List[Dict]
    ) -> List[Dict]:

        entities = self._extract_question_entities(
            question
        )

        focus_tokens = self._question_focus_tokens(
            question
        )

        candidates = []

        for result_index, result in enumerate(
            search_results
        ):

            text = result.get(
                "text",
                ""
            )

            if not text:
                continue

            sentences = self._split_sentences(
                text
            )

            for sentence_index, sentence in enumerate(
                sentences
            ):

                sentence = self._clean_answer_text(
                    sentence
                )

                if self._is_bad_sentence(
                    sentence
                ):
                    continue

                candidates.append({
                    "text": sentence,

                    "source": result.get(
                        "source",
                        "Unknown"
                    ),

                    "retrieval_score": float(
                        result.get(
                            "score",
                            0.0
                        )
                    ),

                    "result_index": result_index,

                    "sentence_index": sentence_index,

                    "entities": entities,

                    "focus_tokens": focus_tokens,
                })

        return candidates

    def _deduplicate(
        self,
        candidates: List[Dict]
    ) -> List[Dict]:

        seen = set()
        output = []

        for candidate in candidates:

            normalized = re.sub(
                r"\W+",
                " ",
                candidate["text"].lower()
            ).strip()

            if normalized in seen:
                continue

            seen.add(normalized)
            output.append(candidate)

        return output

    # =========================================================
    # GENERIC SCORING
    # =========================================================

    def _overlap_score(
        self,
        question: str,
        sentence: str
    ) -> float:

        question_words = self._question_focus_tokens(
            question
        )

        sentence_words = self._important_tokens(
            sentence
        )

        if not question_words:
            return 0.0

        overlap = (
            question_words &
            sentence_words
        )

        return len(overlap) / len(
            question_words
        )

    def _topic_overlap_score(
        self,
        candidate: Dict
    ) -> float:

        focus_tokens = candidate.get(
            "focus_tokens",
            set()
        )

        if not focus_tokens:
            return 0.0

        sentence_tokens = self._important_tokens(
            candidate["text"]
        )

        return len(
            focus_tokens &
            sentence_tokens
        ) / len(
            focus_tokens
        )

    def _entity_score(
        self,
        sentence: str,
        entities: List[str]
    ) -> float:

        if not entities:
            return 0.0

        lower = sentence.lower()

        matched = sum(
            1
            for entity in entities
            if entity.lower() in lower
        )

        return matched / len(
            entities
        )

    def _cue_score(
        self,
        sentence: str,
        cues: Tuple[str, ...]
    ) -> float:

        lower = sentence.lower()

        return sum(
            1
            for cue in cues
            if cue in lower
        )

    def _base_score(
        self,
        question: str,
        candidate: Dict
    ) -> float:

        overlap = self._overlap_score(
            question,
            candidate["text"]
        )

        entity = self._entity_score(
            candidate["text"],
            candidate["entities"]
        )

        topic_overlap = self._topic_overlap_score(
            candidate
        )

        retrieval = candidate[
            "retrieval_score"
        ]

        return (
            0.20 * retrieval
            + 0.35 * overlap
            + 0.25 * entity
            + 0.20 * topic_overlap
        )

    # =========================================================
    # ADDRESSED PROBLEM
    # =========================================================

    def _problem_score(
        self,
        question: str,
        candidate: Dict
    ) -> float:

        text = candidate["text"]
        lower = text.lower()

        score = self._base_score(
            question,
            candidate
        )

        score += (
            0.25 *
            self._cue_score(
                text,
                self.PROBLEM_CUES
            )
        )

        for pattern in self.STRONG_PROBLEM_PATTERNS:

            if pattern in lower:
                score += 1.00

        # Concrete consequences.
        if re.search(
            r"\b(crash|crashes|stuck|"
            r"halt|halts|reset|resets|"
            r"infinite loop|hang|hangs)\b",
            lower
        ):
            score += 0.70

        # Domain-specific evidence.
        if re.search(
            r"\b(interrupt|interrupts|"
            r"interrupt triggering|"
            r"triggering interrupts|"
            r"interrupt handling)\b",
            lower
        ):
            score += 0.55

        # Solution statement should not beat the
        # actual problem statement.
        if (
            re.search(
                r"\bwe\s+(present|introduce|propose)\b",
                lower
            )
            and
            re.search(
                r"\b(to\s+tackle|to\s+address|"
                r"to\s+solve)\b",
                lower
            )
        ):
            score -= 0.50

        if self._is_comparison_sentence(
            text
        ):
            score -= 2.00

        return score

    def _extract_addressed_problem(
        self,
        question: str,
        candidates: List[Dict]
    ) -> str:

        ranked = sorted(
            (
                (
                    self._problem_score(
                        question,
                        candidate
                    ),
                    candidate
                )
                for candidate in candidates
            ),
            key=lambda item: item[0],
            reverse=True
        )

        direct = []

        for score, candidate in ranked:

            if score <= 0:
                continue

            text = candidate["text"]
            lower = text.lower()

            if self._is_comparison_sentence(
                text
            ):
                continue

            # Skip "we present X to tackle..."
            # as the primary problem answer.
            if (
                re.search(
                    r"\bwe\s+(present|introduce|propose)\b",
                    lower
                )
                and
                re.search(
                    r"\b(to\s+tackle|to\s+address|"
                    r"to\s+solve)\b",
                    lower
                )
            ):
                continue

            direct_problem = (
                any(
                    pattern in lower
                    for pattern
                    in self.STRONG_PROBLEM_PATTERNS
                )
                or (
                    "challenge" in lower
                    and (
                        "interrupt" in lower
                        or "trigger" in lower
                    )
                )
                or (
                    "problem" in lower
                    and (
                        "interrupt" in lower
                        or "trigger" in lower
                    )
                )
            )

            if direct_problem:
                direct.append(candidate)

        if direct:

            answer_parts = [
                direct[0]["text"]
            ]

            # Add one supporting consequence sentence.
            for candidate in direct[1:]:

                lower = candidate[
                    "text"
                ].lower()

                if (
                    "crash" in lower
                    or "stuck" in lower
                    or "halt" in lower
                    or "reset" in lower
                    or "wrong" in lower
                    or "incorrect" in lower
                    or "random" in lower
                ):
                    answer_parts.append(
                        candidate["text"]
                    )
                    break

            return " ".join(
                answer_parts
            )

        # Safe fallback.
        for score, candidate in ranked:

            if score <= 0:
                continue

            if self._is_comparison_sentence(
                candidate["text"]
            ):
                continue

            return candidate["text"]

        return self._not_found()

    # =========================================================
    # DEFINITION
    # =========================================================

    def _has_explicit_definition(
        self,
        text: str,
        entities: List[str]
    ) -> bool:

        if not text or not entities:
            return False

        lower = text.lower()

        for entity in entities:

            entity_pattern = re.escape(
                entity.lower()
            )

            patterns = (
                rf"\b{entity_pattern}\s+"
                rf"is\s+(?:an?|the)\b",

                rf"\b{entity_pattern},\s+"
                rf"(?:an?|the)\b",

                rf"\bwe\s+introduce\s+"
                rf"{entity_pattern},\s+"
                rf"(?:an?|the)\b",

                rf"\bwe\s+present\s+"
                rf"{entity_pattern},\s+"
                rf"(?:an?|the)\b",

                rf"\bwe\s+propose\s+"
                rf"{entity_pattern},\s+"
                rf"(?:an?|the)\b",
            )

            if any(
                re.search(
                    pattern,
                    lower
                )
                for pattern in patterns
            ):
                return True

        return False

    def _definition_score(
        self,
        question: str,
        candidate: Dict
    ) -> float:

        text = candidate["text"]
        lower = text.lower()

        score = self._base_score(
            question,
            candidate
        )

        if candidate["entities"]:

            if self._contains_entity(
                text,
                candidate["entities"]
            ):
                score += 1.50
            else:
                score -= 2.50

        if self._has_explicit_definition(
            text,
            candidate["entities"]
        ):
            score += 2.75

        if re.search(
            r"\bwe\s+(introduce|present|propose)\b",
            lower
        ):
            score += 0.40

        # Strongly reject comparison material.
        if self._is_comparison_sentence(
            text
        ):
            score -= 4.00

        if "orthogonal challenge" in lower:
            score -= 4.00

        if "not addressed by" in lower:
            score -= 4.00

        if "not supported by" in lower:
            score -= 3.50

        if self._is_limitation_sentence(
            text
        ):
            score -= 0.50

        return score

    def _extract_definition(
        self,
        question: str,
        candidates: List[Dict]
    ) -> str:

        ranked = sorted(
            (
                (
                    self._definition_score(
                        question,
                        candidate
                    ),
                    candidate
                )
                for candidate in candidates
            ),
            key=lambda item: item[0],
            reverse=True
        )

        # Pass 1 — explicit paper-level purpose/objective
        # Pass 2 — strong author statements.
        # Pass 3 — "we aim/seek to ..."
        for score, candidate in ranked:

            if score <= 0:
                continue

            text = candidate["text"]
            lower = text.lower()

            if not self._contains_entity(
                text,
                candidate["entities"]
            ):
                continue

            if self._is_comparison_sentence(
                text
            ):
                continue

            if (
                "not addressed by" in lower
                or "orthogonal challenge" in lower
                or "not supported by" in lower
            ):
                continue

            if self._has_explicit_definition(
                text,
                candidate["entities"]
            ):
                return text

        # -----------------------------------------------------
        # Pass 2: introduction sentence
        # -----------------------------------------------------

        for score, candidate in ranked:

            if score <= 0:
                continue

            text = candidate["text"]
            lower = text.lower()

            if self._is_comparison_sentence(
                text
            ):
                continue

            if not self._contains_entity(
                text,
                candidate["entities"]
            ):
                continue

            if (
                "not addressed by" in lower
                or "orthogonal challenge" in lower
            ):
                continue

            if re.search(
                r"\bwe\s+(introduce|present|propose)\b",
                lower
            ):
                return text

        return self._not_found()

    # =========================================================
    # MECHANISM
    # =========================================================

    def _mechanism_score(
        self,
        question: str,
        candidate: Dict
    ) -> float:

        text = candidate["text"]
        lower = text.lower()

        score = self._base_score(
            question,
            candidate
        )

        # Primary entity.
        if candidate["entities"]:

            if self._contains_entity(
                text,
                candidate["entities"]
            ):
                score += 1.80
            else:
                score -= 1.80

        # Topic match.
        score += (
            0.80 *
            self._topic_overlap_score(
                candidate
            )
        )

        # Mechanism vocabulary.
        score += (
            0.35 *
            self._cue_score(
                text,
                self.MECHANISM_CUES
            )
        )

        # Strong mechanism structure.
        if re.search(
            r"\b(uses|using|via|through|"
            r"handles|triggers|firing|"
            r"monitors|identifies|models|"
            r"analyzes|selects|adapts|"
            r"determines|tracks|checks)\b",
            lower
        ):
            score += 1.00

        if re.search(
            r"\bmechanism\b|"
            r"\balgorithm\b|"
            r"\bframework\b|"
            r"\barchitecture\b",
            lower
        ):
            score += 0.35


        # Paper-introduction problem statements are not the mechanism itself.
        if (
            re.search(
                r"\bwe\s+(present|introduce|propose)\b",
                lower
            )
            and
            re.search(
                r"\b(to\s+tackle|to\s+address|to\s+solve)\b",
                lower
            )
        ):
            score -= 1.00
        # Do not select comparison sentences.
        if self._is_comparison_sentence(
            text
        ):
            score -= 2.00

        # Result-only sentences should not dominate.
        if re.search(
            r"\b(results?|vulnerabilit|"
            r"outperforms?|evaluation|"
            r"experiments?)\b",
            lower
        ):
            score -= 0.30

        return score

    def _extract_mechanism(
        self,
        question: str,
        candidates: List[Dict]
    ) -> str:

        ranked = sorted(
            (
                (
                    self._mechanism_score(
                        question,
                        candidate
                    ),
                    candidate
                )
                for candidate in candidates
            ),
            key=lambda item: item[0],
            reverse=True
        )

        for score, candidate in ranked:

            if score <= 0:
                continue

            text = candidate["text"]

            if self._is_comparison_sentence(
                text
            ):
                continue

            if (
                candidate["entities"]
                and not self._contains_entity(
                    text,
                    candidate["entities"]
                )
            ):
                continue

            return text

        return self._not_found()


    # =========================================================
    # OBJECTIVE / PURPOSE
    # =========================================================

    def _objective_score(
        self,
        question: str,
        candidate: Dict
    ) -> float:

        text = candidate["text"]
        lower = text.lower()

        score = 0.0

        # -----------------------------------------------------
        # Retrieval relevance
        # -----------------------------------------------------
        score += 0.15 * candidate.get(
            "retrieval_score",
            0.0
        )

        # -----------------------------------------------------
        # Question/topic overlap
        # -----------------------------------------------------
        score += 0.20 * self._overlap_score(
            question,
            text
        )

        score += 0.15 * self._topic_overlap_score(
            candidate
        )

        # -----------------------------------------------------
        # Strong objective / purpose language
        # -----------------------------------------------------
        strong_objective_patterns = (
            "the purpose of this paper is",
            "the purpose of this work is",
            "the purpose of this study is",
            "the purpose of this document is",

            "the main purpose",
            "the primary purpose",

            "the objective of this paper is",
            "the objective of this work is",
            "the objective of this study is",

            "the main objective",
            "the primary objective",

            "the goal of this paper is",
            "the goal of this work is",
            "the goal of this study is",

            "our goal is",
            "our objective is",
            "our purpose is",

            "this paper aims to",
            "this work aims to",
            "this study aims to",

            "we aim to",
            "we seek to",

            "this paper focuses on",
            "this work focuses on",
            "this study focuses on",
        )

        for pattern in strong_objective_patterns:
            if pattern in lower:
                score += 4.0

        # -----------------------------------------------------
        # Common objective structures
        # -----------------------------------------------------
        if re.search(
            r"\b(this\s+(paper|work|study)\s+"
            r"(aims?|seeks?|focuses?|"
            r"investigates?|examines?|"
            r"presents?|proposes?|introduces?|"
            r"develops?|addresses?))\b",
            lower
        ):
            score += 3.0

        if re.search(
            r"\b(we\s+"
            r"(aim|seek|propose|present|introduce|"
            r"develop|design|investigate|examine))\b",
            lower
        ):
            score += 2.5

        if re.search(
            r"\b(designed\s+to|"
            r"developed\s+to|"
            r"intended\s+to|"
            r"aimed\s+at|"
            r"focuses?\s+on)\b",
            lower
        ):
            score += 2.0

        # -----------------------------------------------------
        # Paper-level objective indicators
        # -----------------------------------------------------
        if re.search(
            r"\b(in\s+this\s+(paper|work|study)|"
            r"this\s+(paper|work|study)|"
            r"we\s+present|"
            r"we\s+introduce|"
            r"we\s+propose|"
            r"we\s+develop)\b",
            lower
        ):
            score += 3.0

        # Statements that explicitly address a paper-level problem
        if re.search(
            r"\b(to\s+(tackle|address|solve|mitigate|"
            r"overcome)\s+(the\s+)?"
            r"(problem|challenge|issue))\b",
            lower
        ):
            score += 2.5

        # -----------------------------------------------------
        # Penalize component/module-level objectives
        # -----------------------------------------------------
        if re.search(
            r"\b(the\s+(main\s+|primary\s+)?"
            r"(goal|objective|purpose)\s+of\s+"
            r"(the\s+)?"
            r"[a-z0-9_-]+\s+"
            r"(model|modeling|engine|module|component|"
            r"system|subsystem|manager|database))\b",
            lower
        ):
            score -= 5.0

        # -----------------------------------------------------
        # Penalize sentences that are clearly NOT objectives
        # -----------------------------------------------------

        # Results / findings
        if re.search(
            r"\b(results?|findings?|"
            r"found|discovered|"
            r"evaluated|evaluation|"
            r"experiments?|"
            r"outperforms?|"
            r"achieved|demonstrated)\b",
            lower
        ):
            score -= 2.0

        # Lessons learned / discussion / conclusion material
        if re.search(
            r"\b(lessons?\s+learned|"
            r"discussion|"
            r"conclusion|"
            r"future\s+work|"
            r"future\s+research)\b",
            lower
        ):
            score -= 3.0

        # Pure methodological descriptions
        if re.search(
            r"\b(we\s+implemented|"
            r"we\s+evaluated|"
            r"we\s+tested|"
            r"we\s+measured|"
            r"we\s+collected)\b",
            lower
        ):
            score -= 1.0

        # Comparisons
        if self._is_comparison_sentence(text):
            score -= 2.5

        # Limitations
        if self._is_limitation_sentence(text):
            score -= 2.0

        return score




    def _extract_objective(
        self,
        question: str,
        candidates: List[Dict]
    ) -> str:
        """Extract the paper-level objective without accepting arbitrary method sentences."""

        excluded_patterns = (
            r"\blessons?\s+learned\b",
            r"\bdiscussion\b",
            r"\bconclusion\b",
            r"\bfuture\s+(work|research)\b",
            r"\blimitations?\b",
            r"\bthe\s+following\s+(heuristics|rules|guidelines|steps)\b",
            r"\bfollowing\s+(heuristics|rules|guidelines|steps)\b",
        )

        def is_excluded_context(text: str) -> bool:
            lower = text.lower()
            return any(
                re.search(pattern, lower)
                for pattern in excluded_patterns
            )

        def is_component_objective(text: str) -> bool:
            lower = text.lower()

            return bool(
                re.search(
                    r"\b(the\s+(main\s+|primary\s+)?"
                    r"(goal|objective|purpose)\s+of\s+"
                    r"(the\s+)?"
                    r"[a-z0-9_-]+\s+"
                    r"(model|modeling|engine|module|component|"
                    r"subsystem|manager|database|classifier|"
                    r"retriever|generator|pipeline))\b",
                    lower
                )
            )

        def is_heuristic_or_method_proposal(text: str) -> bool:
            lower = text.lower()

            return bool(
                re.search(
                    r"\bwe\s+propose\s+the\s+following\b",
                    lower
                )
                or re.search(
                    r"\bwe\s+propose\s+(a|an|the)\s+"
                    r"(heuristic|heuristics|rule|rules|algorithm|"
                    r"strategy|method|procedure|approach)\b",
                    lower
                )
                or re.search(
                    r"\bwe\s+(develop|design|implement)\s+"
                    r"(a|an|the)\s+"
                    r"(heuristic|algorithm|module|component|"
                    r"engine|model|database|system)\b",
                    lower
                )
            )

        def valid(sentence: str) -> bool:
            sentence = sentence.strip()

            if not sentence:
                return False

            if len(sentence.split()) < 6:
                return False

            if is_excluded_context(sentence):
                return False

            if is_component_objective(sentence):
                return False

            if is_heuristic_or_method_proposal(sentence):
                return False

            return True

        # -----------------------------------------------------
        # Rank candidates, but never allow retrieval score alone
        # to override a clear paper-level objective statement.
        # -----------------------------------------------------
        ranked = sorted(
            candidates,
            key=lambda item: self._objective_score(question, item),
            reverse=True
        )

        # -----------------------------------------------------
        # Pass 1 ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â explicit paper-level purpose/objective
        # -----------------------------------------------------
        explicit_patterns = (
            r"\bthe\s+(main\s+|primary\s+)?purpose\s+of\s+this\s+"
            r"(paper|work|study)\b",

            r"\bthe\s+(main\s+|primary\s+)?objective\s+of\s+this\s+"
            r"(paper|work|study)\b",

            r"\bthe\s+(main\s+|primary\s+)?goal\s+of\s+this\s+"
            r"(paper|work|study)\b",

            r"\bthis\s+(paper|work|study)\s+aims?\s+to\b",

            r"\bthis\s+(paper|work|study)\s+seeks?\s+to\b",
        )

        for pattern in explicit_patterns:
            for candidate in ranked:
                text = candidate.get("text", "").strip()

                if not text:
                    continue

                for sentence in self._split_sentences(text) or [text]:
                    if (
                        valid(sentence)
                        and re.search(pattern, sentence, re.IGNORECASE)
                    ):
                        return sentence.strip()

        # -----------------------------------------------------
        # Pass 2 ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â strong author statements.
        #
        # "we present X to tackle Y" is an objective.
        # "we propose the following heuristics" is NOT.
        # -----------------------------------------------------
        for candidate in ranked:
            text = candidate.get("text", "").strip()

            if not text:
                continue

            for sentence in self._split_sentences(text) or [text]:
                lower = sentence.lower()

                if not valid(sentence):
                    continue

                paper_intro = bool(
                    re.search(
                        r"\b(in\s+this\s+(paper|work|study)|"
                        r"this\s+(paper|work|study))\b",
                        lower
                    )
                )

                author_action = bool(
                    re.search(
                        r"\bwe\s+(present|introduce|develop|"
                        r"propose|design|investigate|examine|"
                        r"address|tackle|solve|study)\b",
                        lower
                    )
                )

                objective_purpose = bool(
                    re.search(
                        r"\b(to\s+(tackle|address|solve|mitigate|"
                        r"overcome|improve|enable|support|"
                        r"investigate|examine|detect|identify))\b",
                        lower
                    )
                )

                if (
                    paper_intro
                    and author_action
                    and objective_purpose
                ):
                    return sentence.strip()

        # -----------------------------------------------------
        # Pass 3 ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â "we aim/seek to ..."
        # -----------------------------------------------------
        for candidate in ranked:
            text = candidate.get("text", "").strip()

            if not text:
                continue

            for sentence in self._split_sentences(text) or [text]:
                lower = sentence.lower()

                if not valid(sentence):
                    continue

                if re.search(
                    r"\bwe\s+(aim|seek)\s+to\b",
                    lower
                ):
                    return sentence.strip()

                if re.search(
                    r"\bthis\s+(paper|work|study)\s+"
                    r"(focuses?|investigates?|examines?|addresses?)\b",
                    lower
                ):
                    return sentence.strip()

        # -----------------------------------------------------
        # IMPORTANT:
        # Do NOT return an arbitrary fallback sentence for an
        # objective question. A wrong objective is worse than
        # reporting that the objective was not retrieved.
        # -----------------------------------------------------
        return self._not_found()

    def _result_score(
        self,
        question: str,
        candidate: Dict
    ) -> float:

        text = candidate["text"]
        lower = text.lower()

        score = self._base_score(
            question,
            candidate
        )

        # Result vocabulary alone is weak evidence.
        score += (
            0.20 *
            self._cue_score(
                text,
                self.RESULT_CUES
            )
        )

        if candidate["entities"]:
            if self._contains_entity(
                text,
                candidate["entities"]
            ):
                score += 0.50

        # Strong result/finding structures.
        if re.search(
            r"\b(results?|findings?)\s+"
            r"(show|showed|indicate|indicated|"
            r"demonstrate|demonstrated)\b",
            lower
        ):
            score += 2.50

        if re.search(
            r"\b("
            r"found|discovered|achieved|"
            r"outperforms?|outperformed|"
            r"demonstrated|"
            r"detected\s+\d+|"
            r"identified\s+\d+"
            r")\b",
            lower
        ):
            score += 1.80

        # Explicit measurable findings.
        if re.search(
            r"\b("
            r"improved|increased|decreased|reduced|"
            r"higher|lower|better|"
            r"accuracy|precision|recall|"
            r"coverage|pass\s+rate|mutation\s+score|"
            r"fault\s+detection"
            r")\b",
            lower
        ) and re.search(
            r"\b\d+(?:\.\d+)?%?\b",
            lower
        ):
            score += 1.50

        # Numeric evidence is useful only with result-oriented language.
        if re.search(
            r"\b\d+(?:\.\d+)?%?\b",
            lower
        ) and re.search(
            r"\b("
            r"results?|findings?|achieved|"
            r"improved|increased|decreased|reduced|"
            r"accuracy|precision|recall|coverage|"
            r"detected|identified|outperformed"
            r")\b",
            lower
        ):
            score += 0.50

        # Evaluation alone is not sufficient evidence of a result.
        if re.search(
            r"^\s*(the\s+)?"
            r"(evaluation|experiments?|experimental\s+results?)"
            r"\s+(were|was|show|showed|"
            r"demonstrate|demonstrated)?\s*$",
            lower
        ):
            score -= 2.50

        # Pure methodological statements are not results.
        if re.search(
            r"\b("
            r"we\s+(implemented|evaluated|tested|"
            r"measured|collected|used|designed|developed)"
            r"|the\s+system\s+(uses|contains|consists)"
            r")\b",
            lower
        ):
            score -= 1.50

        # Comparison-only sentences should not dominate.
        if self._is_comparison_sentence(
            text
        ):
            score -= 2.50

        # Limitations are not results.
        if self._is_limitation_sentence(
            text
        ):
            score -= 2.00

        return score


    def _extract_result(
        self,
        question: str,
        candidates: List[Dict]
    ) -> str:

        def is_strong_result(text: str) -> bool:
            lower = text.lower()

            if self._is_comparison_sentence(text):
                return False

            if self._is_limitation_sentence(text):
                return False

            # Strong explicit result/finding structures.
            if re.search(
                r"\b(results?|findings?)\s+"
                r"(show|showed|indicate|indicated|"
                r"demonstrate|demonstrated)\b",
                lower
            ):
                return True

            if re.search(
                r"\b("
                r"found|discovered|achieved|"
                r"outperforms?|outperformed|"
                r"demonstrated"
                r")\b",
                lower
            ):
                return True

            # Detection/identification counts are explicit findings.
            if re.search(
                r"\b("
                r"detected|identified"
                r")\s+\d+(?:\.\d+)?\b",
                lower
            ):
                return True

            # Quantified improvement/performance evidence.
            if (
                re.search(
                    r"\b("
                    r"improved|increased|decreased|reduced|"
                    r"higher|lower|better|"
                    r"accuracy|precision|recall|coverage|"
                    r"pass\s+rate|mutation\s+score|"
                    r"fault\s+detection"
                    r")\b",
                    lower
                )
                and
                re.search(
                    r"\b\d+(?:\.\d+)?%?\b",
                    lower
                )
            ):
                return True

            return False

        ranked = sorted(
            (
                (
                    self._result_score(
                        question,
                        candidate
                    ),
                    candidate
                )
                for candidate in candidates
            ),
            key=lambda item: item[0],
            reverse=True
        )

        selected = []

        for score, candidate in ranked:

            if score <= 0:
                continue

            if not is_strong_result(
                candidate["text"]
            ):
                continue

            selected.append(candidate)

            if len(selected) >= 2:
                break

        if selected:
            return " ".join(
                item["text"]
                for item in selected
            )

        return self._not_found()


    # =========================================================
    # LIMITATIONS
    # =========================================================

    def _limitation_score(
        self,
        question: str,
        candidate: Dict
    ) -> float:

        text = candidate["text"]
        lower = text.lower()

        score = self._base_score(
            question,
            candidate
        )

        # Limitation vocabulary alone is weak evidence.
        score += (
            0.20 *
            self._cue_score(
                text,
                self.LIMITATION_CUES
            )
        )

        # Strong explicit limitation structures.
        strong_limitation = bool(
            re.search(
                r"\b("
                r"limitation|limitations|"
                r"major limitation|key limitation|"
                r"main limitation|"
                r"shortcoming|shortcomings|"
                r"drawback|drawbacks|"
                r"constraint|constraints"
                r")\b",
                lower
            )
        )

        explicit_gap = bool(
            re.search(
                r"\b("
                r"(?:is|are|was|were)\s+not\s+"
                r"(?:addressed|covered|supported)|"
                r"not addressed|"
                r"not covered|"
                r"not supported|"
                r"does not support|"
                r"do not support|"
                r"cannot handle|"
                r"cannot detect|"
                r"cannot identify|"
                r"unable to|"
                r"unable to handle|"
                r"unable to detect|"
                r"unable to identify|"
                r"remains challenging|"
                r"remains difficult|"
                r"remains unresolved"
                r")\b",
                lower
            )
        )

        future_gap = bool(
            re.search(
                r"\b("
                r"future work|"
                r"future research|"
                r"future studies|"
                r"requires further investigation|"
                r"requires further research|"
                r"should be investigated|"
                r"should be addressed"
                r")\b",
                lower
            )
            and
            re.search(
                r"\b("
                r"limitation|"
                r"challenge|"
                r"gap|"
                r"lack|"
                r"remain|"
                r"not addressed|"
                r"not covered|"
                r"improve|"
                r"extend|"
                r"investigate|"
                r"support"
                r")\b",
                lower
            )
        )

        # Strong structures receive substantial evidence weight.
        if strong_limitation:
            score += 2.50

        if explicit_gap:
            score += 2.50

        if future_gap:
            score += 2.00

        # A bare negative statement is not enough.
        if re.search(
            r"\b(cannot|could not|unable|"
            r"does not|do not|not support|"
            r"not addressed|not covered)\b",
            lower
        ):
            if not (
                strong_limitation
                or explicit_gap
                or future_gap
            ):
                score -= 1.50

        # Pure result/evaluation sentences are not limitations.
        if re.search(
            r"\b(results?|evaluation|experiments?|"
            r"outperforms?|coverage|"
            r"detected|identified|achieved)\b",
            lower
        ):
            score -= 1.50

        # Pure methodological statements are not limitations.
        if re.search(
            r"\b(uses|using|via|through|"
            r"handles|triggers|models|"
            r"analyzes|selects|adapts|"
            r"determines|tracks|checks)\b",
            lower
        ) and not (
            strong_limitation
            or explicit_gap
            or future_gap
        ):
            score -= 1.25

        # Comparison sentences should not dominate limitation extraction.
        if self._is_comparison_sentence(
            text
        ):
            score -= 2.00

        # Candidate-level limitation classifier is useful supporting evidence.
        if self._is_limitation_sentence(
            text
        ):
            score += 1.00

        if candidate["entities"]:
            if self._contains_entity(
                text,
                candidate["entities"]
            ):
                score += 0.30

        return score


    def _extract_limitation(
        self,
        question: str,
        candidates: List[Dict]
    ) -> str:

        def is_strong_limitation(text: str) -> bool:
            lower = text.lower()

            if self._is_comparison_sentence(
                text
            ):
                return False

            # Explicit limitation/gap language.
            if re.search(
                r"\b("
                r"limitation|limitations|"
                r"major limitation|key limitation|"
                r"main limitation|"
                r"shortcoming|shortcomings|"
                r"drawback|drawbacks|"
                r"constraint|constraints"
                r")\b",
                lower
            ):
                return True

            if re.search(
                r"\b("
                r"(?:is|are|was|were)\s+not\s+"
                r"(?:addressed|covered|supported)|"
                r"not addressed|"
                r"not covered|"
                r"not supported|"
                r"does not support|"
                r"do not support|"
                r"cannot handle|"
                r"cannot detect|"
                r"cannot identify|"
                r"unable to|"
                r"remains challenging|"
                r"remains difficult|"
                r"remains unresolved"
                r")\b",
                lower
            ):
                return True

            # Future-work language counts only when tied to an actual gap.
            if re.search(
                r"\b("
                r"future work|"
                r"future research|"
                r"future studies|"
                r"requires further investigation|"
                r"requires further research|"
                r"should be investigated|"
                r"should be addressed"
                r")\b",
                lower
            ) and re.search(
                r"\b("
                r"limitation|"
                r"challenge|"
                r"gap|"
                r"lack|"
                r"remain|"
                r"not addressed|"
                r"not covered|"
                r"improve|"
                r"extend|"
                r"investigate|"
                r"support"
                r")\b",
                lower
            ):
                return True

            return False

        ranked = sorted(
            (
                (
                    self._limitation_score(
                        question,
                        candidate
                    ),
                    candidate
                )
                for candidate in candidates
            ),
            key=lambda item: item[0],
            reverse=True
        )

        selected = []

        for score, candidate in ranked:

            text = candidate["text"].strip()

            if score <= 0:
                continue

            if not is_strong_limitation(
                text
            ):
                continue

            if re.search(
                r"\b(results?|evaluation|experiments?)\b",
                text.lower()
            ) and not re.search(
                r"\b(limitation|shortcoming|drawback|"
                r"not addressed|not covered|"
                r"cannot|unable|remains)\b",
                text.lower()
            ):
                continue

            selected.append(candidate)

            if len(selected) >= 2:
                break

        if selected:
            return " ".join(
                item["text"]
                for item in selected
            )

        return self._not_found()


    # =========================================================
    # GENERAL QUESTION
    # =========================================================

    def _general_score(
        self,
        question: str,
        candidate: Dict
    ) -> float:

        text = candidate["text"]
        lower = text.lower()

        # General QA must not answer a question that clearly
        # belongs to a specialized intent such as problem,
        # mechanism, definition, objective, result, or limitation.
        intent = self._detect_intent(
            question
        )

        if intent != "general":
            return -10.0

        if self._is_comparison_sentence(
            text
        ):
            return -10.0

        score = self._base_score(
            question,
            candidate
        )

        # General paper-level questions such as:
        # "What does the paper discuss?"
        # "What is the paper about?"
        # "What does this study focus on?"
        # should rely on document-content evidence rather
        # than requiring an exact match for words like
        # "discuss" or "about".
        broad_general_question = bool(
            re.search(
                r"\b("
                r"what\s+does\s+(?:the\s+)?paper\s+"
                r"(?:discuss|cover|focus\s+on|address)|"
                r"what\s+is\s+(?:the\s+)?paper\s+about|"
                r"what\s+does\s+(?:the\s+)?study\s+"
                r"(?:discuss|cover|focus\s+on|address)|"
                r"what\s+is\s+(?:the\s+)?study\s+about"
                r")\b",
                question.lower()
            )
        )

        # Broad general questions need recognizable
        # paper-content evidence.
        if broad_general_question:
            if not re.search(
                r"\b("
                r"paper|study|research|approach|method|"
                r"system|framework|algorithm|architecture|"
                r"experiment|evaluation|results?|findings?|"
                r"problem|challenge|limitation|objective|"
                r"purpose|aim|propose|present|introduce|"
                r"develop|developed|design|designed|"
                r"detect|detected|identify|identified|"
                r"analy[sz]|model|models|"
                r"trigger|interrupt|firmware|hardware|"
                r"fuzzing|vulnerability|vulnerabilities"
                r")\b",
                lower
            ):
                return -5.0

            score += 0.75

        # Other general questions still need meaningful
        # lexical overlap or identifiable paper evidence.
        else:
            focus_tokens = candidate.get(
                "focus_tokens",
                set()
            )

            sentence_tokens = self._important_tokens(
                text
            )

            overlap = (
                focus_tokens &
                sentence_tokens
            )

            if focus_tokens and not overlap:
                return -5.0

            if focus_tokens:
                score += (
                    1.50 *
                    (
                        len(overlap) /
                        len(focus_tokens)
                    )
                )

        # Reject clearly unrelated content.
        if re.search(
            r"\b("
            r"weather|temperature|sunny|rain|"
            r"sports?|football|basketball|"
            r"movie|restaurant|holiday"
            r")\b",
            lower
        ):
            return -5.0

        return score


    def _extract_general(
        self,
        question: str,
        candidates: List[Dict]
    ) -> str:

        # Do not let General QA bypass a specialized intent.
        intent = self._detect_intent(
            question
        )

        if intent != "general":
            return self._not_found()

        ranked = sorted(
            (
                (
                    self._general_score(
                        question,
                        candidate
                    ),
                    candidate
                )
                for candidate in candidates
            ),
            key=lambda item: item[0],
            reverse=True
        )

        for score, candidate in ranked:

            if score <= 0:
                continue

            text = candidate["text"]

            if self._is_comparison_sentence(
                text
            ):
                continue

            lower = text.lower()

            if re.search(
                r"\b("
                r"weather|temperature|sunny|rain|"
                r"sports?|football|basketball|"
                r"movie|restaurant|holiday"
                r")\b",
                lower
            ):
                continue

            return text

        return self._not_found()

    # =========================================================
    # ANSWER VALIDATION
    # =========================================================

    def _validate_answer(
        self,
        question: str,
        answer: str,
        intent: str
    ) -> bool:

        if not answer:
            return False

        if answer == self._not_found():
            return False

        if len(answer.strip()) < 20:
            return False

        lower = answer.lower()

        # Definition validation.
        if intent == "definition":

            if (
                "not addressed by" in lower
                or "orthogonal challenge" in lower
                or "not supported by" in lower
            ):
                return False

            if self._is_comparison_sentence(
                answer
            ):
                return False

        # Mechanism validation.
        if intent == "mechanism":

            if self._is_comparison_sentence(
                answer
            ):
                return False

        # Problem validation.
        if intent == "addressed_problem":

            if self._is_comparison_sentence(
                answer
            ):
                return False

        return True

    # =========================================================
    # NOT FOUND
    # =========================================================

    def _not_found(self) -> str:
        return (
            "I could not find relevant information "
            "in the uploaded document."
        )

    # =========================================================
    # PUBLIC API
    # =========================================================

    def answer_question(
        self,
        question: str,
        search_results: List[Dict]
    ) -> str:

        if not question or not question.strip():
            return self._not_found()

        if not search_results:
            return self._not_found()

        question = self._normalize_text(
            question
        )

        intent = self._detect_intent(
            question
        )

        candidates = self._collect_candidates(
            question,
            search_results
        )

        candidates = self._deduplicate(
            candidates
        )

        if not candidates:
            return self._not_found()

        # -----------------------------------------------------
        # Intent-specific extraction
        # -----------------------------------------------------

        if intent == "addressed_problem":

            answer = self._extract_addressed_problem(
                question,
                candidates
            )

        elif intent == "definition":

            answer = self._extract_definition(
                question,
                candidates
            )

        elif intent == "mechanism":

            answer = self._extract_mechanism(
                question,
                candidates
            )

        elif intent == "objective":

            answer = self._extract_objective(
                question,
                candidates
            )

        elif intent == "result":

            answer = self._extract_result(
                question,
                candidates
            )

        elif intent == "limitation":

            answer = self._extract_limitation(
                question,
                candidates
            )

        else:

            answer = self._extract_general(
                question,
                candidates
            )

        # -----------------------------------------------------
        # Final validation
        # -----------------------------------------------------

        if not self._validate_answer(
            question,
            answer,
            intent
        ):
            return self._not_found()

        return answer
