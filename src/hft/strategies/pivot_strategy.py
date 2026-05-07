"""
Pivot Point Strategy
Detects pivot high/low points and generates signals on breakouts
"""
import pandas as pd
import numpy as np
from hft.strategies.base_strategy import BaseStrategy


class PivotStrategy(BaseStrategy):
    """Pivot point and market structure strategy"""
    
    def __init__(self, left_bars: int = 5):
        super().__init__(
            name="Pivot Strategy",
            description="Detects pivot highs/lows and trades breakouts based on market structure"
        )
        self.left_bars = left_bars
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate pivot-based signals
        
        Args:
            df: DataFrame with columns: time, open, high, low, close, volume
            
        Returns:
            DataFrame with BUY and SELL signals
        """
        df = df.copy()
        
        # Calculate pivot highs and lows
        df['pvh'] = self._pivot_high(df['high'], self.left_bars)
        df['pvl'] = self._pivot_low(df['low'], self.left_bars)
        
        # Forward fill to get current levels
        df['ph'] = df['pvh'].ffill()
        df['pl'] = df['pvl'].ffill()
        
        # Determine market structure (uptrend=1, downtrend=-1)
        ms = [0] * len(df)
        for i in range(2, len(df)):
            if df.iloc[i]['close'] > df.iloc[i]['ph']:
                ms[i] = 1
            elif df.iloc[i]['close'] < df.iloc[i]['pl']:
                ms[i] = -1
            else:
                ms[i] = ms[i-1]
        
        df['ms'] = ms
        
        # Generate signals
        df['BUY'] = (df['close'] > df['ph']) & (df['ms'].shift(1) < 0)
        df['SELL'] = (df['close'] < df['pl']) & (df['ms'].shift(1) > 0)
        
        return df
    
    @staticmethod
    def _pivot_high(high, left):
        """Find pivot highs"""
        return high[(high.shift(left) < high) & (high.shift(-left) < high)]
    
    @staticmethod
    def _pivot_low(low, left):
        """Find pivot lows"""
        return low[(low.shift(left) > low) & (low.shift(-left) > low)]
    
    def get_parameters(self) -> dict:
        """Return strategy parameters"""
        return {
            'strategy': self.name,
            'left_bars': self.left_bars
        }
