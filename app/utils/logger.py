import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logger():
    logger = logging.getLogger()

    logHandler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(levelname)s %(name)s %(message)s',
        timestamp=True
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)

    return logger

logger = setup_logger()
