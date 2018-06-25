import numpy as np
import traceback
import os
import talib #pylint: skip-file

from scipy.stats import linregress
from sklearn.externals import joblib
from core.services import internal
from core.ta import indicators, levels, channels

# Data class
class PairData:
    def __init__(self, app, pair, timeframe, limit, untill=None):
        # to post data without NaN values indicators are calculated on period of length: limit + magic_limit
        # returned data has length = limit
        self.magic_limit = 79
        self.margin = 26

        self.pair = pair
        self.timeframe = timeframe
        self.app = app

        if limit <15:
            self.limit=15
        else:
            self.limit = limit

        self.untill = untill
        self.output = dict()

    def prepare(self):
        for maker in [self._makeCandles, self._makeIndicatorsChannels, self._makeLevels, self._makeInfo]:
            status, message = maker()
            if not status:
                return message, 500
        return self.output, 200
    
    def _makeCandles(self):
        # Minimum response is 11 candles:
        if self.limit <11:
            self.limit=11
        
        # Data request
        if isinstance(self.untill, int):
            data = internal.import_numpy_untill(self.pair, self.timeframe, self.limit + self.magic_limit, self.untill)
        else:
            data = internal.import_numpy(self.pair, self.timeframe, self.limit + self.magic_limit)

        if not data:
            self.app.logger.warning('Empty database response {}'.format(self.pair+self.timeframe))
            return False, 'Empty databse response'

        # Add data
        self.data = data

        # Generate timestamps for future
        dates = internal.generate_dates(data, self.timeframe, self.margin)
        self.output.update(dates = dates[self.magic_limit:])

        # Candles
        candles = dict(open = data['open'].tolist()[self.magic_limit:],
                        high = data['high'].tolist()[self.magic_limit:],
                        close =  data['close'].tolist()[self.magic_limit:],
                        low = data['low'].tolist()[self.magic_limit:],
                        volume = data['volume'].tolist()[self.magic_limit:]
                        )
        self.output.update(candles = candles)

        info_price = self._makeInfoPrice()
        price.update(info = info_price)

        volume_values = data['volume'] #np.array
        info_volume = self._makeInfoVolume(volume_values)
        volume = dict(volume = volume_values.tolist()[self.magic_limit:], info = info_volume)

        return True, price, volume
    
    def _makeInfoPrice(self):
        info_price = []
        close = self.data.get('close')[self.magic_limit:]
        open = self.data.get('open')[self.magic_limit:]
        high = self.data.get('high')[self.magic_limit:]
        low = self.data.get('low')[self.magic_limit:]
        check_period = -20

        # # Hihghest /lowest tokens
        # ath = [24, 168, 4*168]
        # ath_names = ['DAY', 'WEEK', 'MONTH']
        # for a, n in zip(ath, ath_names):
        #     points2check = int(a / int(self.timeframe[:-1]))
        #     if points2check < self.limit + self.magic_limit:
        #         if max(price['high'][check_period:])  >= max(price['high'][-points2check:]):
        #             info_price.append('PRICE_HIGHEST_{}'.format(n))
        #         elif max(price['low'][check_period:])  >= max(price['low'][-points2check:]):
        #             info_price.append('PRICE_LOWEST_{}'.format(n))
        
        # Chart tokens
        clf = joblib.load('{}/core/ta/clfs/TrendRecognition_RandomForest_100.pkl'.format(os.getcwd())) 
        try:
            X = close[-100:]
            X = (X - np.min(X))/(np.max(X)-np.min(X))
            chart_type = clf.predict([X])
            info_price.append('CHART_{}'.format(chart_type[-1].upper()))
        except:
            info_price.append('CHART_NONE')
            pass

        # Last moves tokens
        n = int(0.70*close.size) 
        s70 = linregress(np.arange(n), close[-n:]).slope
        s20 = linregress(np.arange(20), close[-20:]).slope
        s5 = linregress(np.arange(5), close[-5:]).slope
        if s5 > s20 > s70 > 0:
            info_price.append('STRONG_UP')
        elif s5 < s20 < s70 < 0:
            info_price.append('STRONG_DOWN')
        elif s70 < 0 and s20 < 0 and s5 > 0:
            info_price.append('SMALL_MOVE_UP')
        elif s70 > 0 and s20 > 0 and s5 < 0:
            info_price.append('SMALL_MOVE_DOWN')
        elif s70 < 0 and s20 > 0 and s5 > 0:
            info_price.append('BIG_MOVE_UP')
        elif s70 > 0 and s20 < 0 and s5 < 0:
            info_price.append('BIG_MOVE_DOWN')
        
        # Candles patterns tokens
        p2check = -10
        hammer = talib.CDLINVERTEDHAMMER(open[p2check:], high[p2check:], low[p2check:], close[p2check:])
        star = talib.CDLSHOOTINGSTAR(open[p2check:], high[p2check:], low[p2check:], close[p2check:])
        if np.sum(hammer) != 0 and np.where(hammer != 0)[0][-1] == 100:
                info_price.append('INVERTED_HAMMER')
        if np.sum(star) != 0 and np.where(hammer != 0)[0][-1] == -100:
                info_price.append('SHOOTING_STAR')

        return info_price

    def _makeInfoVolume(self, volume):
        info_volume = []
        check_period = -10

        # Volume tokens
        threshold = np.percentile(volume, 80)
        if volume[-2] > threshold or volume[-1] > threshold:
            info_volume.append('VOLUME_SPIKE')
        
        slope = linregress(np.arange(volume[check_period:].size), volume[check_period:]).slope
        if slope < 0.0:
            info_volume.append('VOLUME_DIRECTION_DOWN')
        else:
            info_volume.append('VOLUME_DIRECTION_UP')

        return info_volume

    def _makeIndicatorsChannels(self):
        indicators_list = internal.get_function_list(indicators)
        indicators_values = dict()

        for indicator in indicators_list:
            try:
                indicators_values[indicator.__qualname__] = indicator(self.data)
            except:
                self.app.logger.warning('Indicator {}, error: /n {}'.format(indicator, traceback.format_exc()))
                pass

        channels_list = internal.get_function_list(channels)
        for ch in channels_list:
            try:
                indicators_values[ch.__qualname__]= ch(self.data)
            except:
                self.app.logger.warning('Indicator {}, error: /n {}'.format(ch, traceback.format_exc()))
                pass

        self.output.update(indicators = indicators_values)
        return True, 'Indicators and channels created'

    def _makeLevels(self):
        try:
            self.output.update(levels = levels.prepareLevels(self.data))
        except:
            self.app.logger.warning(traceback.format_exc())
            self.output.update(levels = {'support':[], 'resistance':[]})
            pass
        return True, 'Levels created'

    def _makePatterns(self):
        # Short data for patterns
        data = self.output.get('candles', [])
        try:
            self.output.update(patterns = patterns.CheckAllPatterns(data))
        except:
            self.app.logger.warning(traceback.format_exc())
            self.output.update(patterns = [])
            pass

        return True, 'Patterns created'

    def _makeInfo(self):
        info = []
        check_period = -10

        # Volume tokens
        threshold = np.percentile(self.data['volume'], 80)
        if self.data['volume'][-2] > threshold or self.data['volume'][-1] > threshold:
            info.append('VOLUME_SPIKE')
        
        slope, i, r, p, std = stats.linregress(np.arange(self.data['volume'][check_period:].size), self.data['volume'][check_period:])
        if slope < 0.0:
            info.append('VOLUME_DIRECTION_DOWN')
        else:
            info.append('VOLUME_DIRECTION_UP')

        # Price tokens
        ath = [24, 168, 4*168]
        ath_names = ['DAY', 'WEEK', 'MONTH']

        for a, n in zip(ath, ath_names):
            points2check = int(a / int(self.timeframe[:-1]))
            if points2check < self.limit + self.magic_limit:
                if max(self.data['high'][check_period:])  >= max(self.data['high'][-points2check:]):
                    info.append('PRICE_HIGHEST_{}'.format(n))
                elif max(self.data['low'][check_period:])  >= max(self.data['low'][-points2check:]):
                    info.append('PRICE_LOWEST_{}'.format(n))
        
        # Chart info
        clf = joblib.load('{}/core/ta/clfs/TrendRecognition_RandomForest_100.pkl'.format(os.getcwd())) 
        try:
            X = self.data['close'][-100:]
            X = (X - np.min(X))/(np.max(X)-np.min(X))
            chart_type = clf.predict([X])
            info.append('CHART_{}'.format(chart_type[-1].upper()))
        except:
            info.append('CHART_NONE')
            pass
        return indicators_values
