import datetime
import requests
import csv
import pandas as pd
import numpy as np

# DATA IMPORT AND EXPORT

# Bitfinex API Import List
# Input: (PAIR, period, limit) , ['BTCUSD', '1h', 200]
# Output: list [[DATE, OPEN, CLOSE, HIGH, LOW, VOLUME], ...]
# Remarks: all available periods formats could be find in Bitfinex documentation
# https://bitfinex.readme.io/v2/reference#rest-public-candles
def import_data(pair, period, limit):
    url = 'https://api.bitfinex.com/v2/candles/trade:'+period+':t'+pair+'/hist?limit='+str(limit)+'&start=946684800000'
    candel_list = requests.get(url).json()
    candel_list.reverse()
    # change mts to date
    candel_list = [[datetime.datetime.fromtimestamp(int(time / 1000.0)).strftime('%Y-%m-%d %H:%M:%S'), *rest] for
                   (time, *rest) in candel_list]
    return candel_list



# Bitfinex API Import Data frame
# Input: (PAIR, period, limit) , ('BTCUSD', '1h', 200)
# Output: pandas data frame [[DATE, OPEN, CLOSE, HIGH, LOW, VOLUME], ...]
# Remarks: all available periods formats could be find in Bitfinex documentation
# https://bitfinex.readme.io/v2/reference#rest-public-candles
def Bitfinex_data_frame(pair, period, limit, type=None):
    url = 'https://api.bitfinex.com/v2/candles/trade:'+period+':t'+pair+'/hist?limit='+str(limit)+'&start=946684800000'
    candel_list = requests.get(url).json()
    candel_list.reverse()
    # change mts to date
    candel_list = [[datetime.datetime.fromtimestamp(int(time / 1000.0)).strftime('%Y-%m-%d %H:%M:%S'), *rest] for
                   (time, *rest) in candel_list]
    labels = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume']

    return pd.DataFrame.from_records(candel_list, columns=labels)



# Bitfinex date csv export
# Input: (PAIR, period, limit) , ('BTCUSD', '1h', 200)
# Output: PAIR_period_limit_time.csv
# Remarks: all available periods formats could be find in Bitfinex documentation
# https://bitfinex.readme.io/v2/reference#rest-public-candles
def export_csv(pair, period, limit):
    # pair formats: BTCUSD, NEOBTC
    list = [['DATE', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']]+import_data(pair, period, limit)
    file_name = pair+'_'+period+'_'+ str(limit) +'_'+ datetime.datetime.now().strftime("%Y-%m-%d")
    with open(file_name+".csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(list)

# INDICATORS
# Simple Moving Average
# Input: (length, [[data, open, close, ... ], type='open'/None]
# Output: [[date, SMA_value], ...]
def SMA(length, data, type=2):
    # default type is close positions
    if type == 'open': t = 1
    l = len(data)
    SMA = []
    sum = 0
    for i in range(length, l):
        for j in range(i - length, i):
            sum = sum + data[j][type]
        SMA.append([data[i][0], sum / length])
        sum = 0

    return SMA



# Exponential Moving Average
# Input: (length, [[data, open, close, ... ]]
# Output: [[date, EMA_value], ...]
def EMA(length, data):
    sma = SMA(length, data)
    EMA = [sma[0]]
    m = 2/ (length + 1)
    for i in range(1 , len(sma)):
        EMA.append([sma[i][0], (data[i+length][2]-EMA[i-1][1])*m + EMA[i-1][1]])

    return EMA



# Bollinger Bands List
# Input: (SMA_length, band_width, [[data, open, close, ... ]], type='open'/None)
# Output: [[date, SMA, DownLine, UpLine], ...]
def BB_list(length, width, data, type=2):
    # default type is close positions
    if type=='open': t=1
    l = len(data)
    band=[]
    sum = sum2 = ave = dev = 0
    for i in range(0, length):
        band.append([data[i][0],data[i][1], data[i][1], data[i][1]])

    for i in range(length,l):
        for j in range(i-length,i):
            sum = sum+data[j][type]
            sum2 = sum2+data[j][type]**2
            ave = sum / length
            dev = width * ((sum2 - length * (sum / length) ** 2) / length) ** 0.5
        band.append([data[i][0], ave, ave - dev, ave + dev])
        sum = sum2 = ave = dev = 0

    return band


# Bollinger Bands Data frame
# Input: (SMA_length, band_width, [[data, open, close, ... ]], type='open'/None)
# Output: pandas data frame [[data, SMA, DownLine, UpLine], ...]
def BB(length, width, data, type=2):
    # returns Bolinger Bands (length, width, type), default type is close positions
    # output format: pandas dataframe
    if type == 'open': t = 1
    l = len(data)
    band = []
    sum = sum2 = ave = dev = 0
    labels = ['Date', 'SMA', 'DownLine', 'UpLine']
    for i in range(0, length):
        band.append([data[i][0], data[i][1], data[i][1], data[i][1]])

    for i in range(length, l):
        for j in range(i - length, i):
            sum = sum + data[j][type]
            sum2 = sum2 + data[j][type] ** 2
            ave = sum / length
            dev = width * ((sum2 - length*(sum / length) ** 2) / length) ** 0.5
        band.append([data[i][0], ave, ave - dev, ave + dev])
        sum = sum2 = ave = dev = 0

    return pd.DataFrame.from_records(band, columns=labels)



# MACD list
# Input: (slow_EMA, fast_EMA, signal, [[data, open, close, ... ]])
# Output: [[date, MACD_line, Signal_line, Histogram], ...]
def MACD_list(fast, slow, signal, data):
    Slow_EMA = EMA(slow, 2, data)
    Fast_EMA = EMA(fast, 2, data)
    MACD_line =  []
    list = []

    # MACD line [data, MACD value, MACD value] second argument need to perform EMA
    for i in range(0, len(Fast_EMA)):
        MACD_line.append([Fast_EMA[i][0],
                          Slow_EMA[i+len(Fast_EMA)-len(Slow_EMA)][1] - Fast_EMA[i][1],
                          Slow_EMA[i+len(Fast_EMA)-len(Slow_EMA)][1] - Fast_EMA[i][1]])

    # Signal line
    signal_line = EMA(signal,2,MACD_line)

    # [data, MACD, Signal, hist]
    for i in range(0, len(signal_line)):
        list.append([signal_line[i][0], MACD_line[i+signal][1], signal_line[i][1], MACD_line[i+9][1] -signal_line[i][1]])

    return list


# MACD Data frame
# Input: (slow_EMA, fast_EMA, signal, [[data, open, close, ... ]])
# Output: pandas data frame [[date, MACD_line, Signal_line, Histogram], ...]
def MACD(slow, fast, signal, data):
    Slow_EMA = EMA(slow, data)
    Fast_EMA = EMA(fast, data)
    MACD_line =  []
    list = []

    # MACD line [data, MACD value, MACD value] second argument need to perform EMA
    for i in range(0, len(Slow_EMA)):
        MACD_line.append([Fast_EMA[i][0],
                          Fast_EMA[i + len(Fast_EMA) - len(Slow_EMA)][1] - Slow_EMA[i][1],
                          Fast_EMA[i + len(Fast_EMA) - len(Slow_EMA)][1] - Slow_EMA[i][1]])

    # Signal line
    #print(pd.DataFrame.from_records(MACD_line, columns=['1','2','3']))
    signal_line = EMA(signal, MACD_line)
    #print(pd.DataFrame.from_records(signal_line, columns=['date', 'ema']))
    # [data, MACD, Signal, hist]
    for i in range(0, len(signal_line)):
        list.append([signal_line[i][0], MACD_line[i+signal][1], signal_line[i][1], MACD_line[i+signal][1] -signal_line[i][1]])

    return pd.DataFrame.from_records(list, columns=['Date', 'MACD', 'Signal_line', 'Histogram'])



# Bitfinex API Import numpy data frames
# Input: (PAIR, period, limit) , ('BTCUSD', '1h', 200)
# Output: dict {'date' : date_list,
#               'open' : np.array,
#               'close' : np.array,
#               'high' : np.array,
#               'low' : np.array,
#               'volume' : np.array}
# Remarks: all available periods formats could be find in Bitfinex documentation:
# https://bitfinex.readme.io/v2/reference#rest-public-candles
def Bitfinex_numpy(pair, period, limit):
    url = 'https://api.bitfinex.com/v2/candles/trade:'+period+':t'+pair+'/hist?limit='+str(limit)+'&start=946684800000'
    candel_list = requests.get(url).json()
    candel_list.reverse()

    date_list=[]
    open_list=[]
    close_list=[]
    high_list=[]
    low_list=[]
    volume_list=[]

    for i in range(0, len(candel_list)):
        # change mts to date
        date_list.append(datetime.datetime.fromtimestamp(int(float(candel_list[i][0]) / 1000.0)).strftime('%Y-%m-%d %H:%M:%S'))
        open_list.append(candel_list[i][1])
        close_list.append(candel_list[i][2])
        high_list.append(candel_list[i][3])
        low_list.append(candel_list[i][4])
        volume_list.append(candel_list[i][5])

    candles_dict = {'date' : date_list,
                    'open' : np.array(open_list),
                    'close' : np.array(close_list),
                    'high' : np.array(high_list),
                    'low' : np.array(low_list),
                    'volume' : np.array(volume_list)
                    }


    return candles_dict




