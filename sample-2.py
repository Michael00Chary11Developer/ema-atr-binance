import pandas as pd
import matplotlib.pyplot as plt
import ccxt
import time
import datetime
from binance.client import Client
class BaseStrategy:
    def __init__(self, data, fast_ema=20, slow_ema=100, atr=200, tp_factor=8, sl_factor=7):
        self.data = data
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.atr_period = atr
        self.tp_factor = tp_factor
        self.sl_factor = sl_factor
        # Calculate indicators
        self.data['FastEMA'] = self.data['Close'].ewm(span=self.fast_ema, adjust=False).mean()
        self.data['SlowEMA'] = self.data['Close'].ewm(span=self.slow_ema, adjust=False).mean()
        self.data['FastEMA'] = self.apply_offset(self.data['FastEMA'], self.fast_ema)
        self.data['SlowEMA'] = self.apply_offset(self.data['SlowEMA'], self.slow_ema)
        self.data['ATR'] = self.calculate_atr()
    def calculate_atr(self):
        high_low = self.data['High'] - self.data['Low']
        high_close = abs(self.data['High'] - self.data['Close'].shift(1))
        low_close = abs(self.data['Low'] - self.data['Close'].shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=self.atr_period).mean()
    def check_signals(self):
        signals = []
        position_active = False  # Tracks if a position is active
        entry_price = None       # Stores the entry price of the active position
        for i in range(1, len(self.data)):
            current_row = self.data.iloc[i]
            previous_row = self.data.iloc[i - 1]
            # Calculate stop loss and take profit prices
            atr_value = current_row['ATR']
            if entry_price is not None:
                sl_price = entry_price + (self.sl_factor * atr_value)
                tp_price = entry_price - (self.tp_factor * atr_value)
            # Check for EMA Cross to enter a Sell position
            if not position_active and previous_row['FastEMA'] > previous_row['SlowEMA'] and current_row['FastEMA'] <= current_row['SlowEMA']:
                entry_price = current_row['Close']
                sl_price = entry_price + (self.sl_factor * atr_value)
                tp_price = entry_price - (self.tp_factor * atr_value)
                position_active = True  # Mark the position as active
                signals.append({
                    'signal': 'Sell Entry',
                    'entry_price': entry_price,
                    'stop_loss': sl_price,
                    'take_profit': tp_price,
                    'reason': 'EMA Cross',
                    'timestamp': current_row['Timestamp']
                })
            # Check for exit conditions only if a position is active
            if position_active:
                if current_row['High'] >= sl_price:
                    signals.append({
                        'signal': 'Sell Exit',
                        'exit_price': sl_price,
                        'exit_reason': 'Stop Loss Triggered',
                        'timestamp': current_row['Timestamp']
                    })
                    position_active = False  # Close the position
                    entry_price = None       # Reset entry price
                elif current_row['Low'] <= tp_price:
                    signals.append({
                        'signal': 'Sell Exit',
                        'exit_price': tp_price,
                        'exit_reason': 'Take Profit Triggered',
                        'timestamp': current_row['Timestamp']
                    })
                    position_active = False  # Close the position
                    entry_price = None       # Reset entry price
        return signals
    def plot_signals(self, signals, filename="chart.png"):
        # Plot the price and EMA lines
        plt.figure(figsize=(12,6))
        plt.plot(self.data['Timestamp'], self.data['Close'], label='Close Price', color='black', alpha=0.5)
        plt.plot(self.data['Timestamp'], self.data['FastEMA'], label='Fast EMA', color='blue')
        plt.plot(self.data['Timestamp'], self.data['SlowEMA'], label='Slow EMA', color='red')
        # Plot buy/sell signals
        buy_signals = [signal for signal in signals if signal['signal'] == 'Sell Entry']
        sell_signals = [signal for signal in signals if signal['signal'] == 'Sell Exit']
        # Plot buy signals (Entry)
        plt.scatter([signal['timestamp'] for signal in buy_signals],
                    [signal['entry_price'] for signal in buy_signals],
                    marker='^', color='green', label='Buy Signal', alpha=1)
        # Plot sell signals (Exit)
        plt.scatter([signal['timestamp'] for signal in sell_signals],
                    [signal['exit_price'] for signal in sell_signals],
                    marker='v', color='red', label='Sell Signal', alpha=1)
        plt.title('Bitcoin Price with Signals')
        plt.xlabel('Timestamp')
        plt.ylabel('Price')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        # Save the plot as PNG
        plt.savefig(filename)
        print(f"Chart saved as {filename}")
        plt.close()
# Fetch Bitcoin data using python-binance
def fetch_bitcoin_data():
    from binance.client import Client
    import pandas as pd
    client = Client()
    all_data = client.futures_klines(
        symbol='BTCUSDT',
        interval='5m',
        start_time = datetime.datetime(2024,1,1),
        limit=1000
    )
    selected_data = [row[:6] for row in all_data]
    columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
    df = pd.DataFrame(selected_data, columns=columns)
    # df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df['Open'] = pd.to_numeric(df['Open'])
    df['High'] = pd.to_numeric(df['High'])
    df['Low'] = pd.to_numeric(df['Low'])
    df['Close'] = pd.to_numeric(df['Close'])
    df['Volume'] = pd.to_numeric(df['Volume'])
    return df
# print(fetch_bitcoin_data())
# Fetch Bitcoin data
bitcoin_data = fetch_bitcoin_data()
# # Apply strategy
strategy = BaseStrategy(bitcoin_data)
signals = strategy.check_signals()
# # Convert signals to DataFrame
signals_df = pd.DataFrame(signals)
# # Save the signals to a CSV file
signals_df.to_csv('signals.csv', index=False)
strategy.plot_signals(signals, filename="bitcoin_chart3.png")
print("Signals saved to signals.csv")