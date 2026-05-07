import pandas as pd
from hft.strategies.base_futures_strategy import BaseFuturesStrategy

class NQFuturesStrategy(BaseFuturesStrategy):
    def __init__(self):
        super().__init__("NQ Futures - Momentum", "Bollinger Bands + MACD", "NQ")
        self.params = {'bb_period': 20, 'bb_std': 2}
    
    def generate_signals(self, df):
        df = df.copy()
        df['SMA'] = df['close'].rolling(20).mean()
        df['STD'] = df['close'].rolling(20).std()
        df['UPPER_BB'] = df['SMA'] + 2 * df['STD']
        df['LOWER_BB'] = df['SMA'] - 2 * df['STD']
        df['BUY'] = df['close'] > df['UPPER_BB']
        df['SELL'] = df['close'] < df['LOWER_BB']
        return df
    
    def get_parameters(self):
        return self.params
