import logging
import pandas as pd
from influxdb import InfluxDBClient

def check_last_tmstmp(influx: InfluxDBClient, measurement: str) -> int:
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
    r = influx.query(f'SELECT * FROM {measurement} ORDER BY time DESC LIMIT 1;', epoch='s')
    df = pd.DataFrame(list(r.get_points(measurement=measurement)))
    if df.shape==(0,0):
        # Return something old enough
        return 1518176375

    return int(df.time.values)


def insert_candles(influx: InfluxDBClient, candles: list,
                   measurement: str, exchange_name: str,
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
    result = influx.write_points(candles, time_precision=time_precision)
    if result:
        logging.info(f'SUCCEDED write  records for {measurement} from {exchange_name}')
    else:
        logging.error(f'FAILED to write records for {measurement} from {exchange_name}')
    return result
