import tkinter
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import json
import pandas as pd
import ta

# Fenetre principale
window = tkinter.Tk()

# personalisation
window.title(".: Black Cube :.")
window.geometry("600x600")
window.minsize(480, 360)
window.config(background='#b1f5b1')

# Splash screen
splash = tkinter.Toplevel()
splash.title("Chargement en cours...")
splash.geometry("300x100")
label = tkinter.Label(splash, text="Chargement en cours...", font=("Helvetica", 16))
label.pack(pady=20)
splash.destroy()
splash.after(30000, splash.destroy)

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

def plot_graph(symbol):
    # Moteur
    url = 'https://api.binance.com/api/v3/klines'
    interval = '1d'
    my_date = datetime.now() - timedelta(30)

    date_start = int(my_date.timestamp()*1000)
    date_end = int(datetime.now().timestamp()*1000)

    res = json.loads(requests.get(url).text)

    data = pd.DataFrame(res)

    data['SMA9'] = ta.trend.sma_indicator(data['close'], 9)
    data['SMA20'] = ta.trend.sma_indicator(data['close'], 20)

    last_sma9 = data['SMA9'].iloc[-1]
    last_sma20 = data['SMA20'].iloc[-1]

    # Récupérer les dernières 50 valeurs
    data_to_plot = data.tail(50)

    # Tracer le graphe avec Matplotlib
    fig, ax = plt.subplots(figsize=(10, 7))

    # Plot the candlestick chart
    candlestick_ohlc(ax, data_to_plot.values, width=0.0005, colorup='green', colordown='red', alpha=0.8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    # Plot the moving averages
    ax.plot(data_to_plot['datetime'], data_to_plot['SMA9'], label='SMA9', linewidth=1, color='blue')
    ax.plot(data_to_plot['datetime'], data_to_plot['SMA20'], label='SMA20', linewidth=1, color='orange')
    ax.plot(data_to_plot['datetime'], data_to_plot['SMA50'], label='SMA50', linewidth=1, color='purple')

    # Add the legend and title
    ax.legend(loc='upper left')
    ax.set_title('BTC/USDT - Last 1000 Candles')

    # Add the grid
    ax.grid(True)

    # Show the plot
    plt.show()