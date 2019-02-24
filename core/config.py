class BaseConfig(object):
    MAGIC_LIMIT = 79
    EVENT_LIMIT = 3
    CHART_TABLE = 'charting'
    LVL_TABLE = 'levels'
    MARGIN=26
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
    INFLUX_DBNAME = 'pairs'
    INFLUX_HOST = 'influx'
    INFLUX_PORT = 8086
    SENTRY_URL = "https://000bf6ba6f0f41a6a1cbb8b74f494d4a@sentry.io/1359679"
    POSTGRES_HOST = 'postgres'
    POSTGRES_DATABSE = 'core'
    POSTGRES_USER = 'postgres'


class Test(BaseConfig):
    INFLUX_DBNAME = 'test'
    INFLUX_HOST = '0.0.0.0'
    INFLUX_PORT = 8086
    POSTGRES_HOST = '0.0.0.0'
    POSTGRES_DATABSE = 'core_test'
    POSTGRES_USER = 'postgres'
