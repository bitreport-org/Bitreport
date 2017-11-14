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

def KC(data,start):
    # Keltner Channels
    # Middle Line: 20-day exponential moving average
    # Upper Channel Line: 20-day EMA + (2 x ATR(10))
    # Lower Channel Line: 20-day EMA - (2 x ATR(10))
    close = data['close']
    high = data['high']
    low = data['low']

    mid = talib.SMA(close, 20)
    upperch = mid + (2 * talib.ATR(high, low, close, 10))
    lowerch = mid - (2 * talib.ATR(high, low, close, 10))
    
    return {'middleband': mid.tolist()[start:], 'upperband': upperch.tolist()[start:], 'lowerband':lowerch.tolist()[start:]}

# Tom Demark Sequential
def TDS(data, start):
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

    return {'tds':td_list_type[start:]}