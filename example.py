import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import ccxt
import time
import datetime
import numpy as np
from binance.client import Client
class BaseStrategy:
    def __init__(self, data:pd.DataFrame, fast_ema=50, slow_ema=180, atr=200, tp_factor=8, sl_factor=7):
        self.data = data
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.atr_period = atr
        self.tp_factor = tp_factor
        self.sl_factor = sl_factor
        self.data['FastEMA'] = self.data['Close'].ewm(span=self.fast_ema, adjust=False).mean()
        self.data['SlowEMA'] = self.data['Close'].ewm(span=self.slow_ema, adjust=False).mean()
        self.data['FastOffset'] = self.data['Close'].ewm(span=self.fast_ema, adjust=False).mean().shift(200)
        self.data['SlowOffset'] = self.data['Close'].ewm(span=self.slow_ema, adjust=False).mean().shift(100)
        self.data['ATR'] = self.calculate_atr()
    def reverse_cross(self, current_index, lookback_period=90):
        if current_index < lookback_period:
            return False
        for i in range(current_index - lookback_period, current_index):
            if self.data.iloc[i]['FastOffset'] < self.data.iloc[i]['SlowOffset'] and \
               self.data.iloc[i + 1]['FastOffset'] >= self.data.iloc[i + 1]['SlowOffset']:
                return True
        return False
    def calculate_atr(self):
        high_low = self.data['High'] - self.data['Low']
        high_close = np.abs(self.data['High'] - self.data['Close'].shift(1))
        low_close = np.abs(self.data['Low'] - self.data['Close'].shift(1))
        tr = np.maximum(high_low, np.maximum(high_close, low_close))
        atr_rma = [None for _ in range(self.atr_period)]
        atr_rma.append(np.mean(tr[:self.atr_period]))
        alpha = 1.0 / self.atr_period
        print(len(atr_rma))
        for i in range(self.atr_period + 1 , len(tr)):
            atr_rma.append((1 - alpha) * atr_rma[i - 1] + alpha * tr.iloc[i])
        # print(len(atr_rma))
        return pd.Series(atr_rma, index=self.data.index)
    def check_signals(self):
        signals = []
        position_active = False
        entry_price = None
        for i in range(1, len(self.data)):
            current_row = self.data.iloc[i]
            previous_row = self.data.iloc[i - 1]
            atr_value = current_row['ATR']
            if not position_active and previous_row['FastOffset'] > previous_row['SlowOffset'] and \
               current_row['FastOffset'] <= current_row['SlowOffset']:
                if self.reverse_cross(i, lookback_period=90):
                    if current_row['FastEMA'] < current_row['SlowEMA']:
                        entry_price = current_row['Close']
                        sl_price = entry_price + (self.sl_factor * atr_value)
                        tp_price = entry_price - (self.tp_factor * atr_value)
                        position_active = True
                        signals.append({
                            'signal': 'Sell Entry',
                            'entry_price': entry_price,
                            'stop_loss': sl_price,
                            'take_profit': tp_price,
                            'reason': 'EMA Cross with Reverse Cross in last 90 candles, FastEMA below SlowEMA with offset, FastEMA below SlowEMA without offset',
                            'timestamp': current_row['Timestamp']
                        })
            if position_active:
                if current_row['High'] >= sl_price:
                    signals.append({
                        'signal': 'Sell Exit',
                        'exit_price': sl_price,
                        'exit_reason': 'Stop Loss Triggered',
                        'timestamp': current_row['Timestamp']
                    })
                    position_active = False
                    entry_price = None
                elif current_row['Low'] <= tp_price:
                    signals.append({
                        'signal': 'Sell Exit',
                        'exit_price': tp_price,
                        'exit_reason': 'Take Profit Triggered',
                        'timestamp': current_row['Timestamp']
                    })
                    position_active = False
                    entry_price = None
        return signals
    def plot_signals(self, signals, filename="chart.png"):
        fig = go.Figure(data=[go.Candlestick(x=self.data['Timestamp'],
                                            open=self.data['Open'],
                                            high=self.data['High'],
                                            low=self.data['Low'],
                                            close=self.data['Close'])])
        fig.update_layout(
            title='Bitcoin Price Candlestick Chart',
            xaxis_title='Timestamp',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False
        )
        fig.add_trace(go.Scatter(x=self.data['Timestamp'], y=self.data['FastEMA'], mode='lines', name='50-period EMA', line=dict(color='blue', width=2)))
        fig.add_trace(go.Scatter(x=self.data['Timestamp'], y=self.data['SlowEMA'], mode='lines', name='180-period EMA', line=dict(color='red', width=2)))
        fig.add_trace(go.Scatter(x=self.data['Timestamp'], y=self.data['FastOffset'], mode='lines', name='50-period EMA(offset)', line=dict(color='green', width=2)))
        fig.add_trace(go.Scatter(x=self.data['Timestamp'], y=self.data['SlowOffset'], mode='lines', name='180-period EMA(offset)', line=dict(color='black', width=2)))
        buy_signals = [signal for signal in signals if signal['signal'] == 'Sell Entry']
        sell_signals = [signal for signal in signals if signal['signal'] == 'Sell Exit']
        fig.add_trace(go.Scatter(
            x=[signal['timestamp'] for signal in buy_signals],
            y=[signal['entry_price'] for signal in buy_signals],
            mode='markers',
            name='Sell Entry',
            marker=dict(color='red', size=15, symbol='triangle-down')
        ))
        fig.add_trace(go.Scatter(
            x=[signal['timestamp'] for signal in sell_signals],
            y=[signal['exit_price'] for signal in sell_signals],
            mode='markers',
            name='Sell Exit',
            marker=dict(color='green', size=15, symbol='triangle-up')
        ))
        fig.write_image(filename)
        fig.show()
def fetch_bitcoin_data():
    df = pd.read_csv('BTCUSDT-5m.csv', usecols=[0, 1, 2, 3, 4, 5], names=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'], header=0)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms', errors='coerce')
    df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
    df['High'] = pd.to_numeric(df['High'], errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    df = df.dropna()
    return df
bitcoin_data = fetch_bitcoin_data()
bitcoin_data = bitcoin_data.tail(10000)
strategy = BaseStrategy(bitcoin_data)
signals = strategy.check_signals()
signals_df = pd.DataFrame(signals)
signals_df.to_csv('signals.csv', index=False)
strategy.plot_signals(signals, filename="bitcoin_chart.png")
print("Signals saved to signals.csv")
# strategy.calculate_atr()