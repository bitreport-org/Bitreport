import celery
from celery.exceptions import SoftTimeLimitExceeded

from app.exchanges.filler import update_pair_data
from app.models.influx import downsample_all_timeframes, get_all_pairs


@celery.task(  # pylint:disable=not-callable
    name="app.queue.tasks.fill_pair",
    bind=True,
    soft_time_limit=12,
    retry_kwargs={"max_retries": 1},
)
def fill_pair(self, pair: str) -> bool:
    status = False
    try:
        status = update_pair_data(pair)
    except SoftTimeLimitExceeded:
        pass
    if status is False:
        return self.retry(countdown=60 * 2)
    return status


@celery.task(name="app.queue.tasks.fill_influx")  # pylint:disable=not-callable
def fill_influx() -> None:
    pairs = get_all_pairs()

    for pair in pairs:
        fill_pair.delay(pair)


@celery.task(name="app.queue.tasks.downsample")  # pylint:disable=not-callable
def downsample(pair) -> None:
    downsample_all_timeframes(pair)
