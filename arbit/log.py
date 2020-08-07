import logging
import logging.handlers
import os


def getLogger(name="root"):
    fmt = "%(asctime)s - %(name)s - %(levelname)-8s - %(message)s"
    formatter = logging.Formatter(fmt)

    file_handler = logging.handlers.RotatingFileHandler(
        os.environ.get("ARBIT_LOGFILE", "data/arbit.log")
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(os.environ.get("ARBIT_LOGLEVEL", "INFO"))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
