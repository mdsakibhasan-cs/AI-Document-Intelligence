from pathlib import Path

import pymupdf
import pytesseract
from docx import Document

from src.logger import get_logger


logger = get_logger(__name__)


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

POPPLER_PATH = Path(
    r"C:\Users\sakib\AppData\Local\Microsoft\WinGet\Packages"
    r"\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\poppler-25.07.0\Library\bin"
)


if TESSERACT_PATH.exists():
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)
else:
    logger.warning(
        "Tesseract executable not found at: %s",
        TESSERACT_PATH,
    )


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

                if not POPPLER_PATH.exists():
                    raise FileNotFoundError(
                        f"Poppler directory not found: {POPPLER_PATH}"
                    )

                images = convert_from_path(
                    str(file_path),
                    first_page=page_number,
                    last_page=page_number,
                    poppler_path=str(POPPLER_PATH),
                )

                if not images:
                    logger.warning(
                        "No image generated for PDF page %d.",
                        page_number,
                    )
                    continue

                ocr_text = pytesseract.image_to_string(images[0])

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