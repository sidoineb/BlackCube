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
menu_2.add_command(label="Bitcoin", command=lambda: plot_graph("BTCUSDT"))
menu_2.add_command(label="Etherium", command=lambda: plot_graph("ETHUSDT"))
menu_2.add_command(label="Avalanche", command=lambda: plot_graph("AVAXUSDT"))
menu_2.add_command(label="Dogecoin", command=lambda: plot_graph("DOGEUSDT"))

menu_3 = tkinter.Menu(mainmenu, tearoff=0)
menu_3.add_command(label="Or")
menu_3.add_command(label="Argent")
menu_3.add_command(label="Cuivre")

mainmenu.add_cascade(label="Fichier", menu=menu_1)
mainmenu.add_cascade(label="Cryptos", menu=menu_2)
mainmenu.add_cascade(label="Métaux", menu=menu_3)

# Afficher la fenêtre
window.config(menu=mainmenu)
window.mainloop()


def plot_graph(symbol):
    # Moteur
    url = 'https://api.binance.com/api/v3/klines'
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

    # Récupérer les dernières 50 valeurs
    data_to_plot = data.tail(50)

    # Tracer le graphe avec Matplotlib
    fig, ax = plt.subplots()
    ax.plot(data_to_plot['datetime'], data_to_plot['close'], label='Close')
    ax.plot(data_to_plot['datetime'], data_to_plot['SMA9'], label='SMA9')
    ax.plot(data_to_plot['datetime'], data_to_plot['SMA20'], label='SMA20')
    ax.legend()
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title(f'Graphique de {symbol}')

    # Afficher le graphe dans la fenêtre Tkinter
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()

