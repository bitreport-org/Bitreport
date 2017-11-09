from flask import Flask
from flask_restful import Resource, Api
from influxdb import InfluxDBClient

# Internal import
from services import internal
from ta import patterns

app = Flask(__name__)
api = Api(app)

# PARAMETERS
db = 'test'
client = InfluxDBClient('localhost', 8086, 'root', 'root', db)

###############################################################

class get_ohlc(Resource):
    def get(self, pair, timeframe, limit):
        global client, db

        # Perform query and return JSON data
        query = 'SELECT * FROM ' + pair + timeframe + ' ORDER BY time DESC LIMIT ' + str(limit) + ';'
        params = 'db=' + db + '&q=' + query
        r =client.request('query', params=params)

        # Unwrap json :D
        return r.json()['results'][0]['series'][0]['values']

class get_pair(Resource):
    def get(self, pair):
        global client, db

        # Perform query and return JSON data
        query = 'SELECT * FROM ' + pair + ';'
        params = 'db=' + db + '&q=' + query
        r = client.request('query', params=params)

        # Unwrap json :D
        return r.json()['results'][0]['series'][0]['values']

class get_patterns(Resource):
    def get(self, pair, timeframe, limit ):
        global client, db

        data = internal.import_numpy(db, client, pair, timeframe, limit)
        return patterns.CheckAllPatterns(data)

##################### ENDPOINTS ############################
# Table with name 'pair'
api.add_resource(get_pair, '/<string:pair>')

# List of last n=limit [close,  high,   low,    open,   volume] candles
api.add_resource(get_ohlc, '/candles/<string:pair>/<string:timeframe>/<int:limit>')

# Patterns {'pattern_name' : {'up' : [dates], 'down' : [dates]}, ...}
api.add_resource(get_patterns, '/patterns/<string:pair>/<string:timeframe>/<int:limit>')



if __name__ == '__main__':
    app.run(host='0.0.0.0')