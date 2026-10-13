from pathlib import Path

from pypdf import PdfReader
from docx import Document
import pytesseract

from src.logger import get_logger


logger = get_logger(__name__)


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}

# Windows Tesseract OCR executable
TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Windows Poppler binaries
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
        TESSERACT_PATH
    )


def extract_text_from_pdf(file_path):
    logger.info("Starting PDF extraction: %s", file_path)

    try:
        reader = PdfReader(file_path)
        text = ""

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()

            if page_text and page_text.strip():
                text += page_text + "\n"

            else:
                logger.info(
                    "No extractable text on PDF page %d. "
                    "OCR will be attempted.",
                    page_number
                )

                try:
                    from pdf2image import convert_from_path

                    if not POPPLER_PATH.exists():
                        raise FileNotFoundError(
                            f"Poppler directory not found: {POPPLER_PATH}"
                        )

                    images = convert_from_path(
                        file_path,
                        first_page=page_number,
                        last_page=page_number,
                        poppler_path=str(POPPLER_PATH)
                    )

                    if images:
                        ocr_text = pytesseract.image_to_string(
                            images[0]
                        )

                        if ocr_text.strip():
                            text += ocr_text + "\n"

                            logger.info(
                                "OCR successful on PDF page %d | "
                                "characters=%d",
                                page_number,
                                len(ocr_text)
                            )
                        else:
                            logger.warning(
                                "OCR returned no text for PDF page %d",
                                page_number
                            )

                except Exception:
                    logger.exception(
                        "OCR failed for PDF page %d: %s",
                        page_number,
                        file_path
                    )

        logger.info(
            "PDF extraction completed: %s | characters=%d",
            file_path,
            len(text)
        )

        return text

    except Exception:
        logger.exception(
            "Failed to extract text from PDF: %s",
            file_path
        )
        raise


def extract_text_from_docx(file_path):
    logger.info("Starting DOCX extraction: %s", file_path)

    try:
        document = Document(file_path)
        text = ""

        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"

        logger.info(
            "DOCX extraction completed: %s | characters=%d",
            file_path,
            len(text)
        )

        return text

    except Exception:
        logger.exception(
            "Failed to extract text from DOCX: %s",
            file_path
        )
        raise


def extract_text(file_path):
    file_path = Path(file_path)

    logger.info(
        "Processing document: %s",
        file_path
    )

    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        logger.error(
            "Unsupported file type: %s",
            extension or "[no extension]"
        )
        raise ValueError(
            "Only PDF and DOCX files are supported."
        )

    if not file_path.exists():
        logger.error(
            "File not found: %s",
            file_path
        )
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    return extract_text_from_docx(file_path)