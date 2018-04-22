# -*- coding: utf-8 -*-
import numpy as np
from influxdb import InfluxDBClient
import datetime
import pandas as pd
import config


def import_numpy(pair, timeframe, limit):
    conf = config.BaseConfig()
    db = conf.DBNAME
    host = conf.HOST
    port = conf.PORT
    client = InfluxDBClient(host, port, 'root', 'root', db)

    # Perform query and return JSON data
    query = 'SELECT * FROM {} ORDER BY time DESC LIMIT {};'.format(pair+timeframe, limit)
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
        return candles_dict
    except:
        return False


def import_numpy_untill(pair, timeframe, limit, untill):
    conf = config.BaseConfig()
    db = conf.DBNAME
    host = conf.HOST
    port = conf.PORT
    client = InfluxDBClient(host, port, 'root', 'root', db)
    # Perform query and return JSON data
    query = 'SELECT * FROM {} WHERE time<={} ORDER BY time DESC LIMIT {};'.format(pair+timeframe, 1000000000*untill, limit)
    params = 'db={}&q={}&epoch=s'.format(db, query)
    r = client.request('query', params=params).json()['results'][0]['series'][0]
    try:
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

        return candles_dict
    except:
        return False


def generate_dates(data, timeframe, margin):
    # Generate timestamps for future
    date = data['date']
    period = timeframe[-1]
    t = int(timeframe[:-1])

    d = 0
    if period == 'm':
        d = 60 * t
    elif period == 'h':
        d = 60 * 60 * t
    elif period == 'W':
        d = 60 * 60 * 168 * t

    for i in range(0, margin):
        date.append(int(date[-1]) + d)

    return date


def get_function_list(module):
    l = dir(module)
    buildin = ['__builtins__', '__cached__', '__doc__', 
    '__file__', '__loader__', '__name__', '__package__', '__spec__', 'talib', 'np', 
    'internal', 'position', 'start', 'phase', 'what_phase', 'dec', 'datetime', 'config', 'math']

    for x in buildin:
        try:
            l.pop(l.index(x))
        except:
            pass
    return l


def show_pairs():
    conf = config.BaseConfig()
    file = conf.EXCHANGES
    df = pd.DataFrame(np.load(file), columns=['pair', 'exchange'])
    return list(df.pair)


def add_pair(pair, exchange):
    conf = config.BaseConfig()
    file = conf.EXCHANGES
    df = pd.DataFrame(np.load(file), columns=['pair', 'exchange'])
    df2 = df.isin([pair])
    if df2[df2['pair'] == True].size != 0:
        return 'Pair already exists', 200
    else:
        try:
            df = df.append(pd.DataFrame([[pair, exchange]], columns=['pair', 'exchange']), ignore_index=True)
            np.save('exchanges', df)
            return 'Pair added', 200
        except:
            return 'shit', 500


def check_exchange(pair):
    conf = config.BaseConfig()
    file = conf.EXCHANGES
    df = pd.DataFrame(np.load(file), columns=['pair', 'exchange'])
    return list(df[df.pair == pair].exchange)[0]


