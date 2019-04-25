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
    LOGGER = {
                'version': 1,
                'formatters': {'default': {
                    'format': '[%(asctime)s] - core - %(levelname)s : %(message)s',
                }},
                'handlers':
                    {'wsgi': {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://flask.logging.wsgi_errors_stream',
                    'formatter': 'default'
                    },
                    'file': {
                        'class': 'logging.FileHandler',
                        'filename': 'app.log',
                        'mode': 'w',
                        'formatter': 'default',
                    }
                },
                'root': {
                    'level': 'INFO',
                    'handlers': ['wsgi']
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
    INFLUX_HOST = os.environ.get('INFLUX_HOST', '0.0.0.0')
    INFLUX = {'host': INFLUX_HOST, 'database': 'test',}

    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', '0.0.0.0')
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres@{host}".format(host=POSTGRES_HOST)
