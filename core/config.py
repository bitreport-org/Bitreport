class BaseConfig(object):
    DBNAME = 'pairs'
    HOST = 'influx'
    PORT = 8086
    MAGIC_LIMIT = 79
    EVENT_LIMIT = 3
    MARGIN=26
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
                'handlers': {'wsgi': {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://flask.logging.wsgi_errors_stream',
                    'formatter': 'default'
                }},
                'root': {
                    'level': 'INFO',
                    'handlers': ['wsgi']
                }
            }
