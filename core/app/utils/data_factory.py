import numpy as np
import traceback
import logging
import config
from typing import List, Tuple
from influxdb import InfluxDBClient

from scipy.stats import linregress
from app.utils import get_candles, generate_dates, get_function_list
import app.ta as ta


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
            return message, 204

        # Price data and information
        price = {k: self.data[k].tolist()[-self.limit:] for k in ['open', 'high', 'close', 'low']}
        price.update(info=self._make_price_info(price['close']))

        # Volume data and information
        volume = dict(volume=self.data['volume'].tolist()[-self.limit:],
                      info=self._make_volume_info(self.data['volume']))

        # Prepare dates
        dates = generate_dates(self.data['date'], self.timeframe, self.margin)
        self.dates = dates[-(self.limit + self.margin):]

        # TODO : handling ??
        # Handle not enough data
        # if self.data['close'].size < self.limit + self.magic_limit:
        #     indicators_dict = dict()
        # else:
        #     # Prepare indicators

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
        indicators_list = get_function_list(ta.indicators)
        for indicator in indicators_list:
            try:
                indicators_values[indicator.__name__] = indicator(self.data)
            except (ValueError, AssertionError):
                logging.error(f'Indicator {indicator}, error: /n {traceback.format_exc()}')

        close: np.ndarray = self.data.get('close')
        dates = np.array(self.dates)

        # Channels
        try:
            ch = ta.Channel(self.pair, self.timeframe, close, dates)
            indicators_values['channel'] = ch.make()
        except (ValueError, AssertionError):
            indicators_values['channel'] = {'info': [], 'upper_band': [], 'lower_band': []}
            logging.error(f'Indicator channel, error: /n {traceback.format_exc()}')
        
        # Wedges
        try:
            wg = ta.Charting(self.pair, self.timeframe, close[-self.limit:], dates[:-self.margin])
            indicators_values['wedge'] = wg()
        except (ValueError, AssertionError):
            indicators_values['wedge'] = {'info': [], 'upper_band': [], 'lower_band': []}
            logging.error(f'Indicator wedge, error: /n {traceback.format_exc()}')

        # Patterns
        try:
            dt = ta.make_double(x_dates=dates[: -self.margin],
                                close=close[self.magic_limit:],
                                type_='top')
            indicators_values['double_top'] = dt
        except (ValueError, AssertionError):
            indicators_values['double_top'] = {'info': [], 'A': (), 'B': (), 'C': ()}
            logging.error(f'Indicator double top, error: /n {traceback.format_exc()}')

        try:
            db = ta.make_double(x_dates=dates[: -self.margin],
                                close=close[self.magic_limit:],
                                type_='bottom')
            indicators_values['double_bottom'] = db
        except (ValueError, AssertionError):
            indicators_values['double_bottom'] = {'info': [], 'A': (), 'B': (), 'C': ()}
            logging.error(f'Indicator double bottom, error: /n {traceback.format_exc()}')

        # Levels
        try:
            lvl = ta.Levels(self.pair, self.timeframe, close[-self.limit::], dates[:-self.margin])
            indicators_values['levels'] = lvl()
        except (ValueError, AssertionError):
            indicators_values['levels'] = {'info': [], 'levels': []}
            logging.error(traceback.format_exc())

        return indicators_values
