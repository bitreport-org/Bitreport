import pandas as pd
import logging
import traceback

from influxdb.exceptions import InfluxDBClientError
from datetime import datetime as dt

from app.api.database import influx_db

def check_exchanges(pair: str, db_name: str = 'pairs') -> list:
    q = f"SHOW TAG VALUES ON {db_name} FROM {pair}1h WITH KEY = exchange"
    result = influx_db.connection.query(q)
    items = result.items()
    if not items:
        return []

    _, exchanges = items[0]
    result = list(map(lambda x: x.get('value'), exchanges))
    return result


def check_last_tmstmp(measurement: str) -> int:
    """
    Returns timestamp of last point in measurement.

    Parameters
    ----------
    influx: influx client
    measurement: name of the measurement

    Returns
    -------
    int: timestamp of last record
    """
    r = influx_db.connection.query(f'SELECT * FROM {measurement} ORDER BY time DESC LIMIT 1;', epoch='s')
    df = pd.DataFrame(list(r.get_points(measurement=measurement)))
    if df.shape == (0, 0):
        # Return something old enough
        return 1518176375

    return int(df.time.values) - 10


def insert_candles(candles: list,
                   measurement: str,
                   exchange_name: str,
                   time_precision: str = None) -> bool:
    """
    Inserts point into a given measurement.

    Parameters
    ----------
    influx: instance of InfluxDBCLient
    candles: list of points to be inserted
    measurement: name of the points' measurement
    exchange_name: name of exchange from which points come from
    time_precision: time precision of the measurement

    Returns
    -------
    bool: True if operation succeeded, otherwise False
    """
    result = influx_db.connection.write_points(candles, time_precision=time_precision)
    if result:
        logging.info(f'SUCCEDED {exchange_name} write {len(candles)} records for {measurement}')
    else:
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
        influx_db.connection.query(query)
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
