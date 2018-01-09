from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import ast
import time
import datetime
import logging
import threading
import requests
import traceback

# Internal import
from core.services import internal, microcaps, eventservice, dbservice
from core.ta import indicators, levels, patterns, channels

app = Flask(__name__)
api = Api(app)
conf = internal.Config('config.ini', 'services')

# TODO: delete dbservices before production deployment

@app.before_first_request
def activate_job():
    def db_service():
        dbservice.run_dbservice()

    def event_service():
        eventservice.run_events()

    thread1 = threading.Thread(target=db_service)
    thread2 = threading.Thread(target=event_service)
    thread1.setDaemon(True)
    thread2.setDaemon(True)

    thread1.start()
    thread2.start()


@app.route('/dbservice')
def db_service():
    def service1():
        dbservice.run_dbservice()

    thread = threading.Thread(target=service1)
    thread.setDaemon(True)
    thread.start()


@app.route('/dbfill')
def db_fill_full():
    def service2():
        dbservice.run_dbfill_full()

    thread = threading.Thread(target=service2)
    thread.setDaemon(True)
    thread.start()
    return 'Database filled'


@app.route("/")
def hello():
    return "Wrong place, is it?"


# Activates db_service
def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            #print('In start loop')
            try:
                r = requests.get('http://0.0.0.0:5000/')
                if r.status_code == 200:
                    #print('Server started, quiting start_loop')
                    not_started = False
                #print(r.status_code)
            except:
                pass
            time.sleep(2)

    print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), 'START runner')
    thread = threading.Thread(target=start_loop)
    thread.start()

#### API ####

# to post data without NaN values indicators are calculated on period of length: limit + magic_limit
# next posted data has length = limit
magic_limit = int(conf['magic_limit'])


class All(Resource):
    def get(self, pair, timeframe):

        ################################## PARSER #######################################
        parser = reqparse.RequestParser()

        parser.add_argument('limit', type=int, help='Limit must be int')
        parser.add_argument('untill', type=int, help='Limit must be int')
        args = parser.parse_args()

        limit = args.get('limit')
        untill = args.get('untill')
        ############################### DATA REQUEST #####################################

        output = {}

        if untill != None:
            data = internal.import_numpy_untill(pair, timeframe, limit + magic_limit, untill)
            if data == False:
                return 'Error', 500

            # SET margin
            margin = 26 #timestamps

            # Generate timestamps for future
            dates = internal.generate_dates(data, timeframe, margin)
            output['dates'] = dates[magic_limit:]

            output['candles'] = { 'open': data['open'].tolist()[magic_limit:],
                                'high': data['high'].tolist()[magic_limit:],
                                'close': data['close'].tolist()[magic_limit:],
                                'low': data['low'].tolist()[magic_limit:],
                                'volume': data['volume'].tolist()[magic_limit:]
                            }
        else:
            data = internal.import_numpy(pair, timeframe, limit + magic_limit)
            if data == False:
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
                indidict[indic] = getattr(indicators, indic)(data, start=magic_limit)
            except Exception as e:
                logging.error(indic)
                logging.error(traceback.format_exc())
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
            indidict['fallingwedge'] = channels.fallingwedge(data, start=magic_limit)
        except:
            pass

        # LAST CHANNELS
        lasts = channels.create_channels(dates, pair, timeframe, magic_limit)
        try:
            indidict['last_channel'] = lasts['last_channel']
        except:
            pass
        try:
            indidict['last_parabola'] = lasts['last_parabola']
        except:
            pass
        try:
            indidict['last_fallingwedge'] = lasts['last_fallingwedge']
        except:
            pass

        output['indicators'] = indidict

        ################################ PATTERNS ########################################
        # Short data for patterns:

        pat_data = internal.import_numpy(pair, timeframe, limit)

        try:
            output['patterns'] = patterns.CheckAllPatterns(pat_data)
        except Exception as e:
            logging.error(traceback.format_exc())
            output['patterns']=[]
            pass

        ################################ LEVELS ##########################################
        try:
            output['levels'] = levels.srlevels(data)
        except Exception as e:
            logging.error(traceback.format_exc())
            output['levels']=[]
            pass

        return output, 200


class Microcaps(Resource):
    def get(self):
        return microcaps.microcaps()


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
    def service3(self, pair, timeframe, limit):
        dbservice.run_dbfill_selected(pair, timeframe, limit)

    def post(self, pair, timeframe, limit):
        try:
            thread = threading.Thread(target=self.service3, args=(pair, timeframe, limit))
            thread.setDaemon(True)
            thread.start()
        except:
            logging.error(traceback.format_exc())
            return 'Request failed', 500

class Pairs(Resource):
    def get(self):
        try:
            pairs_list = internal.show_pairs()
            output = []
            for p in pairs_list:
                output.append(p[0])

            return output
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
            if exchange == None:
                exchange='bitfinex'

            response = internal.add_pair(pair, exchange)
            return response

        except:
            return 'Shit!', 500


class Channels(Resource):
    def post(self, pair, timeframe):
        parser = reqparse.RequestParser()

        parser.add_argument('limit', type=int, help='Limit must be int')
        parser.add_argument('channel_type')
        args = parser.parse_args()

        limit = args.get('limit')
        channel_type = args.get('channel_type')

        return channels.save_channel(pair, timeframe, limit, channel_type)

    def get(self, pair, timeframe):
        parser = reqparse.RequestParser()
        parser.add_argument('channel_type')
        args = parser.parse_args()
        channel_type = args.get('channel_type')

        l=channels.last_channel(pair, timeframe, channel_type)

        return l



##################### ENDPOINTS ############################
# Table with name 'pair'
api.add_resource(All, '/data/<string:pair>/<string:timeframe>/')
api.add_resource(Microcaps, '/microcaps')
api.add_resource(Events, '/events')
api.add_resource(Fill, '/fill/<string:pair>/<string:timeframe>/<int:limit>')
api.add_resource(Pairs, '/pairs')
api.add_resource(Channels, '/channel/<string:pair>/<string:timeframe>')


if __name__ == '__main__':
    logging.basicConfig(filename='api_app.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)

    start_runner()
    app.run(host='0.0.0.0', debug=False)

