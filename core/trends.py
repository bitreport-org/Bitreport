import Bitfinex_API as ba
import numpy as np
import talib
import matplotlib.pyplot as plt
import statistics

# followingMax finds first maximum in close
# Input: (Bitfinex_numpy['close'], strength) the strength determinates how pointed maximas must be
# Output: [max , max_position_in_close]
# Remarks: strength in <0, 1> as a %
def followingMax(close, strength):
    max = close[0]
    max_pos = 0
    for i in range(0, close.size-1):
        if close[i+1] > (1 + strength) * close[i]:
            max = close[i+1]
            max_pos = i+1
        else:
            break
    return [max, max_pos]

# followingMin finds first minimum in close
# Input: (Bitfinex_numpy['close'], strength) the strength determinates how pointed minimas must be
# Output: [min , min_position_in_close]
# Remarks:strength in <0, 1> as a %
def followingMin(close, strength):
    min = close[0]
    min_pos = 0
    for i in range(0, close.size-1):
        if close[i+1] < (1 - strength) * close[i]:
            min = close[i+1]
            min_pos= i+1
        else:
            break
    return [min, min_pos]

# Levels finds support and resistance [levels, position]
# Input: (Bitfinex_numpy['close'], strength) the strength determinates how pointed extremas must be
# Output: [[var1, var2,... ], [var1_position_in_close, ...], [var1_type,...]]
# Remarks:
#           strength in <0, 1> as a %
#           var_type = 100 -> resistance
#           var_type = -100 -> support
def Levels(close, strength=0.0):
    l =[]
    l_pos = []
    l_type = []
    c=0
    while c < close.size-1:
        check = c
        if close[c+1] > (1 + strength) * close[c]:
            l.append(followingMax(close[c:], 0)[0])
            l_pos.append(c + followingMax(close[c:], 0)[1])
            l_type.append(100)
            c = c + followingMax(close[c:], strength)[1]
            #print('max' , c)

        elif close[c+1] < (1 - strength) *close[c]:
            l.append(followingMin(close[c:], 0)[0])
            l_pos.append(c + followingMin(close[c:], 0)[1])
            l_type.append(-100)
            c = c + followingMin(close[c:], 0)[1]
            #print('min', c)

        if check == c:
            c += 1
            #print('neutral',c)

    return [l, l_pos, l_type]

# Example data  Levels
#pair, period = 'ETPUSD', '1h'
# data = ba.Bitfinex_numpy(pair, period, 60)
# print(data['close'])
# close = data['close']
# rs = Levels(close, 0.06)
# print(rs)

# dictionary of {[period, limit] : [sub_period, sub_limit]} must be created to determine sub values
# Input: ex. 'BTCUSD, '1D', '1h', 24, '2017-10-14 16','2017-10-17 13'
# Outpu: {'date' : HLdirectory_list_date , 'direction': HLdirectory_list_value}
# Remarks: HighLowDirectory calculates difference between high, low  and
# checks which one was first in gven period timeframe
def HLdirection(pair, period, sub_period, limit, multiplier, startDate, endDate):
    data = ba.Bitfinex_numpy_complet(pair, period, limit,startDate,endDate )
    high = data['high'].tolist()
    low = data['low'].tolist()

    sub_limit = limit * multiplier + 30 # +30 for safety, should be fixe after database import
    sub_data = ba.Bitfinex_numpy_complet(pair, sub_period, sub_limit, startDate,endDate )
    sub_high = sub_data['high'].tolist()
    sub_low = sub_data['low'].tolist()

    date = data['date']

    HLdirectory_list_date = []
    HLdirectory_list_value = []
    start = 0
    for i in range(0, date.size):
        print('H: ', date[i], high[i], low[i])
        search_list_high = sub_high[start: start + multiplier-1]
        print('High: ', search_list_high)
        search_list_low = sub_low[start: start + multiplier-1]
        print('Low: ', search_list_low)

        if search_list_high.index(max(search_list_high)) >= search_list_low.index((min(search_list_low))):
            HLdirectory_list_date.append(date[i])
            HLdirectory_list_value.append(high[i]-low[i])
        elif search_list_high.index(max(search_list_high)) < search_list_low.index((min(search_list_low))):
            HLdirectory_list_date.append(date[i])
            HLdirectory_list_value.append(low[i] - high[i])
        start += multiplier

    return {'date' : HLdirectory_list_date , 'direction': HLdirectory_list_value}



# Elliott Wave Oscillator
def elliottWaveOscillator(data, fast = 5, slow = 35):
    close = data['close']
    return talib.EMA(close, fast) - talib.EMA(close, slow)


#Channel

def channel(data, const = 1):
    ewo = elliottWaveOscillator(data).tolist()
    start = ewo[-const]
    minimum = start
    maximum = start

    positive = [] #list of last positive ewo value
    negative = [] # #list of last non-positive ewo value
    for i in ewo:
        if i > 0:
            positive.append(i)
        else:
            negative.append(i)

    if start <= 0:
        positive.reverse()
        maximum = positive[0]
        for i in range(1, len(positive)):
            if maximum < positive[i]:
                maximum = positive[i]

    if start > 0:
        negative.reverse()
        minimum = negative[0]
        for i in range(1, len(negative)):
            if minimum > negative[i]:
                minimum = negative[i]

    close = data['close']
    minindex = ewo.index(minimum)
    maxindex = ewo.index(maximum)

    channel_list = close[min(minindex, maxindex) : max(minindex, maxindex)]

    channel_dev = 0
    if len(channel_list) > 1:
        channel_dev = statistics.stdev(channel_list)

    #check
    print(len(channel_list))
    print(minindex, maxindex)

    return {'min_index': minindex , 'min_value': close[minindex],
            'max_index': maxindex, 'max_value': close[maxindex],
            'dev' : channel_dev} # assumes that ewo values are unique


