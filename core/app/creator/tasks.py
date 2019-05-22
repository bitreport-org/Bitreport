import celery
from time import sleep, time

import config
from app.api.database import connect_influx
from app.exchanges.filler import update_pair_data
from app.utils.helpers import get_all_pairs


@celery.task()
def fill_influx():
    # TODO: use config according to env
    Config = config.Development
    influx = connect_influx(Config.INFLUX)

    tic = time()
    pairs = get_all_pairs(influx)
    print(f'Influx {time() - tic}')

    pairs = [p for p in pairs if p[:4] != 'TEST']

    if not pairs:
        return None

    tic = time()

    # First pair
    update_pair_data(influx, pairs[0])

    for pair in pairs[1:]:
        sleep(2)
        update_pair_data(influx, pair)

    print(f'Filling {time() - tic}')
