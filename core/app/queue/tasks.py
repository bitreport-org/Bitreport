import celery
import os
from time import sleep

from config import Development, Production
from app.api.database import influx
from app.exchanges.filler import update_pair_data
from app.utils.helpers import get_all_pairs



@celery.task(name='app.queue.tasks.fill_pair')
def fill_pair(conf: dict, pair: str) -> bool:
    with influx(conf) as flux:
        status = update_pair_data(flux, pair)

    sleep(2)
    return status


@celery.task(name='app.queue.tasks.fill_influx')
def fill_influx() -> None:
    # Setup proper config
    environment = {'development': Development, 'production': Production}
    conf = environment[os.environ['FLASK_ENV']]

    with influx(conf.INFLUX) as flux:
        pairs = get_all_pairs(flux)

    for pair in pairs:
        fill_pair.delay(conf.INFLUX, pair)
