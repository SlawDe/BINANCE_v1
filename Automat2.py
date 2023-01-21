import Automat_config
import ccxt
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
import tkinter as tk

def buy():
    global pair, df, order_type, amount, auto_trade_var
    order_type = 'buy'
    if auto_trade_var.get() == 1:
        predictions = model.predict(df[['sma_5','sma_20']].tail(1))
        if predictions == 1:
            order = binance.create_order(pair, 'market', 'buy', amount)
            message_label.config(text=f'Otwarto pozycję kupna dla {pair}, kwota: {amount}, cena: {df["close"].iloc[-1]}')
        else:
            message_label.config(text=f'Warunki nie zostały spełnione, pozycja nie została otwarta')
    else:
        if df['close'].iloc[-1] > df['sma_5'].iloc[-1] and df['sma_5'].iloc[-1] > df['sma_20'].iloc[-1]:
            order = binance.create_order(pair, 'market', 'buy', amount)
            message_label.config(text=f'Otwarto pozycję kupna dla {pair}, kwota: {amount}, cena: {df["close"].iloc[-1]}')
        else:
            message_label.config(text=f'Warunki nie zostały spełnione, pozycja nie została otwarta')

def sell():
    global pair, df, order_type, amount, auto_trade_var
    order_type = 'sell'
    if auto_trade_var.get() == 1:
        predictions = model.predict(df[['sma_5','sma_20']].tail(1))
        if predictions == 0:
            order = binance.create_order(pair, 'market', 'sell', amount)
            message_label.config(text=f'Otwarto pozycję sprzedaży dla {pair}, kwota: {amount}')

# Tworzenie obiektu giełdy
binance = ccxt.binance({
    'rateLimit': 2000,
    'enableRateLimit': True,
    'apiKey': Automat_config.API_KEY,
    'secret': Automat_config.SECRET_KEY,
})

# GUI
# Tworzenie okna aplikacji
root = tk.Tk()
root.title("Crypto Trader")

# Tworzenie przycisków i pola tekstowego
buy_button = tk.Button(root, text="Kup", command=buy)
sell_button = tk.Button(root, text="Sprzedaj", command=sell)
pair_entry = tk.Entry(root)
amount_entry = tk.Entry(root)
message_label = tk.Label(root, text='')
auto_trade_var = tk.IntVar(value=0)
auto_trade_checkbox = tk.Checkbutton(root, text="Automatyczny handel", variable=auto_trade_var)

# Umieszczanie elementów na oknie
buy_button.pack()
sell_button.pack()
pair_entry.pack()
amount_entry.pack()
auto_trade_checkbox.pack()
message_label.pack()

##################################
currency_var = tk.StringVar()
currency_var.set('BTC/USDT')

order_type = tk.StringVar()
order_type.set('buy')

amount = tk.DoubleVar()
amount.set(0.1)
##################################

# Pobranie danych historycznych dla wybranej pary walutowej
pair = currency_var.get()
ohlcv = binance.fetch_ohlcv(pair, '1M')

# Konwersja danych do DataFrame
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Konwersja timestampów na daty
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

# Analiza danych, np. wykres ceny
df['close'].plot()

# Dodanie kodu do analizy danych historycznych
# np. obliczanie średniej kroczącej
df['sma_5'] = df['close'].rolling(window=5).mean()
df['sma_20'] = df['close'].rolling(window=20).mean()
    
# Splitting dataset into train and test data
X_train, X_test, y_train, y_test = train_test_split(df[['sma_5','sma_20']], df['close'], test_size=0.3)
    
# Budowanie modelu sieci neuronowej
model = MLPClassifier()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
    
# Uruchomienie aplikacji
root.mainloop()