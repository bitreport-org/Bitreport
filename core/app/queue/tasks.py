import celery
from time import sleep
from flask import current_app

from app.exchanges.filler import update_pair_data
from app.utils.helpers import get_all_pairs



@celery.task(name='app.queue.tasks.fill_pair')
def fill_pair(pair: str) -> bool:
    ctx = current_app.app_context()

    status = update_pair_data(pair)

    sleep(2)
    return status


@celery.task(name='app.queue.tasks.fill_influx')
def fill_influx() -> None:

    pairs = get_all_pairs()

    for pair in pairs:
        fill_pair.delay(pair)
