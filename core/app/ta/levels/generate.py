import logging
import numpy as np

from app.utils.helpers import get_candles
from .levels import Levels
from app.ta.charting.base import Universe


def generate_levels(ctx,
                    pair: str,
                    limit: int = 500) -> None:

    logged = False
    with ctx:
        for tf in ['1h', '2h', '3h', '6h', '12h', '24h']:
            data = get_candles(pair, tf, limit)
            close = data.get('close')
            date = np.array(data.get('date'))

            if close.size < 1 and date.size < 1:
                continue

            universe = Universe(
                pair=pair,
                timeframe=tf,
                close=close,
                time=date[:close.size],
                future_time=[]
            )

            # Find levels and save them
            try:
                Levels(universe)()
            except (ValueError, AssertionError):
                if not logged:
                    logging.error(f'Levels production unsuccessful for {pair} and {tf}')
                    logged = True
                pass
