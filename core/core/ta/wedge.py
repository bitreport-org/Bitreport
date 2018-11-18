import numpy as np
import talib #pylint: skip-file
import config

Config = config.BaseConfig()


def last_wedge():
    NotImplemented

def save_wedge():
    NotImplemented

def make_wedge(data: dict):

    new_wedge = wedge(data)
    old_wedge = last_wedge()

    # Compare wedge
    NotImplemented

def wedge(data: dict):
    margin = Config.MARGIN
    start = Config.MAGIC_LIMIT

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

        return upper_band, lower_band, width, info

    # Falling wedge
    upper_band, lower_band, width, info = make_wedge('falling')

    # Check if wedge makes sense
    if width.size > 0  and width[0] - width[-1] < 0: 
        # Rising wedge
        upper_band, lower_band, width, info = make_wedge('raising')
        # Check if wedge makes sense
        if width.size > 0  and width[0] - width[-1] < 0:
            lower_band, upper_band = np.array([]), np.array([])
            info = []
      

    return {'upper_band': upper_band.tolist(),
            'middle_band': [],
            'lower_band': lower_band.tolist(),
            'info': info}
