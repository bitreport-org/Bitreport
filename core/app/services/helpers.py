# -*- coding: utf-8 -*-
import pandas as pd
from influxdb import InfluxDBClient
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import config


def sentry_setup(active: bool) -> bool:
    """
    Activates Sentry logging.

    :param active: if True logging to Sentry is activated
    :return:
    """
    if active:
        sentry_sdk.init(
            dsn=config.BaseConfig.SENTRY_URL,
            integrations=[FlaskIntegration()]
        )
        return True
    return False


def get_candles(influx: InfluxDBClient, pair: str, timeframe: str, limit: int) -> dict:
    """
    Retrieves `limit` points for measurement `pair + timeframe`. Returns dictionary:
    `{'date': list,
    'open': numpy.ndarray,
    'close': numpy.ndarray,
    'high': numpy.ndarray,
    'low': numpy.ndarray,
    'volume': numpy.ndarray}`

    :param influx: influx client
    :param pair: pair name ex. 'BTCUSD'
    :param timeframe: timeframe ex. '1h'
    :param limit: number of candles to retrieve
    :return: dict
    """
    measurement = pair + timeframe

    q = f"""
    SELECT
    mean(close) AS close, 
    mean(high) AS high, 
    mean(low) AS low, 
    mean(open) AS open, 
    mean(volume) AS volume
    FROM {measurement}
    WHERE time >= now() - {limit * int(timeframe[:-1])}h
    AND ("exchange" = 'binance'
    OR "exchange" = 'bitfinex'
    OR "exchange" = 'poloniex'
    OR "exchange" = 'bittrex') 
    GROUP BY  time({timeframe}) FILL(none)
    """

    r = influx.query(q, epoch='s')
    df = pd.DataFrame(list(r.get_points(measurement=measurement)))
    if df.shape==(0,0):
        return dict()

    candles_dict = {'date': list(df.time),
                    'open': df.open.values,
                    'close': df.close.values,
                    'high': df.high.values,
                    'low': df.low.values,
                    'volume': df.volume.values
                    }

    return candles_dict


def generate_dates(date: list, timeframe: str, n: int) -> list:
    """
    Generates next n timestamps in interval of a given timeframe
    :param date: list of timestamps
    :param timeframe: name of the timeframe in hours, minutes, weeks ex. '1h', '30m', '1W'
    :param n: number of future timestamps to generate
    :return: input list with new points appended
    """
    _map = { 'm': 60, 'h': 3600,'W': 648000}
    dt = _map[timeframe[-1]]
    date = date + [int(date[-1]) + i*dt for i, x in enumerate(range(n))]
    return date


def get_function_list(module) -> list:
    """
    Helper to obtain list of functions in the given module
    :param module: module
    :return:
    """
    return [getattr(module, a) for a in module.__all__]
