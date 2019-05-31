import influxdb
from collections import namedtuple
from flask import current_app, _app_ctx_stack, Flask
from flask.globals import _app_ctx_err_msg



class InfluxDB(object):
    """
    Taken from https://github.com/btashton/flask-influxdb
    """
    _DB = namedtuple('DB', ['switch', 'create', 'drop', 'all'])
    _MEA = namedtuple('Mea', ['drop', 'all'])

    def __init__(self, app: Flask = None) -> None:
        """
        Class constructor
        :param app: Flask Application object
        """
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Initialize extension for application
        :param app: Flask Application object
        :return:
        """
        app.config.setdefault('INFLUXDB_HOST', 'localhost')
        app.config.setdefault('INFLUXDB_PORT', '8086')
        app.config.setdefault('INFLUXDB_USER', 'root')
        app.config.setdefault('INFLUXDB_PASSWORD', 'root')
        app.config.setdefault('INFLUXDB_DATABASE', None)
        app.config.setdefault('INFLUXDB_SSL', False)
        app.config.setdefault('INFLUXDB_VERIFY_SSL', False)
        app.config.setdefault('INFLUXDB_RETRIES', 4)
        app.config.setdefault('INFLUXDB_TIMEOUT', None)
        app.config.setdefault('INFLUXDB_USE_UDP', False)
        app.config.setdefault('INFLUXDB_UDP_PORT', 4444)
        app.config.setdefault('INFLUXDB_PROXIES', None)
        app.config.setdefault('INFLUXDB_POOL_SIZE', 20)

        app.teardown_appcontext(self.teardown)

    @staticmethod
    def connect() -> influxdb.InfluxDBClient:
        """
        Connect to InfluxDB using configuration parameters
        :return: InfluxDBClient object
        """
        return influxdb.InfluxDBClient(
            host=current_app.config['INFLUXDB_HOST'],
            port=current_app.config['INFLUXDB_PORT'],
            username=current_app.config['INFLUXDB_USER'],
            password=current_app.config['INFLUXDB_PASSWORD'],
            database=current_app.config['INFLUXDB_DATABASE'],
            ssl=current_app.config['INFLUXDB_SSL'],
            verify_ssl=current_app.config['INFLUXDB_VERIFY_SSL'],
            timeout=current_app.config['INFLUXDB_TIMEOUT'],
            retries=current_app.config['INFLUXDB_RETRIES'],
            use_udp=current_app.config['INFLUXDB_USE_UDP'],
            udp_port=current_app.config['INFLUXDB_UDP_PORT'],
            proxies=current_app.config['INFLUXDB_PROXIES'],
            pool_size=current_app.config['INFLUXDB_POOL_SIZE']
        )

    @staticmethod
    def teardown(exception) -> None:
        """This is really a sub in case a influxdb input actually does need
        to be able to be torn down"""
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'influxdb_db'):
            ctx.influxdb_db.close()

    @property
    def connection(self) -> influxdb.InfluxDBClient:
        """
        InfluxDBClient object
        :return:
        """
        ctx = _app_ctx_stack.top
        if ctx is None:
            raise RuntimeError(_app_ctx_err_msg)

        if not hasattr(ctx, 'influxdb_db'):
            ctx.influxdb_db = self.connect()

        return ctx.influxdb_db

    @property
    def query(self) -> callable:
        return self.connection.query

    @property
    def database(self):
        return self._DB(switch=self.connection.switch_database,
                        create=self.connection.create_database,
                        drop=self.connection.drop_database,
                        all=self.connection.get_list_database)

    @property
    def measurement(self):
        return self._MEA(drop=self.connection.drop_measurement,
                         all=self.connection.get_list_measurements)
    @property
    def write(self) -> callable:
        return self.connection.write

    @property
    def write_points(self) -> callable:
        return self.connection.write_points

    def tag_values(self, measurement: str, key: str, db_name: str = None, *args, **kwargs):
        conn = self.connection
        if conn._database and db_name is None:
            db_name = conn._database

        q = f"SHOW TAG VALUES ON {db_name} FROM {measurement} WITH KEY = {key}"
        return conn.query(query=q, *args, **kwargs)
