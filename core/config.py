class BaseConfig(object):
    DBNAME = 'test'
    HOST = 'localhost'
    PORT = 8086
    MAGIC_LIMIT = 79
    EVENT_LIMIT = 3
    EXCHANGES = 'core/services/exchanges.npy'


class DevelopmentConfig(BaseConfig):
    DBNAME = 'test'
    HOST = 'localhost'
    PORT = 8086
    MAGIC_LIMIT = 79
    EVENT_LIMIT = 3
    EXCHANGES = 'core/services/exchanges.npy'


class TestingConfig(BaseConfig):
    DBNAME = 'test'
    HOST = 'localhost'
    PORT = 8086
    MAGIC_LIMIT = 79
    EVENT_LIMIT = 3
    EXCHANGES = 'core/services/exchanges.npy'