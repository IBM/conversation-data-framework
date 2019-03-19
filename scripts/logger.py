import logging
import sys

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

stdoutHandler = logging.StreamHandler(sys.stdout)
stdoutHandler.setFormatter(formatter)
stdoutHandler.setLevel(LEVELS[LOGLEVEL])
logger.addHandler(stdoutHandler)

stderrHandler = logging.StreamHandler(sys.stderr)
stderrHandler.setLevel(logging.WARNING)
stderrHandler.setFormatter(formatter)
logger.addHandler(stderrHandler)

fileHandler = logging.FileHandler(LOGFILE)
fileHandler.setFormatter(formatter)
fileHandler.setLevel(logging.INFO)
logger.addHandler(fileHandler)