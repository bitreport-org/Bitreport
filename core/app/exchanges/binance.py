# -*- coding: utf-8 -*-
import requests
import logging
from app.exchanges.helpers import insert_candles, downsample


class Binance:
    def __init__(self, influx_client):
        self.influx = influx_client
        self.name = 'Binance'

    @staticmethod
    def _pair_format(pair):
        end_pair = pair[-3:]
        start_pair = pair[:-3]
        if end_pair == 'USD':
            end_pair = end_pair + 'T'
        return start_pair + end_pair

    def _downsample_3h(self, pair):
        downsample(self.influx, from_tf='1h', to_tf='3h', pair=pair)


    def fetch_candles(self, pair, timeframe):
        measurement = pair + timeframe
        pair_formated = self._pair_format(pair)

        # Map timeframes for Binance
        timeframeR = timeframe
        if timeframe == '24h':
            timeframeR = '1d'
        elif timeframe == '168h':
            timeframeR = '1w'

        # max last 500 candles
        url = f'https://api.binance.com/api/v1/klines'
        params = {
            'symbol': pair_formated,
            'interval': timeframeR,
            'limit': 500
        }
        request = requests.get(url, params=params)
        response = request.json()

        if not isinstance(response, list) or request.status_code != 200:
            logging.info(f"FAILED {measurement} Binance response: {response.get('msg', 'no error')}")
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
                    "close": float(row[4]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "volume": float(row[5]),
                }
            }
            points.append(json_body)

        result = insert_candles(self.influx, points, measurement, self.name, time_precision='ms')

        if timeframe == '1h':
            self._downsample_3h(pair)

        return result

    def fill(self, pair):
        for tf in  ['1h', '2h', '6h', '12h', '24h']:
            status = self.fetch_candles(pair, tf)
            if not status:
                return False
        return status
