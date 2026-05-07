import pandas as pd
import numpy as np
from hft.strategies.base_futures_strategy import BaseFuturesStrategy

class ESFuturesStrategy(BaseFuturesStrategy):
    def __init__(self):
        super().__init__("ES Futures - Mean Reversion + Trend", "Combines RSI mean reversion with trend", "ES")
        self.params = {'rsi_period': 14, 'rsi_oversold': 30, 'rsi_overbought': 70, 'sma_fast': 20, 'sma_slow': 50, 'atr_period': 14}
    
    def generate_signals(self, df):
        df = df.copy()
        df['RSI'] = self._rsi(df['close'], 14)
        df['SMA_20'] = df['close'].rolling(20).mean()
        df['SMA_50'] = df['close'].rolling(50).mean()
        df['BUY'] = False
        df['SELL'] = False
        
        for i in range(50, len(df)):
            if pd.isna(df['RSI'].iloc[i]):
                continue
            rsi = df['RSI'].iloc[i]
            price = df['close'].iloc[i]
            sma20 = df['SMA_20'].iloc[i]
            sma50 = df['SMA_50'].iloc[i]
            
            if rsi < 30 and price > sma20 and sma20 > sma50:
                df.loc[i, 'BUY'] = True
            elif rsi > 70 and price < sma20 and sma20 < sma50:
                df.loc[i, 'SELL'] = True
        
        return df
    
    def _rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def get_parameters(self):
        return self.params.copy()
