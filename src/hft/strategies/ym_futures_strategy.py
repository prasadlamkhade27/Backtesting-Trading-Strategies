import pandas as pd
from hft.strategies.base_futures_strategy import BaseFuturesStrategy

class YMFuturesStrategy(BaseFuturesStrategy):
    def __init__(self):
        super().__init__("YM Futures - Trend Following", "MA Crossover", "YM")
        self.params = {'fast_ma': 10, 'slow_ma': 30}
    
    def generate_signals(self, df):
        df = df.copy()
        df['MA_FAST'] = df['close'].rolling(10).mean()
        df['MA_SLOW'] = df['close'].rolling(30).mean()
        df['BUY'] = (df['MA_FAST'] > df['MA_SLOW']) & (df['MA_FAST'].shift(1) <= df['MA_SLOW'].shift(1))
        df['SELL'] = (df['MA_FAST'] < df['MA_SLOW']) & (df['MA_FAST'].shift(1) >= df['MA_SLOW'].shift(1))
        return df
    
    def get_parameters(self):
        return self.params
