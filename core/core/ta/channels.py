import numpy as np
import talib
from operator import itemgetter

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


def fallingwedge(data, start, margin=26):
    full_size = data['close'].size
    close = data['close'][start:]
    close_size = close.size

    point1 = talib.MAXINDEX(close, timeperiod=close_size)[-1]
    # min_index = talib.MININDEX(close, timeperiod=close_size)[-1]

    # From max_index calculate alpha for points (max_index, close(max_index)), (i, close(i))
    a_list = []

    if point1 < close_size-4:
        for i in range(point1 + 1, close_size - 2):
            a = (close[i] - close[point1]) / (i - point1)
            b = close[i] - a * i

            a2 = (close[i + 2] - close[point1]) / (i + 2 - point1)
            if a2 < 0.8 * a:
                a_list.append((i, a, b))

        break_tuple1 = max(a_list, key=itemgetter(1))
        upper_a = break_tuple1[1]
        upper_b = break_tuple1[2]
        point2 = break_tuple1[0]

        point3 = point1 + talib.MININDEX(close[point1:point2+2], timeperiod=point2 - point1)[-1]

        a_list = []
        for i in range(point3 + 1, close_size):
            a = (close[i] - close[point3]) / (i - point3)
            b = close[i] - a * i
            a_list.append((i, a, b))

        break_tuple2 = min(a_list, key=itemgetter(1))
        lower_a = break_tuple2[1]
        lower_b = break_tuple2[2]
        point4 = break_tuple2[0]

        # Check if the wedge make sense:
        # Check if the wedge is expanding

        up_start_value = upper_a * close[point1] + upper_b
        down_start_value = lower_a * close[point1] + lower_b

        up_end_value = upper_a * close[point4] + upper_b
        down_end_value = lower_a * close[point4] + lower_b

        if up_start_value - down_start_value < up_end_value - down_end_value:
            upper_band = [None] * (start + point1 - 1)
            middle_band = [None] * (full_size + margin)
            lower_band = [None] * (start + point1 - 1)

            for i in range(point1, close_size + margin + 1):
                up = upper_a * i + upper_b
                down = lower_a * i + lower_b
                # Check if wedge arms are crossing
                if up >= down:
                    upper_band.append(up)
                    lower_band.append(down)
                else:
                    upper_band.append(None)
                    lower_band.append(None)

            # parameters for channel extrapolation
            x0 = data['date'][start + point1]
        else:
            upper_band = []
            middle_band = []
            lower_band = []
            # parameters for channel extrapolation
            x0 = 0
    else:
        upper_band = [None] * (full_size + margin)
        middle_band = [None] * (full_size + margin)
        lower_band = [None] * (full_size + margin)
        x0 = 0
        lower_b, lower_a, upper_a, upper_b = 0,0,0,0

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
