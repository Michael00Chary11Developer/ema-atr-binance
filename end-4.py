import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import plotly.graph_objects as go
# import ccxt
# import time
# import datetime
import numpy as np
# from binance.client import Client
class BaseStrategy:
    def __init__(self, data, fast_ema=50, slow_ema=180, atr=200, tp_factor=8, sl_factor=7):
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
        # self.data['Close'] = np.roll(self.data['Close'].values, -1)
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
        tr = []
        for i in range(len(self.data['High'])):
            if i == 0:
                last_close = self.data['Close'].iloc[-1]
                high_low = self.data['High'].iloc[i] - self.data['Low'].iloc[i]
                high_close = abs(self.data['High'].iloc[i] - last_close)
                low_close = abs(self.data['Low'].iloc[i] - last_close)
                tr.append(max(high_low, high_close, low_close))
                # tr.append(0)
            else:
                high_low = self.data['High'].iloc[i] - self.data['Low'].iloc[i]
                high_close = abs(self.data['High'].iloc[i] - self.data['Close'].iloc[i - 1])
                low_close = abs(self.data['Low'].iloc[i] - self.data['Close'].iloc[i - 1])
                tr.append(max(high_low, high_close, low_close))
            # print(tr[:5])
        atr_rma = [None for _ in range(self.atr_period-1)]
        atr_rma.append(np.mean(tr[:self.atr_period]))
        print(atr_rma[:200])
        alpha = 1.0 / self.atr_period
        for i in range(self.atr_period, len(tr)):
            atr_rma.append((1 - alpha) * atr_rma[i - 1] + alpha * tr[i])
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
                            'reason': 'EMA Cross',
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
        if filename == "btcusdt_chart.png":
            fig.update_layout(
                title='BTC Candlestick Chart',
                xaxis_title='Timestamp',
                yaxis_title='Price',
                xaxis_rangeslider_visible=False
            )
        elif filename == 'etcusdt_chart.png':
            fig.update_layout(
                title='ETH Candlestick Chart',
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
def fetch_data(filename):
    df = pd.read_csv(filename, usecols=[0, 1, 2, 3, 4, 5], names=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms', errors='coerce')
    df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
    df['High'] = pd.to_numeric(df['High'], errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    df = df.dropna()
    # print("DataFrame 1:")
    # print(btc.head(2000))
    # print("Columns:", btc.columns)
    # print("\nDataFrame 2:")
    # print(etc.head())
    # print("Columns:", etc.columns)
    return df
# data1
bitcoin_data = fetch_data('BTCUSDT-5m.csv')
bitcoin_data = bitcoin_data.tail(10000)
strategy_btc = BaseStrategy(bitcoin_data)
signals_btc = strategy_btc.check_signals()
signals_btc_df = pd.DataFrame(signals_btc)
signals_btc_df['symbol'] = 'BTCUSDT'
# signals_btc_df.to_csv('signals_btcusdt_data.csv', index=False)
strategy_btc.plot_signals(signals_btc, filename="btcusdt_chart.png")
# data2
ethusdt_data = fetch_data('ETHUSDT-5m.csv')
ethusdt_data = ethusdt_data.tail(10000)
strategy_eth = BaseStrategy(ethusdt_data)
signals_eth = strategy_eth.check_signals()
signals_eth_df = pd.DataFrame(signals_eth)
signals_eth_df['symbol'] = 'ETHUSDT'
# signals_eth_df.to_csv('signals_etcusdt_data.csv', index=False)
strategy_eth.plot_signals(signals_eth, filename="etcusdt_chart.png")
signals_df = pd.concat([signals_btc_df, signals_eth_df], ignore_index=True)
signals_df = signals_df.sort_values(by='timestamp', ascending=True)
signals_df.to_csv('signals_data.csv', index=False)
print("Signals datas saved to signals_data.csv")