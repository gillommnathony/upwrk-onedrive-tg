import os
import logging
from datetime import datetime, time

today = datetime.today()


# ONEDRIVE_USER = "aeea9409-222c-4ac8-b9c9-7a04050adfae"
# ONEDRIVE_FOLDER = "01QJJ7FGDKTUN2YFMU7RFKPT3V3L2MJO4X"
ONEDRIVE_USER = "b14e0b11-0a70-4575-8be2-f36615271dfb"
ONEDRIVE_FOLDER = "014KPYZE3MHHHOGOVAVFEKJCXWK3BI6IUC"

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

LOGGING_NAME = "info.log"
LOGGING_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOGGING_PATH = os.path.join(LOGGING_DIR, LOGGING_NAME)
LOGGING_CONF = dict(
    version=1,
    disable_existing_loggers=False,
    formatters={
        'f': {
            'format':
                '%(asctime)s %(name)s:%(lineno)5s %(levelname)s:%(message)s'
        }
    },
    handlers={
        'h': {
            'level': logging.INFO,
            'formatter': 'f',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOGGING_PATH,
            'when': "midnight",
            'atTime': time(0, 0),
            'interval': 1,
            'backupCount': 10
        }
    },
    loggers={
        None: {
            'handlers': ['h'],
            'level': logging.INFO,
        }
    }
)

if not os.path.exists(LOGGING_DIR):
    os.makedirs(LOGGING_DIR)
