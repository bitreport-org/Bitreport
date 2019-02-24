import numpy as np
import traceback
import logging
import config

from scipy.stats import linregress
from app.services import get_candles, generate_dates, get_function_list
from app.ta import indicators, levels, channels, wedge


# Data class
class PairData:
    def __init__(self, influx, pair: str, timeframe: str, limit: int):
        self.influx = influx
        # to return data without NaN values indicators are calculated on period of length: limit + magic_limit
        # returned data has length = limit
        self.magic_limit = config.BaseConfig.MAGIC_LIMIT
        self.margin = config.BaseConfig.MARGIN

        self.pair = pair
        self.timeframe = timeframe
        self.limit = max(limit, 20)

        self.dates = []
        self.output = dict()

    def prepare(self):
        # Data request
        self.data = get_candles(self.influx, self.pair, self.timeframe, self.limit + self.magic_limit)

        if not self.data:
            message = f'Empty database response {self.pair+self.timeframe}'
            logging.error(message)
            return message, 500

        # Price data and information
        price = dict(open=self.data['open'].tolist()[self.magic_limit:],
                     high=self.data['high'].tolist()[self.magic_limit:],
                     close=self.data['close'].tolist()[self.magic_limit:],
                     low=self.data['low'].tolist()[self.magic_limit:])

        info_price = self._make_price_info()
        price.update(info=info_price)

        # Volume data and information
        info_volume = self._make_volume_info(self.data['volume'])
        volume = dict(volume=self.data['volume'].tolist()[self.magic_limit:], info=info_volume)

        # Prepare dates
        dates = generate_dates(self.data['date'], self.timeframe, self.margin)
        self.dates = dates[self.magic_limit:]

        # Prepare indicators
        indicators_dict = self._make_indicators()
        indicators_dict.update(price=price)
        indicators_dict.update(volume=volume)

        response = dict(dates=self.dates, indicators=indicators_dict)
        return response, 200


    def _make_price_info(self):
        info_price = []
        close = self.data.get('close')[self.magic_limit:]

        # TODO: remove this useless token

        # Last moves tokens
        n = int(0.70*close.size) 
        s70 = linregress(np.arange(n), close[-n:]).slope
        s20 = linregress(np.arange(20), close[-20:]).slope
        s5 = linregress(np.arange(5), close[-5:]).slope
        if s5 > s20 > s70 > 0:
            info_price.append('MOVE_STRONG_UP')
        elif s5 < s20 < s70 < 0:
            info_price.append('MOVE_STRONG_DOWN')
        elif s70 < 0 and s20 < 0 and s5 > 0:
            info_price.append('MOVE_SMALL_UP')
        elif s70 > 0 and s20 > 0 and s5 < 0:
            info_price.append('MOVE_SMALL_DOWN')
        elif s70 < 0 and s20 > 0 and s5 > 0:
            info_price.append('MOVE_BIG_UP')
        elif s70 > 0 and s20 < 0 and s5 < 0:
            info_price.append('MOVE_BIG_DOWN')

        return info_price

    def _make_volume_info(self, volume: np.array):
        info_volume = []
        check_period = int(0.35 * self.limit)

        # Volume tokens
        threshold = np.percentile(volume, 80)
        if volume[-2] > threshold or volume[-1] > threshold:
            info_volume.append('VOLUME_SPIKE')
        
        slope = linregress(np.arange(volume[check_period:].size), volume[check_period:]).slope
        if slope < -0.05:
            info_volume.append('VOLUME_DIRECTION_DOWN')
        elif slope > 0.05:
            info_volume.append('VOLUME_DIRECTION_UP')

        return info_volume

    def _make_indicators(self):
        indicators_values = dict()

        # Indicators
        indicators_list = get_function_list(indicators)
        for indicator in indicators_list:
            try:
                indicators_values[indicator.__name__] = indicator(self.data)
            except:
                logging.error(f'Indicator {indicator}, error: /n {traceback.format_exc()}')
                pass

        # Channels
        close = self.data.get('close', np.array([]))
        dates = self.dates
        try:
            ch = channels.Channel(self.pair, self.timeframe, close, dates)
            indicators_values['channel'] = ch.make()
        except:
            logging.error(f'Indicator channel, error: /n {traceback.format_exc()}')
            pass
        try:
            indicators_values['channel12'] = channels.makeLongChannel(self.influx, self.pair, '12h', dates)
        except:
            logging.error(f'Indicator channel12, error: /n {traceback.format_exc()}')
            pass
        
        # Wedges
        try:
            wg = wedge.Wedge(self.pair, self.timeframe, close, dates)
            indicators_values['wedge'] = wg.make()
        except:
            logging.error(f'Indicator wedge, error: /n {traceback.format_exc()}')
            pass

        try:
            indicators_values['wedge12'] = wedge.makeLongWedge(self.influx, self.pair, '12h', dates)
        except:
            logging.error(f'Indicator wedge12, error: /n {traceback.format_exc()}')
            pass

        # Levels
        try:
            lvl = levels.Levels(self.pair, self.timeframe, close, dates)
            indicators_values['levels'] = lvl.make()
        except:
            logging.error(traceback.format_exc())
            indicators_values.update(levels={'support': [], 'resistance': [], 'auto': [], 'info': []})
            pass

        return indicators_values
