import pandas as pd
import ccxt
import time

class BaseStrategy:
    def __init__(self, data, fast_ema=50, slow_ema=180, atr=200, tp_factor=8, sl_factor=7):
        self.data = data
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.atr_period = atr
        self.tp_factor = tp_factor
        self.sl_factor = sl_factor
        # Calculate indicators
        # Evm Exponential Moving Average
        self.data['FastEMA'] = self.data['Close'].ewm(span=self.fast_ema, adjust=False).mean()
        self.data['SlowEMA'] = self.data['Close'].rolling(window=self.slow_ema).mean()
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
# Fetch Bitcoin data using ccxt
def fetch_bitcoin_data():
    exchange = ccxt.binance()
    symbol = 'BTC/USDT'
    timeframe = '5m'
    since = exchange.parse8601('2024-01-01T00:00:00Z')
    limit = 1000
    all_data = []
    while True:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
        if len(ohlcv) == 0:
            break
        # Append the data to the list
        all_data.extend(ohlcv)
        # Update the `since` parameter to the timestamp of the last data point
        since = ohlcv[-1][0] + 1  # Move to the next timestamp
        time.sleep(1)  # Sleep to avoid hitting the rate limit
    # Convert the data into a DataFrame
    df = pd.DataFrame(all_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    return df
# Fetch Bitcoin data
bitcoin_data = fetch_bitcoin_data()
# Apply strategy
strategy = BaseStrategy(bitcoin_data)
signals = strategy.check_signals()
# Convert signals to DataFrame
signals_df = pd.DataFrame(signals)
# Save the signals to a CSV file
signals_df.to_csv('signals.csv', index=False)
print("Signals saved to signals.csv")