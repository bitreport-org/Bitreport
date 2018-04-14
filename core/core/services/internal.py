import numpy as np
import configparser
from influxdb import InfluxDBClient
import math
import datetime
from decimal import Decimal as dec
import psycopg2
import pandas as pd

def Config(file, section):
    config = configparser.ConfigParser()
    config.read(file)

    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


def import_numpy(pair, timeframe, limit):
    conf = Config('config.ini', 'services')
    db = conf['db_name']
    host = conf['host']
    port = int(conf['port'])
    client = InfluxDBClient(host, port, 'root', 'root', db)

    # Perform query and return JSON data
    query = 'SELECT * FROM {} ORDER BY time DESC LIMIT {};'.format(pair+timeframe, limit)
    params = 'db={}&q={}&epoch=s'.format(db, query)
    r = client.request('query', params=params).json()['results'][0]['series'][0]
    try:
        candle_list = r['values']
        candle_list.reverse()
        df = pd.DataFrame(candle_list, columns=r['columns'])

        candles_dict = {'date': list(df.time),
                        'open': np.array(df.open),
                        'close': np.array(df.close),
                        'high': np.array(df.high),
                        'low': np.array(df.low),
                        'volume': np.array(df.volume)
                        }

        return candles_dict
    except:
        return False


def import_numpy_untill(pair, timeframe, limit, untill):
    conf = Config('config.ini', 'services')
    db = conf['db_name']
    host = conf['host']
    port = int(conf['port'])
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
                        'open': np.array(df.open),
                        'close': np.array(df.close),
                        'high': np.array(df.high),
                        'low': np.array(df.low),
                        'volume': np.array(df.volume)
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
    buildin = ['__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'talib', 'np', 'internal']
    for x in buildin:
        try:
            l.pop(l.index(x))
        except:
            pass
    return l


# FUNNY MOON STUFF
def position(now=None):
   if now is None:
      now = datetime.datetime.now()

   diff = now - datetime.datetime(2001, 1, 1)
   days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
   lunations = dec("0.20439731") + (days * dec("0.03386319269"))

   return lunations % dec(1)


def phase(pos):
   index = (pos * dec(8)) + dec("0.5")
   index = math.floor(index)
   return {
      0: "🌑",
      1: "🌒",
      2: "🌓",
      3: "🌔",
      4: "🌕",
      5: "🌖",
      6: "🌗",
      7: "🌘"
   }[int(index) & 7]


def what_phase(timestamp):
   t = datetime.datetime.fromtimestamp(int(timestamp))
   pos = position(t)
   phasename = phase(pos)

   roundedpos = round(float(pos), 3)
   return (phasename, roundedpos)

#PostgreSQL stuff
def show_pairs():
    conf = Config('config.ini', 'services')
    db = conf['postgre_db']

    conn = psycopg2.connect(dbname=db, host='localhost')
    cur = conn.cursor()

    SQL = "SELECT * FROM available_pairs;"
    cur.execute(SQL)
    rows = cur.fetchall()

    pairs_list = []
    for row in rows:
        pairs_list.append(row)

    conn.commit()
    cur.close()
    conn.close()

    return pairs_list

def add_pair(pair, exchange):
    conf = Config('config.ini', 'services')
    db = conf['postgre_db']

    q = "dbname='"+db+"' host='localhost' "
    conn = psycopg2.connect(q)
    cur = conn.cursor()

    data = (pair, exchange)
    SQL = "SELECT * FROM available_pairs WHERE pair=%s and exchange=%s"
    cur.execute(SQL, data,)
    rows=cur.fetchall()

    if len(rows) == 0:
        SQL = "INSERT INTO available_pairs VALUES (%s, %s);"
        cur.execute(SQL, data,)
        message = 'Pair added'
    else:
        message = 'Pair already exist'

    conn.commit()
    cur.close()
    conn.close()

    return message

def check_exchange(pair):
    conf = Config('config.ini', 'services')
    db = conf['postgre_db']

    q = "dbname='" + db + "' host='localhost' "
    conn = psycopg2.connect(q)
    cur = conn.cursor()

    SQL = "SELECT * FROM available_pairs WHERE pair = '{}';".format(pair)
    cur.execute(SQL)
    rows = cur.fetchall()
    if rows == []:
        return 'None'

    conn.commit()
    cur.close()
    conn.close()

    return rows[0][1]

