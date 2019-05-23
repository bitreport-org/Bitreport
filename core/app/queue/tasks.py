import celery
import os
from time import sleep
import logging
import traceback

from config import Development, Production
from app.api.database import connect_influx
from app.exchanges.filler import update_pair_data
from app.utils.helpers import get_all_pairs


@celery.task(name='app.queue.tasks.fill_influx')
def fill_influx() -> None:
    # Setup proper config
    environment = {'development': Development, 'production': Production}
    Config = environment[os.environ['FLASK_ENV']]

    influx = connect_influx(Config.INFLUX)

    pairs = get_all_pairs(influx)

    if not pairs:
        return None

    for pair in pairs:
        try:
            update_pair_data(influx, pair)
            sleep(2)
        except:
            logging.error(f'Fill task for {pair} has failed, traceback: \n {traceback.format_exc()}')
            pass
