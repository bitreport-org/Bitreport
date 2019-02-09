# -*- coding: utf-8 -*-
import pandas as pd
import config
import types

conf = config.BaseConfig()


def get_candles(influx, pair, timeframe, limit, untill=None):
    mesurement = pair + timeframe
    if untill and isinstance(untill, int):
        q = f'SELECT * FROM {mesurement} WHERE time <= {untill} ORDER BY time ASC LIMIT {limit};'
    else:
        q = f'SELECT * FROM {mesurement} ORDER BY time ASC LIMIT {limit};'

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
    return [module.__dict__.get(a) for a in dir(module) if isinstance(module.__dict__.get(a), types.FunctionType)]
