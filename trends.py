import Bitfinex_API as ba
import numpy as np
import talib
import matplotlib.pyplot as plt

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



# dictionary of {[period, limit] : [sub_period, sub_limit]} must be created to determine sub values
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




# Example data  Levels
#pair, period = 'ETPUSD', '1h'
# data = ba.Bitfinex_numpy(pair, period, 60)
# print(data['close'])
# close = data['close']
# rs = Levels(close, 0.06)
# print(rs)

# Example data HLdirectory
# pair, period , limit= 'ETPUSD', '1h', 100
#
# data = ba.Bitfinex_numpy_complet(pair, period, limit,'2017-10-14 16','2017-10-17 13' )
# HL = HLdirection(pair,period, '15m', limit, 4, '2017-10-14 16','2017-10-17 13')
# print(HL)
#
# x=range(0,data['close'].size)
# fig, ax = plt.subplots()
# date, open, high, low, close = data['date'], data['open'], data['high'], data['low'], data['close']
#
# from matplotlib.finance import candlestick2_ohlc
# candlestick2_ohlc(ax, open, high, low, close, width=0.6)
#
# plt.bar(x, HL['direction'])
# plt.show()


