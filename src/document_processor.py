from pathlib import Path
import os
import shutil

import pymupdf
import pytesseract
from docx import Document

from src.logger import get_logger


logger = get_logger(__name__)


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


# -------------------------------------------------------------------
# OCR configuration
# -------------------------------------------------------------------

# Optional environment variables for deployment/custom environments.
# Example:
# TESSERACT_CMD=/usr/bin/tesseract
# POPPLER_PATH=/usr/bin
#
# If these are not provided, the application tries to discover
# the required executables automatically.
TESSERACT_ENV = os.getenv("TESSERACT_CMD")
POPPLER_ENV = os.getenv("POPPLER_PATH")


# Existing Windows installation fallback.
WINDOWS_TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

WINDOWS_POPPLER_PATH = Path(
    r"C:\Users\sakib\AppData\Local\Microsoft\WinGet\Packages"
    r"\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\poppler-25.07.0\Library\bin"
)


def _configure_tesseract():
    """
    Configure Tesseract for both local Windows and cloud environments.
    """
    if TESSERACT_ENV:
        tesseract_path = Path(TESSERACT_ENV)

        if tesseract_path.exists():
            pytesseract.pytesseract.tesseract_cmd = str(
                tesseract_path
            )
            logger.info(
                "Using Tesseract from TESSERACT_CMD: %s",
                tesseract_path,
            )
            return

        logger.warning(
            "TESSERACT_CMD was provided but does not exist: %s",
            tesseract_path,
        )

    discovered_tesseract = shutil.which("tesseract")

    if discovered_tesseract:
        pytesseract.pytesseract.tesseract_cmd = discovered_tesseract
        logger.info(
            "Tesseract discovered automatically: %s",
            discovered_tesseract,
        )
        return

    if WINDOWS_TESSERACT_PATH.exists():
        pytesseract.pytesseract.tesseract_cmd = str(
            WINDOWS_TESSERACT_PATH
        )
        logger.info(
            "Using Windows Tesseract installation: %s",
            WINDOWS_TESSERACT_PATH,
        )
        return

    logger.warning(
        "Tesseract executable was not found. "
        "OCR will be unavailable until Tesseract is installed."
    )


def _get_poppler_path():
    """
    Resolve Poppler path for local or cloud environments.

    Returns:
        str | None: Poppler directory when explicitly required,
        otherwise None so pdf2image can use the system PATH.
    """
    if POPPLER_ENV:
        poppler_path = Path(POPPLER_ENV)

        if poppler_path.exists():
            logger.info(
                "Using Poppler from POPPLER_PATH: %s",
                poppler_path,
            )
            return str(poppler_path)

        logger.warning(
            "POPPLER_PATH was provided but does not exist: %s",
            poppler_path,
        )

    if WINDOWS_POPPLER_PATH.exists():
        logger.info(
            "Using Windows Poppler installation: %s",
            WINDOWS_POPPLER_PATH,
        )
        return str(WINDOWS_POPPLER_PATH)

    discovered_pdftoppm = shutil.which("pdftoppm")

    if discovered_pdftoppm:
        logger.info(
            "Poppler discovered automatically through PATH: %s",
            discovered_pdftoppm,
        )
        return None

    logger.warning(
        "Poppler was not found. "
        "OCR for scanned PDFs may be unavailable."
    )

    return None


_configure_tesseract()


def extract_text_from_pdf(file_path):
    """
    Extract text from PDF using PyMuPDF.

    Pages without extractable text are processed with
    Tesseract OCR as a fallback.
    """
    logger.info("Starting PDF extraction: %s", file_path)

    document = None

    try:
        text_parts = []

        document = pymupdf.open(str(file_path))

        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text("text")

            if page_text and page_text.strip():
                text_parts.append(page_text)
                continue

            logger.info(
                "No extractable text on PDF page %d. "
                "Attempting OCR.",
                page_number,
            )

            try:
                from pdf2image import convert_from_path

                poppler_path = _get_poppler_path()

                images = convert_from_path(
                    str(file_path),
                    first_page=page_number,
                    last_page=page_number,
                    poppler_path=poppler_path,
                )

                if not images:
                    logger.warning(
                        "No image generated for PDF page %d.",
                        page_number,
                    )
                    continue

                ocr_text = pytesseract.image_to_string(
                    images[0]
                )

                if ocr_text and ocr_text.strip():
                    text_parts.append(ocr_text)

                    logger.info(
                        "OCR successful on PDF page %d | characters=%d",
                        page_number,
                        len(ocr_text),
                    )
                else:
                    logger.warning(
                        "OCR returned no text for PDF page %d.",
                        page_number,
                    )

            except Exception:
                logger.exception(
                    "OCR failed for PDF page %d: %s",
                    page_number,
                    file_path,
                )

        text = "\n".join(text_parts)

        logger.info(
            "PDF extraction completed: %s | characters=%d",
            file_path,
            len(text),
        )

        return text

    except Exception:
        logger.exception(
            "Failed to extract text from PDF: %s",
            file_path,
        )
        raise

    finally:
        if document is not None:
            document.close()


def extract_text_from_docx(file_path):
    """
    Extract text from non-empty DOCX paragraphs.
    """
    logger.info("Starting DOCX extraction: %s", file_path)

    try:
        document = Document(str(file_path))

        text_parts = []

        for paragraph in document.paragraphs:
            paragraph_text = paragraph.text.strip()

            if paragraph_text:
                text_parts.append(paragraph_text)

        text = "\n".join(text_parts)

        logger.info(
            "DOCX extraction completed: %s | characters=%d",
            file_path,
            len(text),
        )

        return text

    except Exception:
        logger.exception(
            "Failed to extract text from DOCX: %s",
            file_path,
        )
        raise


def extract_text(file_path):
    """
    Extract text from a supported PDF or DOCX file.
    """
    file_path = Path(file_path)

    logger.info("Processing document: %s", file_path)

    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        logger.error(
            "Unsupported file type: %s",
            extension or "[no extension]",
        )

        raise ValueError(
            "Only PDF and DOCX files are supported."
        )

    if not file_path.exists():
        logger.error(
            "File not found: %s",
            file_path,
        )

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    return extract_text_from_docx(file_path)