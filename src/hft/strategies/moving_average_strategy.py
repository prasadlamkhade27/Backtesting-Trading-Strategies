"""
Moving Average Strategy (Example)
Simple MA crossover strategy - easy to understand example
"""
import pandas as pd
from hft.strategies.base_strategy import BaseStrategy


class MovingAverageStrategy(BaseStrategy):
    """Simple moving average crossover strategy"""
    
    def __init__(self, fast_ma: int = 5, slow_ma: int = 20):
        super().__init__(
            name="Moving Average Strategy",
            description=f"MA Crossover: {fast_ma}x{slow_ma}"
        )
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals based on MA crossover
        """
        df = df.copy()
        
        # Calculate moving averages
        df['ma_fast'] = df['close'].rolling(self.fast_ma).mean()
        df['ma_slow'] = df['close'].rolling(self.slow_ma).mean()
        
        # Generate crossover signals
        # BUY: Fast MA crosses above Slow MA
        df['BUY'] = (df['ma_fast'] > df['ma_slow']) & (df['ma_fast'].shift(1) <= df['ma_slow'].shift(1))
        
        # SELL: Fast MA crosses below Slow MA
        df['SELL'] = (df['ma_fast'] < df['ma_slow']) & (df['ma_fast'].shift(1) >= df['ma_slow'].shift(1))
        
        return df
    
    def get_parameters(self) -> dict:
        return {
            'strategy': self.name,
            'fast_ma': self.fast_ma,
            'slow_ma': self.slow_ma
        }


# ====================== HOW TO USE THIS ======================
# 1. To enable this strategy, add it to strategies/__init__.py:
#
#    from strategies.moving_average_strategy import MovingAverageStrategy
#
#    AVAILABLE_STRATEGIES = {
#        'Pivot Strategy': PivotStrategy,
#        'Moving Average': MovingAverageStrategy  # Add this line
#    }
#
# 2. Then it will automatically appear in the Streamlit app
# 3. Users can select it from the dropdown menu
# ============================================================
