from app.models import influx_db, Series
from app.utils.influx_utils import get_candles

class TestInflux:
    def test(self, app):
        with app.ctx:
            ms = influx_db.connection.get_list_measurements()

        assert isinstance(ms, list)

    def test2(self, app, filled_influx):
        with app.ctx:
            xs = get_candles('TEST', '1h', 10)

        assert isinstance(xs, Series)
