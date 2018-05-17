class BaseConfig(object):
    DBNAME = 'pairs'
    HOST = 'influx'
    PORT = 8086
    MAGIC_LIMIT = 79
    EVENT_LIMIT = 3
    EXCHANGES = 'exchanges.npz'
    MARGIN=26


# class BaseConfig(object):
#     DBNAME = 'test'
#     HOST = 'localhost'
#     PORT = 8086
#     MAGIC_LIMIT = 79
#     EVENT_LIMIT = 3
#     EXCHANGES = 'exchanges.npz'
#     MARGIN=26
