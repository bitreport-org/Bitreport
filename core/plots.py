from matplotlib.finance import candlestick2_ohlc
import Bitfinex_API as ba
import trends
import numpy as np
import talib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import elliott


def PlotPair(pair, period, limit, levelStrength = 0.0, savePlot = False):
    data = ba.Bitfinex_numpy(pair, period, limit)
    date, open, high, low, close = data['date'], data['open'], data['high'], data['low'], data['close']

    # CANDELSTICK PLOT

    x=range(0,data['close'].size)
    fig, ax = plt.subplots()
    candlestick2_ohlc(ax, open, high, low, close, width=0.6)

    # LABELS
    labels = [i for i in date]
    # labels[1] = 'Testing'

    ax.set_xticklabels(labels)
    x = range(0, data['close'].size)
    plt.xticks(x, labels, rotation=45)
    plt.xticks(np.arange(0, data['close'].size, 12))


    # CHANNELS
    plt.plot(x, low, 'r', alpha = 0.2)
    plt.plot(x, high, 'r', alpha = 0.2)

    # LEVELS PLOT
    rs = trends.Levels(close, levelStrength)
    for j in range(0, len(rs[1])):
        if rs[2][j] == 100:
            color = 'g'
        else:
            color = 'r'
        plt.plot(x, np.array([rs[0][j] for i in x]), color, alpha = 0.3)

    #TimeSeries Forecast
    # real = talib.TSF(close, timeperiod=8)
    # real_x = range(0,data['close'].size)
    # plt.plot(real_x, real, 'b')

    #LinearRegression
    real_lin = talib.LINEARREG(close, 40)
    lin_x = range(0, data['close'].size)
    plt.plot(lin_x, real_lin, 'b')

    ## MAX, MIN talib
    # rs = talib.MAX(close, 30)
    # for j in range(0, rs.size):
    #     plt.plot(x, np.array([rs[j] for i in x]), 'g', alpha = 0.3)
    #
    # rs = talib.MIN(close, 30)
    # for j in range(0, rs.size):
    #     plt.plot(x, np.array([rs[j] for i in x]), 'r', alpha=0.3)


    # MAIN PLOT
    plot_name = pair+':'+period
    plt.title(plot_name)
    plt.show()

    # SAVING PLOT
    if savePlot == True:
        fig.savefig(plot_name+'.svg', dpi = 200)

#PlotPair(pair, period, 0)


#Plot Waves 1
def plotWaveDaily(pair, index = 0, limit = 200, start = '2017-08', end = '2017-10', period = '12'):
    data = ba.Bitfinex_numpy_complet(pair, period, limit , start , end )
    low = data['low']
    high = data['high']

    month = []

    for i in range(1, low.size):
        if low[i] > low[i-1] and high[i]>high[i-1]:
            month.append(low[i-1])
            month.append(high[i])
        elif low[i] >= low[i-1] and high[i]<=high[i-1]: # often may be not true
            month.append(high[i])
            month.append(low[i-1])
        elif low[i] < low[i-1] and high[i]<high[i-1]:
            month.append(high[i - 1])
            month.append(low[i])
        elif low[i] < low[i-1] and high[i]> high[i-1]:
            month.append(low[i])
            month.append(high[i])

    fragment = month[index:]
    x=range(0, len(fragment))
    fig, ax = plt.subplots()
    plt.plot(x, fragment)
    plot_name = 'Daily chart [High / Low , Low / High] for ' + pair
    plt.title(plot_name)
    plt.show()


#Plot Levels
def PlotLevels(pair, period, limit, levelStrength = 0.0, savePlot = False):
    data = ba.Bitfinex_numpy(pair, period, limit)
    date, open, high, low, close = data['date'].tolist(), data['open'], data['high'], data['low'], data['close']

    # CANDELSTICK PLOT


    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.3)
    fig.set_size_inches(18.5, 10.5)
    candlestick2_ohlc(ax, open, high, low, close, width=0.9,  colorup='#77d879', colordown='#db3f3f')

    # LABELS
    labels = [i[:10] for i in date]
    # labels[1] = 'Testing'

    ax.set_xticklabels(labels)
    x = range(0, data['close'].size)
    plt.xticks(x, labels,  rotation=90)
    #plt.xticks(np.arange(0, data['close'].size, 4))

    # LEVELS PLOT
    rs = trends.Levels(close, levelStrength)
    for j in range(0, len(rs[1])):
        if rs[2][j] == 100:
            color = 'g'
            position = limit
        else:
            color = 'r'
            position = 0
        plt.plot(x, np.array([rs[0][j] for i in x]), color, alpha = 0.3)
        ax.text(position, rs[0][j], rs[0][j], color = color)


    # MAIN PLOT
    plot_name = pair+':'+period
    plt.title(plot_name)
    plt.show()

    # SAVING PLOT
    if savePlot == True:
        fig.savefig(plot_name+'.svg', dpi = 200)


#Plot Channel
def PlotChannel(pair, period, limit, const = -1):
    data = ba.Bitfinex_numpy(pair, period, limit)
    date, open, high, low, close = data['date'], data['open'], data['high'], data['low'], data['close']

    # CANDELSTICK PLOT

    x=range(0,data['close'].size)
    fig, ax = plt.subplots()
    candlestick2_ohlc(ax, open, high, low, close, width=0.6)

    # LABELS
    labels = [i for i in date]
    # labels[1] = 'Testing'

    ax.set_xticklabels(labels)
    x = range(0, data['close'].size)
    plt.xticks(x, labels, rotation=45)
    plt.xticks(np.arange(0, data['close'].size, 12))


    # CHANNELS
    channel_points = trends.channel(data, const)
    dev = channel_points['dev']
    x_channel = [channel_points['min_index'], channel_points['max_index']]
    y1_channel = [channel_points['min_value'] - dev, channel_points['max_value'] - dev]
    y2_channel = [channel_points['min_value'], channel_points['max_value']]
    y3_channel = [channel_points['min_value'] + dev, channel_points['max_value'] + dev]

    plt.plot(x_channel, y1_channel)
    plt.plot(x_channel, y2_channel)
    plt.plot(x_channel, y3_channel)

    # MAIN PLOT
    plot_name = pair+':'+period
    plt.title(plot_name)
    plt.show()



# Example
#data = ba.Bitfinex_numpy('BTCUSD', '1D',60)
PlotChannel('ETPUSD', '3h', 80, 3)
