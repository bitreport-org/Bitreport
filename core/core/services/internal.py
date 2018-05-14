# -*- coding: utf-8 -*-
import numpy as np
from influxdb import InfluxDBClient
import datetime
import pandas as pd
import config
import types

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
        if list(df.time) != []:
            return candles_dict
        else:
            return False
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

    for i in range(margin):
        date.append(int(date[-1]) + d)

    return date


def get_function_list(module):
    return [module.__dict__.get(a) for a in dir(module) if isinstance(module.__dict__.get(a), types.FunctionType)]


def show_pairs():
    conf = config.BaseConfig()
    file = conf.EXCHANGES
    with np.load('exchanges.npz') as data:
        pairs = data['pairs']

    return pairs.tolist()


def add_pair(pair, exchange):
    conf = config.BaseConfig()
    file = conf.EXCHANGES

    with np.load('exchanges.npz') as data:
        pairs = data['pairs']
        exchanges = data['exchanges']
    
    if pair in pairs:
        return 'Pair already exists', 200
    else:
        try:
            pairs = np.append(pairs, [pair])
            exchanges = np.append(exchanges, [exchange])
            np.savez('exchanges', pairs= pairs, exchanges = exchanges)
            return 'Pair added', 200
        except:
            return 'shit', 500


def check_exchange(pair):
    conf = config.BaseConfig()
    file = conf.EXCHANGES

    with np.load('exchanges.npz') as data:
        pairs = data['pairs']
        exchanges = data['exchanges']

    try:
        i = np.where(pairs == pair)[0][0]
        return exchanges[i]
    except:
        return None

def show_pairs_exchanges():
    conf = config.BaseConfig()
    file = conf.EXCHANGES
    with np.load('exchanges.npz') as data:
        pairs = data['pairs']
        exchanges = data['exchanges']
        
    return np.stack((pairs, exchanges), axis=1).tolist()





