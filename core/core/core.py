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
db_name = conf.DBNAME
host = conf.HOST
port = conf.PORT
client = InfluxDBClient(host, port, 'root', 'root', db_name)
client.create_database(db_name)

# Logger
handler = logging.FileHandler('app.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

@app.route("/")
def hello():
    return "Wrong place, is it?"

#### API ####

# to post data without NaN values indicators are calculated on period of length: limit + magic_limit
# returned data has length = limit
magic_limit = conf.MAGIC_LIMIT

@app.route('/<pair>', methods=['GET'])
def data_service(pair: str):
    if request.method == 'GET':
        timeframe = request.args.get('timeframe', default='1h', type=str)
        limit = request.args.get('limit', default=11, type=int)
        untill = request.args.get('untill', default=None, type=int)

        # Minimum response is 11 candles:
        if limit <11:
            limit=11

        app.logger.warning('Request for {} {} limit {} untill {}'.format(pair, timeframe, limit, untill))
        tic = time.time()
        ############################### DATA REQUEST #####################################
        output = dict()

        if isinstance(untill, int):
            data = internal.import_numpy_untill(pair, timeframe, limit + magic_limit, untill)
        else:
            data = internal.import_numpy(pair, timeframe, limit + magic_limit)

        if data == False:
            app.logger.warning('Empty database response {}'.format(pair+timeframe))
            return 'Error', 500

        # SET margin
        margin = 26  # timestamps

        # Generate timestamps for future
        dates = internal.generate_dates(data, timeframe, margin)
        output.update(dates = dates[magic_limit:])

        candles = dict(open = data['open'].tolist()[magic_limit:],
                                high = data['high'].tolist()[magic_limit:],
                                close =  data['close'].tolist()[magic_limit:],
                                low = data['low'].tolist()[magic_limit:],
                                volume = data['volume'].tolist()[magic_limit:]
                             )
        output.update(candles = candles)

        ################################ INDICATORS ######################################

        indicators_list = internal.get_function_list(indicators)
        indicators_dict = dict()

        for ind in indicators_list:
            try:
                indicators_dict[ind.__qualname__] = ind(data)
            except Exception as e:
                app.logger.warning('Indicator {}, error: /n {}'.format(ind, traceback.format_exc()))
                pass

        ################################ CHANNELS #########################################
        # Basic channels

        channels_list = internal.get_function_list(channels)
        for ch in channels_list:
            try:
                indicators_dict[ch.__qualname__]= ch(data)
            except Exception as e:
                app.logger.warning('Indicator {}, error: /n {}'.format(ch, traceback.format_exc()))
                pass

        output.update(indicators = indicators_dict)

        ################################ PATTERNS ########################################
        output.update(patterns = [])
        # # Short data for patterns
        # if isinstance(untill, int):
        #     pat_data = internal.import_numpy_untill(pair, timeframe, limit + magic_limit, untill)
        # else:
        #     pat_data = internal.import_numpy(pair, timeframe, limit + magic_limit)

        # try:
        #     output['patterns'] = patterns.CheckAllPatterns(pat_data)
        # except Exception as e:
        #     app.logger.warning(traceback.format_exc())
        #     output['patterns'] = []
        #     pass

        ################################ LEVELS ##########################################
        try:
            output.update(levels = levels.prepareLevels(data))
        except Exception as e:
            app.logger.warning(traceback.format_exc())
            output.update(levels=[])
            pass

        ################################ INFO ##########################################
        info = {}

        # Volume tokens
        price_info = []
        threshold = np.percentile(data['volume'], 80)
        if data['volume'][-2] > threshold or data['volume'][-1] > threshold:
            price_info.append('VOLUME_SPIKE')
        
        slope, i, r, p, std = stats.linregress(np.arange(data['volume'][-10:].size), data['volume'][-10:])
        if slope < 0.0:
            price_info.append('DIRECTION_DOWN')
        else:
            price_info.append('DIRECTION_UP')

        # Price tokens
        info['price'] = []
        ath = [24, 168, 4*168]
        ath_names = ['DAY', 'WEEK', 'MONTH']

        for a, n in zip(ath, ath_names):
            points2check = int(a / int(timeframe[:-1]))
            if points2check < limit + magic_limit:
                if max(data['high'][-15:])  >= max(data['high'][-points2check:]):
                    info['price'].append('ATH_{}'.format(n))
                elif max(data['low'][-15:])  >= max(data['low'][-points2check:]):
                    info['price'].append('ATL_{}'.format(n))


        output.update(info = price_info)

        toc = time.time()
        response_time = '{0:.2f} ms'.format(1000*(toc - tic))
        output.update(response_time = response_time)
        return jsonify(output), 200


events_list = []
@app.route('/events', methods=['GET'])
def event_service():
    if request.method == 'GET':
        return jsonify(events_list)


@app.route('/fill', methods=['POST'])
def fill_service():
    pair = request.args.get('pair',default=None, type=str)
    last = request.args.get('last',default=None, type=int)
    if pair != None:
        exchange = internal.check_exchange(pair)
        if exchange != None:
            try:
                return dbservice.pair_fill(app, pair, exchange)
            except:
                app.logger.warning(traceback.format_exc())
                return 'Request failed', 500
        else:
            return 'Pair not added', 400
    else:
        return 'Pair not provided', 400


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

