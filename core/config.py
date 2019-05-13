import os


class BaseConfig(object):
    # Core
    MAGIC_LIMIT = 79
    MARGIN = 26

    # Admin
    ADMIN_ENABLED = True
    SESSION_TYPE = 'filesystem'
    BASIC_AUTH_USERNAME = 'admin'
    BASIC_AUTH_PASSWORD = 'magicPassword'

    # Sentry
    SENTRY_URL = "https://000bf6ba6f0f41a6a1cbb8b74f494d4a@sentry.io/1359679"
    SENTRY = False

    # Flask
    SECRET_KEY = '#OKQ2DvC\xddpg\xcd\xc2E\x84'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True
    TESTING = False
    DEVELOPMENT = True
    DEBUG = False
    LOGGER = {
                'version': 1,
                'formatters': {
                    'default': {
                        'format': '[%(asctime)s] -\u001b[35m\u001b[1m CORE \u001b[0m- %(levelname)s : %(message)s',
                    }
                },
                'handlers': {
                    'default': {
                        'level': 'INFO',
                        'formatter': 'default',
                        'class': 'logging.StreamHandler',
                        'stream': 'ext://sys.stdout',  # Default is stderr
                    },
                },
                'loggers': {
                    '': {  # root logger
                        'handlers': ['default'],
                        'level': 'INFO',
                        'propagate': True
                    }
                }
            }


class Production(BaseConfig):
    DEBUG = False
    DEVELOPMENT = False
    ADMIN_ENABLED = False
    INFLUX = {'host': 'influx', 'database': 'pairs'}
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres@postgres"
    SENTRY = True


class Development(BaseConfig):
    DEVELOPMENT = True
    DEBUG = True
    INFLUX = {'host': 'influx', 'database': 'pairs'}
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres@postgres"


class Test(BaseConfig):
    TESTING = True
    DEVELOPMENT = False
    DEBUG = False
    _INFLUX_HOST = os.environ.get('INFLUX_HOST', '0.0.0.0')
    INFLUX = {'host': _INFLUX_HOST, 'database': 'test',}

    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', '0.0.0.0')
    _DB_NAME = 'test'
    SQLALCHEMY_DATABASE_URI = f"postgresql://postgres@{POSTGRES_HOST}/{_DB_NAME}"
