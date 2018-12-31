import pytest
import requests
from random import random


def getpair(pair, tf, limit, untill=None):
    return requests.get('http://0.0.0.0:5001/{}?timeframe={}&limit={}&untill={}'.format(pair, tf, limit, untill))


def filler(pair, exchange, force = False):
	return requests.post('http://0.0.0.0:5001/fill?pair={}&exchange={}&force={}'.format(pair, exchange, force))


class TestData(object):
	pair = 'BTCUSD'
	timeframe = '3h'
	limit = 30

	def make_all(self, pair):
		self.pair = pair
		self.test_get_pair_0()
		self.test_get_pair_1()
		self.test_get_pair_2()
		self.test_get_pair_3()

	def test_get_pair_0(self):
		# Assure a response and that if 200 then it is a dictionary
		response = getpair(self.pair, self.timeframe, self.limit)
		assert response.status_code == 200

		response = response.json()
		assert isinstance(response,dict)

	def test_get_pair_1(self):
		# Assure that only available keys in response are 'dates' and 'indicators'
		response = getpair(self.pair,self.timeframe, self.limit)
		assert response.status_code == 200
		response = response.json()
		assert isinstance(response, dict)

		keys = response.keys()
		required_keys = ['dates', 'indicators']
		for k in keys:
			assert k in required_keys

		assert len(keys) == len(required_keys)

	def test_get_pair_2(self):
		# Assure that there is price and it has required keys and that the price data has equal lenght
		response = getpair(self.pair,self.timeframe, self.limit)
		assert response.status_code == 200

		response = response.json()
		assert isinstance(response, dict)

		candles = response['indicators']['price']
		keys = candles.keys()
		required_keys = ['close', 'open', 'high', 'low', 'info']
		for k in keys:
			assert k in required_keys
			if k!='info':
				assert len(candles.get(k)) == self.limit

	def test_get_pair_3(self):
		# Assure that dates are in interval of timeframe
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
		required_keys =  ['price', 'ADX', 'ALLIGATOR', 'AROON', 'BB', 'EMA', 'EWO', 
						'ICM', 'KC', 'MACD', 'MOM', 'OBV', 'RSI', 
						'SAR', 'SMA', 'STOCH', 'STOCHRSI', 'TDS']

		for k in required_keys:
			assert k in keys

	def test_info(self):
		# Check if each indicators have 'info'
		response = getpair(self.pair,self.timeframe, self.limit)
		assert response.status_code == 200
		
		response = response.json()
		assert isinstance(response, dict)
		
		indicators = response.get('indicators')
		keys_to_check = indicators.keys()

		for k in keys_to_check:
			assert 'info' in indicators.get(k).keys()

	def test_channels(self):
		response = getpair(self.pair,self.timeframe, self.limit)
		assert response.status_code == 200
		response = response.json()
		indicators = response.get('indicators', {})
		keys = indicators.keys()
		required_keys =  ['channel', 'wedge', 'levels', 'channel12', 'wedge12']

		for k in required_keys:
			assert k in keys
	
	def test_bands(self):
		# Check if 'band' indicators have unified bands' names
		response = getpair(self.pair,self.timeframe, self.limit)
		assert response.status_code == 200
		
		response = response.json()
		assert isinstance(response, dict)
		
		indicators = response.get('indicators')
		keys_to_check = ['channel', 'wedge', 'BB', 'KC', 'channel12', 'wedge12']

		for k in keys_to_check:
			key_list = indicators.get(k).keys() 
			assert 'upper_band' in key_list
			assert 'middle_band' in key_list
			assert 'lower_band' in key_list


class TestFilling(object):
	def test_no_pair(self):
		pair = 'lilfasddsdfaWE'
		response = filler(pair, True)
		assert response.status_code == 500

	def test_bitfinex(self):
		pair = 'BTCUSD'
		response = filler(pair, 'bitfinex', True)
		assert response.status_code == 200

	def test_bitfinex2(self):
		pair = 'BTCUSD'
		# Test if filled
		data_test = TestData()
		data_test.make_all(pair)

	def test_binance(self):
		pair = 'GASBTC'
		response = filler(pair, 'binance', True)
		assert response.status_code == 200

	def test_binance2(self):
		pair = 'GASBTC'
		# Test if filled
		data_test = TestData()
		data_test.make_all(pair)

	def test_poloniex(self):
		pair = 'SCBTC'
		response = filler(pair, 'poloniex', True)
		assert response.status_code == 200

	def test_poloniex2(self):
		pair = 'SCBTC'
		# Test if filled
		data_test = TestData()
		data_test.make_all(pair)

	def test_bittrex(self):
		pair = 'POLYBTC'
		response = filler(pair, 'bittrex', True)
		assert response.status_code == 200

	def test_bittrex2(self):
		pair = 'POLYBTC'
		# Test if filled
		data_test = TestData()
		data_test.make_all(pair)

