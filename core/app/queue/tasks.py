import celery
from flask import current_app
from celery.exceptions import SoftTimeLimitExceeded

from app.exchanges.filler import update_pair_data
from app.exchanges.helpers import downsample_all_timeframes
from app.database.helpers import get_all_pairs


@celery.task(
    name="app.queue.tasks.fill_pair",
    bind=True,
    soft_time_limit=12,
    retry_kwargs={"max_retries": 1},
)
def fill_pair(self, pair: str) -> bool:
    status = False
    try:
        status = update_pair_data(pair)
        return status
    except SoftTimeLimitExceeded as exc:
        if status is False:
            return self.retry(exc=exc, countdown=60)


@celery.task(name="app.queue.tasks.fill_influx")
def fill_influx() -> None:
    pairs = get_all_pairs()

    for pair in pairs:
        fill_pair.delay(pair)


@celery.task(name="app.queue.tasks.downsample")
def downsample(pair) -> None:
    ctx = current_app.app_context()
    downsample_all_timeframes(ctx, pair)
