class BaseConfig(object):
    MAGIC_LIMIT = 79
    EVENT_LIMIT = 3
    MARGIN = 26
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True
    SENTRY_URL = "https://000bf6ba6f0f41a6a1cbb8b74f494d4a@sentry.io/1359679"
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
    INFLUX = {'host': 'influx',
              'database': 'pairs'
              }
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres@postgres/core"
    SENTRY = True


class Development(BaseConfig):
    DEVELOPMENT = True
    DEBUG = True
    INFLUX = {'host': 'influx',
              'database': 'pairs'
              }
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres@postgres/core"
    SENTRY = False


class Test(BaseConfig):
    TESTING = True
    INFLUX = {'host': '0.0.0.0',
              'port': 5002,
              'database': 'test',
              }
    INFLUX_PROD = {'host': '0.0.0.0',
              'port': 5002,
              'database': 'pairs'
              }
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres@postgres/core"
    SENTRY = False
