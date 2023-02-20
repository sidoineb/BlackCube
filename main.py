#################################
##       -  BlackCube -        ##
##         bot trading         ##
#################################


import tkinter
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from tkinter import *
import json
import pandas as pd
import ta

# Fenetre principale
window = Tk()

# personalisation
window.title(".: Black Cube :.")
window.geometry("600x600")
window.minsize(480, 360)
window.config(background='#b1f5b1')

# Barre de menu
mainmenu = tkinter.Menu(window)

menu_1 = tkinter.Menu(mainmenu, tearoff=0)
menu_1.add_command(label="Option1")
menu_1.add_command(label="Option2")
menu_1.add_command(label="Quitter", command=window.quit)

menu_2 = tkinter.Menu(mainmenu, tearoff=0)
menu_2.add_command(label="Bitcoin")
menu_2.add_command(label="Etherium")
menu_2.add_command(label="Avalanche")
menu_2.add_command(label="Avalanche")

menu_3 = tkinter.Menu(mainmenu, tearoff=0)
menu_3.add_command(label="Or")
menu_3.add_command(label="Argent")
menu_3.add_command(label="Cuivre")

mainmenu.add_cascade(label="Fichier", menu=menu_1)
mainmenu.add_cascade(label="Cryptos", menu=menu_2)
mainmenu.add_cascade(label="Métaux", menu=menu_3)

# Créer une figure matplotlib
fig, ax = plt.subplots()

# Dessiner une ligne
x = [1, 2, 3, 4, 5]
y = [10, 8, 6, 4, 2]
ax.plot(x, y)

# Créer un canvas tkinter
root = Tk()
frame = Frame(root)
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.draw()
canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
frame.pack()

# Moteur
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

# Afficher
window.config(menu=mainmenu)
window.mainloop()

#print(".: Derniere valeur de SMA9 :.")
#print(last_sma9)
#print("")
#print(".: Derniere valeur de SMA20 :.")
#print(last_sma20)
# print (data)
