import talib

def BB(data, start, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0):
    upperband, middleband, lowerband = talib.BBANDS(data['close'], timeperiod, nbdevup, nbdevdn, matype)

    return {'upperband' : upperband.tolist()[start:],
            'middleband':middleband.tolist()[start:],
            'lowerband':lowerband.tolist()[start:]}

def MACD(data, start, fastperiod=12, slowperiod=26, signalperiod=9 ):
    macd, signal, hist = talib.MACD(data['close'], fastperiod, slowperiod, signalperiod)
    #
    # print('data ask macd :', data['close'].size)
    # print(len(data['date'].tolist()[slowperiod+7:]), 'macd', macd.tolist()[slowperiod:])

    # to avoid NaN values skip 7 first values...
    return {'macd' : macd.tolist()[start:],
            'signal':signal.tolist()[start:],
            'hist':hist.tolist()[start:]}

def RSI(data, start, timeperiod=14):
    real = talib.RSI(data['close'], timeperiod)

    # print('data ask rsi:', data['close'].size)
    # print(len(data['date'].tolist()[timeperiod:]), len(real.tolist()[timeperiod:]))

    return {'rsi':real.tolist()[start:]} #,'date': data['date'].tolist()[start:]}

def STOCH(data, start, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0):
    slowk, slowd = talib.STOCH(data['high'], data['low'], data['close'],
                               fastk_period, slowk_period, slowk_matype, slowd_period, slowd_matype)
    return {'slowk': slowk.tolist()[start:], 'slowd': slowd.tolist()[start:]}

def STOCHRSI(data, start, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0):
    fastk, fastd = talib.STOCHRSI(data['close'], timeperiod, fastk_period, fastd_period, fastd_matype)
    return {'fastk': fastk.tolist()[start:], 'fastd': fastd.tolist()[start:]}

def MOM(data, start, timeperiod=10):
    real = talib.MOM(data['close'], timeperiod)
    return {'mom': real.tolist()[start:]}

def ADX(data, start, timeperiod=14):
    real = talib.ADX(data['high'], data['low'], data['close'], timeperiod)
    return {'adx': real.tolist()[start:]}

def AROON(data, start, timeperiod=14):
    aroondown, aroonup = talib.AROON(data['high'], data['low'], timeperiod)
    return {'down': aroondown.tolist()[start:], 'up': aroonup.tolist()[start:]}

def SMA(data, start):

    periods = [10, 20 ,50]
    names = ['fast', 'medium','slow']
    dict = {}

    for i in range(len(periods)):
        real = talib.SMA(data['close'], periods[i])
        dict[names[i]] = real.tolist()[start:]

    return dict

def EMA(data, start):
    periods = [10, 20, 50]
    names = ['fast', 'medium', 'slow']
    dict = {}

    for i in range(len(periods)):
        real = talib.EMA(data['close'], periods[i])
        dict[names[i]] = real.tolist()[start:]

    return dict

def SAR(data, start):
    real = talib.SAR(data['high'], data['low'],acceleration=0.02, maximum=0.2)

    return {'sar': real.tolist()[start:]}

# Elliott Wave Oscillator
def EWO(data, start, fast = 5, slow = 35):
    close = data['close']
    real = talib.EMA(close, fast) - talib.EMA(close, slow)
    return {'ewo': real.tolist()[start:]}

def TDS(data, start, candlesUntilSignal = 9, candlesPastTocompare = 4):
    close = data['close']
    low = data['low']
    high = data['high']