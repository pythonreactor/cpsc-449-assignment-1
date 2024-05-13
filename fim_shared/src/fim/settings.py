import logging

# Logging settings
LOGGING_LEVEL = logging.INFO

LOG_STREAM_HANDLER = logging.StreamHandler()
LOG_STREAM_FORMATTER = logging.Formatter('%(module)s::%(levelname)s::%(asctime)s: %(message)s')

LOG_STREAM_HANDLER.setLevel(LOGGING_LEVEL)
LOG_STREAM_HANDLER.setFormatter(LOG_STREAM_FORMATTER)

PROPAGATE_LOGS = False


def getLogger(name: str = None):
    """
    Custom method to retrieve a logger instance with a given name
    and set the necessary configurations.
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOGGING_LEVEL)
    logger.propagate = PROPAGATE_LOGS

    if not logger.handlers:
        logger.addHandler(LOG_STREAM_HANDLER)

    return logger
