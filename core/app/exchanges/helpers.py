import pandas as pd
import logging
import traceback

from influxdb.exceptions import InfluxDBClientError
from datetime import datetime as dt

from app.database.models import influx_db


def check_exchanges(pair: str) -> list:
    result = influx_db.tag_values(measurement=f'{pair}1h', key='exchange')
    items = result.items()
    if not items:
        return []

    _, exchanges = items[0]
    result = list(map(lambda x: x.get('value'), exchanges))
    return result


def check_last_tmstmp(measurement: str, minus: int = 10) -> int:
    """
    Returns timestamp of last point in measurement.

    Parameters
    ----------
    measurement: name of the measurement
    minus: small shift in time

    Returns
    -------
    int: timestamp of last record
    """
    r = influx_db.query(f'SELECT * FROM {measurement} ORDER BY time DESC LIMIT 1;', epoch='s')
    df = pd.DataFrame(list(r.get_points(measurement=measurement)))
    if df.shape == (0, 0):
        # Return something old enough
        return 1518176375

    return int(df.time.values) - minus


def insert_candles(candles: list,
                   measurement: str,
                   exchange_name: str,
                   time_precision: str = None,
                   verbose: bool = True) -> bool:
    """
    Inserts point into a given measurement.

    Parameters
    ----------
    candles: list of points to be inserted
    measurement: name of the points' measurement
    exchange_name: name of exchange from which points come from
    time_precision: time precision of the measurement

    Returns
    -------
    bool: True if operation succeeded, otherwise False
    """
    result = influx_db.write_points(candles, time_precision=time_precision)
    if result and verbose:
        logging.info(f'SUCCEDED {exchange_name} write {len(candles)} records for {measurement}')
    elif verbose:
        logging.error(f'FAILED {exchange_name} to write records for {measurement}')

    return result


def downsample(pair: str,
               from_tf: str,
               to_tf: str) -> None:
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
        influx_db.query(query)
    except InfluxDBClientError:
        logging.error(f'FAILED {to_tf} downsample {pair} error: \n {traceback.format_exc()}')


def downsample_all_timeframes(ctx, pair: str):
    with ctx:
        downsample(pair, from_tf='30m', to_tf='1h')
        downsample(pair, from_tf='1h', to_tf='2h')
        downsample(pair, from_tf='1h', to_tf='3h')
        downsample(pair, from_tf='1h', to_tf='4h')
        downsample(pair, from_tf='1h', to_tf='6h')
        downsample(pair, from_tf='1h', to_tf='12h')
        downsample(pair, from_tf='1h', to_tf='24h')
