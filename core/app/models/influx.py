import contextlib
import logging
import re
import traceback
from datetime import datetime as dt
from functools import wraps
from typing import Optional

import pandas as pd
from influxdb.exceptions import InfluxDBClientError

from app.models import Series
from app.vendors.influx import InfluxDB
from config import resolve_config


@contextlib.contextmanager
def create_influx():
    """
    Contextmanager that will create and teardown a session.
    """
    config = resolve_config()
    influx = InfluxDB(host=config.INFLUXDB_HOST, database=config.INFLUXDB_DATABASE)

    yield influx
    influx.close()


def provide_influx(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        influx_name = "influx"

        func_params = func.__code__.co_varnames
        session_in_args = influx_name in func_params and func_params.index(
            influx_name
        ) < len(args)
        session_in_kwargs = influx_name in kwargs

        if session_in_kwargs or session_in_args:
            return func(*args, **kwargs)
        else:
            with create_influx() as influx:
                kwargs[influx_name] = influx
                return func(*args, **kwargs)

    return wrapper


@provide_influx
def get_all_pairs(influx: InfluxDB = None) -> list:
    pairs = influx.measurement.all()
    pairs = [re.match("[A-Z]+", m["name"])[0] for m in pairs]
    pairs = [p for p in set(pairs) if p[:4] != "TEST"]
    return pairs


@provide_influx
def get_candles(
    pair: str,
    timeframe: str,
    limit: int,
    last_timestamp: Optional[int] = None,
    influx: InfluxDB = None,
) -> Series:
    measurement = pair + timeframe

    if not last_timestamp:
        last_timestamp = 9000000000

    q = f"""
    SELECT * FROM (
        SELECT
        median(close) AS close, 
        median(high) AS high, 
        median(low) AS low, 
        median(open) AS open, 
        median(volume) AS volume
        FROM {measurement}
        WHERE ("exchange" = 'binance'
        OR "exchange" = 'bitfinex'
        OR "exchange" = 'poloniex'
        OR "exchange" = 'bittrex')
        GROUP BY  time({timeframe}) FILL(none)
        )
    WHERE time < {last_timestamp}s
    ORDER BY time DESC
    LIMIT {limit}
    """

    result = influx.query(q, epoch="s")
    df = pd.DataFrame(result.get_points(measurement=measurement))

    if df.shape[0] == 0:
        return Series(pair=pair, timeframe=timeframe)

    candles = Series(
        pair=pair,
        timeframe=timeframe,
        time=df.time.values[::-1],
        open=df.open.values[::-1],
        close=df.close.values[::-1],
        high=df.high.values[::-1],
        low=df.low.values[::-1],
        volume=df.volume.values[::-1],
    )

    return candles


@provide_influx
def check_last_timestamp(
    measurement: str, minus: int = 10, influx: InfluxDB = None
) -> int:
    """
    Returns timestamp of last point in measurement.
    """
    result = influx.query(
        f"SELECT * FROM {measurement} ORDER BY time DESC LIMIT 1;", epoch="s"
    )
    df = pd.DataFrame(result.get_points(measurement=measurement))
    if df.shape == (0, 0):
        # Return something old enough
        return 1518176375

    return int(df.time.values) - minus


@provide_influx
def check_exchanges(pair: str, influx: InfluxDB = None) -> list:
    result = influx.measurement.tag_values(measurement=f"{pair}1h", key="exchange")
    return list(result)


@provide_influx
def insert_candles(
    candles: list, time_precision: str = None, influx: InfluxDB = None
) -> bool:
    """
    Inserts point into a given measurement.
    """
    result = influx.write_points(candles, time_precision=time_precision)
    return result


@provide_influx
def downsample(pair: str, from_tf: str, to_tf: str, influx: InfluxDB = None) -> None:
    time_now = dt.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    query = f"""
                SELECT 
                first(open) AS open, 
                max(high) AS high, 
                min(low) AS low, 
                last(close) AS close, 
                sum(volume) AS volume 
                INTO {pair}{to_tf} FROM {pair}{from_tf} WHERE time <= '{time_now}' GROUP BY time({to_tf}), *

        """
    try:
        influx.query(query)
    except InfluxDBClientError:
        logging.error(
            f"FAILED %s downsample %s error: \n %s", to_tf, pair, traceback.format_exc()
        )


def downsample_all_timeframes(pair):
    downsample(pair, from_tf="30m", to_tf="1h")
    downsample(pair, from_tf="1h", to_tf="2h")
    downsample(pair, from_tf="1h", to_tf="3h")
    downsample(pair, from_tf="1h", to_tf="4h")
    downsample(pair, from_tf="1h", to_tf="6h")
    downsample(pair, from_tf="1h", to_tf="12h")
    downsample(pair, from_tf="1h", to_tf="24h")
