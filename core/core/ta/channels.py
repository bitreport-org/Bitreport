import numpy as np
import talib
from operator import itemgetter
from influxdb import InfluxDBClient
import time
from core.services import internal
import ast


def channel(data, start, percent=80, margin=26):
    magic_limit = start
    close, open, high, low = data['close'], data['open'], data['high'], data['low']
    avg = (close+open)/2

    length = int(percent/100 * close.size)

    probe_data = avg[:length]
    a = talib.LINEARREG_SLOPE(probe_data, length)[-1]
    b = talib.LINEARREG_INTERCEPT(probe_data, length)[-1]

    # To increase precision for small values
    m = 10000
    std = talib.STDDEV(m * avg, timeperiod=close.size, nbdev=1)[-1]/m

    up_channel, bottom_channel , channel= [], [], []
    for i in range(close.size+margin):
        up_channel.append(i*a+b+std)
        bottom_channel.append(i * a + b - std)
        channel.append(i * a + b)

    # parameters for channel extrapolation
    x0 = data['date'][0]
    dx = int(data['date'][1] - data['date'][0])

    return {'upperband': up_channel[start:],
            'middleband': channel[start:],
            'lowerband': bottom_channel[start:],
            'params': {
                'x0': x0,
                'dx': dx,
                'vector': (a, b, std)
            }
        }

def parabola(data, start, percent=70, margin=26):
    magic_limit = start
    open = data['open']
    close = data['close']

    avg = (open+close)/2

    # mini = talib.MININDEX(close, open.size)[-1]
    # maxi = talib.MAXINDEX(close, open.size)[-1]

    start = 0 # min(mini,maxi)
    end = int(percent/100*close.size) # max(mini,maxi)+1

    x = np.array(range(start, end))
    longer_x = np.array(range(close.size+margin))

    y = avg[start : end]

    # creates parabola polynomial
    poly = np.poly1d(np.polyfit(x, y, 2))

    vector = 0 # poly(start) - open[start]
    # To increase precision for small values
    m = 10000
    std = talib.STDDEV(m*y, timeperiod=y.size, nbdev=2)[-1]/m

    z, zp, zm = [], [], []
    for point in longer_x:
        z.append(poly(point)-vector)
        zm.append(poly(point) - vector-std)
        zp.append(poly(point) - vector+std)

    # parameters for channel extrapolation
    x0 = data['date'][0]
    dx = int(data['date'][1] - data['date'][0])

    return {'middleband': z[magic_limit:],
            'upperband': zp[magic_limit:],
            'lowerband':zm[magic_limit:],
            'params':{
                'x0': x0,
                'dx': dx,
                'poly': (poly[0],poly[1], poly[2]),
                'std': std,
            }
            }


def linear(data, start, period = 20):
    close = data['close']

    indicator_values = [0] * period
    up_channel, bottom_channel = [0] * period, [0] * period

    for i in range(period,close.size):
        probe_data = close[i-period : i]
        a = talib.LINEARREG_SLOPE(probe_data, period)[-1]
        b = talib.LINEARREG_INTERCEPT(probe_data, period)[-1]
        y = a*period+b
        std = talib.STDDEV(probe_data, timeperiod=probe_data.size, nbdev=1)[-1]

        indicator_values.append(y)
        up_channel.append(y + std)
        bottom_channel.append(y - std)

    return {'upperband': up_channel[start:], 'middleband':indicator_values[start:], 'lowerband': bottom_channel[start:]}


def fallingwedge(data, start, margin=26):
    full_size = data['close'].size
    close = data['close'][start:]
    close_size = close.size

    point1 = talib.MAXINDEX(close, timeperiod=close_size)[-1]
    # min_index = talib.MININDEX(close, timeperiod=close_size)[-1]

    # From max_index calculate alpha for points (max_index, close(max_index)), (i, close(i))
    a_list = []
    for i in range(point1 + 1, close_size - 3):
        a = (close[i] - close[point1]) / (i - point1)
        b = close[i] - a * i

        a1 = (close[i] - close[point1]) / (i - point1)
        a2 = (close[i + 2] - close[point1]) / (i + 2 - point1)
        a3 = (close[i] - close[point1]) / (i - point1)
        if a2 < 0.6 * a:
            a_list.append((i, a, b))

    break_tuple1 = max(a_list, key=itemgetter(1))
    upper_a = break_tuple1[1]
    upper_b = break_tuple1[2]
    point2 = break_tuple1[0]

    point3 = point1 + talib.MININDEX(close[point1:point2], timeperiod=point2 - point1)[-1]

    a_list = []
    for i in range(point2 + 1, close_size):
        a = (close[i] - close[point3]) / (i - point3)
        b = close[i] - a * i
        a_list.append((i, a, b))

    break_tuple2 = min(a_list, key=itemgetter(1))
    lower_a = break_tuple2[1]
    lower_b = break_tuple2[2]
    point4 = break_tuple2[0]

    # check if the wedge make sense:
    up_start_value = upper_a * close[point1] + upper_b
    down_start_value = lower_a * close[point1] + lower_b

    up_end_value = upper_a * close[point4] + upper_b
    down_end_value = lower_a * close[point4] + lower_b

    if up_start_value - down_start_value < up_end_value - down_end_value:
        upper_band = [None] * (start + point1 - 1)
        middle_band = [None] * (full_size + margin)
        lower_band = [None] * (start + point1 - 1)

        for i in range(point1, close_size + margin + 1):
            upper_band.append(upper_a * i + upper_b)
            lower_band.append(lower_a * i + lower_b)

        # parameters for channel extrapolation
        x0 = data['date'][start + point1]
    else:
        upper_band = [None] * (full_size + margin)
        middle_band = [None] * (full_size + margin)
        lower_band = [None] * (full_size + margin)
        # parameters for channel extrapolation
        x0 = 0

    # parameters for channel extrapolation
    dx = int(data['date'][1]-data['date'][0])

    return {'upperband': upper_band[start:],
            'middleband': middle_band[start:],
            'lowerband': lower_band[start:],
            'params': {'x0': x0,
                       'dx': dx,
                       'upper': (upper_a, upper_b),
                       'lower': (lower_a, lower_b)
                       }}


# Channels saver
def save_channel(pair, timeframe,limit, channel_type):
    conf = internal.Config('config.ini', 'services')
    db_name = conf['db_name']
    host = conf['host']
    port = int(conf['port'])
    client = InfluxDBClient(host, port, 'root', 'root', db_name)

    magic_limit = int(conf['magic_limit'])
    data = internal.import_numpy(pair, timeframe,limit+magic_limit)
    callChannel = globals()[channel_type]
    ch = callChannel(data, magic_limit)
    params = str(ch['params'])
    ch = str(ch)

    json_body = [
        {
            "measurement": 'channels',
            "time": int(1000000000 * time.time()),
            "fields": {"channel": ch},
            "tags": {
                "pair": pair,
                "timeframe": timeframe,
                "chtype": channel_type,
                "params": params
            }
        }
    ]
    # TODO: retention policy
    status = client.write_points(json_body)  # retention_policy='tickerdelete')

    return status

def last_channel(pair, timeframe, channel_type):
    conf = internal.Config('config.ini', 'services')
    db = conf['db_name']
    host = conf['host']
    port = int(conf['port'])
    client = InfluxDBClient(host, port, 'root', 'root', db)

    # Perform query and return JSON data
    query = "SELECT * FROM channels WHERE chtype='"+channel_type+"' AND pair='" +pair + "' AND timeframe='" +timeframe +"' ORDER BY time DESC LIMIT 1;"
    request = 'db=' + db + '&q=' + query
    r = client.request('query', params=request)
    try:
        response = r.json()['results'][0]['series'][0]['values'][0]

        channel_type = response[2]
        pair = response[3]
        timeframe = response[5]
        dictionary = ast.literal_eval(response[1])
        channel = {'lowerband': dictionary['lowerband'], 'middleband':dictionary['middleband'],'upperband': dictionary['upperband']}
        params = dictionary['params']

        return {'channel_type': channel_type,
                'pair':pair,
                'timeframe':timeframe,
                'channel': channel,
                'params':params
                }
    except:
        return False

def create_channels(dates, pair, timeframe, start):

    channel_dict ={}

    # parabola
    last_parabola = last_channel(pair, timeframe, 'parabola')
    if last_parabola != False:
        middleband = []
        upperband = []
        lowerband =[]

        params =last_parabola['params']
        x0 = params['x0']
        dx = params['dx']
        poly = params['poly']
        std = params['std']
        for timestamp in dates:
            x = int((timestamp-x0)/dx)
            y = poly[2] *  x**2 + poly[1] * x + poly[0]
            middleband.append(y)
            upperband.append(y+std)
            lowerband.append(y-std)

        channel_dict['last_parabola'] = {'middleband': middleband[start:], 'upperband':upperband[start:], 'lowerband':lowerband[start:]}
    else:
        channel_dict['last_parabola'] = {'middleband': [], 'upperband':[], 'lowerband':[]}

    #channel
    lastchannel = last_channel(pair, timeframe, 'channel')
    if lastchannel != False:
        middleband = []
        upperband = []
        lowerband = []

        params = lastchannel['params']
        x0 = params['x0']
        dx = params['dx']
        vector= params['vector']
        std = vector[2]
        for timestamp in dates:
            x = int((timestamp - x0) / dx)
            y = vector[0]*x + vector[1]
            middleband.append(y)
            upperband.append(y + std)
            lowerband.append(y - std)

        channel_dict['last_channel'] = {'middleband': middleband[start:], 'upperband': upperband[start:], 'lowerband': lowerband[start:]}
    else:
        channel_dict['last_channel'] = {'middleband': [], 'upperband': [], 'lowerband': []}


    #fallingwedge
    lastfallingwedge = last_channel(pair, timeframe, 'fallingwedge')
    if lastfallingwedge != False:
        middleband = []
        upperband = []
        lowerband = []

        params = lastfallingwedge['params']
        x0 = params['x0']
        # Check if falling wedge exists
        if x0 != 0:
            dx = params['dx']
            upper = params['upper']
            lower = params['lower']

            for timestamp in dates:
                x = int((timestamp - x0) / dx)
                upperband.append(upper[0] * x + upper[1])
                lowerband.append(lower[0] * x + lower[1])

            channel_dict['last_fallingwedge'] = {'middleband': middleband[start:], 'upperband': upperband[start:], 'lowerband': lowerband[start:]}
        else:
            channel_dict['last_fallingwedge'] = {'middleband': [], 'upperband': [], 'lowerband': []}
    else:
        channel_dict['last_fallingwedge'] = {'middleband': [], 'upperband': [], 'lowerband': []}

    return channel_dict