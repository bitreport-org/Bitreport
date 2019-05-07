import numpy as np
import traceback
import logging
import config
from typing import List, Tuple
from influxdb import InfluxDBClient

from scipy.stats import linregress
from app.services import get_candles, generate_dates, get_function_list
from app.ta import indicators, levels, channels, wedge, patterns


class PairData:
    def __init__(self, influx: InfluxDBClient, pair: str, timeframe: str, limit: int):
        """
        To return data without NaN values indicators are calculated on period of
        length: limit + magic_limit, however data returned by prepare() has length = limit

        Parameters
        ----------
        influx: influx client
        pair: pair name ex. 'BTCUSD'
        timeframe: timeframe ex. '1h'
        limit: number of candles to retrieve
        """
        self.influx = influx
        self.magic_limit = config.BaseConfig.MAGIC_LIMIT
        self.margin = config.BaseConfig.MARGIN

        self.pair = pair
        self.timeframe = timeframe
        self.limit = max(limit, 20)

        self.dates = []
        self.data = dict()
        self.output = dict()

    def prepare(self) -> Tuple[dict, int]:
        """
        Selects price data from influx database, adds technical indicators and some other magic

        Returns
        -------
        (response, code)
        """
        # Data request
        self.data = get_candles(self.influx, self.pair, self.timeframe, self.limit + self.magic_limit)

        # Handle empty measurement
        if not self.data.get('date'):
            message = dict(msg=f'No data for {self.pair+self.timeframe}')
            logging.error(message)
            return message, 404

        # Price data and information
        price = {k: self.data[k].tolist()[-self.limit:] for k in ['open', 'high', 'close', 'low']}
        price.update(info=self._make_price_info(price['close']))

        # Volume data and information
        volume = dict(volume=self.data['volume'].tolist()[-self.limit:],
                      info=self._make_volume_info(self.data['volume']))

        # Prepare dates
        dates = generate_dates(self.data['date'], self.timeframe, self.margin)
        self.dates = dates[-(self.limit + self.margin):]

        # Handle not enough data
        if self.data['close'].size < self.limit + self.magic_limit:
            indicators_dict = dict()
        else:
            # Prepare indicators
            indicators_dict = self._make_indicators()

        indicators_dict.update(price=price)
        indicators_dict.update(volume=volume)

        response = dict(dates=self.dates, indicators=indicators_dict)
        return response, 200

    @staticmethod
    def _make_price_info(close: np.ndarray) -> List[str]:
        info_price = []
        if isinstance(close, list):
            close = np.array(close)

        # Last moves tokens
        n = int(0.70 * close.size)
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

    def _make_volume_info(self, volume: np.array) -> List[str]:
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

    def _make_indicators(self) -> dict:
        indicators_values = dict()

        # Indicators
        indicators_list = get_function_list(indicators)
        for indicator in indicators_list:
            try:
                indicators_values[indicator.__name__] = indicator(self.data)
            except ValueError:
                logging.error(f'Indicator {indicator}, error: /n {traceback.format_exc()}')

        close: np.ndarray = self.data.get('close')
        dates = np.array(self.dates)

        # Channels
        try:
            ch = channels.Channel(self.pair, self.timeframe, close, dates)
            indicators_values['channel'] = ch.make()
        except ValueError:
            logging.error(f'Indicator channel, error: /n {traceback.format_exc()}')
        try:
            indicators_values['channel12'] = channels.make_long_channel(self.influx, self.pair, '12h', dates)
        except ValueError:
            logging.error(f'Indicator channel12, error: /n {traceback.format_exc()}')
        
        # Wedges
        try:
            wg = wedge.Wedge(self.pair, self.timeframe, close[self.magic_limit:], dates)
            indicators_values['wedge'] = wg.make()
        except ValueError:
            logging.error(f'Indicator wedge, error: /n {traceback.format_exc()}')

        try:
            indicators_values['wedge12'] = wedge.make_long_wedge(self.influx, self.pair, '12h', dates)
        except ValueError:
            logging.error(f'Indicator wedge12, error: /n {traceback.format_exc()}')

        # Patterns
        try:
            dt = patterns.make_double(x_dates=dates[: -self.margin],
                                      close=close[self.magic_limit:],
                                      type_='top')
            indicators_values['double_top'] = dt
        except ValueError:
            logging.error(f'Indicator double top, error: /n {traceback.format_exc()}')

        try:
            db = patterns.make_double(x_dates=dates[: -self.margin],
                                      close=close[self.magic_limit:],
                                      type_='bottom')
            indicators_values['double_bottom'] = db
        except ValueError:
            logging.error(f'Indicator double bottom, error: /n {traceback.format_exc()}')

        # Levels
        try:
            lvl = levels.Levels(self.pair, self.timeframe, close[self.magic_limit:])
            indicators_values['levels'] = lvl()
        except ValueError:
            logging.error(traceback.format_exc())

        return indicators_values
