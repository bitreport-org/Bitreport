# -*- coding: utf-8 -*-
import talib
import numpy as np
from decimal import Decimal as dec
import datetime
import math
#from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
import os

import config
config = config.BaseConfig()


###################     TAlib indicators    ###################
def BB(data, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0):
    start = config.MAGIC_LIMIT
    m = 10000
    close = m * data['close']
    upperband, middleband, lowerband = talib.BBANDS(close, timeperiod, nbdevup, nbdevdn, matype)
    
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
    else:
        info.append('PRICE_BETWEEN')

    width = upperband - lowerband
    test_data = width[-15:] / np.max(width[-15:])
    squeeze = joblib.load('{}/core/ta/clfs/squeeze01CLF15.pkl'.format(os.getcwd())) 
    if squeeze.predict([test_data])[0] == 1:
        info.append('BANDS_SQUEEZE')

    upperband = upperband/m
    middleband = middleband/m
    lowerband = lowerband/m

    return {'upperband' : upperband.tolist()[start:],
            'middleband':middleband.tolist()[start:],
            'lowerband':lowerband.tolist()[start:],
            'info': info}


def MACD(data, fastperiod=12, slowperiod=26, signalperiod=9 ):
    start = config.MAGIC_LIMIT
    macd, signal, hist = talib.MACD(data['close'], fastperiod, slowperiod, signalperiod)
    return {'macd' : macd.tolist()[start:],
            'signal':signal.tolist()[start:],
            'hist':hist.tolist()[start:]}


def RSI(data, timeperiod=14):
    start = config.MAGIC_LIMIT
    close = data['close']
    real = talib.RSI(close, timeperiod)

    info = []
    if real[-1] >= 70:
        info.append('OSCILLATOR_OVERBOUGHT')
    elif real[-1] <= 30:
        info.append('OSCILLATOR_OVERSOLD')

    delta = 5
    direction = real[-1] - real[-1 - delta]
    if direction < 0:
        info.append('DIRECTION_FALLING')
    else:
        info.append('DIRECTION_RISING')

    div = np.corrcoef(close[-26:], real[-26:])[0][1]

    if div >0.9:
        info.append('DIV_POSITIVE')
    elif div < 0.87:
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

    return {'slowk': slowk.tolist()[start:], 'slowd': slowd.tolist()[start:], 'info': info}


def STOCHRSI(data, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0):
    start = config.MAGIC_LIMIT
    fastk, fastd = talib.STOCHRSI(data['close'], timeperiod, fastk_period, fastd_period, fastd_matype)
    return {'fastk': fastk.tolist()[start:], 'fastd': fastd.tolist()[start:]}


def MOM(data, timeperiod=10):
    start = config.MAGIC_LIMIT
    real = talib.MOM(data['close'], timeperiod)
    return {'mom': real.tolist()[start:]}


def ADX(data, timeperiod=14):
    start = config.MAGIC_LIMIT
    real = talib.ADX(data['high'], data['low'], data['close'], timeperiod)
    return {'adx': real.tolist()[start:]}


def AROON(data, timeperiod=14):
    start = config.MAGIC_LIMIT
    aroondown, aroonup = talib.AROON(data['high'], data['low'], timeperiod)
    return {'down': aroondown.tolist()[start:], 'up': aroonup.tolist()[start:]}


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
    for i in range(-10, 0):
        if dic['fast'][i] < dic['slow'][i] and dic['fast'][i-1] >= dic['slow'][i-1]:
            info.append('CROSS_BEARISH')
        elif dic['fast'][i] > dic['slow'][i] and dic['fast'][i-1] <= dic['slow'][i-1]:
            info.append('CROSS_BULLISH')

        for name in names:
            if close[i] > real[i] and close[i-1] < real[i-1]:
                info.append('CROSS_UP_{}'.format(name.upper()))
            elif close[i] < real[i] and close[i-1] > real[i-1]:
                info.append('CROSS_DOWN_{}'.format(name.upper()))

    dic['info'] = info
    return dic


def OBV(data):
    start = config.MAGIC_LIMIT
    real = talib.OBV(data['close'], data['volume'])
    return {'obv': real.tolist()[start:]}


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
    for i in range(-10, 0):
        if dic['fast'][i] < dic['slow'][i] and dic['fast'][i-1] >= dic['slow'][i-1]:
            info.append('CROSS_BEARISH')
        elif dic['fast'][i] > dic['slow'][i] and dic['fast'][i-1] <= dic['slow'][i-1]:
            info.append('CROSS_BULLISH')

        for name in names:
            if close[i] > real[i] and close[i-1] < real[i-1]:
                info.append('CROSS_UP_{}'.format(name.upper()))
            elif close[i] < real[i] and close[i-1] > real[i-1]:
                info.append('CROSS_DOWN_{}'.format(name.upper()))

    dic['info'] = info
    return dic


def SAR(data):
    start = config.MAGIC_LIMIT
    close = data['close']
    real = talib.SAR(data['high'], data['low'], acceleration=0.02, maximum=0.2)

    # TOKENS
    info = []
    for i in range(-10,0):
        if real[i-1] <= close[i-1] and real[i] >= close[i]:
            info.append('DIRECTION_DOWN')
        elif real[i-1] >= close[i-1] and real[i] <= close[i]:
            info.append('DIRECTION_UP')

    return {'sar': real.tolist()[start:], 'info': info}


def ALLIGATOR(data):
    start = config.MAGIC_LIMIT
    close = data['close']
    data_len = close.size
    output = {}

    N1, N2, N3 = 13, 8, 5
    jaw = [talib.SUM(close, N1)[N1-1] / N1]
    teeth = [talib.SUM(close, N2)[N2-1] / N2]
    lips = [talib.SUM(close, N3)[N3-1] / N3]

    for i in range(1, data_len):
        jaw.append((jaw[-1] * (N1 - 1) + close[i])/N1)
        teeth.append((teeth[-1] * (N2 - 1) + close[i])/N2)
        lips.append((lips[-1] * (N3 - 1) + close[i])/N3)

    return {'jaw': jaw[start:], 'teeth': teeth[start:], 'lips': lips[start:]}


###################   Bitreport indicators   ###################

# Elliott Wave Oscillator:
def EWO(data, fast = 5, slow = 35):
    start = config.MAGIC_LIMIT
    close = data['close']
    real = talib.EMA(close, fast) - talib.EMA(close, slow)
    return {'ewo': real.tolist()[start:]}


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
    
    return {'middleband': mid.tolist()[start:], 'upperband': upperch.tolist()[start:], 'lowerband':lowerch.tolist()[start:]}


# Tom Demark Sequential
def TDS(data):
    start = config.MAGIC_LIMIT
    close = data['close']
    low = data['low']
    high = data['high']
    m, n = 9, 4
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
    open, high, low, close=data['open'], data['high'], data['low'], data['close']
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

    return {'conversion line': [],
            'base line': [],
            'leading span A': leading_spanA.tolist()[start-n2:],
            'leading span B': leading_spanB[start-n2:],
            'lagging span': []}

# Ichimoku Cloud FULL:
def ICMF(data):
    start = config.MAGIC_LIMIT
    open, high, low, close=data['open'], data['high'], data['low'], data['close']
    close_size = close.size

    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
    n1=9
    #TODO: czy tu ma być [0] czy [None] ?
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

    # Chikou Span (Lagging Span): Close plotted 26 days in the past
    n4 = 26
    lagging_span =[]
    for i in range(0, close_size-n4):
        lagging_span.append(close[i+n4])
    lagging_span = np.array(lagging_span)


    return {'conversion line': conversion_line.tolist()[start:],
            'base line': base_line.tolist()[start:],
            'leading span A': leading_spanA.tolist()[start-n2:],
            'leading span B': leading_spanB.tolist()[start-n2:],
            'lagging span': lagging_span.tolist()[start:]}


# # Correlation Oscillator
# def CORRO(data, oscillator='RSI', period=25):
#     start = config.MAGIC_LIMIT
#     close = data['close']

#     oscillator_values = getattr(talib, oscillator)(close)
#     corr_list= [0]*period

#     for i in range(period, close.size):
#         corr_list.append(np.corrcoef(close[i-period:i], oscillator_values[i-period:i])[0][1])

#     return {'corro': corr_list[start:]}

# Phase indicator
# def position(now=None):
#    if now is None:
#       now = datetime.datetime.now()

#    diff = now - datetime.datetime(2001, 1, 1)
#    days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
#    lunations = dec("0.20439731") + (days * dec("0.03386319269"))

#    return lunations % dec(1)

# def phase(pos):
#    index = (pos * dec(8)) + dec("0.5")
#    index = math.floor(index)
#    return {
#       0: "🌑",
#       1: "🌒",
#       2: "🌓",
#       3: "🌔",
#       4: "🌕",
#       5: "🌖",
#       6: "🌗",
#       7: "🌘"
#    }[int(index) & 7]

# def what_phase(timestamp):
#    t = datetime.datetime.fromtimestamp(int(timestamp))
#    pos = position(t)
#    phasename = phase(pos)

#    roundedpos = round(float(pos), 3)
#    return (phasename, roundedpos)

# def MOON(data):
#     start = config.MAGIC_LIMIT
#     dates = data['date']
#     phase_list = []

#     for moment in dates:
#         p = what_phase(moment)
#         phase_list.append(p[0])

#     return {'labels': phase_list[start:], 'timestamps': dates[start:]}
