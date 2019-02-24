# -*- coding: utf-8 -*-
import time
import traceback
import requests
import logging
from datetime import datetime as dt

from app.exchanges.helpers import check_last_tmstmp, insert_candles

class Bitfinex:
    def __init__(self, influx_client):
        self.influx = influx_client
        self.name='Bitfinex'

    def downsample_2h(self, pair):
            time_now = dt.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            try:
                query = f"""
                        SELECT 
                        first(open) AS open, 
                        max(high) AS high, 
                        min(low) AS low, 
                        last(close) AS close, 
                        sum(volume) AS volume 
                        INTO {pair}2h FROM {pair}1h WHERE time <= '{time_now}' GROUP BY time(2h), *
                
                """
                self.influx.query(query)
            except:
                logging.error(f'FAILED 2h downsample {pair} error: \n {traceback.format_exc()}')
                pass

    def fetch_candles(self, pair, timeframe):
        measurement = pair + timeframe

        timeframeR = timeframe
        if timeframe == '24h':
            timeframeR = '1D'
        elif timeframe == '168h':
            timeframeR = '7D'

        start = (check_last_tmstmp(self.influx, measurement)) * 1000 # ms
        end = (int(time.time()) + 100) * 1000 # ms

        url = f'https://api.bitfinex.com/v2/candles/trade:{timeframeR}:t{pair}/hist?start={start}&end={end}&limit=5000'
        request = requests.get(url)
        response = request.json()

        # Check if response was successful
        if not isinstance(response, list):
            logging.error('Bitfinex response is not a list.')
            return False
        if len(response)>0 and response[0]=='error':
            logging.error(f'Bitfinex response failed: {response}')
            return False
        if len(response)==0:
            logging.error(f'Bitfinex empty response.')
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
            self.downsample_2h(pair)

        return result

    def fill(self, pair):
        for tf in ['1h', '3h', '6h', '12h', '24h']:
            status = self.fetch_candles(pair, tf)
            if not status:
                return False
        return status
