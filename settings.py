import os
import logging

ONEDRIVE_USER = "aeea9409-222c-4ac8-b9c9-7a04050adfae"
ONEDRIVE_FOLDER = "01QJJ7FGDKTUN2YFMU7RFKPT3V3L2MJO4X"

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

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
            'class': 'logging.StreamHandler'
        }
    },
    loggers={
        None: {
            'handlers': ['h'],
            'level': logging.INFO,
        }
    }
)
