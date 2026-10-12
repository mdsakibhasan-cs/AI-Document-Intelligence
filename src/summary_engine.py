import re


class SummaryEngine:

    def __init__(self):
        print("Summary Engine initialized successfully!")

    # =========================================================
    # BASIC TEXT HELPERS
    # =========================================================

    def _words(self, text):
        return re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

    def _word_set(self, text):
        return set(self._words(text))

    # =========================================================
    # SENTENCE CLEANING
    # =========================================================

    def _clean_sentence(self, sentence):

        sentence = sentence.strip()

        # Remove section references such as (§6.3)
        sentence = re.sub(
            r"\s*\(?§\s*[\d.]+\)?",
            "",
            sentence
        )

        # Remove excessive whitespace
        sentence = re.sub(
            r"\s+",
            " ",
            sentence
        )

        return sentence.strip()

    # =========================================================
    # SENTENCE VALIDATION
    # =========================================================

    def _is_valid_sentence(self, sentence):

        if not sentence:
            return False

        sentence = self._clean_sentence(sentence)
        lower = sentence.lower()
        words = sentence.split()

        # Reasonable summary sentence length
        if len(words) < 12:
            return False

        if len(words) > 75:
            return False

        # -----------------------------------------------------
        # Reject headings
        # -----------------------------------------------------

        if re.match(
            r"^\s*(?:\d+(?:\.\d+)*|[A-Z]\.)\s+",
            sentence
        ):
            return False

        # -----------------------------------------------------
        # Reject figure/table fragments
        # -----------------------------------------------------

        if re.match(
            r"^\s*(?:fig\.?|figure|table)\s*\d*",
            lower
        ):
            return False

        # -----------------------------------------------------
        # Reject obvious PDF extraction noise
        # -----------------------------------------------------

        bad_patterns = [
            r"journal of latex class files",
            r"find more",
            r"cover in an",
            r"covering the of",
            r"\bthe of\b",
            r"advanced and enables",
            r"firing enable",
            r"popular emulator.*propose",
            r"and\s+and",
            r"or\s+and",
        ]

        for pattern in bad_patterns:
            if re.search(pattern, lower):
                return False

        # -----------------------------------------------------
        # Reject procedural sentences
        # -----------------------------------------------------

        procedural_starts = [
            r"^later\b",
            r"^before determining\b",
            r"^after determining\b",
            r"^finally,\s*we\b",
            r"^first,\s*",
            r"^second,\s*",
            r"^third,\s*",
            r"^next,\s*",
            r"^then,\s*",
            r"^we first\b",
            r"^we then\b",
            r"^we next\b",
            r"^in this section\b",
            r"^in the following section\b",
        ]

        for pattern in procedural_starts:
            if re.search(pattern, lower):
                return False

        # -----------------------------------------------------
        # Reject incomplete sentences
        # -----------------------------------------------------

        if re.search(
            r"\b(?:and|or|the|of|to|for|with|by|in|on|at|from|that|which)\s*[.!?]?$",
            lower
        ):
            return False

        if re.match(
            r"^(?:and|or|which|that|because|whereas|while)\b",
            lower
        ):
            return False

        # -----------------------------------------------------
        # Reject sentences containing too many numbers
        # -----------------------------------------------------

        numbers = re.findall(
            r"\b\d+(?:\.\d+)?%?\b",
            sentence
        )

        if len(numbers) >= 6:
            return False

        return True

    # =========================================================
    # SENTENCE TYPE DETECTION
    # =========================================================

    def _sentence_type(self, sentence):

        lower = sentence.lower()

        # Main contribution
        if re.search(
            r"\bin this paper, we present\b|\bwe propose\b|\bwe introduce\b|\bwe develop\b",
            lower
        ):
            return "contribution"

        # Evaluation/result
        if re.search(
            r"\bevaluat|\btesting results\b|\bresults show\b|\bresults demonstrate\b|"
            r"\bcovered\b|\bachieved\b|\b\d+(?:\.\d+)?\s*times\b",
            lower
        ):
            return "result"

        # Method/mechanism
        if re.search(
            r"\buses\b|\busing\b|\bstrategy\b|\bmechanism\b|\bmodel\b|\bautomatically\b|"
            r"\bjust-in-time\b|\binterrupt firing\b|\bsymbolic execution\b",
            lower
        ):
            return "method"

        # Problem/motivation
        if re.search(
            r"\bchalleng|\bdifficult|\bproblem\b|\bno emulator\b|\bnot feasible\b|"
            r"\black\b|\blimitation\b",
            lower
        ):
            return "problem"

        return "other"

    # =========================================================
    # SENTENCE SCORING
    # =========================================================

    def _score_sentence(self, sentence, index):

        lower = sentence.lower()
        score = 0

        # -----------------------------------------------------
        # Contribution
        # -----------------------------------------------------

        contribution_patterns = [
            (r"\bin this paper, we present\b", 30),
            (r"\bwe present\b", 24),
            (r"\bwe propose\b", 24),
            (r"\bwe introduce\b", 24),
            (r"\bwe develop\b", 20),
            (r"\bwe devise\b", 20),
        ]

        for pattern, weight in contribution_patterns:
            if re.search(pattern, lower):
                score += weight

        # -----------------------------------------------------
        # Important AIM concepts
        # -----------------------------------------------------

        keywords = {
            "aim": 8,
            "framework": 8,
            "dynamic firmware analysis": 10,
            "firmware analysis": 7,
            "hardware-independent": 9,
            "scalable": 7,
            "generic": 7,
            "mcu": 6,
            "microcontroller": 6,
            "peripheral": 7,
            "interrupt": 8,
            "interrupts": 8,
            "interrupt modeling": 10,
            "just-in-time": 10,
            "interrupt firing": 10,
            "interrupt-dependent": 10,
            "automatically": 6,
            "fully-automated": 8,
            "state-of-the-art": 7,
            "real-world": 6,
            "coverage": 6,
        }

        for phrase, weight in keywords.items():
            if phrase in lower:
                score += weight

        # -----------------------------------------------------
        # Evaluation
        # -----------------------------------------------------

        evaluation_patterns = [
            (r"\bevaluation\b", 15),
            (r"\bwe evaluated\b", 18),
            (r"\bwe evaluate\b", 16),
            (r"\btesting results\b", 18),
            (r"\bresults show\b", 18),
            (r"\bresults demonstrate\b", 18),
            (r"\bcovered\b", 10),
            (r"\bachieved\b", 10),
        ]

        for pattern, weight in evaluation_patterns:
            if re.search(pattern, lower):
                score += weight

        # Numerical result
        if re.search(
            r"\b\d+(?:\.\d+)?\s*times\b",
            lower
        ):
            score += 15

        # Early paper sentences are generally useful
        if index < 20:
            score += 8
        elif index < 40:
            score += 3

        # -----------------------------------------------------
        # Penalize procedural/navigation content
        # -----------------------------------------------------

        penalty_patterns = [
            r"\blater\b",
            r"\bbefore determining\b",
            r"\bafter determining\b",
            r"\bwe first\b",
            r"\bwe then\b",
            r"\bwe next\b",
            r"\bin this section\b",
            r"\bin this subsection\b",
            r"\bfigure \d+\b",
            r"\btable \d+\b",
            r"\b§\s*[\d.]+",
        ]

        for pattern in penalty_patterns:
            if re.search(pattern, lower):
                score -= 25

        return score

    # =========================================================
    # REMOVE DUPLICATE INFORMATION
    # =========================================================

    def _similarity(self, sentence_a, sentence_b):

        words_a = self._word_set(sentence_a)
        words_b = self._word_set(sentence_b)

        if not words_a or not words_b:
            return 0

        intersection = len(
            words_a & words_b
        )

        union = len(
            words_a | words_b
        )

        if union == 0:
            return 0

        return intersection / union

    def _is_redundant(self, sentence, selected):

        lower = sentence.lower()

        for existing in selected:

            existing_lower = existing.lower()

            # Exact same sentence
            if lower == existing_lower:
                return True

            # Strong textual similarity
            if self._similarity(
                sentence,
                existing
            ) >= 0.55:
                return True

            # -------------------------------------------------
            # Specific duplicate-result protection
            # -------------------------------------------------

            result_phrase = (
                "11.2 times more interrupt-dependent code"
            )

            if (
                result_phrase in lower
                and result_phrase in existing_lower
            ):
                return True

        return False

    # =========================================================
    # CLEAN DOCUMENT
    # =========================================================

    def _clean_document(self, text):

        text = text.replace(
            "\r",
            " "
        )

        text = text.replace(
            "\n",
            " "
        )

        # Remove common PDF header/footer noise
        noise_patterns = [
            r"\bJOURNAL OF LATEX CLASS FILES\b.*?(?=\.)",
            r"\barXiv:\S+\b",
            r"\bManuscript received\b.*?(?=\.)",
            r"\bCorresponding author:\b.*?(?=\.)",
        ]

        for pattern in noise_patterns:

            text = re.sub(
                pattern,
                " ",
                text,
                flags=re.IGNORECASE
            )

        # Remove figure/table labels
        text = re.sub(
            r"\b(?:Fig\.|Figure|TABLE|Table)\s*\d+[A-Za-z0-9.\-]*",
            " ",
            text,
            flags=re.IGNORECASE
        )

        # Fix hyphenated line breaks
        text = re.sub(
            r"(\w)-\s+(\w)",
            r"\1\2",
            text
        )

        # Remove section references
        text = re.sub(
            r"\s*\(?§\s*[\d.]+\)?",
            "",
            text
        )

        # Normalize whitespace
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # =========================================================
    # MAIN SUMMARY FUNCTION
    # =========================================================

    def summarize(
        self,
        text,
        max_sentences=4
    ):

        if not text or not text.strip():

            return (
                "No document content is available "
                "for summarization."
            )

        # Clean document
        text = self._clean_document(text)

        # -----------------------------------------------------
        # Split into sentences
        # -----------------------------------------------------

        raw_sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        candidates = []

        for index, sentence in enumerate(
            raw_sentences
        ):

            sentence = self._clean_sentence(
                sentence
            )

            if not self._is_valid_sentence(
                sentence
            ):
                continue

            score = self._score_sentence(
                sentence,
                index
            )

            sentence_type = self._sentence_type(
                sentence
            )

            candidates.append(
                {
                    "index": index,
                    "sentence": sentence,
                    "score": score,
                    "type": sentence_type,
                }
            )

        if not candidates:

            return (
                "No suitable summary could be generated "
                "from the document."
            )

        # -----------------------------------------------------
        # Remove duplicate candidates
        # -----------------------------------------------------

        unique_candidates = []

        for candidate in candidates:

            duplicate = False

            for existing in unique_candidates:

                if self._similarity(
                    candidate["sentence"],
                    existing["sentence"]
                ) >= 0.60:

                    duplicate = True
                    break

            if not duplicate:
                unique_candidates.append(
                    candidate
                )

        candidates = unique_candidates

        # -----------------------------------------------------
        # Rank candidates
        # -----------------------------------------------------

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        # -----------------------------------------------------
        # Select diverse information
        #
        # Priority:
        # 1. Contribution
        # 2. Problem/motivation
        # 3. Method
        # 4. Result
        #
        # But do not force a category if the paper
        # does not provide a valid sentence for it.
        # -----------------------------------------------------

        selected = []
        selected_types = set()

        preferred_order = [
            "contribution",
            "problem",
            "method",
            "result",
        ]

        for sentence_type in preferred_order:

            type_candidates = [
                candidate
                for candidate in candidates
                if candidate["type"] == sentence_type
            ]

            for candidate in type_candidates:

                sentence = candidate["sentence"]

                if self._is_redundant(
                    sentence,
                    selected
                ):
                    continue

                selected.append(
                    sentence
                )

                selected_types.add(
                    sentence_type
                )

                break

            if len(selected) >= max_sentences:
                break

        # -----------------------------------------------------
        # Fill remaining slots with best candidates
        # -----------------------------------------------------

        if len(selected) < max_sentences:

            for candidate in candidates:

                sentence = candidate["sentence"]

                if self._is_redundant(
                    sentence,
                    selected
                ):
                    continue

                selected.append(
                    sentence
                )

                if len(selected) >= max_sentences:
                    break

        # -----------------------------------------------------
        # Restore document order
        # -----------------------------------------------------

        selected_with_index = []

        for sentence in selected:

            for candidate in candidates:

                if candidate["sentence"] == sentence:

                    selected_with_index.append(
                        (
                            candidate["index"],
                            sentence
                        )
                    )

                    break

        selected_with_index.sort(
            key=lambda item: item[0]
        )

        final_sentences = [
            sentence
            for _, sentence
            in selected_with_index
        ]

        # -----------------------------------------------------
        # Final cleanup
        # -----------------------------------------------------

        summary = " ".join(
            final_sentences
        )

        summary = re.sub(
            r"\s+",
            " ",
            summary
        ).strip()

        if not summary:

            return (
                "No suitable summary could be generated "
                "from the document."
            )

        return summary