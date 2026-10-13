from pathlib import Path

from src.logger import get_logger


def test_logger_creates_log_file():
    logger = get_logger("test_logger")

    logger.info("Test log message")

    log_file = Path("logs/app.log")

    assert log_file.exists()


def test_logger_returns_named_logger():
    logger = get_logger("document_processor")

    assert logger.name == "document_processor"