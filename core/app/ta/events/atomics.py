from app.models import Series, Point
from .helpers import add_peak


class Atomics:
    # size of maximum neighbourhood
    space_size: int = 40

    def __init__(self, series: Series):
        self._pair = series.pair
        self._timeframe = series.timeframe
        self.points = list(series.values(key="close"))

    def detect_top(self, strength: int, peak: Point, neighbours):
        if not all(peak.y >= p.y for p in neighbours):
            return None

        params = {
            'pair' : self._pair,
            'timeframe': self._timeframe,
            'time': int(peak.x),
            'value': float(peak.y),
            'name': 'TOP',
        }
        return add_peak(params, strength)

    def detect_bottom(self, strength: int, peak: Point, neighbours):
        if not all(peak.y <= p.y for p in neighbours):
            return None

        params = {
            'pair': self._pair,
            'timeframe': self._timeframe,
            'time': int(peak.x),
            'value': float(peak.y),
            'name': 'BOTTOM'
        }
        return add_peak(params, strength)

    @staticmethod
    def neighbourhood(i, xs, n, size: int = 10):
        if (i < size) or (i > n - size):
            return xs[i], None

        return xs[i], xs[i - size:i + size]


    def detect_peak(self, position, close, min_size: int = 10):
        close_size = len(close)
        for strength, size in enumerate(range(min_size, self.space_size)):
            point, ngbr = self.neighbourhood(position, close, close_size, size)
            if ngbr is not None:
                self.detect_top(strength + min_size, point, ngbr)
                self.detect_bottom(strength + min_size, point, ngbr)

    def find_all_peaks(self, close):
        close = close[-self.space_size:]

        for i, c in enumerate(close):
            self.detect_peak(i, close)

    def remake(self):
        for i, p in enumerate(self.points):
            self.find_all_peaks(self.points[:i])
