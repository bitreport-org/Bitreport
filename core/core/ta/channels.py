import numpy as np
import talib #pylint: skip-file
import config

config = config.BaseConfig()


def channel(data: dict, sma_type: int = 50):
    margin = config.MARGIN
    start = config.MAGIC_LIMIT
    close = data.get('close')[start:]
    limit = close.size
    
    sma = talib.SMA(data.get('close'), timeperiod = sma_type)
    sma = (close - sma[start:]) / sma[start:]
    sma = np.where(sma >=0, 1., -1.)
    filter_value =5
    f1 = np.where(talib.SMA(sma, timeperiod = filter_value)[filter_value:] >= 0.0, 1., -1.)
    f2 = np.where(talib.SMA(f1, timeperiod = 2) == 0.0 , 1., 0.)
    points, = np.where(f2>0)
    ch_points = np.array([0] + (points+filter_value).tolist())

    def _make(start, end, close):
        x = np.arange(start, end)
        y = close[start:end]
        lm = np.poly1d(np.polyfit(x,y, 1))
        std = np.std(close[start:end])     
        return lm, std
    
    
    # If price was below / above the SMA then ch_points could contain only 1 point
    if len(ch_points) < 2:
        if ch_points == []:
            s, e = 0, limit
        elif ch_points[0] < limit/2.0:
            s, e = ch_points[0], limit
        else:
            s, e = 0, ch_points[0]

    else:
        # Find longest channel
        lenghts = ch_points[1:] - ch_points[:-1]
        s_position = np.where(lenghts == np.max(lenghts))[0][0]
        s, e = ch_points[s_position], ch_points[s_position+1]
    
    # Calculate channel and slope
    lm, std =  _make(s,e, close)
    slope = lm[1]
    
    # Prepare channel
    x = np.arange(close.size + margin)
    up_channel= lm(x) + 2 * std
    bottom_channel = lm(x) - 2 * std
    
     # TOKENS
    info = []
    p = ( close[-1] - bottom_channel[-1-margin] ) / (up_channel[-1-margin]-bottom_channel[-1-margin]) 

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
    if np.sum(close[-n_last_points:] > up_channel[-n_last_points-margin : -margin]) > 0 and close[-1] < up_channel[-1-margin]:
        info.append('FALSE_BREAK_UP')
    elif np.sum(close[-n_last_points:] < bottom_channel[-n_last_points-margin : -margin]) > 0 and close[-1] > bottom_channel[-1-margin]:
        info.append('FLASE_BREAK_DOWN')

    # Drirection Tokens
    if slope < -0.2:
        info.append('DIRECTION_DOWN')
    elif slope > 0.2:
        info.append('DIRECTION_UP')
    else:
        info.append('DIRECTION_HORIZONTAL')

    return {'upperband': up_channel.tolist(), 'lowerband': bottom_channel.tolist(), 'middleband':[], 'info': info}
    

def parabola(data: dict):
    #margin = config.MARGIN
    start = config.MAGIC_LIMIT

    close = data.get('close')[start:]
    open = data.get('open')[start:]
    avg = (close + open)/2

    M = np.max(avg)
    dist = M-avg
    index1, = np.where(avg == M)
    index2, = np.where(dist == np.max(dist))
    l = [index1[0], index2[0]]
    l.sort()
    point1, point2 = l
    
    # fit parabola
    x = np.arange(point1, point2)
    y = avg[point1: point2]
    parabola = np.poly1d(np.polyfit(x,y,2))
    std = np.std(y)
    
    # prepare channel
    x = np.arange(avg.size)
    upperband = parabola(x) + std
    lowerband = parabola(x) - std

    return {'middleband': [],
            'upperband': upperband.tolist(),
            'lowerband': lowerband.tolist()}
            

def wedge(data: dict):
    margin = config.MARGIN
    start = config.MAGIC_LIMIT

    close, low, high = data['close'][start:], data['low'][start:], data['high'][start:]
    close_size = close.size

    def make_wedge(t):
        lower_band, upper_band, width, info = np.array([]), np.array([]), np.array([]), []
        
        if t == 'falling':
            f0 = talib.MAXINDEX
            f1 = np.max
            f2 = talib.MININDEX
            f3 = np.min
        else:
            f0 = talib.MININDEX
            f1 = np.min
            f2 = talib.MAXINDEX
            f3 = np.max

        lower_band, upper_band = np.array([]), np.array([])
        point1 = f0(close, timeperiod=close_size)[-1]
    
        end = close_size-5
        threshold = 10
        if point1 < close_size - 30:
            # Band 1
            a_values = np.divide(np.array(close[point1 + threshold : end+1]) - close[point1], np.arange(point1 + threshold, end+1) - point1)
            a1 = f1(a_values)
            b1 = close[point1] - a1 * point1

            # End point
            point2, = np.where(a_values == a1)[0]
            point2 = ( point1 + threshold ) + point2 

            # Mid point
            point3 = point1 + f2(close[point1 : point2], timeperiod=len(close[point1: point2]))[-1]
            point3_value = close[point3]
            
            # Band 2
            a_values = np.divide(np.array(close[point3+5 : end+1]) - point3_value, np.arange(point3+5, end+1) - point3)
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
            elif width[-1]/width[0] < 0.5:
                info.append('SHAPE_TRIANGLE')
            else:
                info.append('SHAPE_CONTRACTING')

            # Break Tokens
            if close[-1] > upper_band[-1]:
                info.append('PRICE_BREAK_UP')
            elif close[-1] < lower_band[-1]:
                info.append('PRICE_BREAK_DOWN')

            # Price Tokens
            if 1 >= (close[-1]-lower_band[-1])/width[-1] >= 0.95:
                info.append('PRICE_ONBAND_UP')
            elif 0 <= (close[-1]-lower_band[-1])/width[-1] <= 0.05:
                info.append('PRICE_ONBAND_DOWN')
            else:
                info.append('PRICE_BETWEEN')

            n_last_points = 10
            if np.sum(close[-n_last_points:] > upper_band[-n_last_points:]) > 0 and close[-1] < upper_band[-1]:
                info.append('BOUNCE_UPPER')
            elif np.sum(close[-n_last_points:] < lower_band[-n_last_points:]) > 0 and close[-1] > lower_band[-1]:
                info.append('BOUNCE_LOWER')
            
            # Direction Tokens
            wedge_dir = ((lower_band[-1] + .5*width[-1]) - (lower_band[0] + .5*width[0])) / lower_band.size
            if wedge_dir > 0.35:
                info.append('DIRECTION_UP')
            elif wedge_dir < -0.35:
                info.append('DIRECTION_DOWN')
            else:
                info.append('DIRECTION_HORIZONTAL')

            # Wedge extension
            cross_point = close_size
            for i in range(margin):
                new_point_up = np.sum(upper * [close_size+i, 1])
                new_point_down = np.sum(lower * [close_size+i, 1])
                if new_point_up > new_point_down:
                    cross_point += i
                    upper_band = np.append(upper_band, new_point_up)
                    lower_band = np.append(lower_band, new_point_down)

            # Position Tokens
            # TODO: maybe we should count bounces?
            price_pos = (close_size - point1) / (cross_point - point1)
            if (price_pos > .85) and ('SHAPE_TRIANGLE' in info):
                info.append('ABOUT_END')

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
            info = []
      

    return {'upperband': upper_band.tolist(),
            'middleband': [],
            'lowerband': lower_band.tolist(),
            'info': info,
            'params': params}
