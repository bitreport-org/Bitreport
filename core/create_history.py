from app.database import get_candles
from app.ta.charting.base import Universe
from app.ta.eventer.atomics import Atomics

from config import resolve_config
from app.api import create_app


def create_history(pair: str, timeframe: str):
    all_data = get_candles(pair=pair, timeframe=timeframe, limit=100000)
    uni = Universe(
        pair=pair,
        timeframe=timeframe,
        close=all_data.close,
        time=all_data.date,
        future_time=[]
    )

    print(f'Creating {uni.pair}{uni.timeframe}. Size: {uni.close.size}')

    atoms = Atomics(uni)
    atoms.remake()

# Setup proper config
Config = resolve_config()

# Create app
app = create_app(Config)

#  Generate history
with app.app_context():
    create_history(pair='BTCUSD', timeframe='1h')