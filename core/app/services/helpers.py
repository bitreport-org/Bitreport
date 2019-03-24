# -*- coding: utf-8 -*-
import pandas as pd
from influxdb import InfluxDBClient
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import config


def sentry_setup(active: bool) -> bool:
    """
    Activates Sentry logging.

    Parameters
    ----------
    active: if True logging to Sentry is activated

    Returns
    -------
    bool
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

    Parameters
    ----------
    influx: influx client
    pair: pair name ex. 'BTCUSD'
    timeframe: timeframe ex. '1h'
    limit: number of candles to retrieve

    Returns
    -------
    candle_dict: dict
    """
    measurement = pair + timeframe

    q = f"""
    SELECT * FROM (
        SELECT
        mean(close) AS close, 
        mean(high) AS high, 
        mean(low) AS low, 
        mean(open) AS open, 
        mean(volume) AS volume
        FROM {measurement}
        WHERE ("exchange" = 'binance'
        OR "exchange" = 'bitfinex'
        OR "exchange" = 'poloniex'
        OR "exchange" = 'bittrex') 
        GROUP BY  time({timeframe}) FILL(none)
        )
    ORDER BY time DESC
    LIMIT {limit}
    """

    r = influx.query(q, epoch='s')
    df = pd.DataFrame(list(r.get_points(measurement=measurement)))

    if df.shape==(0,0):
        return dict()

    candles_dict = {'date': df.time.values.tolist()[::-1],
                    'open': df.open.values[::-1],
                    'close': df.close.values[::-1],
                    'high': df.high.values[::-1],
                    'low': df.low.values[::-1],
                    'volume': df.volume.values[::-1]
                    }

    return candles_dict


def generate_dates(date: list, timeframe: str, n: int) -> list:
    """
    Generates next n timestamps in interval of a given timeframe

    Parameters
    ----------
    date: list of timestamps
    timeframe: name of the timeframe in hours, minutes, weeks ex. '1h', '30m', '1W'
    n: number of future timestamps to generate

    Returns
    -------
    date: the input list with new points appended
    """
    _map = { 'm': 60, 'h': 3600,'W': 648000}
    dt = _map[timeframe[-1]] * int(timeframe[:-1])
    date = date + [date[-1] + (i+1)*dt for i, x in enumerate(range(n))]

    return date


def get_function_list(module) -> list:
    """
    Helper to obtain list of functions in the given module

    Parameters
    ----------
    module: the module for which list have to be obtained

    Returns
    -------
    list
    """
    return [getattr(module, a) for a in module.__all__]
