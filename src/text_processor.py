import re

from src.logger import get_logger


logger = get_logger(__name__)


def clean_text(text):
    """Clean extracted PDF/DOCX text for search and summarization."""

    logger.info("Starting text cleaning")

    try:
        text = text.replace("\r", "\n")

        text = re.sub(
            r"(?im)^\s*(fig\.?|figure|table)\s*\d+[A-Za-z0-9\.\-]*.*$",
            "",
            text
        )

        text = re.sub(
            r"(?im)^\s*(journal of latex class files|copyright|arxiv).*?$",
            "",
            text
        )

        # Remove standalone page numbers
        text = re.sub(r"(?m)^\s*\d+\s*$", "", text)
        text = re.sub(r"(?m)^\s*\d+(?:\.\d+)*\s*$", "", text)

        # Fix broken words from PDF extraction
        text = re.sub(
            r"(\w)-\s*\n\s*(\w)",
            r"\1\2",
            text
        )

        text = re.sub(r"\s*\n\s*", " ", text)
        text = re.sub(r"[ \t]+", " ", text)

        diagram_patterns = [
            r"\bPath\s+\d+\b",
            r"\bInt\.\b",
            r"\bInterrupt\s+lines?\b",
            r"\bFirmware\s+Binary\b",
            r"\bProcessor\s+Emulator\b",
            r"\bSecurity\s+Bugs\b",
            r"\bInterrupt\s+Modeling\b",
            r"\bDynamic\s+Symbolic\s+Execution\b",
        ]

        for pattern in diagram_patterns:
            text = re.sub(
                pattern,
                "",
                text,
                flags=re.IGNORECASE
            )

        text = re.sub(r"\s+", " ", text)

        result = text.strip()

        logger.info(
            "Text cleaning completed | characters=%d",
            len(result)
        )

        return result

    except Exception:
        logger.exception("Text cleaning failed")
        raise


def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks."""

    logger.info(
        "Starting text chunking | chunk_size=%d | overlap=%d",
        chunk_size,
        overlap
    )

    try:
        words = text.split()
        chunks = []

        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])

            if chunk.strip():
                chunks.append(chunk)

            start += chunk_size - overlap

        logger.info(
            "Text chunking completed | chunks=%d",
            len(chunks)
        )

        return chunks

    except Exception:
        logger.exception("Text chunking failed")
        raise