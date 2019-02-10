class BaseConfig(object):
    DBNAME = 'pairs'
    HOST = 'influx'
    PORT = 8086
    MAGIC_LIMIT = 79
    EVENT_LIMIT = 3
    MARGIN=26
    SENTRY_URL = "https://000bf6ba6f0f41a6a1cbb8b74f494d4a@sentry.io/1359679"
    POSTGRES_HOST = 'postgres'
    POSTGRES_DATABSE = 'core'
    POSTGRES_USER = 'postgres'
    CHART_TABLE = 'charting'
    LVL_TABLE = 'levels'
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

class Prodcution(BaseConfig):
    DBNAME = 'pairs'
    HOST = 'influx'
    PORT = 8086

class Test(BaseConfig):
    DBNAME = 'pairs'
    HOST = 'influx'
    PORT = 8086
