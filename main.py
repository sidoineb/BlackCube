import tkinter as tk
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import json
import pandas as pd
import ta
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates

# Fenêtre principale
window = tk.Tk()

# Personnalisation
window.title(".: Black Cube :.")
window.geometry("600x600")
window.minsize(480, 360)
window.config(background='#b1f5b1')

# Splash screen
splash = tk.Toplevel()
splash.title("Chargement en cours...")
splash.geometry("300x100")
label = tk.Label(splash, text="Chargement en cours...", font=("Helvetica", 16))
label.pack(pady=20)
splash.after(3000, splash.destroy)

# Barre de menu
mainmenu = tk.Menu(window)

menu_1 = tk.Menu(mainmenu, tearoff=0)
menu_1.add_command(label="Option1")
menu_1.add_command(label="Option2")
menu_1.add_command(label="Quitter", command=window.quit)

menu_2 = tk.Menu(mainmenu, tearoff=0)
menu_2.add_command(label="Bitcoin", command=lambda: plot_graph("BTCUSDT"))
menu_2.add_command(label="Etherium", command=lambda: plot_graph("ETHUSDT"))
menu_2.add_command(label="Avalanche", command=lambda: plot_graph("AVAXUSDT"))
menu_2.add_command(label="Dogecoin", command=lambda: plot_graph("DOGEUSDT"))

menu_3 = tk.Menu(mainmenu, tearoff=0)
menu_3.add_command(label="Or")
menu_3.add_command(label="Argent")
menu_3.add_command(label="Cuivre")

mainmenu.add_cascade(label="Fichier", menu=menu_1)
mainmenu.add_cascade(label="Cryptos", menu=menu_2)
mainmenu.add_cascade(label="Métaux", menu=menu_3)

window.config(menu=mainmenu)

def plot_graph(symbol):
    # Requête à l'API Binance
    url = 'https://api.binance.com/api/v3/klines'
    interval = '1d'
    my_date = datetime.now() - timedelta(30)
    date_start = int(my_date.timestamp() * 1000)
    date_end = int(datetime.now().timestamp() * 1000)

    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': date_start,
        'endTime': date_end
    }
    
    res = requests.get(url, params=params)
    data = pd.DataFrame(json.loads(res.text), columns=['datetime', 'open', 'high', 'low', 'close', 'volume', 
                                                       'close_time', 'quote_asset_volume', 'number_of_trades', 
                                                       'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    # Convertir le timestamp en datetime
    data['datetime'] = pd.to_datetime(data['datetime'], unit='ms')
    data['datetime'] = data['datetime'].map(mdates.date2num)

    # Calcul des moyennes mobiles
    data['SMA9'] = ta.trend.sma_indicator(data['close'].astype(float), 9)
    data['SMA20'] = ta.trend.sma_indicator(data['close'].astype(float), 20)
    data['SMA50'] = ta.trend.sma_indicator(data['close'].astype(float), 50)

    # Tracer le graphe avec Matplotlib
    fig, ax = plt.subplots(figsize=(10, 7))
    candlestick_ohlc(ax, data[['datetime', 'open', 'high', 'low', 'close']].astype(float).values, 
                     width=0.6, colorup='green', colordown='red', alpha=0.8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Plot des moyennes mobiles
    ax.plot(data['datetime'], data['SMA9'], label='SMA9', linewidth=1, color='blue')
    ax.plot(data['datetime'], data['SMA20'], label='SMA20', linewidth=1, color='orange')
    ax.plot(data['datetime'], data['SMA50'], label='SMA50', linewidth=1, color='purple')

    # Légendes et titre
    ax.legend(loc='upper left')
    ax.set_title(f'{symbol} - Dernières 30 Jours')

    # Ajout de la grille
    ax.grid(True)

    # Convertir le graphe Matplotlib en objet Tkinter
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()

    # Afficher le graphe dans la fenêtre principale
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Afficher la fenêtre principale
window.mainloop()
