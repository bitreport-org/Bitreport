# -*- coding: utf-8 -*-
import requests
import logging

from app.exchanges.helpers import insert_candles, check_last_tmstmp
from .base import BaseExchange


class Poloniex(BaseExchange):
    timeframes = ['30m', '2h', '24h']
    name = 'Poloniex'
    pool = 3

    @staticmethod
    def _pair_format(pair: str) -> str:
        end_pair = pair[-3:]
        start_pair = pair[:-3]
        if end_pair == 'USD':
            end_pair = end_pair + 'T'
        return end_pair + '_' + start_pair

    def json(self, measurement: str, row: dict) -> dict:
        json_body = {
            "measurement": measurement,
            "tags": {'exchange': self.name.lower()},
            "time": int(row['date']),
            "fields": {
                "open": float(row['open']),
                "close": float(row['close']),
                "high": float(row['high']),
                "low": float(row['low']),
                "volume": float(row['volume']),
            }
        }
        return json_body

    def fetch_candles(self, pair: str, timeframe: str) -> bool:
        measurement = pair + timeframe
        pair_formatted = self._pair_format(pair)

        start = check_last_tmstmp(measurement)

        # Here we map our possible timeframes 1h, 2h, 3h, 6h, 12h to
        # format acceptable by Poloniex API
        tf_map = {'30m': 1800, '2h': 7200, '24h': 86400}
        if timeframe not in tf_map.keys():
            if timeframe in ['1h', '3h']:
                timeframe = '30m'
            else:
                timeframe = '2h'

        measurement = pair + timeframe

        url = f'https://poloniex.com/public'

        params = {
            'command': 'returnChartData',
            'currencyPair': pair_formatted,
            'start': start - 30,
            'period': tf_map[timeframe]
        }

        request = requests.get(url, params=params)
        response = request.json()

        # Check if response was successful
        if request.status_code != 200 or not isinstance(response, list):
            logging.info(f"FAILED {measurement} Poloniex response: {response}")
            return False

        points = [self.json(measurement, row) for row in response]

        result = insert_candles(points, measurement, self.name, time_precision='s')

        return result

