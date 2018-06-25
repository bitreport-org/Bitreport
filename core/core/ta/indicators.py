# -*- coding: utf-8 -*-
import talib #pylint: skip-file
import numpy as np
import os
import config

from sklearn.externals import joblib
from scipy import stats

config = config.BaseConfig()

###################     TAlib indicators    ###################
def BB(data, timeperiod=20):
    start = config.MAGIC_LIMIT
    m = 10000
    close = m * data['close']
    upperband, middleband, lowerband = talib.BBANDS(close, timeperiod, 2, 2, matype = 0)
    
    # TOKENS
    info = []
    band_position = ( close - lowerband ) / (upperband -lowerband)
    p = band_position[-1] 

    if p > 1:
        info.append('PRICE_BREAK_UP')
    elif p < 0:
        info.append('PRICE_BREAK_DOWN')
    elif p > 0.95:
        info.append('PRICE_ONBAND_UP')
    elif p < 0.05:
        info.append('PRICE_ONBAND_DOWN')
    elif 0.40 <= p <= 0.60 :
        info.append('PRICE_BETWEEN')

    width = upperband - lowerband
    test_data = width[-15:] / np.max(width[-15:])
    squeeze = joblib.load('{}/core/ta/clfs/squeeze01CLF15.pkl'.format(os.getcwd())) 
    if squeeze.predict([test_data])[0] == 1:
        info.append('BANDS_SQUEEZE')

    upperband = upperband/m
    middleband = middleband/m
    lowerband = lowerband/m

    return {'upper_band' : upperband.tolist()[start:],
            'middle_band':middleband.tolist()[start:],
            'lower_band':lowerband.tolist()[start:],
            'info': info}


def MACD(data, fastperiod=12, slowperiod=26, signalperiod=9 ):
    start = config.MAGIC_LIMIT
    macd, signal, hist = talib.MACD(data['close'], fastperiod, slowperiod, signalperiod)
    return {'macd' : macd.tolist()[start:],
            'signal':signal.tolist()[start:],
            'histogram':hist.tolist()[start:],
            'info': []}


def RSI(data, timeperiod=14):
    start = config.MAGIC_LIMIT
    close = data['close']
    real = talib.RSI(close, timeperiod)

    # TOKENS
    info = []
    points2check = -10

    if real[-1] >= 70:
        info.append('OSCILLATOR_OVERBOUGHT')
    elif real[-1] <= 30:
        info.append('OSCILLATOR_OVERSOLD')

    slice2check = real[points2check:]
    direction = stats.linregress(np.arange(slice2check.size), slice2check).slope
    threshold = 0.1
    if direction < -1*threshold:
        info.append('DIRECTION_FALLING')
    elif direction > threshold:
        info.append('DIRECTION_RISING')

    n = int(0.25 * (close.size - start))
    dir_rsi = stats.linregress(np.arange(n), real[-n:]).slope
    dir_price = stats.linregress(np.arange(n), close[-n:]).slope
    if dir_rsi * dir_price >= 0.0:
        info.append('DIV_POSITIVE')
    elif dir_rsi * dir_price < 0.0:
        info.append('DIV_NEGATIVE')

    return {'rsi':real.tolist()[start:], 'info': info }


def STOCH(data, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0):
    start = config.MAGIC_LIMIT
    slowk, slowd = talib.STOCH(data['high'], data['low'], data['close'],
                               fastk_period, slowk_period, slowk_matype, slowd_period, slowd_matype)
    
    #TOKENS
    info = []
    if slowk[-1] >= 80:
        info.append('OSCILLATOR_OVERBOUGHT')
    elif slowk[-1] <= 20:
        info.append('OSCILLATOR_OVERSOLD')

    return {'k': slowk.tolist()[start:], 'd': slowd.tolist()[start:], 'info': info}


def STOCHRSI(data, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0):
    start = config.MAGIC_LIMIT
    fastk, fastd = talib.STOCHRSI(data['close'], timeperiod, fastk_period, fastd_period, fastd_matype)
    return {'k': fastk.tolist()[start:], 'd': fastd.tolist()[start:], 'info': []}


def MOM(data, timeperiod=10):
    start = config.MAGIC_LIMIT
    real = talib.MOM(data['close'], timeperiod)
    return {'mom': real.tolist()[start:], 'info': []}


def ADX(data, timeperiod=14):
    start = config.MAGIC_LIMIT
    real = talib.ADX(data['high'], data['low'], data['close'], timeperiod)
    return {'adx': real.tolist()[start:], 'info': []}


def AROON(data, timeperiod=14):
    start = config.MAGIC_LIMIT
    aroondown, aroonup = talib.AROON(data['high'], data['low'], timeperiod)
    return {'down': aroondown.tolist()[start:], 'up': aroonup.tolist()[start:], 'info': []}


def SMA(data):
    start = config.MAGIC_LIMIT
    close = data['close']
    periods = [10, 20 ,50]
    names = ['fast', 'medium','slow']
    dic = {}
    info =[]

    for name, p in zip(names, periods):
        real = talib.SMA(close, p)
        dic[name] = real.tolist()[start:]
        # TOKENS
        if close[-1] > real[-1]:
                info.append('POSITION_UP_{}'.format(name.upper() ) )
        else:
            info.append('POSITION_DOWN_{}'.format(name.upper() ) )

    #TOKENS
    points2check = -10
    for i in range(points2check, 0):
        if dic['fast'][i] < dic['slow'][i] and dic['fast'][i-1] >= dic['slow'][i-1]:
            info.append('CROSS_BEARISH')
        elif dic['fast'][i] > dic['slow'][i] and dic['fast'][i-1] <= dic['slow'][i-1]:
            info.append('CROSS_BULLISH')

        for name in names:
            if close[i] > real[i] and close[i-1] < real[i-1]:
                info.append('CROSS_UP_{}'.format(name.upper()))
            elif close[i] < real[i] and close[i-1] > real[i-1]:
                info.append('CROSS_DOWN_{}'.format(name.upper()))

    dic.update(info = info)
    return dic


def OBV(data):
    start = config.MAGIC_LIMIT
    real = talib.OBV(data['close'], data['volume'])
    return {'obv': real.tolist()[start:], 'info': []}


def EMA(data):
    start = config.MAGIC_LIMIT
    close = data['close']
    periods = [10, 20 ,50]
    names = ['fast', 'medium','slow']
    dic = {}
    info =[]

    for name, p in zip(names, periods):
        real = talib.EMA(close, p)
        dic[name] = real.tolist()[start:]
        # TOKENS
        if close[-1] > real[-1]:
                info.append('POSITION_UP_{}'.format(name.upper() ) )
        else:
            info.append('POSITION_DOWN_{}'.format(name.upper() ) )

    #TOKENS
    points2check = -10
    for i in range(points2check, 0):
        if dic['fast'][i] < dic['slow'][i] and dic['fast'][i-1] >= dic['slow'][i-1]:
            info.append('CROSS_BEARISH')
        elif dic['fast'][i] > dic['slow'][i] and dic['fast'][i-1] <= dic['slow'][i-1]:
            info.append('CROSS_BULLISH')

        for name in names:
            if close[i] > real[i] and close[i-1] < real[i-1]:
                info.append('CROSS_UP_{}'.format(name.upper()))
            elif close[i] < real[i] and close[i-1] > real[i-1]:
                info.append('CROSS_DOWN_{}'.format(name.upper()))

    dic.update(info = info)
    return dic


def SAR(data):
    start = config.MAGIC_LIMIT
    close = data['close']
    real = talib.SAR(data['high'], data['low'], acceleration=0.02, maximum=0.2)

    # TOKENS
    info = []
    points2check = -10
    for i in range(points2check,0):
        if real[i-1] <= close[i-1] and real[i] >= close[i]:
            info.append('DIRECTION_DOWN')
        elif real[i-1] >= close[i-1] and real[i] <= close[i]:
            info.append('DIRECTION_UP')
    
    if info != []:
        info = list(info[-1])
    return {'sar': real.tolist()[start:], 'info': info}


def ALLIGATOR(data):
    start = config.MAGIC_LIMIT
    close = data['close']
    data_len = close.size

    N1, N2, N3 = 13, 8, 5
    jaw = [talib.SUM(close, N1)[N1-1] / N1]
    teeth = [talib.SUM(close, N2)[N2-1] / N2]
    lips = [talib.SUM(close, N3)[N3-1] / N3]

    for i in range(1, data_len):
        jaw.append((jaw[-1] * (N1 - 1) + close[i])/N1)
        teeth.append((teeth[-1] * (N2 - 1) + close[i])/N2)
        lips.append((lips[-1] * (N3 - 1) + close[i])/N3)

    return {'jaw': jaw[start:], 'teeth': teeth[start:], 'lips': lips[start:], 'info': []}

###################   Bitreport indicators   ###################

# Elliott Wave Oscillator:
def EWO(data, fast = 5, slow = 35):
    start = config.MAGIC_LIMIT
    close = data['close']
    real = talib.EMA(close, fast) - talib.EMA(close, slow)
    return {'ewo': real.tolist()[start:], 'info': []}

# Keltner channels:
def KC(data):
    # Keltner Channels
    # Middle Line: 20-day exponential moving average
    # Upper Channel Line: 20-day EMA + (2 x ATR(10))
    # Lower Channel Line: 20-day EMA - (2 x ATR(10))
    start = config.MAGIC_LIMIT
    close = data['close']
    high = data['high']
    low = data['low']

    mid = talib.SMA(close, 20)
    upperch = mid + (2 * talib.ATR(high, low, close, 10))
    lowerch = mid - (2 * talib.ATR(high, low, close, 10))
    
    return {'middle_band': mid.tolist()[start:], 
            'upper_band': upperch.tolist()[start:], 
            'lower_band':lowerch.tolist()[start:], 
            'info': []}

# Tom Demark Sequential
def TDS(data):
    start = config.MAGIC_LIMIT
    close = data['close']
    low = data['low']
    high = data['high']
    n = 4
    #m2, n2 = 13, 2

    # TD Sequential based on TD Setup 9,4
    # https://www.ethz.ch/content/dam/ethz/special-interest/mtec/chair-of-entrepreneurial-risks-dam/documents/dissertation/LISSANDRIN_demark_thesis_final.pdf
    start_point = n
    td_list_type = []
    while start_point < close.size:
        # Check perfect buy:
        if (low[start_point] < low[start_point - 3] and low[start_point] < low[start_point - 2]) or (
                        low[start_point - 1] < low[start_point - 4] and low[start_point - 1] < low[
                        start_point - 3]):
            td_list_type.append('pbuy')

        # Check buy:
        elif close[start_point] < close[start_point - n]:
            td_list_type.append('buy')

        # Check perfect sell
        elif (high[start_point] > high[start_point - 3] and high[start_point] > high[start_point - 2]) or (
                        high[start_point - 1] > high[start_point - 4] and high[start_point - 1] > high[
                        start_point - 3]):
            td_list_type.append('psell')

        # Check sell
        elif close[start_point] > close[start_point - n]:
            td_list_type.append('sell')
        start_point += 1

    td_list_type = [0]*n + td_list_type

    # TOKEN
    info = []
    if 'psell' in td_list_type[-5:]:
        info.append('PERFECT_SELL')
    elif 'pbuy' in td_list_type[-5:]:
        info.append('PERFECT_BUY')

    if td_list_type[-1] in ['sell', 'psell']:
        info.append('LAST_SELL')
    else:
        info.append('LAST_BUY')

    return {'tds':td_list_type[start:], 'info': info}

# Ichimoku Cloud:
def ICM(data):
    start = config.MAGIC_LIMIT
    margin = config.MARGIN
    high, low, close = data['high'], data['low'], data['close']
    close_size = close.size

    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
    n1=9
    #TODO: czy tu ma byc [0] czy [None] ?
    conversion_line = [0]*n1
    for i in range(n1, close_size):
        conversion_line.append((np.max(high[i-n1:i]) + np.min(low[i-n1:i]))/2)
    conversion_line = np.array(conversion_line)

    # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    n2=26
    base_line = [0]*n2
    for i in range(n2, close_size):
         base_line.append((np.max(high[i-n2:i]) + np.min(low[i-n2:i]))/2)

    base_line = np.array(base_line)

    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    leading_spanA = (conversion_line+base_line) /2

    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    n3 = 52
    leading_spanB = [0]*n3
    for i in range(n3, close_size):
        leading_spanB.append((np.max(high[i-n3:i]) + np.min(low[i-n3:i]))/2)

    leading_spanB = np.array(leading_spanB)

    # Some magic
    leading_spanA = leading_spanA[start-n2:]
    leading_spanB = leading_spanB[start-n2:]

    # Tokens
    info = []
    actualA = leading_spanA[-margin]
    actualB = leading_spanB[-margin]
    if actualA >= actualB and close[-1] < actualA:
        if close[-1] < actualB:
            info.append('PIERCED_UP')
        else:
            info.append('IN_CLOUD_UP')

    elif actualB > actualA and close[-1] > actualA:
        if close[-1] > actualB:
            info.append('PIERCED_DOWN')
        else:
            info.append('IN_CLOUD_DOWN')

    width = np.abs(leading_spanA - leading_spanB)
    p1 = np.percentile(width, .80)
    p2 = np.percentile(width, .25)
    if width[-margin] >= p1:
        info.append('WIDE')
    elif width[-margin] <= p2:
        info.append('THIN')

    return {'leading_span_a': leading_spanA.tolist(),
            'leading_span_b': leading_spanB.tolist(),
            'base_line': base_line.tolist()[start:],
            'info': info}
