# -*- coding: utf-8 -*-
import numpy as np
import datetime
import pandas as pd
import config
import types

from influxdb import InfluxDBClient

conf = config.BaseConfig()

def import_numpy(pair, timeframe, limit):
    db = conf.DBNAME
    host = conf.HOST
    port = conf.PORT
    client = InfluxDBClient(host, port, 'root', 'root', db)

    # Perform query and return JSON data
    query = f'SELECT * FROM {pair+timeframe} ORDER BY time DESC LIMIT {limit};'
    params = 'db={}&q={}&epoch=s'.format(db, query)
    try:
        r = client.request('query', params=params).json()['results'][0]['series'][0]
        candle_list = r['values']
        candle_list.reverse()
        df = pd.DataFrame(candle_list, columns=r['columns'])
        candles_dict = {'date': list(df.time),
                        'open': np.array(df.open, dtype='float'),
                        'close': np.array(df.close, dtype='float'),
                        'high': np.array(df.high, dtype='float'),
                        'low': np.array(df.low, dtype='float'),
                        'volume': np.array(df.volume, dtype='float')
                        }
        if list(df.time) != []:
            return candles_dict
        else:
            return False
    except:
        return False


def import_numpy_untill(pair, timeframe, limit, untill):
    db = conf.DBNAME
    host = conf.HOST
    port = conf.PORT
    client = InfluxDBClient(host, port, 'root', 'root', db)
    # Perform query and return JSON data
    query = f"SELECT * FROM {pair+timeframe} WHERE time <= {untill*1000000000} ORDER BY time DESC LIMIT {limit}"
    params = 'db={}&q={}&epoch=s'.format(db, query)
    try:
        r = client.request('query', params=params).json()['results'][0]['series'][0]
        candle_list = r['values']
        candle_list.reverse()
        df = pd.DataFrame(candle_list, columns=r['columns'])

        candles_dict = {'date': list(df.time),
                        'open': np.array(df.open, dtype='float'),
                        'close': np.array(df.close, dtype='float'),
                        'high': np.array(df.high, dtype='float'),
                        'low': np.array(df.low, dtype='float'),
                        'volume': np.array(df.volume, dtype='float')
                        }
        if list(df.time) != []:
            return candles_dict
        else:
            return False
    except:
        return False


def make_retention_policies(client):
    timeframes = ['30m', '1h', '2h', '3h', '6h', '12h', '24h', '168h']

    for tf in timeframes:
        rp_name = 'RP{}'.format(tf)
        duration = str(300*int(tf[:-1])) + 'h'
        client.create_retention_policy(name=rp_name, duration=duration, replication='1')

    return client.get_list_retention_policies()


def generate_dates(date, timeframe, margin):
    # Generate timestamps for future
    period = timeframe[-1]
    t = int(timeframe[:-1])

    d = 0
    if period == 'm':
        d = 60 * t
    elif period == 'h':
        d = 60 * 60 * t
    elif period == 'W':
        d = 60 * 60 * 168 * t

    for _ in range(margin):
        date.append(int(date[-1]) + d)

    return date


def get_function_list(module):
    return [module.__dict__.get(a) for a in dir(module) if isinstance(module.__dict__.get(a), types.FunctionType)]
