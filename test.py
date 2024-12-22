import pandas as pd
import ccxt
import time
class BaseStrategy:
    def __init__(self, data, fast_ema=20, slow_ema=100, atr=200, take_profit_factor=1):
        self.data = data
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.atr_period = atr
        self.take_profit_factor = take_profit_factor
        # Calculate indicators
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
        position_active = False  
        entry_price = None       
        for i in range(1, len(self.data)):
            current_row = self.data.iloc[i]
            previous_row = self.data.iloc[i - 1]
            
            atr_value = current_row['ATR']
            if entry_price is not None:  
                sl_price = entry_price + atr_value
                tp_price = entry_price - (self.take_profit_factor * atr_value)
     
            if not position_active and previous_row['FastEMA'] > previous_row['SlowEMA'] and current_row['FastEMA'] <= current_row['SlowEMA']:
                entry_price = current_row['Close']
                sl_price = entry_price + atr_value
                tp_price = entry_price - (self.take_profit_factor * atr_value)
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
    
        all_data.extend(ohlcv)
        
        since = ohlcv[-1][0] + 1  
        time.sleep(1)  
    
    df = pd.DataFrame(all_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    return df
bitcoin_data = fetch_bitcoin_data()
strategy = BaseStrategy(bitcoin_data)
signals = strategy.check_signals()
for signal in signals:
    print(signal)