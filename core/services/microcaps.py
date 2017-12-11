import datetime
import requests
from time import gmtime, strftime
from datetime import timedelta

def microcaps():
    url = 'https://api.coinmarketcap.com/v1/ticker/?limit=0'
    market = requests.get(url).json()

    caps = []
    for coin in market:
        # last = datetime.fromtimestamp(int(coin['last_updated']))
        # print(last, datetime.today(), datetime.today() - last < timedelta(weeks=2))
        try:
            if float(coin['market_cap_usd']) < 250000 and (
                        float(coin['available_supply']) <= 50000000) and (
                            float(coin['24h_volume_usd']) / float(coin['market_cap_usd']) > 0.02) and (
                            float(coin['available_supply']) / float(coin['total_supply']) > 0.66):

                tempdict = {}
                for key in ['symbol', 'price_usd', 'price_btc', '24h_volume_usd', 'market_cap_usd',
                            'available_supply', 'total_supply', 'percent_change_24h', 'percent_change_7d']:
                    tempdict[key] = coin[key]

                caps.append(tempdict)
        except:
            pass

    return {'microcaps': caps}