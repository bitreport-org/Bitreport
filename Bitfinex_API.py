import datetime
import requests
import csv
import pandas as pd
import numpy as np

# DATA IMPORT AND EXPORT


# Bitreport Import List
# Bitfinex API Import List
# Input: (PAIR, period, limit) , ['BTCUSD', '1h', 200]
# Output: list [[DATE, OPEN, CLOSE, HIGH, LOW, VOLUME], ...]
# Remarks: all available periods formats could be find in Bitfinex documentation
# https://bitfinex.readme.io/v2/reference#rest-public-candles
def import_data(pair, period, limit):
    url = 'https://api.bitfinex.com/v2/candles/trade:'+period+':t'+pair+'/hist?limit='+str(limit)+'&start=946684800000'
    candel_list = requests.get(url).json()
    candel_list.reverse()
    # change mts to date
    candel_list = [[datetime.datetime.fromtimestamp(int(time / 1000.0)).strftime('%Y-%m-%d %H:%M:%S'), *rest] for
                   (time, *rest) in candel_list]
    return candel_list


# Bitreport Import Data frame
# Bitfinex API Import Data frame
# Input: (PAIR, period, limit) , ('BTCUSD', '1h', 200)
# Output: pandas data frame [[DATE, OPEN, CLOSE, HIGH, LOW, VOLUME], ...]
# Remarks: all available periods formats could be find in Bitfinex documentation
# https://bitfinex.readme.io/v2/reference#rest-public-candles
def Bitfinex_data_frame(pair, period, limit, type=None):
    url = 'https://api.bitfinex.com/v2/candles/trade:'+period+':t'+pair+'/hist?limit='+str(limit)+'&start=946684800000'
    candel_list = requests.get(url).json()
    candel_list.reverse()
    # change mts to date
    candel_list = [[datetime.datetime.fromtimestamp(int(time / 1000.0)).strftime('%Y-%m-%d %H:%M:%S'), *rest] for
                   (time, *rest) in candel_list]
    labels = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume']

    return pd.DataFrame.from_records(candel_list, columns=labels)



# Bitfinex date csv export
# Input: (PAIR, period, limit) , ('BTCUSD', '1h', 200)
# Output: PAIR_period_limit_time.csv
# Remarks: all available periods formats could be find in Bitfinex documentation
# https://bitfinex.readme.io/v2/reference#rest-public-candles
def export_csv(pair, period, limit):
    # pair formats: BTCUSD, NEOBTC
    list = [['DATE', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']]+import_data(pair, period, limit)
    file_name = pair+'_'+period+'_'+ str(limit) +'_'+ datetime.datetime.now().strftime("%Y-%m-%d")
    with open(file_name+".csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(list)



# Bitreport Import numpy data frames
# Bitfinex API Import numpy data frames
# Input: (PAIR, period, limit) , ('BTCUSD', '1h', 200)
# Output: dict {'date' : date_list,
#               'open' : np.array,
#               'close' : np.array,
#               'high' : np.array,
#               'low' : np.array,
#               'volume' : np.array}
# Remarks: all available periods formats could be find in Bitfinex documentation:
# https://bitfinex.readme.io/v2/reference#rest-public-candles
def Bitfinex_numpy(pair, period, limit):
    url = 'https://api.bitfinex.com/v2/candles/trade:'+period+':t'+pair+'/hist?limit='+str(limit)+'&start=946684800000'
    candel_list = requests.get(url).json()
    candel_list.reverse()

    date_list=[]
    open_list=[]
    close_list=[]
    high_list=[]
    low_list=[]
    volume_list=[]

    for i in range(0, len(candel_list)):
        # change mts to date
        date_list.append(datetime.datetime.fromtimestamp(int(float(candel_list[i][0]) / 1000.0)).strftime('%Y-%m-%d %H:%M:%S'))
        open_list.append(candel_list[i][1])
        close_list.append(candel_list[i][2])
        high_list.append(candel_list[i][3])
        low_list.append(candel_list[i][4])
        volume_list.append(candel_list[i][5])

    candles_dict = {'date' : date_list,
                    'open' : np.array(open_list),
                    'close' : np.array(close_list),
                    'high' : np.array(high_list),
                    'low' : np.array(low_list),
                    'volume' : np.array(volume_list)
                    }


    return candles_dict




