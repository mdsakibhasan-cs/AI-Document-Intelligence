import re

from src.logger import get_logger


logger = get_logger(__name__)


def clean_text(text):
    """
    Clean extracted PDF/DOCX text while preserving useful
    paragraph and sentence structure for downstream QA.
    """
    logger.info("Starting text cleaning")

    try:
        if not text:
            return ""

        # ---------------------------------------------------------
        # 1. Normalize line endings
        # ---------------------------------------------------------
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # ---------------------------------------------------------
        # 2. Remove soft-hyphen characters
        # ---------------------------------------------------------
        text = text.replace("\u00ad", "")

        # ---------------------------------------------------------
        # 3. Join words broken across PDF lines
        #
        # Example:
        #   emula-
        #   tion
        # becomes:
        #   emulation
        # ---------------------------------------------------------
        text = re.sub(
            r"([A-Za-z])-\s*\n\s*([A-Za-z])",
            r"\1\2",
            text
        )

        cleaned_lines = []

        # ---------------------------------------------------------
        # 4. Clean individual lines
        # ---------------------------------------------------------
        for line in text.split("\n"):
            line = line.strip()

            # Preserve paragraph boundaries
            if not line:
                cleaned_lines.append("")
                continue

            # Remove standalone page numbers
            if re.fullmatch(r"\d+", line):
                continue

            # Remove standalone section numbers
            # Example: 1 / 2.1 / 3.2.1
            if re.fullmatch(r"\d+(?:\.\d+)*", line):
                continue

            # Remove obvious figure/table caption lines
            if re.match(
                r"^(fig\.?|figure|table)\s+\d+[\w.\-]*\s*[:.\-]?",
                line,
                flags=re.IGNORECASE
            ):
                continue

            # Normalize repeated spaces/tabs
            line = re.sub(r"[ \t]+", " ", line)

            cleaned_lines.append(line)

        # ---------------------------------------------------------
        # 5. Rebuild paragraphs
        # ---------------------------------------------------------
        paragraphs = []
        current_paragraph = []

        for line in cleaned_lines:
            if not line:
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []
            else:
                current_paragraph.append(line)

        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))

        result = "\n\n".join(paragraphs)

        # ---------------------------------------------------------
        # 6. Fix only known extraction artifacts
        #
        # These are intentionally specific so that technical
        # identifiers are not accidentally modified.
        # ---------------------------------------------------------
        known_fixes = {
            "T o": "To",
            "A DFEmu": "ADFEmu",
        }

        for wrong, correct in known_fixes.items():
            result = result.replace(wrong, correct)

        # ---------------------------------------------------------
        # 7. Normalize excessive spaces
        # ---------------------------------------------------------
        result = re.sub(r"[ \t]+", " ", result)

        # Preserve paragraph breaks
        result = re.sub(r"\n{3,}", "\n\n", result)

        result = result.strip()

        logger.info(
            "Text cleaning completed | characters=%d",
            len(result)
        )

        return result

    except Exception:
        logger.exception("Text cleaning failed")
        raise


def chunk_text(text, chunk_size=500, overlap=100):
    """
    Split text into overlapping word-based chunks.

    Newlines are preserved inside chunks so that downstream
    QA logic can still use paragraph boundaries when useful.
    """
    logger.info(
        "Starting text chunking | chunk_size=%d | overlap=%d",
        chunk_size,
        overlap
    )

    try:
        if not text or not text.strip():
            return []

        words = text.split()
        chunks = []

        start = 0
        step = chunk_size - overlap

        if step <= 0:
            raise ValueError(
                "overlap must be smaller than chunk_size"
            )

        while start < len(words):
            end = start + chunk_size

            chunk = " ".join(words[start:end]).strip()

            if chunk:
                chunks.append(chunk)

            start += step

        logger.info(
            "Text chunking completed | chunks=%d",
            len(chunks)
        )

        return chunks

    except Exception:
        logger.exception("Text chunking failed")
        raise