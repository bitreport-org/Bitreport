# -*- coding: utf-8 -*-
import pandas as pd
import config
import types

conf = config.BaseConfig()

def get_candles(influx, pair, timeframe, limit):
    mesurement = pair + timeframe

    q = f"""
    SELECT
    mean(close) AS close, 
    mean(high) AS high, 
    mean(low) AS low, 
    mean(open) AS open, 
    mean(volume) AS volume
    FROM {mesurement}
    WHERE time > now() - {(limit-1) * int(timeframe[:-1])}h
    AND ("exchange" = 'binance'
    OR "exchange" = 'bitfinex'
    OR "exchange" = 'poloniex'
    OR "exchange" = 'bittrex') 
    GROUP BY  time({timeframe}) FILL(none)
    """

    r = influx.query(q, epoch='s')
    df = pd.DataFrame(list(r.get_points(measurement=mesurement)))
    if df.shape==(0,0):
        return False

    candles_dict = {'date': list(df.time),
                    'open': df.open.values,
                    'close': df.close.values,
                    'high': df.high.values,
                    'low': df.low.values,
                    'volume': df.volume.values
                    }

    return candles_dict


def generate_dates(date, timeframe, margin):
    # Generate timestamps for future
    map = { 'm': 60, 'h': 3600,'W': 648000}
    dt = map[timeframe[-1]]
    date = date + [int(date[-1]) + i*dt for i,x in enumerate(range(margin))]
    return date


def get_function_list(module):
    return [getattr(module, a) for a in module.__all__]
