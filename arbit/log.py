import logging
import logging.handlers

from arbit.config import Config


def setup_logger(config: Config) -> logging.Logger:
    fmt = "%(asctime)s - %(name)s - %(levelname)-8s - %(message)s"
    formatter = logging.Formatter(fmt)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=config.log_file,
        maxBytes=1_000_000,
        backupCount=10,
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger("arbit")
    logger.setLevel(config.log_level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
