# -*- coding: utf-8 -*-
import talib  # pylint: skip-file
import numpy as np

from scipy import stats

from app.ta.helpers import indicator, nan_to_null


@indicator('BB', ['upper_band', 'middle_band', 'lower_band'])
def BB(data, limit, timeperiod=20):
    m = 1000000
    close = m * data['close']
    upperband, middleband, lowerband = talib.BBANDS(close, timeperiod, 2, 2, matype=0)

    # TOKENS
    info = []
    band_position = (close - lowerband) / (upperband - lowerband)
    p = band_position[-1]

    if p > 1:
        info.append('PRICE_BREAK_UP')
    elif p < 0:
        info.append('PRICE_BREAK_DOWN')
    elif p > 0.95:
        info.append('PRICE_ONBAND_UP')
    elif p < 0.05:
        info.append('PRICE_ONBAND_DOWN')
    elif 0.40 <= p <= 0.60:
        info.append('PRICE_BETWEEN')

    # Check Squeeze
    width = upperband - lowerband
    period = 20
    width = width[-period:]
    x = np.arange(width.size)
    slope = np.polyfit(x, width, 1)[0]

    if width[-1] / width[0] < 0.8 and slope < 0:
        info.append('BANDS_SQUEEZE')

    upperband = upperband / m
    middleband = middleband / m
    lowerband = lowerband / m

    return {'upper_band': nan_to_null(upperband.tolist()[-limit:]),
            'middle_band': nan_to_null(middleband.tolist()[-limit:]),
            'lower_band': nan_to_null(lowerband.tolist()[-limit:]),
            'info': info}


@indicator('MACD', ['macd', 'signal', 'histogram'])
def MACD(data, limit, fastperiod=12, slowperiod=26, signalperiod=9):
    macd, signal, hist = talib.MACD(data['close'], fastperiod, slowperiod, signalperiod)
    return {'macd': nan_to_null(macd.tolist()[-limit:]),
            'signal': nan_to_null(signal.tolist()[-limit:]),
            'histogram': nan_to_null(hist.tolist()[-limit:]),
            'info': []}


@indicator('RSI', ['rsi'])
def RSI(data, limit, timeperiod=14):
    close = data['close']
    m = 10000000
    real = talib.RSI(m * close, timeperiod)

    # TOKENS
    info = []
    if real[-1] >= 70:
        info.append('OSCILLATOR_OVERBOUGHT')
    elif real[-1] <= 30:
        info.append('OSCILLATOR_OVERSOLD')

    n = int(0.20 * limit)
    dir_rsi = stats.linregress(np.arange(n), real[-n:]).slope
    dir_price = stats.linregress(np.arange(n), close[-n:]).slope
    if dir_rsi * dir_price >= 0.01:
        info.append('DIV_POSITIVE')
    elif dir_rsi * dir_price < -0.01:
        info.append('DIV_NEGATIVE')

    return {'rsi': nan_to_null(real.tolist()[-limit:]), 'info': info}


@indicator('STOCH', ['k', 'd'])
def STOCH(data, limit, fastk_period=14, slowk_period=14, slowk_matype=3, slowd_period=14, slowd_matype=3):
    slowk, slowd = talib.STOCH(data['high'], data['low'], data['close'],
                               fastk_period, slowk_period, slowk_matype, slowd_period, slowd_matype)

    # TOKENS
    info = []
    if slowk[-1] >= 80:
        info.append('OSCILLATOR_OVERBOUGHT')
    elif slowk[-1] <= 20:
        info.append('OSCILLATOR_OVERSOLD')

    return {'k': nan_to_null(slowk.tolist()[-limit:]),
            'd': nan_to_null(slowd.tolist()[-limit:]), 'info': info}


@indicator('STOCHRSI', ['k', 'd'])
def STOCHRSI(data, limit, timeperiod=14, fastk_period=14, fastd_period=14, fastd_matype=3):
    m = 10000000
    fastk, fastd = talib.STOCHRSI(m * data['close'], timeperiod, fastk_period, fastd_period, fastd_matype)
    return {'k': nan_to_null(fastk.tolist()[-limit:]),
            'd': nan_to_null(fastd.tolist()[-limit:]), 'info': []}


@indicator('MOM', ['mom'])
def MOM(data, limit, timeperiod=10):
    real = talib.MOM(data['close'], timeperiod)
    return {'mom': nan_to_null(real.tolist()[-limit:]), 'info': []}


@indicator('SMA', ['fast', 'medium', 'slow'])
def SMA(data, limit):
    close = data['close']
    periods = [10, 20, 50]
    names = ['fast', 'medium', 'slow']
    dic = {}
    info = []

    for name, p in zip(names, periods):
        real = talib.SMA(close, p)
        dic[name] = nan_to_null(real.tolist()[-limit:])
        # TOKENS
        if close[-1] > real[-1]:
            info.append('POSITION_UP_{}'.format(name.upper()))
        else:
            info.append('POSITION_DOWN_{}'.format(name.upper()))

    # TOKENS
    points2check = -10
    for i in range(points2check, 0):
        if dic['fast'][i] < dic['slow'][i] and dic['fast'][i - 1] >= dic['slow'][i - 1]:
            info.append('CROSS_BEARISH')
        elif dic['fast'][i] > dic['slow'][i] and dic['fast'][i - 1] <= dic['slow'][i - 1]:
            info.append('CROSS_BULLISH')

        for name in names:
            if close[i] > real[i] and close[i - 1] < real[i - 1]:
                info.append('CROSS_UP_{}'.format(name.upper()))
            elif close[i] < real[i] and close[i - 1] > real[i - 1]:
                info.append('CROSS_DOWN_{}'.format(name.upper()))

    dic.update(info=info)
    return dic


@indicator('OBV', ['obv'])
def OBV(data, limit):
    real = talib.OBV(data['close'], data['volume'])
    return {'obv': nan_to_null(real.tolist()[-limit:]), 'info': []}


@indicator('EMA', ['fast', 'medium', 'slow'])
def EMA(data, limit):
    close = data['close']
    periods = [10, 20, 50]
    names = ['fast', 'medium', 'slow']
    dic = {}
    info = []

    for name, p in zip(names, periods):
        real = talib.EMA(close, p)
        dic[name] = nan_to_null(real.tolist()[-limit:])
        # TOKENS
        if close[-1] > real[-1]:
            info.append('POSITION_UP_{}'.format(name.upper()))
        else:
            info.append('POSITION_DOWN_{}'.format(name.upper()))

    # TOKENS
    points2check = -10
    for i in range(points2check, 0):
        if dic['fast'][i] < dic['slow'][i] and dic['fast'][i - 1] >= dic['slow'][i - 1]:
            info.append('CROSS_BEARISH')
        elif dic['fast'][i] > dic['slow'][i] and dic['fast'][i - 1] <= dic['slow'][i - 1]:
            info.append('CROSS_BULLISH')

        for name in names:
            if close[i] > real[i] and close[i - 1] < real[i - 1]:
                info.append('CROSS_UP_{}'.format(name.upper()))
            elif close[i] < real[i] and close[i - 1] > real[i - 1]:
                info.append('CROSS_DOWN_{}'.format(name.upper()))

    dic.update(info=info)
    return dic
