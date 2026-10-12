import re


def clean_text(text):
    """Clean extracted PDF/DOCX text for search and summarization."""

    text = text.replace("\r", "\n")

    # Remove common figure/table captions
    text = re.sub(
        r"(?im)^\s*(fig\.?|figure|table)\s*\d+[A-Za-z0-9\.\-]*.*$",
        "",
        text
    )

    # Remove journal/header/footer noise
    text = re.sub(
        r"(?im)^\s*(journal of latex class files|copyright|arxiv).*?$",
        "",
        text
    )

    # Remove page-number-only lines
    text = re.sub(
        r"(?m)^\s*\d+\s*$",
        "",
        text
    )

    # Remove common standalone section numbering
    text = re.sub(
        r"(?m)^\s*\d+(?:\.\d+)*\s*$",
        "",
        text
    )

    # Fix words broken across lines
    text = re.sub(
        r"(\w)-\s*\n\s*(\w)",
        r"\1\2",
        text
    )

    # Replace line breaks with spaces
    text = re.sub(
        r"\s*\n\s*",
        " ",
        text
    )

    # Remove excessive spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Remove obvious diagram fragments
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

    # Remove repeated spaces again
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks."""

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(
            words[start:end]
        )

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks