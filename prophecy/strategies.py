import talib
import numpy as np

__all__ = ['TwoMAs', 'SimpleRSI', 'Test']


class BaseStrategy:
    def __init__(self):
        self.info = "Base class for startegies"
        
    def decide(self):
        # Returns decision and last price
        return 'keep', 1000

    
class Test(BaseStrategy):
    def decide(self, data, trader):
        print(data)
        print(trader)
        return 'keep', 1000

    
class TwoMAs(BaseStrategy):
    def __init__(self, window=10, long=90, short=30, ma_type='SMA'):
        self.info = "Two Moving Averages cross over startegy."
        self.long = long
        self.short = short
        
        if window < 2:
            print('Window was changed to minimal value: 2')
        
        self.window = max(window, 2)
        
        assert ma_type in ['SMA', 'EMA'], 'Allowed MA types: SMA, EMA'
        self.MA = getattr(talib, ma_type)
        
    def decide(self, close: np.ndarray, trader):
        msg = 'Input data must at least have size equal t0 long MA + window, expected size {}, got {}'.format(
            self.long+self.window, close.size)
        assert close.size >= self.long + self.window, msg

        
        long_ma = self.MA(close, timeperiod=self.long)
        short_ma = self.MA(close, timeperiod=self.short)
        
        decision = 'keep'
        for i in range(-self.window, -1):
            if long_ma[i] >= short_ma[i] and long_ma[i+1] < short_ma[i+1]:
                decision = 'short'
            elif long_ma[i] <= short_ma[i] and long_ma[i+1] > short_ma[i+1]:
                decision = 'long'
                
        # Returns decision and last price
        return decision, close[-1]
        
        
class SimpleRSI(BaseStrategy):
    def __init__(self, window=5, timeperiod=14, oversold=30, overbought=70):
        """
        window - how many last points should be considered
        timeperiod - RSI timeperiod
        oversold - threshold for RSI oversold
        overbought - threshold for RSI overbought
        """
        self.info = "RSI startegy which buys when oversold and sells when overbought."
        self.timeperiod = timeperiod
        self.oversold = oversold
        self.overbought = overbought
        
        if window < 2:
            print('Window was changed to minimal value: 2')
        self.window = max(window, 2)
        
    def decide(self, close: np.ndarray, trader):
        msg = 'Input data must at least have size equal to timeperiod + window, expected size {}, got {}'.format(
            self.timeperiod+self.window, close.size)
        assert close.size >= self.timeperiod+self.window, msg

        
        rsi = talib.RSI(close, self.timeperiod)
        
        decision = 'keep'
        for r in rsi[-self.window:]:
            if r >= self.overbought:
                decision = 'short'
            elif r <= self.oversold:
                decision = 'long'
                
        # Returns decision and last price
        return decision, close[-1]
    