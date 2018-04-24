# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import ast
import time
import datetime
import logging
import traceback
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
def data_service(pair):
    if request.method == 'GET':
        timeframe = request.args.get('timeframe', default='1h', type=str)
        limit = request.args.get('limit', default=10, type=int)
        untill = request.args.get('untill', default=None, type=int)
        app.logger.info('Request for {} {} limit {} untill {}'.format(pair, timeframe, limit, untill))
        tic = time.time()
        ############################### DATA REQUEST #####################################
        output = {}
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
        output['dates'] = dates[magic_limit:]

        output['candles'] = {'open': data['open'].tolist()[magic_limit:],
                             'high': data['high'].tolist()[magic_limit:],
                             'close': data['close'].tolist()[magic_limit:],
                             'low': data['low'].tolist()[magic_limit:],
                             'volume': data['volume'].tolist()[magic_limit:]
                             }
        ################################ INDICATORS ######################################

        indicators_list = internal.get_function_list(indicators)
        indidict = {}
        for indic in indicators_list:
            try:
                indidict[indic] = getattr(indicators, indic)(data)
            except Exception as e:
                app.logger.warning('Indicator {}, error: /n {}'.format(indic, traceback.format_exc()))
                pass

        ################################ CHANNELS #########################################
        # Basic channels
        try:
            indidict['channel'] = channels.channel(data)
        except:
            app.logger.warning(traceback.format_exc())
            pass

        try:
            indidict['parabola'] = channels.parabola(data)
        except:
            app.logger.warning(traceback.format_exc())
            pass

        try:
            indidict['wedge'] = channels.fallingwedge(data)
        except:
            app.logger.warning(traceback.format_exc())
            pass

        try:
            indidict['rwedge'] = channels.raisingwedge(data)
        except:
            app.logger.warning(traceback.format_exc())
            pass

        output['indicators'] = indidict

        ################################ PATTERNS ########################################
        # Short data for patterns
        if isinstance(untill, int):
            pat_data = internal.import_numpy_untill(pair, timeframe, limit + magic_limit, untill)
        else:
            pat_data = internal.import_numpy(pair, timeframe, limit + magic_limit)

        try:
            output['patterns'] = patterns.CheckAllPatterns(pat_data)
        except Exception as e:
            app.logger.warning(traceback.format_exc())
            output['patterns'] = []
            pass

        ################################ LEVELS ##########################################
        try:
            output['levels'] = levels.srlevels(data)
        except Exception as e:
            app.logger.warning(traceback.format_exc())
            output['levels'] = []
            pass

        toc = time.time()
        output['response_time'] = '{0:.2f} ms'.format(1000*(toc - tic))
        return jsonify(output), 200


events_list = []
@app.route('/events', methods=['GET', 'PUT'])
def event_service():
    if request.method == 'PUT':
        events_list.append(ast.literal_eval(request.form['data']))
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        for event in events_list:
            if now - event['time'] > 60 * int(conf.EVENT_LIMIT):
                events_list.pop(events_list.index(event))
    elif request.method == 'GET':
        return jsonify(events_list)


@app.route('/fill', methods=['POST'])
def fill_service():
    pair = request.args.get('pair', type=str)
    last = request.args.get('last',default=None, type=int)
    exchange = internal.check_exchange(pair)
    if exchange != 'None':
        try:
            return dbservice.pair_fill(app, pair, exchange, last)
        except:
            app.logger.warning(traceback.format_exc())
            return 'Request failed', 500
    else:
        return 'Pair not added'


@app.route('/pairs', methods=['GET', 'POST'])
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

        app.logger.info('Pair added: {} | {}'.format(pair, exchange))

        try:
            response = internal.add_pair(pair, exchange)
            return jsonify(response)
        except:
            app.logger.warning(traceback.format_exc())
            return 'Request failed', 500
