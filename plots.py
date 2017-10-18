from matplotlib.finance import candlestick2_ohlc
import Bitfinex_API as ba
import trends
import numpy as np
import talib
import matplotlib.pyplot as plt



# Example data
pair, period = 'BTCUSD', '3h'



def PlotPair(pair, period, levelStrength = 0.0, savePlot = False):
    data = ba.Bitfinex_numpy(pair, period, 100)
    date, open, high, low, close = data['date'], data['open'], data['high'], data['low'], data['close']

    # CANDELSTICK PLOT

    x=range(0,data['close'].size)
    fig, ax = plt.subplots()
    candlestick2_ohlc(ax, open, high, low, close, width=0.6)

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
    real = talib.TSF(close, timeperiod=8)
    real_x = range(0,data['close'].size)
    plt.plot(real_x, real, 'b')

    #LinearRegression
    real_lin = talib.LINEARREG(close, 24)
    lin_x = range(0, data['close'].size)
    plt.plot(lin_x, real_lin, 'b')

    # MAIN PLOT
    plot_name = pair+':'+period
    plt.title(plot_name)
    plt.show()

    # SAVING PLOT
    if savePlot == True:
        fig.savefig(plot_name+'.svg')

PlotPair(pair, period,0)