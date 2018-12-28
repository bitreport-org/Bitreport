import numpy as np
import talib #pylint: skip-file
import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.services.dbservice import Chart

Config = config.BaseConfig()
engine = create_engine(Config.POSTGRES_URI)
Session = sessionmaker(bind=engine)
session = Session()


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
        last = session.query(Chart).filter_by(type=self.type,
                                              timeframe=self.timeframe,
                                              pair=self.pair).order_by(Chart.id.desc()).first()
        params = None
        if last is not None:
            params = last.params
        
        return params

    def _save_wedge(self, params):
        ch = Chart(pair=self.pair, timeframe=self.timeframe,
                    type=self.type, params=params)
        session.add(ch)
        session.commit()

    def _compare(self, params):
        margin = self.margin

        candles2check = 20
        upper_band = params['upper_a'] * self.x_dates[:-margin] + params['upper_b']
        lower_band = params['lower_a'] * self.x_dates[:-margin] + params['lower_b']

        # Check price position
        price = self.close[-candles2check:]
        above = price > upper_band[-candles2check:]
        below = price < lower_band[-candles2check:]

        threshold = 0.8
        if np.sum(above)/candles2check > threshold or np.sum(below)/candles2check > threshold:
            return True
        else:
            return False

    def _plot(self, params):
        # Creates wedge till it crosses
        upper_band = params['upper_a'] * self.x_dates + params['upper_b']
        lower_band = params['lower_a'] * self.x_dates + params['lower_b']

        s = np.sum([u > l for u, l in zip(upper_band, lower_band)])
        return upper_band[:s], lower_band[:s]

    def make(self):
        short_close = self.close[self.start:]

        new_params = self._wedge(short_close, self.x_dates)
        params = self._last_wedge()
        
        # Compare channels
        if params:
            # Check if price is out of the channel
            if self._compare(params):
                params = new_params
                self._save_wedge(params)
        else:
            params = new_params
            self._save_wedge(params)

        # Prepare channel
        if params['upper_a']: # If wedge exists
            upper_band, lower_band = self._plot(params)
            info = self._tokens(upper_band, lower_band, short_close)
        else:
            upper_band = np.array([])
            lower_band = np.array([])
            info = []

        return {'upper_band': upper_band.tolist(),
                'middle_band': [],
                'lower_band': lower_band.tolist(),
                'info': info}

    def _wedge(self, close, x_dates):
        margin = self.margin
        close_size = close.size
        end = close_size - 5
        threshold = 10
        upper_a, lower_a, upper_b, lower_b = None, None, None, None

        types = {
                'falling': (
                    talib.MAXINDEX,
                    np.max,
                    talib.MININDEX,
                    np.min),
                'rising': (
                    talib.MININDEX,
                    np.min,
                    talib.MAXINDEX,
                    np.max)
                }

        for t, funcs in types.items():
            f0, f1, f2, f3 = funcs
            point1 = f0(close, timeperiod=close_size)[-1]

            if point1 < close_size - 30:
                # Band 1
                a_values = np.divide(close[point1 + threshold : end+1] - close[point1], x_dates[point1 + threshold: end+1] - x_dates[point1])
                a1 = f1(a_values)
                b1 = close[point1] - a1 * x_dates[point1]

                # End point
                point2, = np.where(a_values == a1)[0]
                point2 = (point1 + threshold) + point2

                # Mid point
                point3 = point1 + f2(close[point1:point2], timeperiod=close[point1: point2].size)[-1]

                # Band 2
                a_values = np.divide(close[point3+5:end+1] - close[point3], x_dates[point3+5: end+1] - x_dates[point3])
                a2 = f3(a_values)
                b2 = close[point3] - a2 * x_dates[point3]

                # Create upper and lower band
                if t == 'falling':
                    upper_a, lower_a, upper_b, lower_b = a1, a2, b1, b2
                else:
                    upper_a, lower_a, upper_b, lower_b = a2, a1, b2, b1

                s, e = x_dates[0], x_dates[-1-margin]
                if (upper_a - lower_a) * (s - e) >= 0:
                    break
            else:
                upper_a, lower_a, upper_b, lower_b = None, None, None, None

        return {'upper_a': upper_a, 'lower_a': lower_a, 'upper_b': upper_b, 'lower_b': lower_b}

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

