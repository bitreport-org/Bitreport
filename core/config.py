import os


def resolve_config():
    environment = {'development': Development, 'production': Production}
    cfg = environment[os.environ['FLASK_ENV']]
    return cfg

class BaseConfig(object):
    # Core
    MAGIC_LIMIT = 79
    MARGIN = 26

    # Celery
    BROKER = 'redis://redis:6379'

    # Admin
    ADMIN_ENABLED = True
    SESSION_TYPE = 'filesystem'
    BASIC_AUTH_USERNAME = 'admin'
    BASIC_AUTH_PASSWORD = 'magicPassword'

    # Sentry
    SENTRY_URL = "https://000bf6ba6f0f41a6a1cbb8b74f494d4a@sentry.io/1359679"
    SENTRY = False

    # Influx
    INFLUX = {'host': 'influx', 'database': 'pairs'}
    INFLUXDB_HOST = 'influx'
    INFLUXDB_DATABASE = 'pairs'
    INFLUXDB_POOL_SIZE = 20
    INFLUXDB_RETRIES = 25

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
    INFLUXDB_HOST = 'influx'
    INFLUXDB_DATABASE = 'pairs'

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres@postgres"
    SENTRY = True


class Development(BaseConfig):
    DEVELOPMENT = True
    DEBUG = True

    INFLUX = {'host': 'influx', 'database': 'pairs'}
    INFLUXDB_HOST = 'influx'
    INFLUXDB_DATABASE = 'pairs'

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres@postgres"


class Test(BaseConfig):
    TESTING = True
    DEVELOPMENT = False
    DEBUG = False

    _INFLUX_HOST = os.environ.get('INFLUX_HOST', '0.0.0.0')
    INFLUX = {'host': _INFLUX_HOST, 'database': 'test'}
    INFLUXDB_HOST = _INFLUX_HOST
    INFLUXDB_DATABASE = 'test'

    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', '0.0.0.0')
    _DB_NAME = 'test'
    SQLALCHEMY_DATABASE_URI = f"postgresql://postgres@{POSTGRES_HOST}/{_DB_NAME}"
