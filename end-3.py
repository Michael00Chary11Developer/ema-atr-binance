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
        self.data['ATR'] = self.calculate_atr()

    def calculate_atr(self):
        tr = np.maximum(self.data['High'] - self.data['Low'], 
                        np.maximum(np.abs(self.data['High'] - self.data['Close'].shift(1)), 
                                   np.abs(self.data['Low'] - self.data['Close'].shift(1))))
        alpha = 1 / self.atr_period
        atr = [np.mean(tr[:self.atr_period])]
        for i in range(self.atr_period, len(tr)):
            atr.append((1 - alpha) * atr[-1] + alpha * tr[i])
        return pd.Series(atr, index=self.data.index)

    def reverse_cross_sell(self, current_index, lookback_period=90):
        if current_index < lookback_period:
            return False
        for i in range(current_index - lookback_period, current_index):
            if self.data.iloc[i]['FastEMA'] < self.data.iloc[i]['SlowEMA'] and \
               self.data.iloc[i + 1]['FastEMA'] >= self.data.iloc[i + 1]['SlowEMA']:
                return True
        return False

    def reverse_cross_buy(self, current_index, lookback_period=90):
        if current_index < lookback_period:
            return False
        for i in range(current_index - lookback_period, current_index):
            if self.data.iloc[i]['FastEMA'] > self.data.iloc[i]['SlowEMA'] and \
               self.data.iloc[i + 1]['FastEMA'] <= self.data.iloc[i + 1]['SlowEMA']:
                return True
        return False

    def check_signals(self):
        signals = []
        position_active = False
        entry_price = None

        for i in range(1, len(self.data)):
            current_row = self.data.iloc[i]
            atr_value = current_row['ATR']

            if not position_active:
                if self.reverse_cross_sell(i) and current_row['FastEMA'] < current_row['SlowEMA']:
                    entry_price = current_row['Close']
                    sl_price = entry_price + (self.sl_factor * atr_value)
                    tp_price = entry_price - (self.tp_factor * atr_value)
                    signals.append({
                        'signal': 'Sell Entry',
                        'entry_price': entry_price,
                        'stop_loss': sl_price,
                        'take_profit': tp_price,
                        'timestamp': current_row['Timestamp']
                    })
                    position_active = True

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
