from app.utils.influx_utils import get_candles
from app.models import Series
from app.ta.events.atomics import Atomics

from config import resolve_config
from app.api import create_app

import argparse

parser = argparse.ArgumentParser(description='Generates history of events.')
parser.add_argument('-p', '--pair', help='pair for the history.', required=True)
parser.add_argument('-t', '--timeframe', help='time frame for the history.', required=True)
parser.add_argument('-l', '--limit', help='history size - number of last candles', default=200)

args = parser.parse_args()


def create_history(pair: str, timeframe: str, limit: int):
    series: Series = get_candles(pair=pair, timeframe=timeframe, limit=limit)
    print(f'Creating {series.pair}{series.timeframe}. Size: {series.close.size}')
    atoms = Atomics(series)
    atoms.remake()

if args.pair and args.timeframe:
    # Setup proper config
    Config = resolve_config()
    # Create app
    app = create_app(Config)
    #  Generate history
    with app.app_context():
        create_history(pair=args.pair, timeframe=args.timeframe, limit=args.limit)
    exit(0)
