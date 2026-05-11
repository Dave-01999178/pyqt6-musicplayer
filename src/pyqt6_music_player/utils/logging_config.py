import logging


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(level=logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Terminal: INFO and above only
    console_logger = logging.StreamHandler()
    console_logger.setLevel(level=logging.INFO)
    console_logger.setFormatter(formatter)

    # File: DEBUG and above (full detail for debugging)
    file_handler = logging.FileHandler("debug.log", mode="w")
    file_handler.setLevel(level=logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_logger)
    logger.addHandler(file_handler)
