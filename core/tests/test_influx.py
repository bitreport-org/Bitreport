from app.models import Series
from app.models.influx import get_candles


class TestInflux:
    def test2(self, filled_influx):
        xs = get_candles("TEST", "1h", 10)

        assert isinstance(xs, Series)

    def test_limit_timestamp(self, filled_influx):
        xs = get_candles("TEST", "1h", 20, last_timestamp=1553018400)

        print(xs.time, xs.close)
        assert xs.time[-1] == 1553014800
