import celery
import os
from time import sleep

from config import Development, Production
from app.api.database import connect_influx
from app.exchanges.filler import update_pair_data
from app.utils.helpers import get_all_pairs


@celery.task()
def fill_influx():
    # Setup proper config
    environment = {'development': Development, 'production': Production}
    Config = environment[os.environ['FLASK_ENV']]

    influx = connect_influx(Config.INFLUX)

    pairs = get_all_pairs(influx)
    pairs = [p for p in pairs if p[:4] != 'TEST']

    if not pairs:
        return None

    # First pair
    update_pair_data(influx, pairs[0])

    for pair in pairs[1:]:
        sleep(2)
        update_pair_data(influx, pair)
