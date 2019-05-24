import numpy as np
import logging
import config
from typing import List, Tuple
from influxdb import InfluxDBClient
from scipy.stats import linregress


import app.ta.charting as charting
import app.ta.patterns as patterns
from app.ta.levels import Levels
from app.ta.charting.base import Universe
from app.utils import get_candles, generate_dates
from app.ta.indicators import make_indicators


class PairData:
    def __init__(self, pair: str, timeframe: str, limit: int) -> None:
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
        self.data = get_candles(self.pair, self.timeframe, self.limit + self.magic_limit)

        # Handle empty measurement
        if not self.data.get('date'):
            message = dict(msg=f'No data for {self.pair+self.timeframe}')
            logging.error(message)
            return message, 204

        # Price data and information
        price = {k: self.data[k].tolist()[-self.limit:] for k in ['open', 'high', 'close', 'low']}
        price.update(info=self._price_info(price['close']))

        # Volume data and information
        volume = dict(volume=self.data['volume'].tolist()[-self.limit:],
                      info=self._volume_info(self.data['volume']))

        # Prepare dates
        dates = generate_dates(self.data['date'], self.timeframe, self.margin)
        self.dates = dates[-(self.limit + self.margin):]

        indicators_dict = self._make_indicators()

        indicators_dict.update(price=price)
        indicators_dict.update(volume=volume)

        response = dict(dates=self.dates, indicators=indicators_dict)
        return response, 200

    @staticmethod
    def _price_info(close: np.ndarray) -> List[str]:
        info_price = []
        return info_price

    def _volume_info(self, volume: np.array) -> List[str]:
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
        indicators_values.update(make_indicators(self.data, self.limit))

        # Setup universe for charting
        close: np.ndarray = self.data.get('close')
        dates = np.array(self.dates)

        universe = Universe(
            pair=self.pair,
            timeframe=self.timeframe,
            close=close[-self.limit:],
            time=dates[:-self.margin],
            future_time=dates[-self.margin:]
        )

        # Wedges
        wg = charting.Charting(universe)
        indicators_values.update(wg())

        # Patterns
        indicators_values.update(patterns.double_top(universe))
        indicators_values.update(patterns.double_bottom(universe))

        # Levels
        lvl = Levels(universe)
        indicators_values.update(lvl())

        return indicators_values
