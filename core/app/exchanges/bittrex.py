# -*- coding: utf-8 -*-
import time
import traceback
import requests
import logging
from datetime import datetime as dt
from app.exchanges.helpers import insert_candles


class Bittrex():
    def __init__(self, influx_client):
        self.influx = influx_client
        self.name = 'Bittrex'

    def pair_format(self, pair):
        end_pair = pair[-3:]
        start_pair = pair[:-3]
        if end_pair == 'USD':
            end_pair = end_pair + 'T'
        return end_pair + '-' + start_pair

    def downsample(self, pair, from_tf, to_tf):
        time_now = dt.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            query = f"""
                        SELECT 
                        first(open) AS open, 
                        max(high) AS high, 
                        min(low) AS low, 
                        last(close) AS close, 
                        sum(volume) AS volume 
                        INTO {pair+to_tf} FROM {pair+from_tf} WHERE time <= '{time_now}' GROUP BY time({to_tf})

                """
            self.influx.query(query)
        except:
            logging.error(f'FAILED {to_tf} downsample {pair} error: \n {traceback.format_exc()}')
            pass

    def get_candles(self, pair, timeframe):
        result = False
        mesurement = pair + timeframe
        pair_formated = self.pair_format(pair)

        # start = helper.check_last_tmstmp(self.influx, pair, timeframe)
        # end = int(time.time()) + 100

        timeframes = {'1h': 'hour', '24h': 'day'}
        btf = timeframes.get(timeframe, '1h')

        url = f'https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName={pair_formated}&tickInterval={btf}'
        request = requests.get(url)
        response = request.json()

        # Check if response was successful
        if response.get('success', False):
            rows = response.get('result', False)
            if rows:
                points = []
                for row in rows:
                    json_body = {
                        "measurement": mesurement,
                        "time": row['T'],
                        "fields": {
                            "open": float(row['O']),
                            "close": float(row['C']),
                            "high": float(row['H']),
                            "low": float(row['L']),
                            "volume": float(row['BV']),
                        }
                    }
                    points.append(json_body)
                result = insert_candles(self.influx, points, mesurement)
                if timeframe == '1h':
                    for tf in ['2h', '3h', '6h', '12h']:
                        self.downsample(pair, '1h', tf)

        else:
            logging.error(f"FAILED {mesurement} Bitrex response: {response.get('message','no message')}")


        return result

    def fill(self, pair):
        for tf in ['1h', '24h']:
            status = self.get_candles(pair, tf)
            logging.error(f'Failed to fill {pair}:{tf}')
            time.sleep(2)
        return status
