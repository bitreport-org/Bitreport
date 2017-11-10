import requests
import numpy as np

def import_data(client, db, pair, timeframe, limit):
    url = 'http://localhost:5000/candles/' +pair + '/' + timeframe + '/' + str(limit)
    candel_list = requests.get(url).json()
    #candel_list.reverse()

    return candel_list

def import_numpy(client, db, pair, timeframe, limit):
    # Perform query and return JSON data
    query = 'SELECT * FROM ' + pair + timeframe + ' ORDER BY time DESC LIMIT ' + str(limit) + ';'
    params = 'db=' + db + '&q=' + query
    r = client.request('query', params=params)

    # Unwrap json :D
    candel_list = r.json()['results'][0]['series'][0]['values']
    #candel_list.reverse()

    date_list=[]
    open_list=[]
    close_list=[]
    high_list=[]
    low_list=[]
    volume_list=[]

    for i in range(0, len(candel_list)):
        # change mts to date
        date_list.append(candel_list[i][0])
        close_list.append(candel_list[i][1])
        high_list.append(candel_list[i][2])
        low_list.append(candel_list[i][3])
        open_list.append(candel_list[i][4])
        volume_list.append(candel_list[i][5])

    candles_dict = {'date' : np.array(date_list),
                    'open' : np.array(open_list),
                    'close' : np.array(close_list),
                    'high' : np.array(high_list),
                    'low' : np.array(low_list),
                    'volume' : np.array(volume_list)
                    }


    return candles_dict
