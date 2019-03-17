import numpy as np
from sklearn.metrics import mean_squared_error as mse

import config
from app.services import get_candles, generate_dates
from app.api.database import Chart
from app.api import db
from app.ta.peaks import detect_peaks

Config = config.BaseConfig()


class Wedge():
    def __init__(self, pair, timeframe, close, x_dates):
        self.pair = pair
        self.timeframe = timeframe
        self.close = close
        self.x_dates = np.array(x_dates) / 10000 # to increase precision
        self.type = 'wedge'
        self.margin = Config.MARGIN
        self.start = Config.MAGIC_LIMIT

    def _last_wedge(self):
        last = db.session.query(Chart).filter_by(type=self.type,
                                              timeframe=self.timeframe,
                                              pair=self.pair).order_by(Chart.id.desc()).first()
        params = None
        if last is not None:
            params = last.params
        
        return params

    def _save_wedge(self, params):
        ch = Chart(pair=self.pair, timeframe=self.timeframe,
                    type=self.type, params=params)
        db.session.add(ch)
        db.session.commit()

    def _check_last_wedge(self):
        params = self._last_wedge()

        if not params:
            return False, [], []

        candles2check = 20
        upper_band = params['upper_a'] * self.x_dates[:-self.margin] + params['upper_b']
        lower_band = params['lower_a'] * self.x_dates[:-self.margin] + params['lower_b']

        # Check price position
        price = self.close[-candles2check:]
        above = price > upper_band[-candles2check:]
        below = price < lower_band[-candles2check:]

        threshold = 0.8
        if np.sum(above)/candles2check > threshold or np.sum(below)/candles2check > threshold:
            return False, [], []
        else:
            return True, upper_band, lower_band

    def _shorten(self, upper_band, lower_band):
        s = np.sum([u > l for u, l in zip(upper_band, lower_band)])
        return upper_band[:s], lower_band[:s]

    def _make_sense(self, band_up, band_down):
        ws = band_up[0] - band_down[0]
        we = band_up[-1] - band_down[-1]
        if ws >= we :
            return True
        return False

    def make(self):
        close = self.close[self.start:]

        # Check if last wedge still make sense
        actual, band_up, band_down = self._check_last_wedge()
        if actual:
            info = self._tokens(band_up, band_down, close)
            return {'upper_band': band_up.tolist(),
                     'middle_band': [],
                     'lower_band': band_down.tolist(),
                     'info': info}

        # Make no sense? Create new wedge:
        assert  close.size == self.x_dates[:-self.margin].size, 'x, y differs'

        band_up, band_down, params = self.wedge(close, self.x_dates[:-self.margin])
        band_up, band_down = self._shorten(band_up, band_down)

        if self._make_sense(band_up, band_down):
            self._save_wedge(params)
            info = self._tokens(band_up, band_down, close)
            return {'upper_band': band_up.tolist(),
                     'middle_band': [],
                     'lower_band': band_down.tolist(),
                     'info': info}
        else:
            return {'upper_band': [],
                     'middle_band': [],
                     'lower_band': [],
                     'info': []}


    def _score_up(self, close, band, start):
        assert close.size == band.size, 'Size differs'
        s = np.sum((close <= band))

        n = close.size
        return s / n, mse(close[start:], band[start:])

    def _score_down(self, close, band, start):
        assert close.size == band.size, 'Size differs'
        s = np.sum((close >= band))
        n = close.size
        return s / n, mse(close[start:], band[start:])

    def _make_bands(self, x_close, close, xs, ys, start, t):
        if t == 'up':
            comp = self._score_up
        else:
            comp = self._score_down
        bands = []
        for i, (x, y) in enumerate(zip(xs[:-1], ys[:-1])):
            nx, ny = xs[i + 1], ys[i + 1]
            slope = (ny - y) / (nx - x)
            coef = y - slope * x
            b = slope * x_close + coef

            s, smse = comp(close, b, start)
            bands.append({'score': s, 'mse': smse,
                          'band': b, 'params': (slope, coef)})

        return bands

    def _simple_band(self, x_close, close, type_, skip_n_last=20, peak_dist=15):
        if type_ == 'up':
            f1, f2 = np.argmax, np.max
        else:
            f1, f2 = np.argmin, np.min

        x = f1(close[:-skip_n_last])
        y = close[x]

        if x < 0.75 * close.size:
            slope = (close[x + peak_dist:-skip_n_last] - y) / (x_close[x + peak_dist: close.size - skip_n_last] - x)
            a = f2(slope)
            coef = y - a * x
            b = a * x_close + coef
        else:
            slope = (close[:-(x + peak_dist)] - y) / (x_close[: -(x + peak_dist)] - x)
            a = f2(slope)
            coef = y - a * x
            b = a * x_close + coef
        return x, b, (a, coef)

    def _unique(self, xs):
        bands = []
        idx = []
        for el in xs:
            s, ms = el.get('score'), el.get('mse')
            if (s, ms) not in idx:
                bands.append(el)
                idx.append((s, ms))
        return bands

    def wedge(self, close, x_dates):
        assert close.size == x_dates.size, "x, y sizes differ"
        # Scale to [0,1]
        m, M = np.min(close), np.max(close)
        close = (close - m) / (M - m)

        # simple bands
        start, up, params = self._simple_band(x_dates, close, 'up')
        s, smse = self._score_up(close, up, start)
        ups = [{'score': s, 'mse': smse, 'band': up, 'params': params}]

        start, down, prams = self._simple_band(x_dates, close, 'down')
        s, smse = self._score_down(close, down, start)
        downs = [{'score': s, 'mse': smse, 'band': down, 'params': params}]

        # Wedge magic
        for t in np.arange(0.0, 0.2, 0.03):
            for d in np.arange(5, 70, 10):
                peaks = detect_peaks(close, mph=t, mpd=d)
                x_max = [x_dates[i] for i in peaks]
                y_max = [close[i] for i in peaks]
                ups += self._make_bands(x_dates, close, x_max, y_max, peaks[0], "up")

                peaks = detect_peaks(1 - close, mph=t, mpd=d)
                x_min = [x_dates[i] for i in peaks]
                y_min = [close[i] for i in peaks]
                downs += self._make_bands(x_dates, close, x_min, y_min, peaks[0], "down")

        ups = self._unique(ups)
        downs = self._unique(downs)

        # sort by score
        ups.sort(key=lambda x: x['score'])
        downs.sort(key=lambda x: x['score'])

        ups = ups[-3:]
        downs = downs[-3:]

        # sort by mse
        ups.sort(key=lambda x: x['mse'], reverse=True)
        downs.sort(key=lambda x: x['mse'], reverse=True)

        up = ups[-1]
        down = downs[-1]

        # Rescale back
        d = M - m
        band_up = d * up['band'] + m
        band_down = d * down['band'] + m

        # Params
        upper_a, upper_b = up['params']
        lower_a, lower_b = down['params']

        upper_a = d * upper_a
        upper_b = d * upper_b + m
        lower_a = d * lower_a
        lower_b = d * lower_b + m

        params = {'upper_a': upper_a, 'lower_a': lower_a, 'upper_b': upper_b, 'lower_b': lower_b}
        return band_up, band_down, params

    def _tokens(self, upper_band, lower_band, close):
            info = []
            # Shape Tokens
            width = upper_band - lower_band
            if width[-1]/width[0] > 0.90:
                info.append('SHAPE_PARALLEL')
            elif width[-1]/width[0] < 0.5:
                info.append('SHAPE_TRIANGLE')
            else:
                info.append('SHAPE_CONTRACTING')

            # Break Tokens
            if close[-1] > upper_band[-1]:
                info.append('PRICE_BREAK_UP')
            elif close[-1] < lower_band[-1]:
                info.append('PRICE_BREAK_DOWN')

            # Price Tokens
            if 1 >= (close[-1]-lower_band[-1])/width[-1] >= 0.95:
                info.append('PRICE_ONBAND_UP')
            elif 0 <= (close[-1]-lower_band[-1])/width[-1] <= 0.05:
                info.append('PRICE_ONBAND_DOWN')
            else:
                info.append('PRICE_BETWEEN')

            n_last_points = 10
            if np.sum(close[-n_last_points:] > upper_band[-n_last_points:]) > 0 and close[-1] < upper_band[-1]:
                info.append('BOUNCE_UPPER')
            elif np.sum(close[-n_last_points:] < lower_band[-n_last_points:]) > 0 and close[-1] > lower_band[-1]:
                info.append('BOUNCE_LOWER')

            # Direction Tokens
            wedge_dir = ((lower_band[-1] + .5*width[-1]) - (lower_band[0] + .5*width[0])) / lower_band.size
            if wedge_dir > 0.35:
                info.append('DIRECTION_UP')
            elif wedge_dir < -0.35:
                info.append('DIRECTION_DOWN')
            else:
                info.append('DIRECTION_HORIZONTAL')

            return info


# Long channels
def remakeWedge(influx, pair, timeframe, limit=200):
    margin = Config.MARGIN

    # Get data
    data = get_candles(influx, pair, timeframe, limit)
    close = data['close']
    x_dates = generate_dates(data['date'], timeframe, margin)

    wg = Wedge(pair, timeframe, close, x_dates)
    wg.make()
    return wg._last_wedge()


def makeLongWedge(influx, pair: str, timeframe: str, x_dates: list, limit: int=200):
    x_dates = np.array(x_dates) / 10000  # to increase precision
    params = remakeWedge(influx, pair, timeframe, limit)

    upper_band = np.array([])
    lower_band = np.array([])

    if params.get('upper_a', None) and params.get('lower_a', None):  # If wedge exists
        upper_band = params['upper_a'] * x_dates + params['upper_b']
        lower_band = params['lower_a'] * x_dates + params['lower_b']

        s = np.sum([u > l for u, l in zip(upper_band, lower_band)])
        upper_band, lower_band = upper_band[:s], lower_band[:s]

    return {'upper_band': upper_band.tolist(), 'lower_band': lower_band.tolist(),
            'middle_band': [], 'info': []}