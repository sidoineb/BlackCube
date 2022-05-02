import requests
from datetime import datetime, timedelta
import json

url = 'https://api.binance.com/api/v3/klines'
symbol = 'AVAXUSDT'
interval = '1d'
my_date = datetime.now() - timedelta(30)

date_start = int(my_date.timestamp()*1000)
date_end = int(datetime.now().timestamp()*1000)

parameters = { 'symbol' : symbol, 'interval' : interval, 'startTime' : date_start, 'endTime' : date_end }

res = json.loads(requests.get(url, parameters).text)

print (res)
