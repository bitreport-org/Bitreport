from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from influxdb import InfluxDBClient
import ast, time, datetime

# Internal import
from services import internal, microcaps
from ta import patterns, indicators, channels, levels

app = Flask(__name__)
api = Api(app)
conf = internal.Config('config.ini', 'services')

##############################################

# to post data without NaN values indicators are calculated on period of length: limit + magic_limit
# next posted data has length = limit
magic_limit = int(conf['magic_limit'])

#########################################################################################

class get_ohlc(Resource):
    def get(self, pair, timeframe):
        parser = reqparse.RequestParser()

        parser.add_argument('limit', type=int)
        args = parser.parse_args()
        limit = args.get('limit')

        # Perform query and return JSON data
        dic = {}
        data = internal.import_numpy(pair, timeframe, limit)
        print(data)


        dic['dates'] = data['date'],
        dic['candles'] = {'open': data['open'].tolist(),
                           'high': data['high'].tolist(),
                           'close': data['close'].tolist(),
                           'low': data['low'].tolist(),
                           }
        return dic


class get_all(Resource):
    def get(self, pair, timeframe):

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

        parser.add_argument('channels',  action='append')
        args = parser.parse_args()
        channel_list = args.get('channels')

        ############################### DATA REQUEST #####################################

        dict = {}
        data = internal.import_numpy(pair, timeframe, limit+magic_limit)

        dict['dates'] = data['date'][magic_limit:]

        # SET margin
        margin = 26 #timestamps

        # Generate timestamps for future
        date = data['date']
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
                except Exception as e:
                    #print(indic, e)
                    pass
            dict['indicators'] = indidict

        ################################ PATTERNS ########################################
        # Short data for patterns:

        if patterns_list != None:
            pat_data = internal.import_numpy(pair, timeframe, limit)

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
        try:
            channel_list = channel_list[0].split(',')
        except:
            pass

        chdict = {}
        if channel_list != None:
            for ch in channel_list:
                try:
                    chdict[ch] = getattr(channels, ch)(data, magic_limit = magic_limit)
                except Exception as e:
                    #print(ch, e)
                    pass
            dict['channels'] = chdict

        return dict

class get_microcaps(Resource):
    def get(self):
        return microcaps.microcaps()


events_list = []
class events(Resource):
    def get(self):
        return events_list

    def put(self):
        events_list.append(ast.literal_eval(request.form['data']))
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        for event in events_list:
            if now - event['time'] > 60*int(conf['event_limit']):
                events_list.pop(events_list.index(event))



##################### ENDPOINTS ############################
# Table with name 'pair'
# api.add_resource(get_pair, '/')
api.add_resource(get_all, '/data/<string:pair>/<string:timeframe>/')
api.add_resource(get_ohlc, '/test/<string:pair>/<string:timeframe>/')
api.add_resource(get_microcaps, '/microcaps')
api.add_resource(events, '/events')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)

