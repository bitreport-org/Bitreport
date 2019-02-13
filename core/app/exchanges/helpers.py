import logging
import pandas as pd

def check_last_tmstmp(influx, measurement):
    # returns last timestamp
    r = influx.query(f'SELECT * FROM {measurement} ORDER BY time DESC LIMIT 1;', epoch='s')
    df = pd.DataFrame(list(r.get_points(measurement=measurement)))
    if df.shape==(0,0):
        return 1518176375
    return int(df.time.values)


def insert_candles(influx, candles, measurement, time_precision=None):
    result = influx.write_points(candles, time_precision=time_precision)
    if result:
        logging.info(f'SUCCEDED write  records for {measurement}')
    else:
        logging.error(f'FAILED to write records for {measurement}')
    return result
