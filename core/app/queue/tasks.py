import celery
from time import sleep
from flask import current_app
from celery.exceptions import SoftTimeLimitExceeded

from app.exchanges.filler import update_pair_data
from app.exchanges.helpers import downsample_all_timeframes
from app.database.helpers import get_all_pairs

@celery.task(name='app.queue.tasks.fill_pair',
             bind=True,
             soft_time_limit=12,
             retry_kwargs={'max_retries': 1})
def fill_pair(self, pair: str) -> bool:
    try:
        status = update_pair_data(pair)
    except SoftTimeLimitExceeded as exc:
        return self.retry(exc=exc, countdown=60)
    else:
        # Wait a moment or fall silently
        try:
            sleep(0.5)
            return status
        except SoftTimeLimitExceeded:
            return status


@celery.task(name='app.queue.tasks.fill_influx')
def fill_influx() -> None:
    pairs = get_all_pairs()

    for pair in pairs:
        fill_pair.delay(pair)


@celery.task(name='app.queue.tasks.downsample')
def downsample(pair) -> None:
    ctx = current_app.app_context()
    downsample_all_timeframes(ctx, pair)
