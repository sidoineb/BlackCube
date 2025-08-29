#!/usr/bin/env python3
"""
BlackCube - Bot d'évaluation et trading de cryptomonnaies
Version 2.0 - Interface graphique moderne avec analyses avancées
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AssetData:
    """Structure pour stocker les données d'un actif"""
    symbol: str
    name: str
    current_price: float
    change_24h: float
    data: Optional[pd.DataFrame] = None

class DataProvider:
    """Gestionnaire des données de marché"""
    
    def __init__(self):
        self.base_url_binance = 'https://api.binance.com/api/v3'
        self.base_url_metals = 'https://api.metals.live/v1/spot'  # API métaux (exemple)
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    def get_crypto_data(self, symbol: str, interval: str = '1d', days: int = 30) -> Optional[pd.DataFrame]:
        """Récupère les données d'une cryptomonnaie depuis Binance"""
        try:
            cache_key = f"{symbol}_{interval}_{days}"
            current_time = time.time()
            
            # Vérifier le cache
            if cache_key in self.cache:
                data, timestamp = self.cache[cache_key]
                if current_time - timestamp < self.cache_timeout:
                    return data
            
            # Requête API
            url = f'{self.base_url_binance}/klines'
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            params = {
                'symbol': symbol,
                'interval': interval,
                'startTime': start_time,
                'endTime': end_time,
                'limit': 1000
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Traitement des données
            data = pd.DataFrame(response.json(), columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Conversion des types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            
            data['datetime'] = pd.to_datetime(data['timestamp'], unit='ms')
            data = data.set_index('datetime')
            
            # Calcul des indicateurs techniques
            data = self._calculate_indicators(data)
            
            # Mise en cache
            self.cache[cache_key] = (data, current_time)
            
            return data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de {symbol}: {e}")
            return None
    
    def _calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcule les indicateurs techniques"""
        try:
            # Moyennes mobiles
            data['SMA_9'] = data['close'].rolling(window=9).mean()
            data['SMA_20'] = data['close'].rolling(window=20).mean()
            data['SMA_50'] = data['close'].rolling(window=50).mean()
            
            # EMA
            data['EMA_12'] = data['close'].ewm(span=12).mean()
            data['EMA_26'] = data['close'].ewm(span=26).mean()
            
            # MACD
            data['MACD'] = data['EMA_12'] - data['EMA_26']
            data['MACD_signal'] = data['MACD'].ewm(span=9).mean()
            data['MACD_histogram'] = data['MACD'] - data['MACD_signal']
            
            # RSI
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # Bandes de Bollinger
            data['BB_middle'] = data['close'].rolling(window=20).mean()
            bb_std = data['close'].rolling(window=20).std()
            data['BB_upper'] = data['BB_middle'] + (bb_std * 2)
            data['BB_lower'] = data['BB_middle'] - (bb_std * 2)
            
            return data
            
        except Exception as e:
            logger.error(f"Erreur calcul indicateurs: {e}")
            return data
    
    def get_current_price(self, symbol: str) -> Optional[AssetData]:
        """Récupère le prix actuel d'un actif"""
        try:
            url = f'{self.base_url_binance}/ticker/24hr'
            params = {'symbol': symbol}
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            return AssetData(
                symbol=symbol,
                name=symbol.replace('USDT', ''),
                current_price=float(data['lastPrice']),
                change_24h=float(data['priceChangePercent'])
            )
            
        except Exception as e:
            logger.error(f"Erreur prix actuel {symbol}: {e}")
            return None

class SplashScreen:
    """Écran de démarrage moderne"""
    
    def __init__(self, main_callback):
        self.main_callback = main_callback
        self.root = tk.Toplevel()
        self.setup_splash()
        self.animate()
    
    def setup_splash(self):
        """Configure l'écran de démarrage"""
        self.root.title("BlackCube")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.configure(bg='#0d1117')
        
        # Centrer la fenêtre
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 400) // 2
        y = (self.root.winfo_screenheight() - 300) // 2
        self.root.geometry(f"400x300+{x}+{y}")
        
        # Supprimer les décorations
        self.root.overrideredirect(True)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#0d1117')
        main_frame.pack(fill='both', expand=True)
        
        # Logo/Titre
        title_label = tk.Label(
            main_frame,
            text="⬛ BLACK CUBE",
            font=('Arial', 24, 'bold'),
            fg='#00d4ff',
            bg='#0d1117'
        )
        title_label.pack(pady=50)
        
        # Sous-titre
        subtitle_label = tk.Label(
            main_frame,
            text="Analyse et Trading de Cryptomonnaies",
            font=('Arial', 12),
            fg='#8b949e',
            bg='#0d1117'
        )
        subtitle_label.pack()
        
        # Barre de progression
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=300,
            mode='determinate'
        )
        progress_bar.pack(pady=30)
        
        # Status
        self.status_label = tk.Label(
            main_frame,
            text="Initialisation...",
            font=('Arial', 10),
            fg='#8b949e',
            bg='#0d1117'
        )
        self.status_label.pack()
        
        # Version
        version_label = tk.Label(
            main_frame,
            text="Version 2.0",
            font=('Arial', 8),
            fg='#6e7681',
            bg='#0d1117'
        )
        version_label.pack(side='bottom', pady=10)
    
    def animate(self):
        """Animation de chargement"""
        steps = [
            (20, "Chargement des modules..."),
            (40, "Connexion aux APIs..."),
            (60, "Initialisation des graphiques..."),
            (80, "Configuration de l'interface..."),
            (100, "Démarrage de BlackCube...")
        ]
        
        def animate_step(index):
            if index < len(steps):
                progress, status = steps[index]
                self.progress_var.set(progress)
                self.status_label.config(text=status)
                self.root.after(500, lambda: animate_step(index + 1))
            else:
                self.root.after(1000, self.close_splash)
        
        animate_step(0)
    
    def close_splash(self):
        """Ferme le splash et lance l'application principale"""
        self.root.destroy()
        self.main_callback()

class ChartWidget:
    """Widget graphique avancé"""
    
    def __init__(self, parent):
        self.parent = parent
        self.figure = Figure(figsize=(12, 8), dpi=100, facecolor='#0d1117')
        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().configure(bg='#0d1117')
        
        # Style sombre
        plt.style.use('dark_background')
        
    def plot_candlestick(self, data: pd.DataFrame, symbol: str, indicators: List[str] = None):
        """Affiche un graphique en chandeliers avec indicateurs"""
        try:
            self.figure.clear()
            
            # Configuration des subplots
            if indicators and any(ind in ['RSI', 'MACD'] for ind in indicators):
                gs = self.figure.add_gridspec(3, 1, height_ratios=[3, 1, 1], hspace=0.3)
                ax_main = self.figure.add_subplot(gs[0])
                ax_rsi = self.figure.add_subplot(gs[1]) if 'RSI' in indicators else None
                ax_macd = self.figure.add_subplot(gs[2]) if 'MACD' in indicators else None
            else:
                ax_main = self.figure.add_subplot(111)
                ax_rsi = ax_macd = None
            
            # Graphique principal - Chandeliers
            self._plot_candlesticks(ax_main, data)
            
            # Indicateurs sur le graphique principal
            if indicators:
                self._plot_main_indicators(ax_main, data, indicators)
            
            # RSI
            if ax_rsi and 'RSI' in indicators:
                self._plot_rsi(ax_rsi, data)
            
            # MACD
            if ax_macd and 'MACD' in indicators:
                self._plot_macd(ax_macd, data)
            
            # Configuration générale
            ax_main.set_title(f'{symbol} - Analyse Technique', 
                            color='white', fontsize=14, fontweight='bold')
            ax_main.grid(True, alpha=0.3)
            ax_main.set_facecolor('#0d1117')
            
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Erreur affichage graphique: {e}")
    
    def _plot_candlesticks(self, ax, data):
        """Dessine les chandeliers"""
        # Conversion pour matplotlib
        ohlc_data = data.reset_index()
        ohlc_data['datetime_num'] = mdates.date2num(ohlc_data['datetime'])
        
        # Chandeliers manuels pour plus de contrôle
        for idx, row in ohlc_data.iterrows():
            date = row['datetime_num']
            open_price, high, low, close = row['open'], row['high'], row['low'], row['close']
            
            # Couleur selon la tendance
            color = '#00ff88' if close >= open_price else '#ff4444'
            
            # Corps du chandelier
            height = abs(close - open_price)
            bottom = min(close, open_price)
            ax.bar(date, height, bottom=bottom, width=0.6, color=color, alpha=0.8)
            
            # Mèches
            ax.plot([date, date], [low, high], color=color, linewidth=1)
        
        # Format des dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    
    def _plot_main_indicators(self, ax, data, indicators):
        """Affiche les indicateurs sur le graphique principal"""
        if 'SMA_20' in indicators and 'SMA_20' in data.columns:
            ax.plot(data.index, data['SMA_20'], label='SMA 20', color='#ffaa00', linewidth=1.5)
        
        if 'SMA_50' in indicators and 'SMA_50' in data.columns:
            ax.plot(data.index, data['SMA_50'], label='SMA 50', color='#ff6600', linewidth=1.5)
        
        if 'BB_upper' in indicators and all(col in data.columns for col in ['BB_upper', 'BB_lower', 'BB_middle']):
            ax.plot(data.index, data['BB_upper'], color='#888888', alpha=0.7, linewidth=1)
            ax.plot(data.index, data['BB_lower'], color='#888888', alpha=0.7, linewidth=1)
            ax.fill_between(data.index, data['BB_upper'], data['BB_lower'], 
                          alpha=0.1, color='gray', label='Bollinger Bands')
        
        ax.legend(loc='upper left')
    
    def _plot_rsi(self, ax, data):
        """Affiche le RSI"""
        if 'RSI' in data.columns:
            ax.plot(data.index, data['RSI'], color='#00aaff', linewidth=2)
            ax.axhline(y=70, color='red', linestyle='--', alpha=0.7)
            ax.axhline(y=30, color='green', linestyle='--', alpha=0.7)
            ax.fill_between(data.index, 30, 70, alpha=0.1, color='gray')
            ax.set_ylabel('RSI', color='white')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#0d1117')
    
    def _plot_macd(self, ax, data):
        """Affiche le MACD"""
        if all(col in data.columns for col in ['MACD', 'MACD_signal', 'MACD_histogram']):
            ax.plot(data.index, data['MACD'], color='#00aaff', label='MACD', linewidth=1.5)
            ax.plot(data.index, data['MACD_signal'], color='#ff6600', label='Signal', linewidth=1.5)
            ax.bar(data.index, data['MACD_histogram'], color='gray', alpha=0.6, 
                  width=0.8, label='Histogram')
            ax.axhline(y=0, color='white', linestyle='-', alpha=0.5)
            ax.legend(loc='upper left')
            ax.set_ylabel('MACD', color='white')
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#0d1117')
    
    def get_widget(self):
        """Retourne le widget canvas"""
        return self.canvas.get_tk_widget()

class BlackCubeApp:
    """Application principale BlackCube"""
    
    def __init__(self):
        self.root = None
        self.data_provider = DataProvider()
        self.current_symbol = "BTCUSDT"
        self.chart_widget = None
        self.watchlist = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "AVAXUSDT", "DOGEUSDT"]
        self.auto_refresh = tk.BooleanVar(value=True)
        self.refresh_interval = 60  # secondes
        self.setup_styles()
        
    def setup_styles(self):
        """Configure les styles personnalisés"""
        self.colors = {
            'bg_primary': '#0d1117',
            'bg_secondary': '#161b22',
            'bg_tertiary': '#21262d',
            'accent': '#00d4ff',
            'text_primary': '#f0f6fc',
            'text_secondary': '#8b949e',
            'success': '#00ff88',
            'error': '#ff4444',
            'warning': '#ffaa00'
        }
    
    def start_app(self):
        """Démarre l'application après le splash screen"""
        SplashScreen(self.create_main_window)
    
    def create_main_window(self):
        """Crée la fenêtre principale"""
        self.root = tk.Tk()
        self.root.title("⬛ BlackCube - Trading & Analysis")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Configuration de la grille
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        self.create_menu()
        self.create_toolbar()
        self.create_main_layout()
        self.create_status_bar()
        
        # Démarrer la mise à jour automatique
        self.start_auto_refresh()
        
        # Charger le premier graphique
        self.load_chart(self.current_symbol)
        
        self.root.mainloop()
    
    def create_menu(self):
        """Crée la barre de menu"""
        menubar = tk.Menu(self.root, bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        file_menu.add_command(label="Exporter données", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Menu Cryptos
        crypto_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        crypto_symbols = [
            ("Bitcoin (BTC)", "BTCUSDT"),
            ("Ethereum (ETH)", "ETHUSDT"),
            ("Cardano (ADA)", "ADAUSDT"),
            ("Solana (SOL)", "SOLUSDT"),
            ("Avalanche (AVAX)", "AVAXUSDT"),
            ("Dogecoin (DOGE)", "DOGEUSDT")
        ]
        
        for name, symbol in crypto_symbols:
            crypto_menu.add_command(label=name, command=lambda s=symbol: self.load_chart(s))
        
        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        tools_menu.add_checkbutton(label="Actualisation auto", variable=self.auto_refresh)
        tools_menu.add_command(label="Paramètres", command=self.show_settings)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        help_menu.add_command(label="À propos", command=self.show_about)
        
        menubar.add_cascade(label="Fichier", menu=file_menu)
        menubar.add_cascade(label="Cryptos", menu=crypto_menu)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        menubar.add_cascade(label="Aide", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=50)
        toolbar.grid(row=0, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        toolbar.grid_propagate(False)
        
        # Sélection de symbole
        tk.Label(toolbar, text="Actif:", bg=self.colors['bg_secondary'], 
                fg=self.colors['text_primary']).pack(side='left', padx=5)
        
        self.symbol_var = tk.StringVar(value=self.current_symbol)
        symbol_combo = ttk.Combobox(toolbar, textvariable=self.symbol_var, 
                                   values=self.watchlist, state='readonly', width=15)
        symbol_combo.pack(side='left', padx=5)
        symbol_combo.bind('<<ComboboxSelected>>', self.on_symbol_change)
        
        # Boutons
        refresh_btn = tk.Button(toolbar, text="🔄 Actualiser", 
                               command=lambda: self.load_chart(self.current_symbol),
                               bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'])
        refresh_btn.pack(side='left', padx=5)
        
        # Indicateurs
        tk.Label(toolbar, text="Indicateurs:", bg=self.colors['bg_secondary'], 
                fg=self.colors['text_primary']).pack(side='left', padx=(20, 5))
        
        self.indicators_frame = tk.Frame(toolbar, bg=self.colors['bg_secondary'])
        self.indicators_frame.pack(side='left', padx=5)
        
        # Variables pour les indicateurs
        self.show_sma = tk.BooleanVar(value=True)
        self.show_rsi = tk.BooleanVar(value=True)
        self.show_macd = tk.BooleanVar(value=True)
        self.show_bb = tk.BooleanVar(value=False)
        
        # Checkboxes indicateurs
        indicators = [
            ("SMA", self.show_sma),
            ("RSI", self.show_rsi),
            ("MACD", self.show_macd),
            ("Bollinger", self.show_bb)
        ]
        
        for name, var in indicators:
            cb = tk.Checkbutton(self.indicators_frame, text=name, variable=var,
                               command=lambda: self.load_chart(self.current_symbol),
                               bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                               selectcolor=self.colors['bg_tertiary'])
            cb.pack(side='left', padx=3)
    
    def create_main_layout(self):
        """Crée la disposition principale"""
        # Panel de gauche - Watchlist
        left_panel = tk.Frame(self.root, bg=self.colors['bg_secondary'], width=250)
        left_panel.grid(row=1, column=0, sticky='ns', padx=(5, 2), pady=5)
        left_panel.grid_propagate(False)
        
        self.create_watchlist_panel(left_panel)
        
        # Panel central - Graphique
        chart_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        chart_frame.grid(row=1, column=1, sticky='nsew', padx=2, pady=5)
        
        self.chart_widget = ChartWidget(chart_frame)
        self.chart_widget.get_widget().pack(fill='both', expand=True)
        
        # Panel de droite - Infos
        right_panel = tk.Frame(self.root, bg=self.colors['bg_secondary'], width=200)
        right_panel.grid(row=1, column=2, sticky='ns', padx=(2, 5), pady=5)
        right_panel.grid_propagate(False)
        
        self.create_info_panel(right_panel)
    
    def create_watchlist_panel(self, parent):
        """Crée le panel de watchlist"""
        title = tk.Label(parent, text="📊 WATCHLIST", font=('Arial', 12, 'bold'),
                        bg=self.colors['bg_secondary'], fg=self.colors['accent'])
        title.pack(pady=10)
        
        # Frame pour la liste
        list_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Listbox
        self.watchlist_box = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                       bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'],
                                       selectbackground=self.colors['accent'],
                                       font=('Courier', 10))
        self.watchlist_box.pack(side='left', fill='both', expand=True)
        self.watchlist_box.bind('<Double-1>', self.on_watchlist_select)
        
        scrollbar.config(command=self.watchlist_box.yview)
        
        # Boutons de gestion
        btn_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        add_btn = tk.Button(btn_frame, text="+ Ajouter", command=self.add_to_watchlist,
                           bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'],
                           font=('Arial', 9))
        add_btn.pack(fill='x', pady=2)
        
        # Remplir la watchlist initiale
        self.update_watchlist()
    
    def create_info_panel(self, parent):
        """Crée le panel d'informations"""
        title = tk.Label(parent, text="📈 INFOS MARCHÉ", font=('Arial', 12, 'bold'),
                        bg=self.colors['bg_secondary'], fg=self.colors['accent'])
        title.pack(pady=10)
        
        # Frame pour les infos
        self.info_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        self.info_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Labels pour les informations
        self.price_label = tk.Label(self.info_frame, text="Prix: -", font=('Courier', 11, 'bold'),
                                   bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        self.price_label.pack(anchor='w', pady=2)
        
        self.change_label = tk.Label(self.info_frame, text="Variation 24h: -", font=('Courier', 10),
                                    bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
        self.change_label.pack(anchor='w', pady=2)
        
        # Séparateur
        separator = tk.Frame(self.info_frame, height=2, bg=self.colors['bg_tertiary'])
        separator.pack(fill='x', pady=10)
        
        # Statistiques techniques
        self.stats_label = tk.Label(self.info_frame, text="ANALYSE TECHNIQUE", font=('Arial', 10, 'bold'),
                                   bg=self.colors['bg_secondary'], fg=self.colors['accent'])
        self.stats_label.pack(anchor='w', pady=(0, 5))
        
        self.rsi_label = tk.Label(self.info_frame, text="RSI: -", font=('Courier', 9),
                                 bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
        self.rsi_label.pack(anchor='w', pady=1)
        
        self.macd_label = tk.Label(self.info_frame, text="MACD: -", font=('Courier', 9),
                                  bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
        self.macd_label.pack(anchor='w', pady=1)
    
    def create_status_bar(self):
        """Crée la barre de statut"""
        self.status_bar = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=25)
        self.status_bar.grid(row=2, column=0, columnspan=3, sticky='ew', padx=5)
        self.status_bar.grid_propagate(False)
        
        # Status text
        self.status_text = tk.Label(self.status_bar, text="Prêt", 
                                   bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                                   font=('Arial', 9))
        self.status_text.pack(side='left', padx=10, pady=2)
        
        # Dernière mise à jour
        self.last_update_label = tk.Label(self.status_bar, text="", 
                                         bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                                         font=('Arial', 9))
        self.last_update_label.pack(side='right', padx=10, pady=2)
    
    def on_symbol_change(self, event):
        """Gestionnaire de changement de symbole"""
        new_symbol = self.symbol_var.get()
        if new_symbol != self.current_symbol:
            self.current_symbol = new_symbol
            self.load_chart(new_symbol)
    
    def on_watchlist_select(self, event):
        """Gestionnaire de sélection dans la watchlist"""
        selection = self.watchlist_box.curselection()
        if selection:
            item_text = self.watchlist_box.get(selection[0])
            # Extraire le symbole (format: "BTC $45,123 +2.34%")
            symbol = item_text.split()[0] + "USDT"
            self.current_symbol = symbol
            self.symbol_var.set(symbol)
            self.load_chart(symbol)
    
    def load_chart(self, symbol):
        """Charge et affiche le graphique pour un symbole"""
        def load_data():
            try:
                self.status_text.config(text=f"Chargement de {symbol}...")
                self.root.update_idletasks()
                
                # Récupération des données
                data = self.data_provider.get_crypto_data(symbol)
                if data is None:
                    raise Exception("Impossible de récupérer les données")
                
                # Préparation des indicateurs à afficher
                indicators = []
                if self.show_sma.get():
                    indicators.extend(['SMA_20', 'SMA_50'])
                if self.show_bb.get():
                    indicators.extend(['BB_upper'])
                if self.show_rsi.get():
                    indicators.append('RSI')
                if self.show_macd.get():
                    indicators.append('MACD')
                
                # Affichage du graphique
                self.chart_widget.plot_candlestick(data, symbol, indicators)
                
                # Mise à jour des informations
                self.update_info_panel(symbol, data)
                
                self.status_text.config(text=f"{symbol} chargé avec succès")
                self.last_update_label.config(text=f"Mis à jour: {datetime.now().strftime('%H:%M:%S')}")
                
            except Exception as e:
                self.status_text.config(text=f"Erreur: {str(e)}")
                logger.error(f"Erreur chargement {symbol}: {e}")
                messagebox.showerror("Erreur", f"Impossible de charger {symbol}:\n{str(e)}")
        
        # Lancer en thread pour éviter de bloquer l'interface
        threading.Thread(target=load_data, daemon=True).start()
    
    def update_info_panel(self, symbol, data):
        """Met à jour le panel d'informations"""
        try:
            # Prix actuel et variation
            current_price = data['close'].iloc[-1]
            prev_price = data['close'].iloc[-2] if len(data) > 1 else current_price
            change_pct = ((current_price - prev_price) / prev_price) * 100
            
            # Mise à jour des labels
            self.price_label.config(text=f"Prix: ${current_price:,.2f}")
            
            change_color = self.colors['success'] if change_pct >= 0 else self.colors['error']
            change_sign = "+" if change_pct >= 0 else ""
            self.change_label.config(text=f"Variation 24h: {change_sign}{change_pct:.2f}%", 
                                   fg=change_color)
            
            # Indicateurs techniques
            if 'RSI' in data.columns:
                rsi_value = data['RSI'].iloc[-1]
                rsi_color = (self.colors['error'] if rsi_value > 70 else 
                           self.colors['success'] if rsi_value < 30 else 
                           self.colors['text_secondary'])
                self.rsi_label.config(text=f"RSI: {rsi_value:.1f}", fg=rsi_color)
            
            if 'MACD' in data.columns:
                macd_value = data['MACD'].iloc[-1]
                macd_signal = data['MACD_signal'].iloc[-1]
                macd_trend = "Haussier" if macd_value > macd_signal else "Baissier"
                macd_color = self.colors['success'] if macd_value > macd_signal else self.colors['error']
                self.macd_label.config(text=f"MACD: {macd_trend}", fg=macd_color)
            
        except Exception as e:
            logger.error(f"Erreur mise à jour info panel: {e}")
    
    def update_watchlist(self):
        """Met à jour la watchlist avec les prix actuels"""
        def update_prices():
            try:
                self.watchlist_box.delete(0, tk.END)
                
                for symbol in self.watchlist:
                    try:
                        asset_data = self.data_provider.get_current_price(symbol)
                        if asset_data:
                            price_str = f"${asset_data.current_price:,.2f}"
                            change_str = f"{asset_data.change_24h:+.2f}%"
                            item_text = f"{asset_data.name:<6} {price_str:>10} {change_str:>8}"
                            self.watchlist_box.insert(tk.END, item_text)
                        else:
                            self.watchlist_box.insert(tk.END, f"{symbol}: Erreur")
                    except Exception as e:
                        logger.error(f"Erreur mise à jour {symbol}: {e}")
                        self.watchlist_box.insert(tk.END, f"{symbol}: N/A")
                        
            except Exception as e:
                logger.error(f"Erreur mise à jour watchlist: {e}")
        
        threading.Thread(target=update_prices, daemon=True).start()
    
    def start_auto_refresh(self):
        """Démarre la mise à jour automatique"""
        def auto_update():
            if self.auto_refresh.get():
                self.update_watchlist()
                # Recharger le graphique actuel si nécessaire
                if hasattr(self, 'current_symbol'):
                    # Ne recharge que si l'utilisateur n'interagit pas
                    self.load_chart(self.current_symbol)
            
            # Programmer la prochaine mise à jour
            self.root.after(self.refresh_interval * 1000, auto_update)
        
        # Démarrer après 5 secondes
        self.root.after(5000, auto_update)
    
    def add_to_watchlist(self):
        """Ajoute un nouveau symbole à la watchlist"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter un actif")
        dialog.geometry("300x150")
        dialog.configure(bg=self.colors['bg_primary'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 300) // 2
        y = (dialog.winfo_screenheight() - 150) // 2
        dialog.geometry(f"300x150+{x}+{y}")
        
        tk.Label(dialog, text="Symbole (ex: ADAUSDT):", 
                bg=self.colors['bg_primary'], fg=self.colors['text_primary']).pack(pady=10)
        
        entry = tk.Entry(dialog, font=('Arial', 12), width=20)
        entry.pack(pady=5)
        entry.focus()
        
        def add_symbol():
            symbol = entry.get().upper().strip()
            if symbol and symbol not in self.watchlist:
                # Vérifier si le symbole existe
                test_data = self.data_provider.get_current_price(symbol)
                if test_data:
                    self.watchlist.append(symbol)
                    self.update_watchlist()
                    dialog.destroy()
                    messagebox.showinfo("Succès", f"{symbol} ajouté à la watchlist")
                else:
                    messagebox.showerror("Erreur", f"Symbole {symbol} non trouvé")
            elif symbol in self.watchlist:
                messagebox.showwarning("Attention", f"{symbol} déjà dans la watchlist")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['bg_primary'])
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Ajouter", command=add_symbol,
                 bg=self.colors['accent'], fg='white').pack(side='left', padx=5)
        tk.Button(btn_frame, text="Annuler", command=dialog.destroy,
                 bg=self.colors['bg_tertiary'], fg=self.colors['text_primary']).pack(side='left', padx=5)
        
        entry.bind('<Return>', lambda e: add_symbol())
    
    def export_data(self):
        """Exporte les données actuelles"""
        try:
            if not hasattr(self, 'current_symbol'):
                messagebox.showwarning("Attention", "Aucune donnée à exporter")
                return
            
            data = self.data_provider.get_crypto_data(self.current_symbol)
            if data is None:
                messagebox.showerror("Erreur", "Impossible de récupérer les données")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")],
                title="Exporter les données"
            )
            
            if filename:
                if filename.endswith('.xlsx'):
                    data.to_excel(filename)
                else:
                    data.to_csv(filename)
                messagebox.showinfo("Succès", f"Données exportées vers {filename}")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def show_settings(self):
        """Affiche les paramètres"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Paramètres")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.colors['bg_primary'])
        settings_window.transient(self.root)
        
        # Centrer la fenêtre
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() - 400) // 2
        y = (settings_window.winfo_screenheight() - 300) // 2
        settings_window.geometry(f"400x300+{x}+{y}")
        
        # Titre
        title = tk.Label(settings_window, text="⚙️ PARAMÈTRES", font=('Arial', 16, 'bold'),
                        bg=self.colors['bg_primary'], fg=self.colors['accent'])
        title.pack(pady=20)
        
        # Frame pour les paramètres
        params_frame = tk.Frame(settings_window, bg=self.colors['bg_primary'])
        params_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Intervalle de mise à jour
        tk.Label(params_frame, text="Intervalle de mise à jour (secondes):",
                bg=self.colors['bg_primary'], fg=self.colors['text_primary']).pack(anchor='w', pady=5)
        
        interval_var = tk.IntVar(value=self.refresh_interval)
        interval_scale = tk.Scale(params_frame, from_=10, to=300, orient='horizontal',
                                 variable=interval_var, bg=self.colors['bg_secondary'],
                                 fg=self.colors['text_primary'], highlightthickness=0)
        interval_scale.pack(fill='x', pady=5)
        
        # Boutons
        btn_frame = tk.Frame(settings_window, bg=self.colors['bg_primary'])
        btn_frame.pack(pady=20)
        
        def save_settings():
            self.refresh_interval = interval_var.get()
            messagebox.showinfo("Paramètres", "Paramètres sauvegardés")
            settings_window.destroy()
        
        tk.Button(btn_frame, text="Sauvegarder", command=save_settings,
                 bg=self.colors['accent'], fg='white', font=('Arial', 10)).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Annuler", command=settings_window.destroy,
                 bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'], 
                 font=('Arial', 10)).pack(side='left', padx=5)
    
    def show_about(self):
        """Affiche la fenêtre À propos"""
        about_window = tk.Toplevel(self.root)
        about_window.title("À propos de BlackCube")
        about_window.geometry("500x400")
        about_window.configure(bg=self.colors['bg_primary'])
        about_window.transient(self.root)
        about_window.resizable(False, False)
        
        # Centrer la fenêtre
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() - 500) // 2
        y = (about_window.winfo_screenheight() - 400) // 2
        about_window.geometry(f"500x400+{x}+{y}")
        
        # Logo et titre
        title_frame = tk.Frame(about_window, bg=self.colors['bg_primary'])
        title_frame.pack(pady=30)
        
        tk.Label(title_frame, text="⬛", font=('Arial', 48),
                bg=self.colors['bg_primary'], fg=self.colors['accent']).pack()
        
        tk.Label(title_frame, text="BLACK CUBE", font=('Arial', 20, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['accent']).pack()
        
        tk.Label(title_frame, text="Version 2.0", font=('Arial', 12),
                bg=self.colors['bg_primary'], fg=self.colors['text_secondary']).pack()
        
        # Description
        desc_frame = tk.Frame(about_window, bg=self.colors['bg_primary'])
        desc_frame.pack(pady=20, padx=30)
        
        description = """Bot d'évaluation et de trading de cryptomonnaies
        
Fonctionnalités:
• Analyse technique avancée
• Graphiques en temps réel
• Indicateurs multiples (RSI, MACD, SMA)
• Watchlist personnalisable
• Export de données
• Interface moderne et intuitive

Développé avec Python, Tkinter et Matplotlib
Données fournies par l'API Binance"""
        
        tk.Label(desc_frame, text=description, font=('Arial', 10),
                bg=self.colors['bg_primary'], fg=self.colors['text_primary'],
                justify='left').pack()
        
        # Copyright
        tk.Label(about_window, text="© 2024 - Sous licence GNU GPL v3",
                font=('Arial', 9), bg=self.colors['bg_primary'], 
                fg=self.colors['text_secondary']).pack(side='bottom', pady=20)
        
        # Bouton fermer
        tk.Button(about_window, text="Fermer", command=about_window.destroy,
                 bg=self.colors['accent'], fg='white', font=('Arial', 10)).pack(side='bottom', pady=10)

def main():
    """Point d'entrée principal"""
    try:
        app = BlackCubeApp()
        app.start_app()
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
        messagebox.showerror("Erreur critique", f"Impossible de démarrer BlackCube:\n{str(e)}")

if __name__ == "__main__":
    main()