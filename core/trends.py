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


#Divergence
# #############################################################################################
# pair, period = 'BTCUSD', '1D'
# limit=100
# data = ba.Bitfinex_numpy(pair, period, limit)
# date, open, high, low, close = data['date'], data['open'], data['high'], data['low'], data['close']
#
# indicator = talib.RSI(close)
#
# # indicator_lev = Levels(indicator, 0.1)
# # close_lev = Levels(close, 0.1)
# # #take shorter list
# # if len(indicator_lev[1]) <= len(close_lev[1]):
# #     indexes = indicator_lev[1]
# # else:
# #     indexes = close_lev[1]
# #
# # #make pairs of maximas
# # maxes = []
# # mines = []
# #
# # for i in range(0, len(indexes)):
# #
# #     # check if max at the same point
# #     if indicator_lev[2][i] == close_lev[2][close_lev[1].index(indexes[i])]== 100:
# #         maxes.append( [ indicator_lev[0][i], close_lev[0][close_lev[1].index(indexes[i])], indexes[i] ])
# #
# #     if indicator_lev[2][i] == close_lev[2][close_lev[1].index(indexes[i])]== -100:
# #         mines.append( [ indicator_lev[0][i], close_lev[0][close_lev[1].index(indexes[i])], indexes[i] ])
# #
# # divergence = []
# # for i in range(1, len(maxes)):
# #     if maxes[i][0] < maxes[i-1][0] and maxes[i][1] > maxes[i-1][1]:
# #         #negative divergence
# #         divergence.append([maxes[i][2], '-d'])
# #
# # for i in range(1, len(mines)):
# #     if mines[i][0] > mines[i-1][0] and mines[i][1] < mines[i-1][1]:
# #         #negative divergence
# #         divergence.append([mines[i][2], '+d'])
#
# #############################################################################################
#
#
# close_max = talib.MAXINDEX(close, timeperiod=15)
# indicator_max = talib.MAXINDEX(indicator, timeperiod=25)
#
# close_min = talib.MININDEX(close, timeperiod=15)
# indicator_min = talib.MININDEX(indicator, timeperiod=25)
#
# start_index=0
# for i in indicator_max:
#     if i != 0:
#         start_index=i
#         break
#
# divergence =[]
# for i in range(start_index,limit):
#     if close_max[i] > indicator_max[i]:
#         divergence.append([i,'-d'])
#     if close_min[i] > indicator_min[i]:
#         divergence.append([i,'+d'])
#
#
# print(close_max)
# print(indicator_max)
# print(divergence)
#
#
#
#
# #
# #
# # print(divergence)
# #
# #
# #
# # from matplotlib.finance import candlestick2_ohlc
# #
# # x=range(0,data['close'].size)
# # fig, ax = plt.subplots()
# # #candlestick2_ohlc(ax, open, high, low, close, width=0.6)
# #
# # plt.plot(x, indicator, 'b')
# #
# # plot_name = pair + ':' + period
# # plt.title(plot_name)
# # plt.show()
#
#
# fig, ax1 = plt.subplots()
# t = np.arange(0, close.size, 1)
#
# s1 = close
# ax1.plot(t, s1, 'b')
# ax1.set_xlabel('CLOSE')
#
# # Make the y-axis label, ticks and tick labels match the line color.
# ax1.set_ylabel('exp', color='b')
# ax1.tick_params('y', colors='b')
#
# ax2 = ax1.twinx()
# s2 = indicator
# ax2.plot(t, s2, 'r')
# ax2.set_ylabel('Indicator', color='r')
# ax2.tick_params('y', colors='r')
#
# fig.tight_layout()
# plt.show()


# Elliott Wave Oscillator
def elliottWaveOscillator(data, fast = 5, slow = 35):
    close = data['close']
    return talib.EMA(close, fast) - talib.EMA(close, slow)


#Channel

def channel(data):
    ewo = elliottWaveOscillator(data).tolist()
    start = ewo[-1]
    min = start
    max = start

    positive = [] #list of last positive ewo value
    negative = [] # #list of last non-positive ewo value
    for i in ewo:
        if i > 0:
            positive.append(i)
        else:
            negative.append(i)

    if start <= 0:
        positive.reverse()
        max = positive[0]
        for i in range(1, len(positive)):
            if max < positive[i]:
                max = positive[i]

    if start > 0:
        negative.reverse()
        min = negative[0]
        for i in range(1, len(negative)):
            if min > negative[i]:
                min = negative[i]

    close = data['close']
    min_index = ewo.index(min)
    max_index = ewo.index(max)

    channel_list = close[min_index : max_index]
    channel_dev = statistics.stdev(channel_list)

    return {'min_index': min_index , 'min_value': close[min_index],
            'max_index': max_index, 'max_value': close[max_index],
            'dev' : channel_dev} # assumes that ewo values are unique


