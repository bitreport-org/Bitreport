import numpy as np
import talib
import config

config = config.BaseConfig()

def channel(data, percent=80):
    margin = config.MARGIN
    start = config.MAGIC_LIMIT

    close, open, high, low = data['close'], data['open'], data['high'], data['low']
    avg = (high+low)/2 #(close+open)/2

    length = int(percent/100 * close.size)

    probe_data = avg[:length]
    a = talib.LINEARREG_SLOPE(probe_data, length)[-1]
    b = talib.LINEARREG_INTERCEPT(probe_data, length)[-1]

    # To increase precision for small values
    std = talib.STDDEV(10000 * avg, timeperiod=close.size, nbdev=1)[-1] / 10000

    up_channel = a * np.arange(close.size+margin) + b + std
    bottom_channel = a * np.arange(close.size+margin) + b - std
    channel = a * np.arange(close.size+margin) + b 

    # parameters for channel extrapolation
    x0 = data['date'][0]
    dx = int(data['date'][1] - data['date'][0])

    return {'upperband': up_channel.tolist()[start:],
            'middleband': channel.tolist()[start:],
            'lowerband': bottom_channel.tolist()[start:],
            'params': {
                'x0': x0,
                'dx': dx,
                'vector': (a, b, std)
            }
        }


def parabola(data, percent=100):
    margin = config.MARGIN
    start = config.MAGIC_LIMIT

    open = data['open']
    close = data['close']
    avg = (open+close)/2

    end = int(percent/100*close.size)
    x = np.arange(start, end)
    y = avg[start : end]
    longer_x = np.arange(close.size+margin) # to plot channel in future

    # creates parabola polynomial
    poly = np.poly1d(np.polyfit(x, y, 2))

    # To increase precision for small values
    std = talib.STDDEV(10000 * y, timeperiod=y.size, nbdev=1)[-1] / 10000

    y =  poly(longer_x)
    yup = y + std
    ydown = y - std 

    # parameters for channel extrapolation
    x0 = data['date'][0]
    dx = int(data['date'][1] - data['date'][0])

    return {'middleband': y.tolist()[start:],
            'upperband': yup.tolist()[start:],
            'lowerband':ydown.tolist()[start:],
            'params':{
                'x0': x0,
                'dx': dx,
                'poly': (poly[0],poly[1], poly[2]),
                'std': std,
            }
            }


def fallingwedge(data):
    margin = config.MARGIN
    start = config.MAGIC_LIMIT

    full_size = data['close'].size
    close = data['close'][start:]
    close_size = close.size

    # Upper start point
    point1 = talib.MAXINDEX(close, timeperiod=close_size)[-1]
    
    if point1 < close_size-4:
        # Upper band
        a_values = np.divide(np.array(close[point1+1 : close_size-4]) - close[point1], np.arange(point1+1, close_size-4) - point1)
        upper_a = np.max(a_values)
        upper_b = close[point1] - upper_a * point1

        # End point
        point2, = np.where(a_values == upper_a)[0]
        point2 = point1 + point2

        # Lower start point
        point3 = point1 + talib.MININDEX(close[point1: point2], timeperiod=len(close[point1: point2]))[-1]
        
        # Lower band
        a_values = np.divide(np.array(close[point3+1 : close_size-4]) - close[point3], np.arange(point3+1, close_size-4) - point3)
        lower_a = np.min(a_values)
        lower_b = close[point3] - lower_a * point3

        # Check if wedge makes sense
        up_start_value = upper_a * close[point1] + upper_b
        down_start_value = lower_a * close[point1] + lower_b
        up_end_value = upper_a * close[point1] + upper_b
        down_end_value = lower_a * close[point1] + lower_b

        # Has shape >
        if up_start_value - down_start_value <= up_end_value - down_end_value:
            upper_band = upper_a * np.arange(full_size) + upper_b
            lower_band = lower_a * np.arange(full_size) + lower_b
        else:
            lower_band, upper_band = np.array([]), np.array([])

    else:
        lower_band, upper_band = np.array([]), np.array([])

    # Parameters for channel extrapolation
    x0 = data['date'][point1]
    dx = int(data['date'][1]-data['date'][0])

    return {'upperband': upper_band.tolist(),
            'middleband': [],
            'lowerband': lower_band.tolist(),
            'params': {'x0': x0,
                       'dx': dx,
                       'upper': (upper_a, upper_b),
                       'lower': (lower_a, lower_b)
                       }}


def raisingwedge(data):
    margin = config.MARGIN
    start = config.MAGIC_LIMIT

    full_size = data['close'].size
    close = data['close'][start:]
    close_size = close.size

    # Lower start point
    point1 = talib.MININDEX(close, timeperiod=close_size)[-1]
    
    if point1 < close_size-4:
        # Lower band
        a_values = np.divide(np.array(close[point1+1 : close_size-4]) - close[point1], np.arange(point1+1, close_size-4) - point1)
        lower_a = np.min(a_values)
        lower_b = close[point1] - lower_a * point1

        # End point
        point2, = np.where(a_values == lower_a)[0]
        point2 = point1 + point2

        # Upper start point
        point3 = point1 + talib.MAXINDEX(close[point1: point2], timeperiod=len(close[point1: point2]))[-1]
        
        # Upper band
        a_values = np.divide(np.array(close[point3+1 : close_size-4]) - close[point3], np.arange(point3+1, close_size-4) - point3)
        upper_a = np.max(a_values)
        upper_b = close[point3] - upper_a * point3

        # Check if wedge makes sense
        up_start_value = upper_a * close[point1] + upper_b
        down_start_value = lower_a * close[point1] + lower_b
        up_end_value = upper_a * close[point1] + upper_b
        down_end_value = lower_a * close[point1] + lower_b

        # Has shape >
        if up_start_value - down_start_value >= up_end_value - down_end_value:
            upper_band = upper_a * np.arange(full_size) + upper_b
            lower_band = lower_a * np.arange(full_size) + lower_b
        else:
            lower_band, upper_band = np.array([]), np.array([])

    else:
        lower_band, upper_band = np.array([]), np.array([])

    # Parameters for channel extrapolation
    x0 = data['date'][point1]
    dx = int(data['date'][1]-data['date'][0])

    return {'upperband': upper_band.tolist(),
            'middleband': [],
            'lowerband': lower_band.tolist(),
            'params': {'x0': x0,
                       'dx': dx,
                       'upper': (upper_a, upper_b),
                       'lower': (lower_a, lower_b)
                       }}
