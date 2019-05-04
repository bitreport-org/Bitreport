# -*- coding: utf-8 -*-
import time
import requests
import logging

from app.exchanges.helpers import check_last_tmstmp, insert_candles, downsample


class Bitfinex:
    def __init__(self, influx_client):
        self.influx = influx_client
        self.name = 'Bitfinex'

    def _downsample_2h(self, pair):
        downsample(self.influx, from_tf='1h', to_tf='2h', pair=pair)

    def fetch_candles(self, pair, timeframe):
        measurement = pair + timeframe

        timeframeR = timeframe
        if timeframe == '24h':
            timeframeR = '1D'

        start = (check_last_tmstmp(self.influx, measurement)) * 1000   # ms
        end = (int(time.time()) + 100) * 1000  # ms

        url = f'https://api.bitfinex.com/v2/candles/trade:{timeframeR}:t{pair}/hist'
        params = {
            'start': start,
            'end': end,
            'limit': 5000
        }
        request = requests.get(url, params=params)
        response = request.json()

        # Check if response was successful
        if request.status_code != 200:
            logging.info(f'No success {response}')
            return False

        if not isinstance(response, list):
            logging.info('Bitfinex response is not a list.')
            return False

        if (response and response[0] == 'error') or (not response):
            logging.info(f'Bitfinex response failed: {response}')
            return False

        # Make candles
        points = []
        for row in response:
            json_body = {
                "measurement": measurement,
                "tags": {'exchange' : self.name.lower()},
                "time": int(row[0]),
                "fields": {
                    "open": float(row[1]),
                    "close": float(row[2]),
                    "high": float(row[3]),
                    "low": float(row[4]),
                    "volume": float(row[5]),
                }
            }
            points.append(json_body)

        result = insert_candles(self.influx, points, measurement, self.name, time_precision="ms")

        if timeframe == '1h':
            self._downsample_2h(pair)

        return result

    def fill(self, pair):
        for tf in ['1h', '3h', '6h', '12h', '24h']:
            status = self.fetch_candles(pair, tf)
            if not status:
                return False
        return status
