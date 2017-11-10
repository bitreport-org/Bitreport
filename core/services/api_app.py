from flask import Flask
from flask_restful import Resource, Api, reqparse
from influxdb import InfluxDBClient
import json

# Internal import
from services import internal
from ta import patterns
from ta import indicators

app = Flask(__name__)
api = Api(app)

# PARAMETERS
db = 'test'
client = InfluxDBClient('localhost', 8086, 'root', 'root', db)

# to post data without NaN values indicators are calculated on period of length: limit + magic_limit
# next posted data has length = limit
magic_limit = 34

###############################################################

class get_ohlc(Resource):
    def get(self):
        global client, db
        parser = reqparse.RequestParser()
        parser.add_argument('pair')
        args = parser.parse_args()
        pair = args.get('pair')

        parser.add_argument('timeframe')
        args = parser.parse_args()
        timeframe = args.get('timeframe')

        parser.add_argument('limit')
        args = parser.parse_args()
        limit = args.get('limit')

        # Perform query and return JSON data
        query = 'SELECT * FROM ' + pair + timeframe + ' ORDER BY time DESC LIMIT ' + str(limit) + ';'
        params = 'db=' + db + '&q=' + query
        r =client.request('query', params=params)

        # Unwrap json :D
        return r.json()['results'][0]['series'][0]['values']

class get_pair(Resource):
    def get(self):
        global client, db
        parser = reqparse.RequestParser()
        parser.add_argument('pair')
        args = parser.parse_args()
        pair = args.get('pair')


        # Perform query and return JSON data
        query = 'SELECT * FROM ' + pair + ';'
        params = 'db=' + db + '&q=' + query
        r = client.request('query', params=params)

        # Unwrap json :D
        print(pair)
        return r.json()['results'][0]['series'][0]['values']

# class get_patterns(Resource):
#     def get(self, pair, timeframe, limit, patterns_list, all ):
#         global client, db
#
#         data = internal.import_numpy(db, client, pair, timeframe, limit)
#         return patterns.CheckAllPatterns(data, patterns_list, all)
#
# class get_bb(Resource):
#     def get(self, pair, timeframe, limit, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0):
#         global client, db
#
#         data = internal.import_numpy(client, db, pair, timeframe, limit)
#         return indicators.BB(data, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
#
# class get_macd(Resource):
#     def get(self, pair, timeframe, limit, fastperiod=12, slowperiod=26, signalperiod=9):
#         global client, db
#
#         data = internal.import_numpy(client, db, pair, timeframe, limit)
#         return indicators.MACD(data, fastperiod=12, slowperiod=26, signalperiod=9)

class get_all(Resource):
    def get(self, pair, timeframe):
        global client, db

        ################################## PARSER ########################################
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

        ############################### DATA REQUEST ###########################################

        # # Perform query and return JSON data
        # query = 'SELECT * FROM ' + pair + timeframe + ' ORDER BY time DESC LIMIT ' + str(limit) + ';'
        # params = 'db=' + db + '&q=' + query
        # r = client.request('query', params=params)
        #
        # data = internal.import_numpy(client, db, pair, timeframe, limit)
        # dict = {}
        # dict['candles'] = r.json()['results'][0]['series'][0]['values']

        dict = {}
        data = internal.import_numpy(client, db, pair, timeframe, limit+magic_limit)
        print(len(data['date'].tolist()[magic_limit:]))

        dict['dates'] = data['date'].tolist()[magic_limit:],
        dict['candles'] = { 'open': data['open'].tolist()[magic_limit:],
                            'high': data['high'].tolist()[magic_limit:],
                            'close': data['close'].tolist()[magic_limit:],
                            'low': data['low'].tolist()[magic_limit:],
                        }

        ################################ INDICATORS ##########################################

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

        if patterns_list != None:
            try:
                patterns_list = patterns_list[0].split(',')
            except:
                pass

            value = 0
            if patterns_list == ['ALL']:
                try:
                    dict['patterns'] = patterns.CheckAllPatterns(data, 'none', 1)
                except:
                    pass
            else:
                try:
                    dict['patterns'] = patterns.CheckAllPatterns(data, patterns_list, 0)
                except:
                  pass

        return dict



##################### ENDPOINTS ############################
# Table with name 'pair'
api.add_resource(get_pair, '/')
api.add_resource(get_all, '/data/<string:pair>/<string:timeframe>/')

# List of last n=limit [close,  high,   low,    open,   volume] candles
api.add_resource(get_ohlc, '/data/')


if __name__ == '__main__':
    app.run(debug=True)

