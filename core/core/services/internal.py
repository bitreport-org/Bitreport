# -*- coding: utf-8 -*-
import numpy as np
from influxdb import InfluxDBClient
import datetime
import pandas as pd
import config
import types

conf = config.BaseConfig()

def import_numpy(pair, timeframe, limit):
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
    db = conf.DBNAME
    host = conf.HOST
    port = conf.PORT
    client = InfluxDBClient(host, port, 'root', 'root', db)
    # Perform query and return JSON data
    query = "SELECT * FROM {} WHERE time <= {} ORDER BY time DESC LIMIT {}".format(pair+timeframe, untill*1000000000, limit)
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
    file = conf.EXCHANGES
    with np.load(file) as data:
        pairs = data['pairs']
    return pairs.tolist()


def build_exchanges():
    pairs = []
    exchanges = []
    with open("exchanges.txt","r")  as file:
        for row in file:
            p, e = row.split(',')
            pairs.append(p)
            exchanges.append(e[:-1])
    
    np.savez('exchanges', pairs=pairs, exchanges=exchanges)


def dump_exchanges():
    file = conf.EXCHANGES
    with np.load(file) as file:
        pairs = file['pairs']
        exchanges = file['exchanges']
        
    with open("exchanges.txt","w") as file:
        for p, e in zip(pairs, exchanges):
            file.write("{},{}\n".format(p,e))


def add_pair(pair, exchange):
    file = conf.EXCHANGES

    with np.load(file) as data:
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
    file = conf.EXCHANGES

    with np.load(file) as data:
        pairs = data['pairs']
        exchanges = data['exchanges']

    try:
        i = np.where(pairs == pair)[0][0]
        return exchanges[i]
    except:
        return None

def show_pairs_exchanges():
    file = conf.EXCHANGES
    with np.load(file) as data:
        pairs = data['pairs']
        exchanges = data['exchanges']
        
    return np.stack((pairs, exchanges), axis=1).tolist()





