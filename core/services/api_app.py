from flask import Flask
from flask_restful import Resource, Api, reqparse
from influxdb import InfluxDBClient
import json


# Internal import
from services import internal
from ta import patterns
from ta import indicators
from ta import levels, channels
from services import microcaps

app = Flask(__name__)
api = Api(app)

# PARAMETERS
db = 'test'
client = InfluxDBClient('localhost', 8086, 'root', 'root', db)

# to post data without NaN values indicators are calculated on period of length: limit + magic_limit
# next posted data has length = limit
magic_limit = 79

#########################################################################################

class get_ohlc(Resource):
    def get(self, pair, timeframe):
        global client, db
        parser = reqparse.RequestParser()

        parser.add_argument('limit', type = int)
        args = parser.parse_args()
        limit = args.get('limit')

        # Perform query and return JSON data
        dict = {}
        data = internal.import_numpy(client, db, pair, timeframe, limit)
        print(data)


        dict['dates'] = data['date'],
        dict['candles'] = {'open': data['open'].tolist(),
                           'high': data['high'].tolist(),
                           'close': data['close'].tolist(),
                           'low': data['low'].tolist(),
                           }
        print(dict)
        return dict


class get_all(Resource):
    def get(self, pair, timeframe):
        global client, db

        ################################## PARSER #######################################
        parser = reqparse.RequestParser()

        parser.add_argument('limit', type=int, help='Limit must be int')
        args = parser.parse_args()
        limit = args.get('limit')

        parser.add_argument('indicators', action='append', help='Indicators must be line or ALL')
        args = parser.parse_args()
        indicators_list = args.get('indicators')

        parser.add_argument('patterns', action='append')
        args = parser.parse_args()
        patterns_list = args.get('patterns')

        parser.add_argument('levels')
        args = parser.parse_args()
        levels_ask = args.get('levels')

        parser.add_argument('channel')
        args = parser.parse_args()
        channel = args.get('channel')

        ############################### DATA REQUEST #####################################

        dict = {}
        data = internal.import_numpy(client, db, pair, timeframe, limit+magic_limit)

        dict['dates'] = data['date'][magic_limit:]

        # SET margin
        margin = 26 #timestamps

        # Generate timestamps for future
        date = data['date']
        last_time = date[-1]
        period = timeframe[-1]
        timef = timeframe[:-1]
        t = int(timef)

        d = 0
        if period == 'm':
            d = 60 * t
        elif period == 'h':
            d = 60 * 60 * t
        elif period == 'W':
            d = 60 * 60 * 168 * t

        for i in range(0, margin):
            date.append(int(date[-1]) + d)

        dict['dates'] = date[magic_limit:]


        dict['candles'] = { 'open': data['open'].tolist()[magic_limit:],
                            'high': data['high'].tolist()[magic_limit:],
                            'close': data['close'].tolist()[magic_limit:],
                            'low': data['low'].tolist()[magic_limit:],
                            'volume': data['volume'].tolist()[magic_limit:]
                        }

        ################################ INDICATORS ######################################

        if indicators_list != None:
            try:
                indicators_list = indicators_list[0].split(',')
            except:
                pass

            indidict = {}
            for indic in indicators_list:
                try:
                    indidict[indic] = getattr(indicators, indic)(data, start = magic_limit)
                except:
                    pass
            dict['indicators'] = indidict

        ################################ PATTERNS ########################################
        # Short data for patterns:

        if patterns_list != None:
            pat_data = internal.import_numpy(client, db, pair, timeframe, limit)

            try:
                patterns_list = patterns_list[0].split(',')
            except:
                pass

            if patterns_list == ['ALL']:
                try:
                    dict['patterns'] = patterns.CheckAllPatterns(pat_data)
                except:
                    pass
            else:
                try:
                    dict['patterns'] = patterns.CheckAllPatterns(pat_data, patterns_list, 0)
                except:
                    pass

        ################################ LEVELS ##########################################

        if levels_ask == 'ALL':
            dict['levels'] = levels.srlevels(data)

        ################################ CHANNELS #########################################
        if channel == 'True':
            dict['channels'] = channels.talib_channel_front(data, magic_limit)

        return dict

class get_microcaps(Resource):
    def get(self):
        return microcaps.microcaps()

##################### ENDPOINTS ############################
# Table with name 'pair'
# api.add_resource(get_pair, '/')
api.add_resource(get_all, '/data/<string:pair>/<string:timeframe>/')
api.add_resource(get_ohlc, '/test/<string:pair>/<string:timeframe>/')
api.add_resource(get_microcaps, '/microcaps')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

