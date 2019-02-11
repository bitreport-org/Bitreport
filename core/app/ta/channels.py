import numpy as np
import talib #pylint: skip-file
import config
from app.services import Chart, make_session, get_candles, generate_dates

Config = config.BaseConfig()
session = make_session()

class Channel():
    def __init__(self, pair, timeframe, close, x_dates):
        self.pair = pair
        self.timeframe = timeframe
        self.close = close
        self.x_dates = np.array(x_dates) / 10000 # to increase precision
        self.type = 'channel'
        self.margin = Config.MARGIN
        self.start = Config.MAGIC_LIMIT

    def _last_channel(self):
        last = session.query(Chart).filter_by(type = self.type, timeframe = self.timeframe,
                                                pair = self.pair).order_by(Chart.id.desc()).first()
        params = None
        if last is not None:
            params = last.params
        
        return params

    def _save_channel(self, params):
        ch = Chart( pair = self.pair, timeframe = self.timeframe, 
                    type = self.type, params = params)
        session.add(ch)
        session.commit()

    def _compare(self, params):

        candles2check = 20
        slope = params['slope']
        coef = params['coef']
        std = params['std']
        up_channel= slope * self.x_dates[-candles2check:] + coef + 2 * std
        bottom_channel = slope * self.x_dates[-candles2check:] + coef - 2 * std

        # Check price position
        price = self.close[-candles2check:]
        above = price > up_channel
        below = price < bottom_channel

        threshold = 0.8
        if np.sum(above)/candles2check > threshold or np.sum(below)/candles2check> threshold:
            return True
        else:
            return False

    def make(self):
        new_params = self._channel(self.close, self.x_dates)
        params = self._last_channel()

        # Compare channels
        if params: # if no previous history
            # Check if price is out of the channel
            if self._compare(params):
                params = new_params
                self._save_channel(params)
        else:
            params = new_params
            self._save_channel(params)

        # Prepare channel
        slope = params['slope']
        coef = params['coef']
        std = params['std']
        up_channel= slope * self.x_dates + coef + 2 * std
        bottom_channel = slope * self.x_dates + coef - 2 * std
        
        # TOKENS
        short_close = self.close[self.start:]
        info = self._tokens(short_close, up_channel, bottom_channel, slope)
        
        return {'upper_band': up_channel.tolist(), 'lower_band': bottom_channel.tolist(), 
                'middle_band':[], 'info': info}

    def _tokens(self, close, upper_band, lower_band, slope):
        margin = self.margin
        info = []
        p = ( close[-1] - lower_band[-1-margin] ) / (upper_band[-1-margin]-lower_band[-1-margin]) 

        # Price Tokens
        if p > 1:
            info.append('PRICE_BREAK_UP')
        elif p < 0:
            info.append('PRICE_BREAK_DOWN')
        elif p > 0.95:
            info.append('PRICE_ONBAND_UP')
        elif p < 0.05:
            info.append('PRICE_ONBAND_DOWN')
        else:
            info.append('PRICE_BETWEEN')

        n_last_points = 10
        if np.sum(close[-n_last_points:] > upper_band[-n_last_points-margin : -margin]) > 0 and close[-1] < upper_band[-1-margin]:
            info.append('FALSE_BREAK_UP')
        elif np.sum(close[-n_last_points:] < lower_band[-n_last_points-margin : -margin]) > 0 and close[-1] > lower_band[-1-margin]:
            info.append('FLASE_BREAK_DOWN')

        # Drirection Tokens
        if slope < -0.2:
            info.append('DIRECTION_DOWN')
        elif slope > 0.2:
            info.append('DIRECTION_UP')
        else:
            info.append('DIRECTION_HORIZONTAL')
        
        return info

    def _channel(self, close, x_dates, sma_type: int = 50):
        margin = self.margin
        start = self.start
        limit = close.size
        short_close = close[start:]

        sma = talib.SMA(close, timeperiod = sma_type)
        sma = (short_close - sma[start:]) / sma[start:]
        sma = np.where(sma >=0, 1., -1.)
        filter_value =5
        f1 = np.where(talib.SMA(sma, timeperiod = filter_value)[filter_value:] >= 0.0, 1., -1.)
        f2 = np.where(talib.SMA(f1, timeperiod = 2) == 0.0 , 1., 0.)
        points, = np.where(f2>0)
        ch_points = np.array([0] + (points+filter_value).tolist())

        
        # If price was below / above the SMA then ch_points could contain only 1 point
        if len(ch_points) < 2:
            if ch_points == []:
                s, e = 0, limit
            elif ch_points[0] < limit/2.0:
                s, e = ch_points[0], limit
            else:
                s, e = 0, ch_points[0]
        else:
            # Find longest channel
            lenghts = ch_points[1:] - ch_points[:-1]
            s_position = np.where(lenghts == np.max(lenghts))[0][0]
            s, e = ch_points[s_position], ch_points[s_position+1]
        
        # Calculate channel and slope
        x = x_dates[:-margin][s: e]
        y = short_close[s: e]

        lm = np.poly1d(np.polyfit(x,y, 1))
        std = np.std(short_close[s:e])     

        return {'slope': lm[1], 'coef': lm[0], 'std': std, 'last_tsmp': x_dates[-margin]}


# Long channels
def remakeChannel(influx, pair, timeframe, limit=200):
    start = Config.MAGIC_LIMIT
    margin = Config.MARGIN

    # Get data
    data = get_candles(influx, pair, timeframe, limit)
    close = data['close'][start:]
    x_dates = generate_dates(data['date'], timeframe, margin)

    ch = Channel(pair, timeframe, close, x_dates)
    ch.make()
    params = ch._last_channel()

    return params


def makeLongChannel(influx, pair: str, timeframe:str, x_dates:list, limit:int=200):
    x_dates = np.array(x_dates) / 10000  # to increase precision
    params = remakeChannel(influx, pair, timeframe, limit)

    slope = params['slope']
    coef = params['coef']
    std = params['std']

    band = slope * x_dates + coef
    upper_band = band + std
    lower_band = band - std

    return {'upper_band': upper_band.tolist(), 'lower_band': lower_band.tolist(),
            'middle_band': [], 'info': []}