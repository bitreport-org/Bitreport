from core.services import internal
from core.ta import indicators, levels, patterns, channels
import numpy as np
from scipy import stats
import traceback
from sklearn.externals import joblib
import os

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
        # Prepare price
        status, price, volume = self._makePrice()
        if not status:
            message = 'Empty database response {}'.format(self.pair+self.timeframe)
            return message, 500

        # Prepare dates
        dates = internal.generate_dates(self.data['date'], self.timeframe, self.margin)
        self.output.update(dates = dates[self.magic_limit:])

        # Prepare indicators
        indicators_dict = self._makeIndicators()
        indicators_dict.update(price = price)
        indicators_dict.update(volume = volume)
        self.output.update(indicators = indicators_dict)

        return self.output, 200
    
    def _makePrice(self):
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
            return False, dict(), dict()

        # Add data
        self.data = data

        # Candles
        price = dict(open = data['open'].tolist()[self.magic_limit:],
                        high = data['high'].tolist()[self.magic_limit:],
                        close =  data['close'].tolist()[self.magic_limit:],
                        low = data['low'].tolist()[self.magic_limit:],
                        )

        info_price = self._makeInfoPrice(price)
        price.update(info = info_price)

        volume_values = data['volume'] #np.array
        info_volume = self._makeInfoVolume(volume_values)
        volume = dict(volume = volume_values.tolist()[self.magic_limit:], info = info_volume)

        return True, price, volume
    
    def _makeInfoPrice(self, price):
        info_price = []
        check_period = -10

        # Price tokens
        ath = [24, 168, 4*168]
        ath_names = ['DAY', 'WEEK', 'MONTH']

        for a, n in zip(ath, ath_names):
            points2check = int(a / int(self.timeframe[:-1]))
            if points2check < self.limit + self.magic_limit:
                if max(price['high'][check_period:])  >= max(price['high'][-points2check:]):
                    info_price.append('PRICE_HIGHEST_{}'.format(n))
                elif max(price['low'][check_period:])  >= max(price['low'][-points2check:]):
                    info_price.append('PRICE_LOWEST_{}'.format(n))
        
        # Chart info_price
        clf = joblib.load('{}/core/ta/clfs/TrendRecognition_RandomForest_100.pkl'.format(os.getcwd())) 
        try:
            X = price['close'][-100:]
            X = (X - np.min(X))/(np.max(X)-np.min(X))
            chart_type = clf.predict([X])
            info_price.append('CHART_{}'.format(chart_type[-1].upper()))
        except:
            info_price.append('CHART_NONE')
            pass

        return info_price

    def _makeInfoVolume(self, volume):
        info_volume = []
        check_period = -10

        # Volume tokens
        threshold = np.percentile(volume, 80)
        if volume[-2] > threshold or volume[-1] > threshold:
            info_volume.append('VOLUME_SPIKE')
        
        slope, i, r, p, std = stats.linregress(np.arange(volume[check_period:].size), volume[check_period:])
        if slope < 0.0:
            info_volume.append('VOLUME_DIRECTION_DOWN')
        else:
            info_volume.append('VOLUME_DIRECTION_UP')

        return info_volume

    def _makeIndicators(self):
        indicators_values = dict()

        # Indicators 
        indicators_list = internal.get_function_list(indicators)
        for indicator in indicators_list:
            try:
                indicators_values[indicator.__name__] = indicator(self.data)
            except:
                self.app.logger.warning('Indicator {}, error: /n {}'.format(indicator, traceback.format_exc()))
                pass

        # Channels
        channels_list = internal.get_function_list(channels)
        for ch in channels_list:
            try:
                indicators_values[ch.__name__]= ch(self.data)
            except:
                self.app.logger.warning('Indicator {}, error: /n {}'.format(ch, traceback.format_exc()))
                pass

        # Channels
        try:
            indicators_values.update(levels = levels.prepareLevels(self.data))
        except:
            self.app.logger.warning(traceback.format_exc())
            indicators_values.update(levels = {'support':[], 'resistance':[], 'auto': [], 'info':[]})
            pass
        return indicators_values

    # def _makePatterns(self):
    #     # Short data for patterns
    #     data = self.output.get('candles', [])
    #     try:
    #         self.output.update(patterns = patterns.CheckAllPatterns(data))
    #     except:
    #         self.app.logger.warning(traceback.format_exc())
    #         self.output.update(patterns = [])
    #         pass

    #     return True, 'Patterns created'