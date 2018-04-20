# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import ast
import time
import datetime
import logging
import traceback
from influxdb import InfluxDBClient

# Internal import
from services import internal, dbservice
from ta import indicators, levels, patterns, channels
import config

app = Flask(__name__)
api = Api(app)

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
# next posted data has length = limit
magic_limit = conf.MAGIC_LIMIT


class All(Resource):
    def get(self, pair, timeframe):
        tic = time.time()
        ################################## PARSER #######################################
        parser = reqparse.RequestParser()

        parser.add_argument('limit', type=int, help='Limit must be int')
        parser.add_argument('untill', type=int, help='Limit must be int')
        args = parser.parse_args()

        limit = args.get('limit')
        untill = args.get('untill')
        ############################### DATA REQUEST #####################################

        output = {}

        #TODO request data always with untill parameter
        if isinstance(untill, int):
            data = internal.import_numpy_untill(pair, timeframe, limit + magic_limit, untill)
        else:
            data = internal.import_numpy(pair, timeframe, limit + magic_limit)

        if data == False:
            return 'Error', 500

        # SET margin
        margin = 26  #timestamps

        # Generate timestamps for future
        dates = internal.generate_dates(data, timeframe, margin)
        output['dates'] = dates[magic_limit:]

        output['candles'] = { 'open': data['open'].tolist()[magic_limit:],
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
                indidict[indic] = getattr(indicators, indic)(data, start=magic_limit)
            except Exception as e:
                app.logger.warning(indic)
                app.logger.warning(traceback.format_exc())
                pass

        ################################ CHANNELS #########################################
        #TODO after channels implementation in Dashboard it must be adjusted
        # Basic channels
        try:
            indidict['channel'] = channels.channel(data, start=magic_limit)
        except:
            pass

        try:
            indidict['parabola'] = channels.parabola(data, start=magic_limit)
        except:
            pass

        try:
            indidict['wedge'] = channels.fallingwedge(data, start=magic_limit)
        except:
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
            output['patterns']=[]
            pass

        ################################ LEVELS ##########################################
        try:
            output['levels'] = levels.srlevels(data)
        except Exception as e:
            app.logger.warning(traceback.format_exc())
            output['levels'] = []
            pass
        toc = time.time()
        output['response_time'] = '{0:.2f} s'.format(toc-tic)
        return output, 200


events_list = []
class Events(Resource):
    def get(self):
        return events_list

    def put(self):
        events_list.append(ast.literal_eval(request.form['data']))
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        for event in events_list:
            if now - event['time'] > 60*int(conf['event_limit']):
                events_list.pop(events_list.index(event))


class Fill(Resource):
    def post(self, pair):
        exchange = internal.check_exchange(pair)
        parser = reqparse.RequestParser()
        parser.add_argument('last', type=int)
        args = parser.parse_args()
        last = args.get('last')
        if exchange != 'None':
            try:
                return dbservice.pair_fill(app, pair, exchange, last)
            except:
                app.logger.warning(traceback.format_exc())
                return 'Request failed', 500
        else:
            return 500


class Pairs(Resource):
    def get(self):
        try:
            pairs_list = internal.show_pairs()
            return pairs_list
        except:
            return 'Shit!', 500

    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('pair')
            parser.add_argument('exchange')
            args = parser.parse_args()
            exchange = args.get('exchange')
            pair = args.get('pair')
            response = internal.add_pair(pair, exchange)
            return response

        except:
            return 'Shit!', 500


##################### ENDPOINTS ############################
# Table with name 'pair'
api.add_resource(All, '/data/<string:pair>/<string:timeframe>/')
api.add_resource(Events, '/events')
api.add_resource(Fill, '/fill/<string:pair>')
api.add_resource(Pairs, '/pairs')
#api.add_resource(Channels, '/channel/<string:pair>/<string:timeframe>')


