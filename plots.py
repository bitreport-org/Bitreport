from matplotlib.finance import candlestick2_ohlc
import Bitfinex_API as ba
import trends
import numpy as np
import talib
import matplotlib.pyplot as plt

# Example data
pair, period = 'ETPUSD', '6h'
data = ba.Bitfinex_numpy(pair, period, 60)
date, open, high, low, close = data['date'], data['open'], data['high'], data['low'], data['close']

# CANDELSTICK PLOT

x=range(0,data['close'].size)
fig, ax = plt.subplots()
candlestick2_ohlc(ax, open, high, low, close, width=0.6)

# CHANNELS
plt.plot(x, low, 'r', alpha = 0.2)
plt.plot(x, high, 'r', alpha = 0.2)

# LEVELS PLOT
rs = trends.Levels(close, 0.05)


for j in range(0, len(rs[1])):
    if rs[2][j] == 100:
        color = 'g'
    else:
        color = 'r'
    plt.plot(x, np.array([rs[0][j] for i in x]), color, alpha = 0.3)



# MAIN PLOT
plt.title(pair+' : '+period)
plt.show()