import requests
from datetime import datetime, timedelta
import json
import pandas as pd
import ta


url = 'https://api.binance.com/api/v3/klines'
symbol = 'BTCUSDT'
interval = '1d'
my_date = datetime.now() - timedelta(30)

date_start = int(my_date.timestamp()*1000)
date_end = int(datetime.now().timestamp()*1000)

parameters = { 'symbol' : symbol, 'interval' : interval, 'startTime' : date_start, 'endTime' : date_end }

res = json.loads(requests.get(url, parameters).text)

data = pd.DataFrame(res)
data.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_traders', 'taker_base_vol','taker_quote_vol', 'ignore']

data['SMA9'] = ta.trend.sma_indicator(data['close'], 9)
data['SMA20'] = ta.trend.sma_indicator(data['close'], 20)

last_sma9 = data['SMA9'].iloc[-1]
last_sma20 = data['SMA20'].iloc[-1]

print("#################################")
print("##       -  BlackCube -        ##")
print("##         bot trading         ##")
print("#################################")
print("")
print(".: Derniere valeur de SMA9 :.")
print(last_sma9)
print("")
print(".: Derniere valeur de SMA20 :.")
print(last_sma20)
# print (data)
