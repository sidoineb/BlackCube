import requests
from datetime import datetime, timedelta
import json
import pandas as pd

url = 'https://api.binance.com/api/v3/klines'
symbol = 'AVAXUSDT'
interval = '1d'
my_date = datetime.now() - timedelta(30)

date_start = int(my_date.timestamp()*1000)
date_end = int(datetime.now().timestamp()*1000)

parameters = { 'symbol' : symbol, 'interval' : interval, 'startTime' : date_start, 'endTime' : date_end }

res = json.loads(requests.get(url, parameters).text)

data = pd.DataFrame(res)
data.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_traders', 'taker_base_vol','taker_quote_vol', 'ignore']

print (data)
