# -*- coding: utf-8 -*-
import requests
import logging
from multiprocessing.dummy import Pool as ThreadPool

from app.exchanges.helpers import insert_candles


class Bittrex:
    timeframes = ['1h', '24h']

    def __init__(self, influx_client):
        self.influx = influx_client
        self.name = 'Bittrex'

    @staticmethod
    def _pair_format(pair: str) -> str:
        end_pair = pair[-3:]
        start_pair = pair[:-3]
        if end_pair == 'USD':
            end_pair = end_pair + 'T'
        return end_pair + '-' + start_pair

    def json(self, measurement: str, row: dict) -> dict:
        json_body = {
            "measurement": measurement,
            "tags": {'exchange': self.name.lower()},
            "time": row['T'],
            "fields": {
                "open": float(row['O']),
                "close": float(row['C']),
                "high": float(row['H']),
                "low": float(row['L']),
                "volume": float(row['BV']),
            }
        }
        return json_body

    def fetch_candles(self, pair, timeframe: str, session=None) -> bool:
        result = False
        measurement = pair + timeframe
        pair_formated = self._pair_format(pair)

        timeframes = {'1h': 'hour', '24h': 'day'}
        btf = timeframes.get(timeframe, '1h')

        url = f'https://bittrex.com/Api/v2.0/pub/market/GetTicks'
        params = {
            'marketName': pair_formated,
            'tickInterval': btf
        }

        request = requests.get(url, params=params)
        response = request.json()

        # Check if response was successful
        if 'success' not in response.keys() or request.status_code != 200:
            logging.info(f"FAILED {measurement} Bitrex response: {response.get('message','no message')}")
            return False

        rows = response.get('result', False)

        if not rows:
            logging.info(f"FAILED {measurement} Bitrex empty response")
            return False

        points = [self.json(measurement, row) for row in rows]

        result = insert_candles(self.influx, points, measurement, self.name, time_precision="s")

        return result

    def fill(self, pair: str) -> bool:
        pool = ThreadPool(2)
        results = pool.map(lambda tf: self.fetch_candles(pair, tf), self.timeframes)
        pool.close()
        pool.join()

        status = all(results)
        return status
