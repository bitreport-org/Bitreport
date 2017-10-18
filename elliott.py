import Bitfinex_API as ba
import numpy as np
import talib
import matplotlib.pyplot as plt

# To view the EliottWave phenomenon right angle is needed
# When directional movement price makes
# And data travels from bottom left to top right (or vice versa)
# Then it should oscillate around diagonal of a perfect square
#
# Define sqrx as length of this square'side
# Define x as distance between two data points -> x = sqrx / [number of points in suare]
def RuleOfNeutrality(a, b, x=1):

    y = abs(a-b)
    tgv = y/x
    if 0 <  tgv < 1:
        return True

    return False


print(RuleOfNeutrality(0,1/2))