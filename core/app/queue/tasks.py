import celery
from time import sleep
from flask import current_app

from app.exchanges.filler import update_pair_data
from app.utils.helpers import get_all_pairs
from app.exchanges.helpers import downsample_all_timeframes


@celery.task(name='app.queue.tasks.fill_pair', time_limit=10)
def fill_pair(pair: str) -> bool:
    status = update_pair_data(pair)
    sleep(1.5)
    return status


@celery.task(name='app.queue.tasks.fill_influx')
def fill_influx() -> None:
    pairs = get_all_pairs()

    for pair in pairs:
        fill_pair.delay(pair)
        # downsample.delay(pair)


@celery.task(name='app.queue.tasks.downsample')
def downsample(pair) -> None:
    ctx = current_app.app_context()
    downsample_all_timeframes(ctx, pair)