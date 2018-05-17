# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import ast
import time
import datetime
import logging
import traceback
import numpy as np
from scipy import stats
from influxdb import InfluxDBClient

# Internal import
from core.services import internal
from core.services import dbservice
from core.ta import indicators, levels, patterns, channels
import config

app = Flask(__name__)

# Config
conf = config.BaseConfig()
client = InfluxDBClient(conf.HOST, conf.PORT, 'root', 'root', conf.DBNAME)
client.create_database(conf.DBNAME)

# Logger
handler = logging.FileHandler('app.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Data class
class PairData:
    def __init__(self, app, pair, timeframe, limit, untill=None):
        # to post data without NaN values indicators are calculated on period of length: limit + magic_limit
        # returned data has length = limit
        self.magic_limit = 79
        self.margin = 26

        self.pair = pair
        self.timeframe = timeframe

        if limit <15:
            self.limit=15
        else:
            self.limit = limit

        self.untill = untill
        self.output = dict()

    def prepare(self):
        for maker in [self._makeCandles, self._makeIndicatorsChannels, self._makeLevels, self._makeInfo]:
            status, message = maker(app)
            if not status:
                return message, 500
        return self.output, 200
    
    def _makeCandles(self, app):
        # Minimum response is 11 candles:
        if self.limit <11:
            self.limit=11
        
        # Data request
        if isinstance(self.untill, int):
            data = internal.import_numpy_untill(self.pair, self.timeframe, self.limit + self.magic_limit, self.untill)
        else:
            data = internal.import_numpy(self.pair, self.timeframe, self.limit + self.magic_limit)

        if not data:
            app.logger.warning('Empty database response {}'.format(self.pair+self.timeframe))
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

        return True, 'Candles and dates created'

    def _makeIndicatorsChannels(self, app):
        indicators_list = internal.get_function_list(indicators)
        indicators_values = dict()

        for indicator in indicators_list:
            try:
                indicators_values[indicator.__qualname__] = indicator(self.data)
            except Exception as e:
                app.logger.warning('Indicator {}, error: /n {}'.format(indicator, traceback.format_exc()))
                pass

        channels_list = internal.get_function_list(channels)
        for ch in channels_list:
            try:
                indicators_values[ch.__qualname__]= ch(self.data)
            except Exception as e:
                app.logger.warning('Indicator {}, error: /n {}'.format(ch, traceback.format_exc()))
                pass

        self.output.update(indicators = indicators_values)
        return True, 'Indicators and channels created'

    def _makeLevels(self, app):
        try:
            self.output.update(levels = levels.prepareLevels(self.data))
        except Exception as e:
            app.logger.warning(traceback.format_exc())
            self.output.update(levels = {'support':[], 'resistance':[]})
            pass
        return True, 'Levels created'

    def _makePatterns(self, app):
        # Short data for patterns
        data = self.output.get(candles, [])

        try:
            self.output.update(patterns = patterns.CheckAllPatterns(data))
        except Exception as e:
            app.logger.warning(traceback.format_exc())
            self.output.update(patterns = [])
            pass

        return True, 'Patterns created'

    def _makeInfo(self, app):
        info = dict()
        check_period = -10

        # Volume tokens
        volume_info = []
        threshold = np.percentile(self.data['volume'], 80)
        if self.data['volume'][-2] > threshold or self.data['volume'][-1] > threshold:
            volume_info.append('VOLUME_SPIKE')
        
        slope, i, r, p, std = stats.linregress(np.arange(self.data['volume'][check_period:].size), self.data['volume'][check_period:])
        if slope < 0.0:
            volume_info.append('DIRECTION_DOWN')
        else:
            volume_info.append('DIRECTION_UP')

        info.update(volume = volume_info)

        # Price tokens
        price_info = []
        ath = [24, 168, 4*168]
        ath_names = ['DAY', 'WEEK', 'MONTH']

        for a, n in zip(ath, ath_names):
            points2check = int(a / int(self.timeframe[:-1]))
            if points2check < self.limit + self.magic_limit:
                if max(self.data['high'][check_period:])  >= max(self.data['high'][-points2check:]):
                    price_info.append('ATH_{}'.format(n))
                elif max(self.data['low'][check_period:])  >= max(self.data['low'][-points2check:]):
                    price_info.append('ATL_{}'.format(n))

        info.update(price =price_info)

        # Update output info
        self.output.update(info = info)
        return True, 'Info created'

# API

@app.route('/<pair>', methods=['GET'])
def data_service(pair: str):
    if request.method == 'GET':
        timeframe = request.args.get('timeframe', default='1h', type=str)
        limit = request.args.get('limit', default=15, type=int)
        untill = request.args.get('untill', default=None, type=int)

        app.logger.warning('Request for {} {} limit {} untill {}'.format(pair, timeframe, limit, untill))

        data = PairData(app, pair, timeframe, limit, untill)
        output, code = data.prepare()

        return jsonify(output), code
    else:
        return 404


events_list = []
@app.route('/events', methods=['GET'])
def event_service():
    if request.method == 'GET':
        return jsonify(events_list)
    else:
        return 404


@app.route('/fill', methods=['POST'])
def fill_service():
    if request.method == 'POST':
        pair = request.args.get('pair',default=None, type=str)
        if pair is not None:
            exchange = internal.check_exchange(pair)
            if exchange is not None:
                try:
                    return dbservice.pair_fill(app, pair, exchange)
                except:
                    app.logger.warning(traceback.format_exc())
                    return 'Request failed', 500
            else:
                return 'Pair not added', 500
        else:
            return 'Pair not provided', 500
    else:
        return 404


@app.route('/pairs', methods=['GET', 'POST', 'VIEW'])
def pair_service():
    if request.method == 'GET':
        try:
            pairs_list = internal.show_pairs()
            return jsonify(pairs_list)
        except:
            return 'Shit!', 500

    elif request.method == 'POST':
        exchange = request.args.get('exchange', type=str)
        pair = request.args.get('pair', type=str)

        try:
            response = internal.add_pair(pair, exchange)
            app.logger.info('Pair added: {} | {}'.format(pair, exchange))
            return jsonify(response)
        except:
            app.logger.warning(traceback.format_exc())
            return 'Request failed', 500

    elif request.method == 'VIEW':
        action = request.args.get('action',default='view', type=str)
        if action == 'view':
            return jsonify(internal.show_pairs_exchanges())
    else:
        return 404



@app.route('/log', methods=['GET'])
def log_service():
    if request.method == 'GET':
        try:
            with open('app.log') as log:
                text = dict()
                for i, line in enumerate(log):
                    text[i] = line
            return jsonify(text)
        except:
            return 'No logfile', 500


@app.route("/")
def hello():
    return "Wrong place, is it?"
