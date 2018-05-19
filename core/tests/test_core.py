import pytest
import requests
from random import random

@pytest.fixture
def getpair(pair, tf, limit, untill=None):
    return requests.get('http://0.0.0.0:5001/{}?timeframe={}&limit={}&untill={}'.format(pair, tf, limit, untill))

@pytest.fixture
def filler(pair, force = False):
	return requests.post('http://0.0.0.0:5001/fill?pair={}&force={}'.format(pair, force))


class TestData(object):
	pair = 'BTCUSD'
	timeframe = '3h'
	limit = 20

	def make_all(self, pair):
		self.pair = pair
		self.test_get_pair_0()
		self.test_get_pair_1()
		self.test_get_pair_2()
		self.test_get_pair_0()

	def test_get_pair_0(self):
		response = getpair(self.pair,self.timeframe, self.limit)
		assert response.status_code == 200
		
		response = response.json()
		assert isinstance(response, str) or isinstance(response,dict)

	def test_get_pair_1(self):
		response = getpair(self.pair,self.timeframe, self.limit)
		assert response.status_code == 200
		
		response = response.json()
		assert isinstance(response, dict)
		
		keys = response.keys()
		required_keys = ['candles', 'dates', 'indicators', 'levels', 'info']
		for k in keys:
			assert k in required_keys

	def test_get_pair_2(self):
		response = getpair(self.pair,self.timeframe, self.limit)
		assert response.status_code == 200
		
		response = response.json()
		assert isinstance(response, dict)
		
		candles = response.get('candles', [])
		keys = candles.keys()
		required_keys = ['close', 'open', 'high', 'low', 'volume']
		for k in keys:
			assert k in required_keys
			assert len(candles.get(k)) == self.limit

	def test_get_pair_3(self):
		response = getpair(self.pair,self.timeframe, self.limit)
		assert response.status_code == 200
		
		response = response.json()
		assert isinstance(response, dict)
		dates = response.get('dates', [])
		assert dates[1]-dates[0] == 3600 * int(self.timeframe[:-1])


class TestTA(object):
	pair = 'BTCUSD'
	timeframe = '3h'
	limit = 20

	def test_indicators(self):
		response = getpair(self.pair,self.timeframe, self.limit)
		assert response.status_code == 200
		
		response = response.json()
		indicators = response.get('indicators', {})
		keys = indicators.keys()
		required_keys =  ['ADX', 'ALLIGATOR', 'AROON', 'BB', 'EMA', 'EWO', 
						'ICM', 'ICMF', 'KC', 'MACD', 'MOM', 'OBV', 'RSI', 
						'SAR', 'SMA', 'STOCH', 'STOCHRSI', 'TDS']

		for k in required_keys:
			assert k in keys

	def test_channels(self):
		response = getpair(self.pair,self.timeframe, self.limit)
		assert response.status_code == 200
		response = response.json()
		indicators = response.get('indicators', {})
		keys = indicators.keys()
		required_keys =  ['channel', 'parabola', 'wedge']

		for k in required_keys:
			assert k in keys


class TestFilling(object):
	def test_no_pair(self):
		pair = 'lilfasddsdfaWE'
		response = filler(pair, True)
		assert response.status_code == 500

	def test_bitfinex(self):
		pair = 'BTCUSD'
		response = filler(pair, True)
		assert response.status_code == 200

		# Test if filled
		data_test = TestData()
		data_test.make_all(pair)

	def test_binance(self):
		pair = 'GASBTC'
		response = filler(pair, True)
		assert response.status_code == 200

		# Test if filled
		data_test = TestData()
		data_test.make_all(pair)

	def test_poloniex(self):
		pair = 'SCBTC'
		response = filler(pair, True)
		assert response.status_code == 200

		# Test if filled
		data_test = TestData()
		data_test.make_all(pair)

	def test_bittrex(self):
		pair = 'POLYBTC'
		response = filler(pair, True)
		assert response.status_code == 200

		# Test if filled
		data_test = TestData()
		data_test.make_all(pair)


class TestPairs(object):
	pair = 'test{}'.format(int(100000000*random()))
	exchange = 'Exchange_'+pair

	def test_add_pair(self):
		response = requests.post('http://0.0.0.0:5001/pairs?pair={}&exchange={}'.format(self.pair, self.exchange))
		assert response.status_code == 200

		response = requests.request('VIEW', 'http://0.0.0.0:5001/pairs')
		assert response.status_code == 200
		last_pair, last_ex = response.json()[-1]
		assert last_pair == self.pair
		assert last_ex == self.exchange
