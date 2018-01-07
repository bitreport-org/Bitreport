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
from core.ta import indicators, levels, patterns

app = Flask(__name__)
api = Api(app)
conf = internal.Config('config.ini', 'services')

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
        args = parser.parse_args()
        limit = args.get('limit')

        parser.add_argument('untill', type=int, help='Limit must be int')
        args = parser.parse_args()
        untill = args.get('untill')

        ############################### DATA REQUEST #####################################

        dict = {}

        if untill != None:
            data = internal.import_numpy_untill(pair, timeframe, limit + magic_limit, untill)
            # SET margin
            margin = 26 #timestamps

            # Generate timestamps for future
            dict['dates'] = internal.generate_dates(data, timeframe, margin)[magic_limit:]

            dict['candles'] = { 'open': data['open'].tolist()[magic_limit:],
                                'high': data['high'].tolist()[magic_limit:],
                                'close': data['close'].tolist()[magic_limit:],
                                'low': data['low'].tolist()[magic_limit:],
                                'volume': data['volume'].tolist()[magic_limit:]
                            }
        else:
            data = internal.import_numpy(pair, timeframe, limit + magic_limit)
            # SET margin
            margin = 26  # timestamps

            # Generate timestamps for future
            dict['dates'] = internal.generate_dates(data, timeframe, margin)[magic_limit:]

            dict['candles'] = {'open': data['open'].tolist()[magic_limit:],
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
        dict['indicators'] = indidict

        ################################ PATTERNS ########################################
        # Short data for patterns:

        pat_data = internal.import_numpy(pair, timeframe, limit)

        try:
            dict['patterns'] = patterns.CheckAllPatterns(pat_data)
        except Exception as e:
            logging.error(traceback.format_exc())
            pass

        ################################ LEVELS ##########################################

        dict['levels'] = levels.srlevels(data)

        ################################ CHANNELS #########################################
        # TODO after channels implementation it must be adjusted
        # try:
        #     channel_list = channel_list[0].split(',')
        # except:
        #     pass
        #
        # chdict = {}
        # if channel_list != None:
        #     for ch in channel_list:
        #         try:
        #             chdict[ch] = getattr(channels, ch)(data, magic_limit = magic_limit)
        #         except Exception as e:
        #             #print(ch, e)
        #             pass
        #     dict['channels'] = chdict

        return dict


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
        return conf['pairs2'].split(',')



##################### ENDPOINTS ############################
# Table with name 'pair'
api.add_resource(All, '/data/<string:pair>/<string:timeframe>/')
api.add_resource(Microcaps, '/microcaps')
api.add_resource(Events, '/events')
api.add_resource(Fill, '/fill/<string:pair>/<string:timeframe>/<int:limit>')
api.add_resource(Pairs, '/pairs')


if __name__ == '__main__':
    logging.basicConfig(filename='api_app.log', format='%(levelname)s:%(message)s', level=logging.INFO)

    start_runner()
    app.run(host='0.0.0.0', debug=False)

