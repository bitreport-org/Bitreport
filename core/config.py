class BaseConfig(object):
    DBNAME = 'pairs'
    HOST = 'influx'
    PORT = 8086
    MAGIC_LIMIT = 79
    EVENT_LIMIT = 3
    EXCHANGES = 'core/services/exchanges.npy'
    MARGIN=26


class DevelopmentConfig(BaseConfig):
    DBNAME = 'test'
    HOST = 'localhost'
    PORT = 8086
    MAGIC_LIMIT = 79
    EVENT_LIMIT = 3
    EXCHANGES = 'core/services/exchanges.npy'


class TestingConfig(BaseConfig):
    DBNAME = 'test'
    HOST = '0.0.0.0'
    PORT = 8086
    MAGIC_LIMIT = 79
    EVENT_LIMIT = 3
    EXCHANGES = 'core/services/exchanges.npy'