import unittest
import unittest.mock as mock

from app.exchanges import Binance, Bitfinex, Bittrex, Poloniex
from app.models.influx import check_exchanges, get_all_pairs


class TestFiller:
    def test_all_pairs(self, app, filled_influx):
        with app.ctx:
            pairs = get_all_pairs()
        assert isinstance(pairs, list)
        assert len(pairs) == 1
        pairs.sort()
        assert pairs == ["BTCUSD"]

    def test_check_exchanges(self, app, filled_influx):
        with app.ctx:
            exchanges = check_exchanges("BTCUSD")
        assert isinstance(exchanges, list)
        assert len(exchanges) == 1
        assert exchanges == ["bitfinex"]

    def test_no_exchange(self, app, filled_influx):
        with app.ctx:
            exchanges = check_exchanges("TESTSMTH")
        assert isinstance(exchanges, list)
        assert not exchanges


class TestBitfinex(unittest.TestCase):
    name = "Bitfinex"
    pair = "TEST"
    timeframe = "24h"
    measurement = pair + timeframe
    exchange = Bitfinex(pair)
    row = [0, 1, 2, 3, 4, 5]
    expected = {
        "fields": {
            "close": row[2],
            "high": row[3],
            "low": row[4],
            "open": row[1],
            "volume": row[5],
        },
        "measurement": measurement,
        "tags": {"exchange": name.lower()},
        "time": row[0],
    }

    def test_base(self):
        self.assertEqual(self.exchange.name, self.name)
        self.assertIsInstance(self.exchange.timeframes, list)

    def test_json(self):
        json = self.exchange.json(self.measurement, self.row)
        self.assertDictEqual(self.expected, json)

    @mock.patch("app.exchanges.bitfinex.check_last_timestamp")
    @mock.patch("app.exchanges.bitfinex.requests.get")
    def test_not_200(self, request_mock, check_mock):
        start = 100
        check_mock.return_value = start
        request_mock.return_value.status_code = 500
        self.assertFalse(self.exchange.fetch_candles(self.timeframe))

    @mock.patch("app.exchanges.bitfinex.check_last_timestamp")
    @mock.patch("app.exchanges.bitfinex.requests.get")
    def test_not_list(self, request_mock, check_mock):
        start = 100
        check_mock.return_value = start
        request_mock.return_value.status_code = 200
        request_mock.return_value.json.return_value = None
        self.assertFalse(self.exchange.fetch_candles(self.timeframe))

    @mock.patch("app.exchanges.bitfinex.check_last_timestamp")
    @mock.patch("app.exchanges.bitfinex.requests.get")
    def test_error(self, request_mock, check_mock):
        start = 100
        check_mock.return_value = start
        request_mock.return_value.status_code = 200
        request_mock.return_value.json.return_value = ["error"]
        self.assertFalse(self.exchange.fetch_candles(self.timeframe))

    @mock.patch("app.exchanges.base.insert_candles")
    @mock.patch("app.exchanges.bitfinex.check_last_timestamp")
    @mock.patch("app.exchanges.bitfinex.requests.get")
    def test_green_path(self, request_mock, check_mock, insert_mock):
        start = 100
        check_mock.return_value = start
        request_mock.return_value.status_code = 200
        request_mock.return_value.json.return_value = [self.row]

        self.exchange.fetch_candles(self.timeframe)
        insert_mock.assert_called_with(candles=[self.expected], time_precision="ms")


class TestBittrex(unittest.TestCase):
    name = "Bittrex"
    pair = "TESTUSD"
    timeframe = "24h"
    measurement = pair + timeframe
    exchange = Bittrex(pair)
    row = {"T": 100, "O": 1, "H": 2, "C": 3, "L": 4, "BV": 5}
    expected = {
        "fields": {
            "close": row["C"],
            "high": row["H"],
            "low": row["L"],
            "open": row["O"],
            "volume": row["BV"],
        },
        "measurement": measurement,
        "tags": {"exchange": name.lower()},
        "time": row["T"],
    }

    def test_base(self):
        self.assertEqual(self.exchange.name, self.name)
        self.assertIsInstance(self.exchange.timeframes, list)

    def test_pair_format(self):
        expected = "USDT-TEST"
        self.assertEqual(expected, self.exchange._pair_format(self.pair))

    def test_json(self):
        json = self.exchange.json(self.measurement, self.row)
        self.assertDictEqual(self.expected, json)

    @mock.patch("app.exchanges.bittrex.requests.get")
    def test_not_200(self, request_mock):
        request_mock.return_value.status_code = 500
        self.assertFalse(self.exchange.fetch_candles(self.timeframe))

    @mock.patch("app.exchanges.bittrex.requests.get")
    def test_not_result(self, request_mock):
        request_mock.return_value.status_code = 200
        request_mock.return_value.json.return_value = {}
        self.assertFalse(self.exchange.fetch_candles(self.timeframe))

    @mock.patch("app.exchanges.base.insert_candles")
    @mock.patch("app.exchanges.bittrex.requests.get")
    def test_green_path(self, request_mock, insert_mock):
        request_mock.return_value.status_code = 200
        request_mock.return_value.json.return_value.keys.return_value = ["success"]
        request_mock.return_value.json.return_value.get.return_value = [self.row]

        self.exchange.fetch_candles(self.timeframe)
        insert_mock.assert_called_with(candles=[self.expected], time_precision="s")


class TestBinance(unittest.TestCase):
    name = "Binance"
    pair = "TESTUSD"
    timeframe = "24h"
    measurement = pair + timeframe
    exchange = Binance(pair)
    row = [0, 1.0, 2.0, 3.0, 4.0, 5.0]
    expected = {
        "fields": {
            "close": row[4],
            "high": row[2],
            "low": row[3],
            "open": row[1],
            "volume": row[5],
        },
        "measurement": measurement,
        "tags": {"exchange": name.lower()},
        "time": row[0],
    }

    def test_base(self):
        self.assertEqual(self.exchange.name, self.name)
        self.assertIsInstance(self.exchange.timeframes, list)

    def test_pair_format(self):
        expected = "TESTUSDT"
        self.assertEqual(expected, self.exchange._pair_format(self.pair))

    def test_json(self):
        json = self.exchange.json(self.measurement, self.row)
        self.assertDictEqual(self.expected, json)

    @mock.patch("app.exchanges.binance.requests.get")
    def test_not_200(self, request_mock):
        request_mock.return_value.status_code = 500
        self.assertFalse(self.exchange.fetch_candles(self.timeframe))

    @mock.patch("app.exchanges.base.insert_candles")
    @mock.patch("app.exchanges.binance.requests.get")
    def test_green_path(self, request_mock, insert_mock):
        request_mock.return_value.status_code = 200
        request_mock.return_value.json.return_value = [self.row]

        self.exchange.fetch_candles(self.timeframe)
        insert_mock.assert_called_with(candles=[self.expected], time_precision="ms")


class TestPoloniex(unittest.TestCase):
    name = "Poloniex"
    pair = "TESTUSD"
    timeframe = "1h"
    measurement = pair + "30m"
    exchange = Poloniex(pair)
    row = {"date": 100, "open": 1, "high": 2, "close": 3, "low": 4, "volume": 5}
    expected = {
        "fields": {
            "open": row["open"],
            "close": row["close"],
            "high": row["high"],
            "low": row["low"],
            "volume": row["volume"],
        },
        "measurement": measurement,
        "tags": {"exchange": name.lower()},
        "time": row["date"],
    }

    def test_base(self):
        self.assertEqual(self.exchange.name, self.name)
        self.assertIsInstance(self.exchange.timeframes, list)

    def test_pair_format(self):
        expected = "USDT_TEST"
        self.assertEqual(expected, self.exchange._pair_format(self.pair))

    def test_json(self):
        json = self.exchange.json(self.measurement, self.row)
        self.assertDictEqual(self.expected, json)

    @mock.patch("app.exchanges.poloniex.check_last_timestamp")
    @mock.patch("app.exchanges.poloniex.requests.get")
    def test_not_200(self, request_mock, check_mock):
        start = 100
        check_mock.return_value = start
        request_mock.return_value.status_code = 500
        self.assertFalse(self.exchange.fetch_candles(self.timeframe))

    @mock.patch("app.exchanges.base.insert_candles")
    @mock.patch("app.exchanges.poloniex.check_last_timestamp")
    @mock.patch("app.exchanges.poloniex.requests.get")
    def test_green_path(self, request_mock, check_mock, insert_mock):
        start = 100
        check_mock.return_value = start
        request_mock.return_value.status_code = 200
        request_mock.return_value.json.return_value = [self.row]

        self.exchange.fetch_candles(self.timeframe)
        insert_mock.assert_called_with(candles=[self.expected], time_precision="s")
