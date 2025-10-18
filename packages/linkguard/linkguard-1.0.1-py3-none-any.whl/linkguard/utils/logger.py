import logging
from rich.logging import RichHandler
from rich.console import Console

console = Console()


def get_logger(name: str, verbose: bool = False) -> logging.Logger:

    level = logging.DEBUG if verbose else logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if the logger already has handlers
    if not logger.handlers:
        handler = RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=True,
            show_path=verbose,
        )
        handler.setFormatter(logging.Formatter("%(message)s"))

        logger.addHandler(handler)

    return logger
