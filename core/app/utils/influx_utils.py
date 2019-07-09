import re
import pandas as pd

from app.models import influx_db, Series


def get_all_pairs() -> list:
    pairs = influx_db.connection.get_list_measurements()
    pairs = [re.match('[A-Z]+', m['name'])[0] for m in pairs]
    pairs = [p for p in set(pairs) if p[:4] != 'TEST']
    return pairs


def get_candles(pair: str, timeframe: str, limit: int) -> Series:
    measurement = pair + timeframe

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
    ORDER BY time DESC
    LIMIT {limit}
    """

    r = influx_db.query(q, epoch='s')
    df = pd.DataFrame(list(r.get_points(measurement=measurement)))

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
        volume=df.volume.values[::-1]
    )

    return candles


def check_last_timestamp(measurement: str, minus: int = 10) -> int:
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
