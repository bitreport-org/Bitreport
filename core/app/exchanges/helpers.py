import logging
import pandas as pd

def check_last_tmstmp(influx, mesurement):
    # returns last timestamp
    r = influx.query(f'SELECT * FROM {mesurement} ORDER BY time DESC LIMIT 1;', epoch='s')
    df = pd.DataFrame(list(r.get_points(measurement=mesurement)))
    if df.shape==(0,0):
        return 1518176375
    return int(df.time.values)


def insert_candles(influx, candles, mesurement):
    result = influx.write_points(candles)

    if result:
        logging.info(f'SUCCEDED write  records for {mesurement}')
    else:
        m = f'FAILED to write records for {mesurement}'
        logging.error(m)
    return result
