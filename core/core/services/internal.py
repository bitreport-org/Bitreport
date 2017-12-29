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
    conf = Config('core/config.ini', 'services')
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

def get_function_list(module):
    l = dir(module)
    buildin = ['__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'talib', 'np']
    for x in buildin:
        try:
            l.pop(l.index(x))
        except:
            pass
    return l

