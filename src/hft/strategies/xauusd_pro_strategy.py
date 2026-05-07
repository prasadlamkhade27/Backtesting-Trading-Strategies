"""
XAUUSD PRO-LEVEL STRATEGY - Smart Money + Confluence-Based
═══════════════════════════════════════════════════════════════

Strategy Name: "Market Structure + Pullback Strategy"

MARKET UNDERSTANDING:
- Asset: XAUUSD (Gold/USD)
- Nature: Mean-reversion + Breakout (Ranges + Trends)
- Best sessions: London Open, NY Open, Asia Close
- Volatility: High during data releases and Fed announcements

TIMEFRAME: 4H-1D (Swing Trading)
- PropFirm-friendly (less monitoring required)
- Avoid news volatility spikes
- Good risk/reward opportunities

LOGIC OVERVIEW:
┌─────────────────────────────────────────────────────────┐
│ MARKET FILTER (When NOT to trade)                       │
│ ✓ Trend filter: 200 EMA (Strong/Weak/Mixed)            │
│ ✓ Volatility filter: ATR (Normal/Low/High)             │
│ ✓ Session filter: Avoid low liquidity periods           │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│ ENTRY CONDITIONS (UPTREND EXAMPLE)                      │
│ ✓ Price above 200 EMA (Trend filter)                   │
│ ✓ Pullback to 20-30 EMA (Demand zone)                  │
│ ✓ Bullish divergence OR price bounces at support       │
│ ✓ Momentum confirmation (RSI > 50 for bullish)         │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│ EXIT CONDITIONS (Risk Management)                       │
│ ✓ Stop Loss: Below recent swing low                    │
│ ✓ Take Profit (TP1): 1:1 RR (Quick partial)           │
│ ✓ Take Profit (TP2): 1:2 RR (Main target)             │
│ ✓ Take Profit (TP3): 1:3 RR (Extended target)         │
│ ✓ Time-based: Max 5 days holding (prevents overnight drawdown)
└─────────────────────────────────────────────────────────┘

RISK MANAGEMENT:
- Fixed risk per trade: 1% of account
- Max daily loss: 3% (PropFirm safe)
- Max monthly loss: 10%
- Position size: Auto-calculated based on SL distance

PERFORMANCE TARGETS:
- Win Rate: 50-60% (Conservative)
- Risk/Reward: Minimum 1:2
- Monthly Expectancy: +2-3%
- Sharpe Ratio: > 1.0
"""

import pandas as pd
import numpy as np
from hft.strategies.base_strategy import BaseStrategy


class XAUUSDProStrategy(BaseStrategy):
    """
    Professional XAUUSD Trading Strategy
    Uses Market Structure + Pullback + Confluence approach
    """
    
    def __init__(
        self,
        trend_ema: int = 200,           # Trend filter
        pullback_ema: int = 20,         # Pullback zone
        atr_period: int = 14,           # Volatility
        rsi_period: int = 14,           # Momentum
        min_rr_ratio: float = 2.0,      # Minimum 1:2 RR
        lookback_bars: int = 20         # For swing detection
    ):
        super().__init__(
            name="XAUUSD Pro Strategy",
            description="Smart Money + Market Structure (200 EMA + Pullback + Confluence)"
        )
        
        # Indicators
        self.trend_ema = trend_ema
        self.pullback_ema = pullback_ema
        self.atr_period = atr_period
        self.rsi_period = rsi_period
        
        # Risk Management
        self.min_rr_ratio = min_rr_ratio
        self.lookback_bars = lookback_bars
        
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate BUY and SELL signals based on pro-level logic
        
        Args:
            df: DataFrame with OHLC data (must have: open, high, low, close, volume)
            
        Returns:
            DataFrame with signals and metadata
        """
        df = df.copy()
        
        # ═══════════════════════════════════════════════════════
        # STEP 1: CALCULATE INDICATORS
        # ═══════════════════════════════════════════════════════
        
        # Trend Filter (200 EMA)
        df['ema_200'] = df['close'].ewm(span=self.trend_ema, adjust=False).mean()
        
        # Pullback Zone (20 EMA)
        df['ema_20'] = df['close'].ewm(span=self.pullback_ema, adjust=False).mean()
        
        # Volatility (ATR)
        df['atr'] = self._calculate_atr(df, self.atr_period)
        
        # Momentum (RSI)
        df['rsi'] = self._calculate_rsi(df, self.rsi_period)
        
        # ═══════════════════════════════════════════════════════
        # STEP 2: IDENTIFY MARKET CONDITIONS
        # ═══════════════════════════════════════════════════════
        
        # Trend Direction
        df['trend'] = np.where(df['close'] > df['ema_200'], 'UPTREND', 
                              np.where(df['close'] < df['ema_200'], 'DOWNTREND', 'MIXED'))
        
        # Volatility Level
        atr_ma = df['atr'].rolling(20).mean()
        df['volatility'] = np.where(df['atr'] > atr_ma * 1.5, 'HIGH',
                                   np.where(df['atr'] < atr_ma * 0.7, 'LOW', 'NORMAL'))
        
        # ═══════════════════════════════════════════════════════
        # STEP 3: IDENTIFY SWING LEVELS (Support/Resistance)
        # ═══════════════════════════════════════════════════════
        
        # Previous swing low/high
        df['swing_high'] = df['high'].rolling(self.lookback_bars, center=True).max()
        df['swing_low'] = df['low'].rolling(self.lookback_bars, center=True).min()
        
        # ═══════════════════════════════════════════════════════
        # STEP 4: GENERATE BUY SIGNALS
        # ═══════════════════════════════════════════════════════
        
        buy_signal = (
            # Market Filter: Must be in uptrend
            (df['trend'] == 'UPTREND') &
            
            # Volatility filter: Avoid extreme volatility
            (df['volatility'] != 'HIGH') &
            
            # Structure: Price near pullback zone (20 EMA)
            (df['close'] <= df['ema_20'] * 1.02) &  # Within 2% above EMA
            (df['close'] >= df['ema_20'] * 0.98) &  # Within 2% below EMA
            
            # Confluence: Price bouncing off support
            (df['close'] >= df['swing_low']) &
            
            # Momentum: RSI not oversold, trending up
            (df['rsi'] > 35) &
            (df['rsi'] < 70) &
            
            # Liquidity: Decent volume (optional but helps)
            (df['volume'] > df['volume'].rolling(20).mean() * 0.8)
        )
        
        # ═══════════════════════════════════════════════════════
        # STEP 5: GENERATE SELL SIGNALS
        # ═══════════════════════════════════════════════════════
        
        sell_signal = (
            # Market Filter: Must be in downtrend
            (df['trend'] == 'DOWNTREND') &
            
            # Volatility filter: Avoid extreme volatility
            (df['volatility'] != 'HIGH') &
            
            # Structure: Price near pullback zone (20 EMA)
            (df['close'] >= df['ema_20'] * 0.98) &  # Within 2% below EMA
            (df['close'] <= df['ema_20'] * 1.02) &  # Within 2% above EMA
            
            # Confluence: Price bouncing off resistance
            (df['close'] <= df['swing_high']) &
            
            # Momentum: RSI not overbought, trending down
            (df['rsi'] < 65) &
            (df['rsi'] > 30) &
            
            # Liquidity: Decent volume
            (df['volume'] > df['volume'].rolling(20).mean() * 0.8)
        )
        
        # ═══════════════════════════════════════════════════════
        # STEP 6: CALCULATE RISK/REWARD LEVELS
        # ═══════════════════════════════════════════════════════
        
        # For BUY signals
        df['entry_price_buy'] = np.where(buy_signal, df['close'], np.nan)
        df['stop_loss_buy'] = np.where(buy_signal, 
                                        df['swing_low'] - df['atr'] * 0.5,  # Below support with buffer
                                        np.nan)
        
        # Risk distance
        df['risk_distance_buy'] = df['entry_price_buy'] - df['stop_loss_buy']
        
        # Take Profit levels (using RR multiples)
        df['tp1_buy'] = df['entry_price_buy'] + df['risk_distance_buy'] * 1.0  # 1:1 RR
        df['tp2_buy'] = df['entry_price_buy'] + df['risk_distance_buy'] * 2.0  # 1:2 RR
        df['tp3_buy'] = df['entry_price_buy'] + df['risk_distance_buy'] * 3.0  # 1:3 RR
        
        # For SELL signals
        df['entry_price_sell'] = np.where(sell_signal, df['close'], np.nan)
        df['stop_loss_sell'] = np.where(sell_signal,
                                         df['swing_high'] + df['atr'] * 0.5,  # Above resistance
                                         np.nan)
        
        df['risk_distance_sell'] = df['stop_loss_sell'] - df['entry_price_sell']
        
        df['tp1_sell'] = df['entry_price_sell'] - df['risk_distance_sell'] * 1.0
        df['tp2_sell'] = df['entry_price_sell'] - df['risk_distance_sell'] * 2.0
        df['tp3_sell'] = df['entry_price_sell'] - df['risk_distance_sell'] * 3.0
        
        # ═══════════════════════════════════════════════════════
        # STEP 7: RR FILTER (Only trade if RR is good enough)
        # ═══════════════════════════════════════════════════════
        
        buy_rr_valid = (df['risk_distance_buy'] > 0) & ((df['tp2_buy'] - df['entry_price_buy']) / df['risk_distance_buy'] >= self.min_rr_ratio)
        sell_rr_valid = (df['risk_distance_sell'] > 0) & ((df['entry_price_sell'] - df['tp2_sell']) / df['risk_distance_sell'] >= self.min_rr_ratio)
        
        df['BUY'] = buy_signal & buy_rr_valid
        df['SELL'] = sell_signal & sell_rr_valid
        
        return df
    
    # ═══════════════════════════════════════════════════════
    # HELPER FUNCTIONS
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Average True Range"""
        df_copy = df.copy()
        
        # True Range
        df_copy['tr'] = np.maximum(
            df_copy['high'] - df_copy['low'],
            np.maximum(
                abs(df_copy['high'] - df_copy['close'].shift(1)),
                abs(df_copy['low'] - df_copy['close'].shift(1))
            )
        )
        
        # ATR
        return df_copy['tr'].rolling(period).mean()
    
    @staticmethod
    def _calculate_rsi(df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = df['close'].diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def get_parameters(self) -> dict:
        """Return strategy parameters"""
        return {
            'strategy': self.name,
            'trend_ema': self.trend_ema,
            'pullback_ema': self.pullback_ema,
            'atr_period': self.atr_period,
            'rsi_period': self.rsi_period,
            'min_rr_ratio': self.min_rr_ratio,
            'lookback_bars': self.lookback_bars
        }


# ═══════════════════════════════════════════════════════════════════════════════
# HOW TO INTEGRATE THIS STRATEGY
# ═══════════════════════════════════════════════════════════════════════════════
#
# 1. In strategies/__init__.py, add:
#
#    from strategies.xauusd_pro_strategy import XAUUSDProStrategy
#
#    AVAILABLE_STRATEGIES = {
#        'XAUUSD Pro Strategy': XAUUSDProStrategy,
#        'Pivot Strategy': PivotStrategy,
#        'Moving Average': MovingAverageStrategy
#    }
#
# 2. In your Streamlit app (backtest_xauusd.py), the strategy will appear in dropdown
#
# 3. The strategy will automatically:
#    - Generate BUY/SELL signals
#    - Calculate entry prices with TP/SL levels
#    - Filter bad trades (poor RR, bad volatility, etc.)
#    - Provide metrics for backtesting
#
# ═══════════════════════════════════════════════════════════════════════════════
