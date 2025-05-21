import logging
from pathlib import Path


def configure_logging(level=logging.INFO, log_file=None, force=False):
    """Configure root logging.

    Args:
        level: Log level or numeric value.
        log_file: Optional path to a log file.
        force: If True reconfigure even if handlers already exist.
    """
    logger = logging.getLogger()
    if force or not logger.handlers:
        # Remove existing handlers when forcing reconfiguration
        if force:
            for h in list(logger.handlers):
                logger.removeHandler(h)
        logger.setLevel(level if isinstance(level, int) else logging.getLevelName(level))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a logger with the given name."""
    return logging.getLogger(name)
