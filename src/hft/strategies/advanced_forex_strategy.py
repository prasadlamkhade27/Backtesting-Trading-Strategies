"""
Advanced Forex & Gold Trading Strategy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Technical Analysis Based Strategy
- Combines RSI + Stochastic + Support/Resistance for clean entries
- Leading indicators: RSI (momentum) + Stochastic (confirmation)
- Risk Management: 1.5x ATR stops, 2-3x risk rewards
- Target Win Rate: >50% with solid risk/reward
"""

import pandas as pd
import numpy as np
from typing import Tuple


class AdvancedForexStrategy:
    """Forex & Gold Trading Strategy - RSI + Stochastic"""
    
    def __init__(self):
        self.name = "Advanced Forex - RSI + Stochastic"
        self.description = "Clean leading indicator strategy: RSI momentum + Stochastic confirmation"
    
    @staticmethod
    def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals using RSI and Stochastic
        
        Required columns: open, high, low, close, volume
        
        Returns df with BUY and SELL columns (1 for signal, 0 for no signal)
        """
        df = df.copy()
        
        # ════════════════════════════════════════════════════════════════════════════
        # STEP 1: Calculate RSI (14 period)
        # ════════════════════════════════════════════════════════════════════════════
        df['rsi'] = AdvancedForexStrategy._calculate_rsi(df['close'], period=14)
        
        # ════════════════════════════════════════════════════════════════════════════
        # STEP 2: Calculate Stochastic Oscillator (14,3,3)
        # ════════════════════════════════════════════════════════════════════════════
        k, d = AdvancedForexStrategy._calculate_stochastic(df, period=14, smooth_k=3, smooth_d=3)
        df['stoch_k'] = k
        df['stoch_d'] = d
        
        # Stochastic Crossovers (leading signal)
        df['stoch_bullish_cross'] = (df['stoch_k'] > df['stoch_d']) & (df['stoch_k'].shift(1) <= df['stoch_d'].shift(1))
        df['stoch_bearish_cross'] = (df['stoch_k'] < df['stoch_d']) & (df['stoch_k'].shift(1) >= df['stoch_d'].shift(1))
        
        # ════════════════════════════════════════════════════════════════════════════
        # STEP 3: Support & Resistance (5-period swing points)
        # ════════════════════════════════════════════════════════════════════════════
        window = 5
        df['swing_high'] = df['high'].rolling(window=window, center=True).max()
        df['swing_low'] = df['low'].rolling(window=window, center=True).min()
        df['recent_resistance'] = df['swing_high'].rolling(window=20).max()
        df['recent_support'] = df['swing_low'].rolling(window=20).min()
        
        # ════════════════════════════════════════════════════════════════════════════
        # STEP 4: Price Action Patterns
        # ════════════════════════════════════════════════════════════════════════════
        df['higher_low'] = (df['low'] > df['low'].shift(1)) & (df['low'].shift(1) > df['low'].shift(2))
        df['lower_high'] = (df['high'] < df['high'].shift(1)) & (df['high'].shift(1) < df['high'].shift(2))
        
        # ════════════════════════════════════════════════════════════════════════════
        # STEP 5: ATR for Stop Loss & Position Sizing
        # ════════════════════════════════════════════════════════════════════════════
        df['atr'] = AdvancedForexStrategy._calculate_atr(df, period=14)
        df['stop_loss_atr'] = df['atr'] * 1.5  # 1.5x ATR stop
        df['take_profit_2r'] = df['atr'] * 3   # 2:1 risk/reward
        df['take_profit_3r'] = df['atr'] * 4.5 # 3:1 risk/reward
        
        # ════════════════════════════════════════════════════════════════════════════
        # STEP 6: BUY SIGNALS (RSI + Stochastic + Price Action)
        # ════════════════════════════════════════════════════════════════════════════
        buy_condition_1 = (
            (df['rsi'] < 30) &  # RSI oversold
            df['stoch_bullish_cross'] &  # Stochastic crossover
            df['higher_low']  # Price action confirms
        )
        
        buy_condition_2 = (
            (df['rsi'] < 40) &  # RSI not far overbought
            df['stoch_bullish_cross'] &
            (df['stoch_k'] < 20)  # Stochastic extreme
        )
        
        buy_condition_3 = (
            (df['rsi'] > df['rsi'].shift(1)) &  # RSI rising
            (df['rsi'] < 50) &  # Not overbought
            df['stoch_bullish_cross'] &
            (df['close'] <= df['recent_support'] * 1.01)  # Near support
        )
        
        df['BUY'] = (buy_condition_1 | buy_condition_2 | buy_condition_3).astype(int)
        
        # ════════════════════════════════════════════════════════════════════════════
        # STEP 7: SELL SIGNALS (RSI + Stochastic + Price Action)
        # ════════════════════════════════════════════════════════════════════════════
        sell_condition_1 = (
            (df['rsi'] > 70) &  # RSI overbought
            df['stoch_bearish_cross'] &  # Stochastic crossover
            df['lower_high']  # Price action confirms
        )
        
        sell_condition_2 = (
            (df['rsi'] > 60) &  # RSI not far oversold
            df['stoch_bearish_cross'] &
            (df['stoch_k'] > 80)  # Stochastic extreme
        )
        
        sell_condition_3 = (
            (df['rsi'] < df['rsi'].shift(1)) &  # RSI falling
            (df['rsi'] > 50) &  # Not oversold
            df['stoch_bearish_cross'] &
            (df['close'] >= df['recent_resistance'] * 0.99)  # Near resistance
        )
        
        df['SELL'] = (sell_condition_1 | sell_condition_2 | sell_condition_3).astype(int)
        
        # ════════════════════════════════════════════════════════════════════════════
        # STEP 8: Clean up temporary columns
        # ════════════════════════════════════════════════════════════════════════════
        columns_to_drop = [
            'rsi', 'stoch_k', 'stoch_d', 'stoch_bullish_cross', 'stoch_bearish_cross',
            'swing_high', 'swing_low', 'recent_resistance', 'recent_support',
            'higher_low', 'lower_high'
        ]
        
        df = df.drop(columns=columns_to_drop, errors='ignore')
        
        return df

    
    @staticmethod
    def _calculate_rsi(prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def _calculate_stochastic(df, period=14, smooth_k=3, smooth_d=3):
        """Calculate Stochastic Oscillator"""
        low_min = df['low'].rolling(window=period).min()
        high_max = df['high'].rolling(window=period).max()
        
        k_raw = 100 * (df['close'] - low_min) / (high_max - low_min)
        k = k_raw.rolling(window=smooth_k).mean()
        d = k.rolling(window=smooth_d).mean()
        
        return k, d
    
    @staticmethod
    def _calculate_atr(df, period=14):
        """Calculate Average True Range"""
        tr1 = df['high'] - df['low']
        tr2 = abs(df['high'] - df['close'].shift())
        tr3 = abs(df['low'] - df['close'].shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def get_strategy_info():
        """Get strategy details and rules"""
        return {
            'name': 'Advanced Forex & Gold Strategy - RSI + Stochastic',
            'type': 'Technical Analysis - Leading Indicators',
            'indicators': ['RSI (14)', 'Stochastic (14,3,3)', 'Support/Resistance', 'ATR (14)'],
            'best_pairs': ['XAUUSD (Gold)', 'EURUSD', 'GBPUSD', 'USDJPY'],
            'timeframes': ['1H', '4H', '1D', '4H'],
            'risk_reward': '1:2 to 1:3',
            'win_rate_target': '>50%',
            'entry_rules': [
                'RSI < 30 + Stochastic bullish cross + Higher low (BUY)',
                'RSI < 40 + Stochastic bullish cross + Stoch K < 20 (BUY)',
                'RSI rising + RSI < 50 + Stochastic cross + Near support (BUY)',
                'RSI > 70 + Stochastic bearish cross + Lower high (SELL)',
                'RSI > 60 + Stochastic bearish cross + Stoch K > 80 (SELL)',
                'RSI falling + RSI > 50 + Stochastic cross + Near resistance (SELL)'
            ],
            'exit_rules': [
                'Take Profit: 2x ATR (1:2 risk/reward)',
                'Take Profit: 3x ATR (1:3 risk/reward)',
                'Stop Loss: 1.5x ATR',
            ],
            'signal_quality': 'Clean - RSI + Stochastic + Price Action confluence'
        }


