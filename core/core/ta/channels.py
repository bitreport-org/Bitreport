import numpy as np
import talib
import config

config = config.BaseConfig()



def channel(data: dict, percent: int = 80):
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

    # TOKENS
    info = []
    p = ( close[-1] - up_channel[-1-margin] ) / (up_channel[-1-margin]-bottom_channel[-1-margin]) 

    # Price Tokens
    if p > 1:
        info.append('PRICE_BREAK_UP')
    elif p < 0:
        info.append('PRICE_BREAK_DOWN')
    elif p > 0.95:
        info.append('PRICE_ONBAND_UP')
    elif p < 0.05:
        info.append('PRICE_ONBAND_DOWN')
    else:
        info.append('PRICE_BETWEEN')

    n_last_points = 10
    if np.sum(close[-n_last_points:] > up_channel[-n_last_points-margin : -margin]) > 0 and close[-1] < up_channel[-1]:
        info.append('PRICE_PULLBACK')
    elif np.sum(close[-n_last_points:] < bottom_channel[-n_last_points-margin : -margin]) > 0 and close[-1] > bottom_channel[-1]:
        info.append('PRICE_THROWBACK')

    # Drirection Tokens
    if a < -0.1:
        info.append('DIRECTION_DOWN')
    elif a > 0.1:
        info.append('DIRECTION_UP')
    else:
        info.append('DIRECTION_HORIZONTAL')

    return {'upperband': up_channel.tolist()[start:],
            'middleband': channel.tolist()[start:],
            'lowerband': bottom_channel.tolist()[start:],
            'info': info,
            'params': {
                'x0': x0,
                'dx': dx,
                'vector': (a, b, std)
            }
        }


def parabola(data: dict, percent: int =100):
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


def wedge(data: dict):
    margin = config.MARGIN
    start = config.MAGIC_LIMIT

    close, low, high = data['close'][start:], data['low'][start:], data['high'][start:]
    close_size = close.size

    def make_wedge(t):
        lower_band, upper_band, width, params, info = np.array([]), np.array([]), np.array([]), [], []
        
        if t == 'falling':
            dt = low
            f0 = talib.MAXINDEX
            f1 = np.max
            f2 = talib.MININDEX
            f3 = np.min
        else:
            dt = high
            f0 = talib.MININDEX
            f1 = np.min
            f2 = talib.MAXINDEX
            f3 = np.max

        lower_band, upper_band = np.array([]), np.array([])
        point1 = f0(close, timeperiod=close_size)[-1]
    
        end = close_size-5
        if point1 < close_size - 30:
            # Band 1
            a_values = np.divide(np.array(close[point1+2 : end+1]) - close[point1], np.arange(point1+2, end+1) - point1)
            a1 = f1(a_values)
            b1 = close[point1] - a1 * point1

            # End point
            point2, = np.where(a_values == a1)[0]
            point2 = ( point1 + 2 ) + point2 

            # Mid point
            point3 = point1 + f2(close[point1 : point2], timeperiod=len(close[point1: point2]))[-1]
            point3_value = close[point3]

            earlier_point3 = f2(dt[:point3], timeperiod=len(dt[:point3]))[-1]
            
            # Band 2
            if earlier_point3 < point3:
                point3 = earlier_point3
                point3_value = dt[point3]

                a_values = np.divide(np.array(dt[point3+1 : end+1]) - point3_value, np.arange(point3+1, end+1) - point3)
                a2 = f3(a_values)
                b2 = dt[point3] - a2 * point3

            else:
                a_values = np.divide(np.array(close[point3+1 : end+1]) - point3_value, np.arange(point3+1, end+1) - point3)
                a2 = f3(a_values)
                b2 = close[point3] - a2 * point3

            # Create upper and lower band
            if t == 'falling':
                upper,lower = np.array([a1, b1]), np.array([a2, b2])
                upper_band = a1 * np.arange(close_size) + b1
                lower_band = a2 * np.arange(close_size) + b2
            else:
                upper,lower = np.array([a2, b2]), np.array([a1, b1])
                upper_band = a2 * np.arange(close_size) + b2
                lower_band = a1 * np.arange(close_size) + b1

            # Shape Tokens
            width = upper_band - lower_band 
            if width[-1]/width[0] > 0.90:
                info.append('SHAPE_PARALLEL')
            elif width[-1]/width[0] < 0.75:
                info.append('SHAPE_TRIANGLE')
            else:
                info.append('SHAPE_CONTRACTING')

            # Break Tokens
            if close[-1] > upper_band[-1]:
                info.append('PRICE_BREAK_UP')
            elif close[-1] < lower_band[-1]:
                info.append('PRICE_BREAK_DOWN')

            # Price Tokens
            if (close[-1]-lower_band[-1])/width[-1] >= 0.95:
                info.append('PRICE_ONBAND_UP')
            elif (close[-1]-lower_band[-1])/width[-1] <= 0.05:
                info.append('PRICE_ONBAND_UP')
            else:
                info.append('PRICE_BETWEEN')

            n_last_points = 10
            if np.sum(close[-n_last_points:] > upper_band[-n_last_points:]) > 0 and close[-1] < upper_band[-1]:
                info.append('PRICE_PULLBACK')
            elif np.sum(close[-n_last_points:] < lower_band[-n_last_points:]) > 0 and close[-1] > lower_band[-1]:
                info.append('PRICE_THROWBACK')

            
            # Direction Tokens
            wedge_dir = (lower_band[0] + width[0] - lower_band[-1] + width[-1]) / lower_band.size
            if wedge_dir > 0.25:
                info.append('DIRECTION_UP')
            elif wedge_dir < -0.25:
                info.append('DIRECTION_DOWN')
            else:
                info.append('DIRECTION_HORIZONTAL')


            # Wedge extension
            for i in range(margin):
                new_point_up = np.sum(upper * [close_size+i, 1])
                new_point_down = np.sum(lower * [close_size+i, 1])
                if new_point_up > new_point_down:
                    upper_band = np.append(upper_band, new_point_up)
                    lower_band = np.append(lower_band, new_point_down)

            # Parameters for channel extrapolation
            params = {'x0': data['date'][point1],
                       'dx': int(data['date'][1]-data['date'][0]),
                       'upper': (a1, b1),
                       'lower': (a2, b2)
                       }

        return upper_band, lower_band, width, info, params

    # Falling wedge
    upper_band, lower_band, width, info, params = make_wedge('falling')

    # Check if wedge makes sense
    if width.size > 0  and width[0] - width[-1] < 0:
        # Rising wedge
        upper_band, lower_band, width, info, params = make_wedge('raising')
        # Check if wedge makes sense
        if width.size > 0  and width[0] - width[-1] < 0:
            lower_band, upper_band = np.array([]), np.array([])
            params, info = [], []
      

    return {'upperband': upper_band.tolist(),
            'middleband': [],
            'lowerband': lower_band.tolist(),
            'info': info,
            'params': params}
