import numpy as np
import time
import iso8601
import configparser
from requests import put, get
import datetime
import talib
from influxdb import InfluxDBClient

def Config(file, section):

    Config = configparser.ConfigParser()
    Config.read(file)
    #print(Config.sections())

    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
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
    query = 'SELECT * FROM ' + pair + timeframe + ' ORDER BY time DESC LIMIT ' + str(limit) + ';'
    params = 'db=' + db + '&q=' + query
    r = client.request('query', params=params)

    # Unwrap json :D
    candel_list = r.json()['results'][0]['series'][0]['values']

    date_list=[]
    open_list=[]
    close_list=[]
    high_list=[]
    low_list=[]
    volume_list=[]

    for i in range(0, len(candel_list)):
        # change data to timestamp
        t = candel_list[i][0]
        dt = iso8601.parse_date(t)
        dt = int(time.mktime(dt.timetuple()))

        date_list.append(dt)
        close_list.append(float(candel_list[i][1]))
        high_list.append(float(candel_list[i][2]))
        low_list.append(float(candel_list[i][3]))
        open_list.append(float(candel_list[i][4]))
        volume_list.append(float(candel_list[i][5]))

    date_list.reverse()
    close_list.reverse()
    open_list.reverse()
    high_list.reverse()
    low_list.reverse()
    volume_list.reverse()

    candles_dict = {'date' : date_list,
                    'open' : np.array(open_list),
                    'close' : np.array(close_list),
                    'high' : np.array(high_list),
                    'low' : np.array(low_list),
                    'volume' : np.array(volume_list)
                    }

    return candles_dict


def check_bb(data):
    close = data['close']
    upperband, middleband, lowerband = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    up = upperband.tolist()[-1]
    low = lowerband.tolist()[-1]
    close1 = close[-1]

    if close1 > up:
        return 'UP'
    elif close1 < low:
        return 'DOWN'

    return False


def check_sma(data):
    close = data['close']
    sma = talib.SMA(close, timeperiod=20)[-1]

    close1 = close[-1]
    close2 = close[-2]

    if close1 > sma > close2:
        return 'UP'
    elif close1 < sma < close2:
        return 'DOWN'

    return False


def check_dildo(data):
    open, close = data['open'], data['close']
    probe = abs(open-close)
    avg = np.mean(probe)

    diff = close[-1] - open[-1]
    adiff = abs(diff)
    if diff >= 1.2*avg:
        return 'UP'
    elif diff < 0 and adiff >= 1.2*avg:
        return 'DOWN'

    return False


def update_events():
    conf = Config('config.ini', 'services')
    pairs = conf['pairs'].split(',')
    timeframes = conf['timeframes'].split(',')

    # TODO: check if now is UTC time
    now = int(time.mktime(datetime.datetime.now().timetuple()))
    #if now % 60 == 0:
    for pair in pairs:
        for tf in timeframes:
            try:
                data = import_numpy(pair, tf, 21)
            except:
                print('Failed import ', pair, tf)
                pass

            try:
                response = check_bb(data)
                name = 'BBBREAK'
                if response != False:
                    event = { 'time' : now,
                              'symbol': pair,
                              'timeframe': tf,
                              'type': name,
                              'direction': response
                            }
                    put('http://localhost:5000/events', data={'data': str(event)})
                    put('localhost:3000/api/events', data={'data': str(event)})
                response = False
            except:
                print('Failed bb ', pair, tf)
                pass

            try:
                response = check_sma(data)
                name = 'SMACROSS'
                if response != False:
                    event = {'time': now,
                             'symbol': pair,
                             'timeframe': tf,
                             'type': name,
                             'direction': response
                             }
                    put('http://localhost:5000/events', data={'data': str(event)})
                response = False
            except:
                print('Failed sma ', pair, tf)
                pass
            try:
                response = check_dildo(data)
                name = 'DILDO'
                if response != False:
                    event = {'time': now,
                             'symbol': pair,
                             'timeframe': tf,
                             'type': name,
                             'direction': response
                             }
                    put('http://localhost:5000/events', data={'data': str(event)})
                response = False
            except:
                print('Failed dildo ', pair, tf)
                pass

