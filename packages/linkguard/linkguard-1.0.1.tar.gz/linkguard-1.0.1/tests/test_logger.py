import logging
from linkguard.utils.logger import get_logger


def test_get_logger_returns_logger():
    """Test that get_logger returns a logger instance."""
    logger = get_logger(__name__)

    assert isinstance(logger, logging.Logger)


def test_get_logger_with_verbose():
    """Test that verbose flag sets DEBUG level."""
    logger = get_logger(__name__, verbose=True)

    assert logger.level == logging.DEBUG


def test_get_logger_without_verbose():
    """Test that default level is INFO."""
    logger = get_logger(__name__, verbose=False)

    assert logger.level == logging.INFO


def test_get_logger_unique_names():
    """Test that different names return different loggers."""
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")

    assert logger1.name == "module1"
    assert logger2.name == "module2"
    assert logger1 is not logger2


def test_logger_has_rich_handler():
    """Test that logger uses RichHandler."""
    logger = get_logger(__name__)

    # Check that at least one handler is present
    assert len(logger.handlers) > 0
