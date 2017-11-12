import requests
import numpy as np
from datetime import datetime
import time
import iso8601

def import_numpy(client, db, pair, timeframe, limit):
    # Perform query and return JSON data
    query = 'SELECT * FROM ' + pair + timeframe + ' ORDER BY time DESC LIMIT ' + str(limit) + ';'
    params = 'db=' + db + '&q=' + query
    r = client.request('query', params=params)

    # Unwrap json :D
    candel_list = r.json()['results'][0]['series'][0]['values']

    date_list=[]
    open_list=[]
    close_list=[]
    high_list=[]
    low_list=[]
    volume_list=[]

    for i in range(0, len(candel_list)):
        # change data to timestamp
        t = candel_list[i][0]
        dt = iso8601.parse_date(t)
        dt = int(time.mktime(dt.timetuple()))

        date_list.append(dt)
        close_list.append(candel_list[i][1])
        high_list.append(candel_list[i][2])
        low_list.append(candel_list[i][3])
        open_list.append(candel_list[i][4])
        volume_list.append(candel_list[i][5])

    date_list.reverse()
    close_list.reverse()
    open_list.reverse()
    high_list.reverse()
    low_list.reverse()
    volume_list.reverse()

    candles_dict = {'date' : date_list,
                    'open' : np.array(open_list),
                    'close' : np.array(close_list),
                    'high' : np.array(high_list),
                    'low' : np.array(low_list),
                    'volume' : np.array(volume_list)
                    }

    return candles_dict
