# -*- coding: utf-8 -*-
from .binance import Binance
from .bitfinex import Bitfinex
from .bittrex import Bittrex
from .poloniex import  Poloniex

import logging
import requests

# Bitfinex 1h, 3h, 6h, 12h, 24h
# Binance 1h, 2h, 6h, 12h, 24h
# Bittrex 1h, 24h

def fill_pair(influx, pair, exchange):
    fillers = dict(
        bitfinex=Bitfinex,
        bittrex=Bittrex,
        binance=Binance,
        # poloniex=poloniex
    )

    if exchange not in fillers.keys():
        msg = f'{exchange} exchange does not exist'
        logging.error(f'{exchange} exchange does not exist')
        return msg, 404


    filler = fillers[exchange]
    status = filler(influx).fill(pair)

    if status:
        return f"{pair} filled from {exchange}", 200
    else:
        return f"{pair} failed to fill from {exchange}", 404


def check_exchange(pair: str):
    pair = pair.upper()
    history = []
    # Bitfinex
    url = f'https://api.bitfinex.com/v2/candles/trade:1D:t{pair}/hist?limit=1'
    request = requests.get(url)
    response = request.json()
    if isinstance(response, list) and response != []:
        history.append(('bitfinex', len(response)))

    # bitrex
    end_pair = pair[-3:]
    start_pair = pair[:-3]
    if end_pair == 'USD':
        end_pair = end_pair + 'T'
    req_pair = end_pair + '-' + start_pair
    url = f'https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName={req_pair}&tickInterval=24h'
    request = requests.get(url)
    response = request.json()
    if response.get('success', False):
        candle_list = response.get('result', None)
        if candle_list:
            history.append(('bittrex', len(candle_list)))

    # binance
    end_pair = pair[-3:]
    start_pair = pair[:-3]
    if end_pair == 'USD':
        end_pair = end_pair + 'T'
    req_pair = start_pair + end_pair
    url = f'https://api.binance.com/api/v1/klines?symbol={req_pair}&interval=1d&limit=500'
    request = requests.get(url)
    response = request.json()
    if isinstance(response, list):
        history.append(('binance', len(response)))

    # poloniex
    end_pair = pair[-3:]
    start_pair = pair[:-3]
    if end_pair == 'USD':
        end_pair = end_pair + 'T'
    req_pair = end_pair + '_' + start_pair
    url = f'https://poloniex.com/public?command=returnChartData&currencyPair={req_pair}&start=339361693&end=9999999999&period=86400'
    request = requests.get(url)
    response = request.json()
    if isinstance(response, list):
        history.append(('poloniex', len(response)))

    history.sort(key=lambda x: x[1])

    if len(history) > 0:
        return history[-1][0], 200
    else:
        return 'Exchange not found...', 404