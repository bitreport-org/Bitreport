from __future__ import print_function
import Bitfinex_API as ba
import numpy as np
import matplotlib.pyplot as plt


# Example data
data = ba.Bitfinex_numpy('ETHUSD', '1D', 200)
close = data['close']


# RESISTANCE LEVELS
# Input: (<class 'numpy.ndarray'>, const  = 2)
# Output: <class 'list'>
# Remarks: add dependency on period etc. 1H, 6H; tbd if change output to numpy.array
def ResistanceLevel(close, const = 2):
    import statistics

    # Search for local maxs
    lis = []
    for i in range(0, close.size-21):
        if max(close[i:(i + 7)]) == max(close[i:(i + 21)]):
            lis.append(max(close[i:(i + 7)]))
        if max(close[i:(i + 7)]) == max(close[i:(i + 14)]):
            lis.append(max(close[i:(i + 7)]))
    resistance = np.sort(list(set(lis)))

    # Frequency distribution
    # The const value is additional param for calculating FD number of boxes
    N = int(resistance.size**0.5 * const)
    vmin = resistance[0]
    vmax = resistance[-1]
    len = resistance[-1] - resistance[0]
    h = len / N

    l =[]
    series = []
    for i in range(0 , N):
        for j in resistance:
            # Add values to i-box
            if (vmin + i * h) <= j <= (vmin + (i+ 1) * h):
                l.append(j)
        if l != []:
            #series.update({i:[statistics.mean(l)]})
            series.append(statistics.mean(l))
        l = []

    return series

'''
x=range(0,data['close'].size)

#series = lis
sup_plot0 = np.array([series[0] for i in range(0,data['close'].size)])
sup_plot1 = np.array([series[1] for i in range(0,data['close'].size)])
sup_plot2 = np.array([series[2] for i in range(0,data['close'].size)])
sup_plot3 = np.array([series[3] for i in range(0,data['close'].size)])
sup_plot4 = np.array([series[4] for i in range(0,data['close'].size)])
sup_plot5 = np.array([series[5] for i in range(0,data['close'].size)])
sup_plot6 = np.array([series[6] for i in range(0,data['close'].size)])
#sup_plot7 = np.array([series[7] for i in range(0,data['close'].size)])
#sup_plot8 = np.array([series[7] for i in range(0,data['close'].size)])
#sup_plot9 = np.array([series[7] for i in range(0,data['close'].size)])

plt.plot(x, data['close'], 'r', x, smooth_close, 'b',
        x, sup_plot0, 'g',
        x, sup_plot1, 'g',
        x, sup_plot2, 'g',
        x, sup_plot3, 'g',
        x, sup_plot4, 'g',
        x, sup_plot5, 'g',
        x, sup_plot6, 'g',
  #      x, sup_plot7, 'g',
   #     x, sup_plot8, 'g',
    #    x, sup_plot9, 'g',

         )

plt.show()

'''



