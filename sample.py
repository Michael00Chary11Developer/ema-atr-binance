import pandas as pd
import ccxt
import time
import matplotlib.pyplot as plt


class BaseStrategy:
    def __init__(self, data: pd.DataFrame, fast_ema=20, slow_ema=100, atr=200, take_profit_factor=1):
        self.data = data
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.atr_period = atr
        self.take_profit_factor = take_profit_factor
        # Calculate indicators
        self.data['FastEMA'] = self.data['Close'].ewm(
            span=self.fast_ema, adjust=False).mean().shift(20)
        self.data['SlowEMA'] = self.data['Close'].ewm(
            span=self.slow_ema, adjust=False).mean().shift(100)
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
            if entry_price is not None:  # Use the entry price if a position is active
                sl_price = entry_price + atr_value
                tp_price = entry_price - (self.take_profit_factor * atr_value)
            # Check for EMA Cross to enter a Sell position
            if not position_active and previous_row['FastEMA'] > previous_row['SlowEMA'] and current_row['FastEMA'] <= current_row['SlowEMA']:
                entry_price = current_row['Close']
                sl_price = entry_price + atr_value
                tp_price = entry_price - (self.take_profit_factor * atr_value)
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
                # Stop Loss Triggered
                if current_row['High'] >= sl_price:
                    signals.append({
                        'signal': 'Sell Exit',
                        'exit_price': sl_price,
                        'exit_reason': 'Stop Loss Triggered',
                        'timestamp': current_row['Timestamp']
                    })
                    position_active = False  # Close the position
                    entry_price = None       # Reset entry price
                # Take Profit Triggered
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
        plt.figure(figsize=(12, 6))
        plt.plot(self.data['Timestamp'], self.data['Close'],
                 label='Close Price', color='black', alpha=0.5)
        plt.plot(self.data['Timestamp'], self.data['FastEMA'],
                 label='Fast EMA', color='blue')
        plt.plot(self.data['Timestamp'], self.data['SlowEMA'],
                 label='Slow EMA', color='red')
        # Plot buy/sell signals
        buy_signals = [
            signal for signal in signals if signal['signal'] == 'Sell Entry']
        sell_signals = [
            signal for signal in signals if signal['signal'] == 'Sell Exit']
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
# Fetch Bitcoin data using ccxt


def fetch_bitcoin_data():
    exchange = ccxt.binance()
    symbol = 'BTC/USDT'
    timeframe = '1d'
    since = exchange.parse8601('2024-01-01T00:00:00Z')
    limit = 1000
    all_data = []
    while True:
        ohlcv = exchange.fetch_ohlcv(
            symbol, timeframe, since=since, limit=limit)
        if len(ohlcv) == 0:
            break
        # Append the data to the list
        all_data.extend(ohlcv)
        # Update the `since` parameter to the timestamp of the last data point
        since = ohlcv[-1][0] + 1  # Move to the next timestamp
        time.sleep(1)  # Sleep to avoid hitting the rate limit
    # Convert the data into a DataFrame
    df = pd.DataFrame(all_data, columns=[
                      'Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    return df


bitcoin_data = fetch_bitcoin_data()
strategy = BaseStrategy(bitcoin_data)
signals = strategy.check_signals()
# for signal in signals:
#     print(signal)
# Plot the signals on the chart and save it as PNG
strategy.plot_signals(signals, filename="bitcoin_signals_chart3.png")
