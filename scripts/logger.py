import logging

# Configuration ---------------------------------------------------
LOGLEVEL = "debug"
LOGFILE = "log"
LOGFORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
# ------------------------------------------------------------------

__all__ = ["logger"]

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

formatter = logging.Formatter(fmt=LOGFORMAT)
logger = logging.getLogger()

logger.setLevel(LEVELS[LOGLEVEL])

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

fileHandler = logging.FileHandler(LOGFILE)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)