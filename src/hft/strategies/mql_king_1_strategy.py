"""
MQL KING 1 Strategy - Python Implementation
Smart Money Concepts + Price Action HFT Strategy for XAUUSD M1
Converted from MQL5 EA to Python
"""

import pandas as pd
import numpy as np
from hft.strategies.base_strategy import BaseStrategy


class MQLKing1Strategy(BaseStrategy):
    """
    MQL King 1 - Professional SMC HFT Strategy
    
    Uses Smart Money Concepts:
    - Market structure detection (HH/HL/LH/LL)
    - Order block identification
    - Fair value gap detection
    - Liquidity zone mapping
    - Displacement confirmation
    """
    
    def __init__(
        self,
        structure_lookback: int = 10,
        min_structure_ratio: float = 1.2,
        order_block_lookback: int = 5,
        fvg_min_gap_percent: float = 0.01,
        displacement_threshold: float = 2.0,
        displacement_bars: int = 3,
        atr_period: int = 14,
        min_rr_ratio: float = 1.5,
        max_rr_ratio: float = 3.0,
        atr_multiplier_stop: float = 1.5,
        atr_multiplier_target: float = 3.0,
    ):
        super().__init__(
            name="MQL King 1 - SMC HFT",
            description="Smart Money Concepts + Price Action HFT (Order Blocks + FVG + Liquidity)"
        )
        
        # Structure Detection
        self.structure_lookback = structure_lookback
        self.min_structure_ratio = min_structure_ratio
        
        # Order Blocks
        self.order_block_lookback = order_block_lookback
        
        # Fair Value Gaps
        self.fvg_min_gap_percent = fvg_min_gap_percent
        
        # Displacement
        self.displacement_threshold = displacement_threshold
        self.displacement_bars = displacement_bars
        
        # ATR & Risk Management
        self.atr_period = atr_period
        self.min_rr_ratio = min_rr_ratio
        self.max_rr_ratio = max_rr_ratio
        self.atr_multiplier_stop = atr_multiplier_stop
        self.atr_multiplier_target = atr_multiplier_target
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals using SMC methodology
        
        8-Step Process:
        1. Detect market structure (HH/HL/LH/LL)
        2. Detect break of structure
        3. Map liquidity zones
        4. Identify order blocks
        5. Detect FVG
        6. Confirm displacement
        7. Find entry point
        8. Execute with RR validation
        """
        
        df = df.copy()
        
        # ═══════════════════════════════════════════════════════
        # STEP 1: Calculate ATR (for all analysis)
        # ═══════════════════════════════════════════════════════
        df['atr'] = self._calculate_atr(df, self.atr_period)
        
        # ═══════════════════════════════════════════════════════
        # STEP 2: Detect Market Structure
        # ═══════════════════════════════════════════════════════
        df['trend'] = self._detect_market_structure(df)
        
        # ═══════════════════════════════════════════════════════
        # STEP 3: Detect Break of Structure
        # ═══════════════════════════════════════════════════════
        df['bos'] = self._detect_break_of_structure(df)
        
        # ═══════════════════════════════════════════════════════
        # STEP 4: Identify Order Blocks
        # ═══════════════════════════════════════════════════════
        df['order_block_high'] = np.nan
        df['order_block_low'] = np.nan
        df['is_bullish_ob'] = False
        
        for i in range(self.order_block_lookback + 5, len(df)):
            ob_high, ob_low, is_bullish = self._find_order_block(df, i)
            if ob_high > 0:
                df.loc[i, 'order_block_high'] = ob_high
                df.loc[i, 'order_block_low'] = ob_low
                df.loc[i, 'is_bullish_ob'] = is_bullish
        
        # Forward fill order blocks
        df['order_block_high'] = df['order_block_high'].ffill()
        df['order_block_low'] = df['order_block_low'].ffill()
        
        # ═══════════════════════════════════════════════════════
        # STEP 5: Detect Fair Value Gaps
        # ═══════════════════════════════════════════════════════
        df['fvg_top'] = np.nan
        df['fvg_bottom'] = np.nan
        df['is_bullish_fvg'] = False
        
        for i in range(2, len(df)):
            fvg_top, fvg_bottom, is_bullish = self._find_fvg(df, i)
            if fvg_top > 0:
                df.loc[i, 'fvg_top'] = fvg_top
                df.loc[i, 'fvg_bottom'] = fvg_bottom
                df.loc[i, 'is_bullish_fvg'] = is_bullish
        
        # Forward fill FVGs
        df['fvg_top'] = df['fvg_top'].ffill()
        df['fvg_bottom'] = df['fvg_bottom'].ffill()
        
        # ═══════════════════════════════════════════════════════
        # STEP 6: Detect Displacement
        # ═══════════════════════════════════════════════════════
        df['displacement'] = self._detect_displacement(df)
        
        # ═══════════════════════════════════════════════════════
        # STEP 7: Generate BUY Signals
        # ═══════════════════════════════════════════════════════
        df['BUY'] = self._generate_buy_signals(df)
        
        # ═══════════════════════════════════════════════════════
        # STEP 8: Generate SELL Signals
        # ═══════════════════════════════════════════════════════
        df['SELL'] = self._generate_sell_signals(df)
        
        # ═══════════════════════════════════════════════════════
        # STEP 9: Calculate Exit Levels
        # ═══════════════════════════════════════════════════════
        df['entry_price'] = np.where(df['BUY'] | df['SELL'], df['close'], np.nan)
        df['stop_loss'] = np.nan
        df['take_profit'] = np.nan
        
        for i in range(len(df)):
            if df.iloc[i]['BUY']:
                ob_low = df.iloc[i]['order_block_low'] if pd.notna(df.iloc[i]['order_block_low']) else df.iloc[i]['low']
                atr = df.iloc[i]['atr']
                
                df.loc[i, 'stop_loss'] = ob_low - atr * self.atr_multiplier_stop
                df.loc[i, 'take_profit'] = df.iloc[i]['close'] + atr * self.atr_multiplier_target
            
            elif df.iloc[i]['SELL']:
                ob_high = df.iloc[i]['order_block_high'] if pd.notna(df.iloc[i]['order_block_high']) else df.iloc[i]['high']
                atr = df.iloc[i]['atr']
                
                df.loc[i, 'stop_loss'] = ob_high + atr * self.atr_multiplier_stop
                df.loc[i, 'take_profit'] = df.iloc[i]['close'] - atr * self.atr_multiplier_target
        
        return df
    
    # ═══════════════════════════════════════════════════════
    # HELPER FUNCTIONS
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Average True Range"""
        df_copy = df.copy()
        
        df_copy['tr'] = np.maximum(
            df_copy['high'] - df_copy['low'],
            np.maximum(
                np.abs(df_copy['high'] - df_copy['close'].shift(1)),
                np.abs(df_copy['low'] - df_copy['close'].shift(1))
            )
        )
        
        return df_copy['tr'].rolling(period).mean()
    
    def _detect_market_structure(self, df: pd.DataFrame) -> pd.Series:
        """
        Detect market structure (UPTREND=1, DOWNTREND=-1, NO_STRUCTURE=0)
        
        UPTREND: Higher High + Higher Low
        DOWNTREND: Lower High + Lower Low
        """
        trend = np.zeros(len(df))
        
        for i in range(self.structure_lookback + 5, len(df)):
            lookback_data = df.iloc[i - self.structure_lookback:i + 1]
            lookback_prev = df.iloc[max(0, i - self.structure_lookback - 5):i - self.structure_lookback]
            
            if len(lookback_prev) == 0:
                continue
            
            highest = lookback_data['high'].max()
            lowest = lookback_data['low'].min()
            highest_prev = lookback_prev['high'].max()
            lowest_prev = lookback_prev['low'].min()
            
            atr = df.iloc[i]['atr']
            if pd.isna(atr) or atr == 0:
                continue
            
            # UPTREND: HH + HL
            if highest > highest_prev and lowest > lowest_prev and (highest - lowest) > atr * self.min_structure_ratio:
                trend[i] = 1
            # DOWNTREND: LH + LL
            elif highest < highest_prev and lowest < lowest_prev and (highest - lowest) > atr * self.min_structure_ratio:
                trend[i] = -1
        
        return pd.Series(trend, index=df.index)
    
    def _detect_break_of_structure(self, df: pd.DataFrame) -> pd.Series:
        """Detect Break of Structure (BOS)"""
        bos = np.zeros(len(df))
        
        for i in range(1, len(df)):
            if df.iloc[i]['trend'] != 0:
                current_close = df.iloc[i]['close']
                prev_close = df.iloc[i - 1]['close']
                
                if df.iloc[i]['trend'] == 1:  # Uptrend
                    resistance = df.iloc[max(0, i - self.structure_lookback - 5):i]['high'].max()
                    if current_close > resistance and prev_close <= resistance:
                        bos[i] = 1
                
                elif df.iloc[i]['trend'] == -1:  # Downtrend
                    support = df.iloc[max(0, i - self.structure_lookback - 5):i]['low'].min()
                    if current_close < support and prev_close >= support:
                        bos[i] = 1
        
        return pd.Series(bos, index=df.index)
    
    def _find_order_block(self, df: pd.DataFrame, bar_idx: int) -> tuple:
        """Find order block (high, low, is_bullish)"""
        atr = df.iloc[bar_idx]['atr']
        if pd.isna(atr):
            return 0, 0, False
        
        # Look for bullish OB (last bearish before bullish move)
        for i in range(1, min(self.order_block_lookback, bar_idx)):
            if bar_idx - i < 0:
                break
            
            is_bearish = df.iloc[bar_idx - i]['close'] < df.iloc[bar_idx - i]['open']
            next_is_bullish = df.iloc[bar_idx - i + 1]['close'] > df.iloc[bar_idx - i + 1]['open']
            
            if is_bearish and next_is_bullish:
                return (df.iloc[bar_idx - i]['high'],
                        df.iloc[bar_idx - i]['low'],
                        True)
        
        # Look for bearish OB (last bullish before bearish move)
        for i in range(1, min(self.order_block_lookback, bar_idx)):
            if bar_idx - i < 0:
                break
            
            is_bullish = df.iloc[bar_idx - i]['close'] > df.iloc[bar_idx - i]['open']
            next_is_bearish = df.iloc[bar_idx - i + 1]['close'] < df.iloc[bar_idx - i + 1]['open']
            
            if is_bullish and next_is_bearish:
                return (df.iloc[bar_idx - i]['high'],
                        df.iloc[bar_idx - i]['low'],
                        False)
        
        return 0, 0, False
    
    def _find_fvg(self, df: pd.DataFrame, bar_idx: int) -> tuple:
        """Find Fair Value Gap (top, bottom, is_bullish)"""
        if bar_idx < 2 or bar_idx >= len(df):
            return 0, 0, False
        
        current_high = df.iloc[bar_idx]['high']
        current_low = df.iloc[bar_idx]['low']
        current_close = df.iloc[bar_idx]['close']
        
        if bar_idx >= 1:
            next_high = df.iloc[bar_idx - 1]['high']
            next_low = df.iloc[bar_idx - 1]['low']
            
            # Bullish FVG (gap up)
            if current_low > next_high:
                gap_size = current_low - next_high
                gap_percent = (gap_size / current_close) * 100
                
                if gap_percent >= self.fvg_min_gap_percent:
                    return current_low, next_high, True
            
            # Bearish FVG (gap down)
            if current_high < next_low:
                gap_size = next_low - current_high
                gap_percent = (gap_size / current_close) * 100
                
                if gap_percent >= self.fvg_min_gap_percent:
                    return next_low, current_high, False
        
        return 0, 0, False
    
    def _detect_displacement(self, df: pd.DataFrame) -> pd.Series:
        """Detect displacement (strong impulse candles)"""
        displacement = np.zeros(len(df))
        
        for i in range(self.displacement_bars + 5, len(df)):
            trend = df.iloc[i]['trend']
            if trend == 0:
                continue
            
            atr = df.iloc[i]['atr']
            if pd.isna(atr):
                continue
            
            displacement_distance = atr * self.displacement_threshold
            
            for j in range(self.displacement_bars):
                if i - j < 0:
                    continue
                
                candle_size = df.iloc[i - j]['high'] - df.iloc[i - j]['low']
                
                if trend == 1:  # Uptrend
                    candle_move = df.iloc[i - j]['close'] - df.iloc[i - j]['open']
                    if candle_size >= displacement_distance and candle_move > 0:
                        displacement[i] = 1
                        break
                
                elif trend == -1:  # Downtrend
                    candle_move = df.iloc[i - j]['open'] - df.iloc[i - j]['close']
                    if candle_size >= displacement_distance and candle_move > 0:
                        displacement[i] = 1
                        break
        
        return pd.Series(displacement, index=df.index)
    
    def _generate_buy_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate BUY signals"""
        buy = np.zeros(len(df))
        
        for i in range(len(df)):
            # Conditions for BUY
            if df.iloc[i]['trend'] != 1:  # Must be uptrend
                continue
            
            if df.iloc[i]['displacement'] != 1:  # Must have displacement
                continue
            
            if df.iloc[i]['bos'] != 1:  # Must have BOS
                continue
            
            # Entry at order block or FVG
            current_price = df.iloc[i]['close']
            
            # Option 1: OB Retest
            if pd.notna(df.iloc[i]['order_block_low']):
                ob_low = df.iloc[i]['order_block_low']
                ob_high = df.iloc[i]['order_block_high']
                
                if current_price >= ob_low and current_price <= ob_high:
                    # Validate RR
                    atr = df.iloc[i]['atr']
                    if pd.notna(atr):
                        stop_loss = ob_low - atr * self.atr_multiplier_stop
                        take_profit = current_price + atr * self.atr_multiplier_target
                        
                        risk = current_price - stop_loss
                        reward = take_profit - current_price
                        
                        if risk > 0 and reward / risk >= self.min_rr_ratio and reward / risk <= self.max_rr_ratio:
                            buy[i] = 1
            
            # Option 2: FVG Fill
            if pd.notna(df.iloc[i]['fvg_bottom']):
                if df.iloc[i]['is_bullish_fvg']:
                    fvg_bottom = df.iloc[i]['fvg_bottom']
                    fvg_top = df.iloc[i]['fvg_top']
                    
                    if current_price >= fvg_bottom and current_price <= fvg_top:
                        buy[i] = 1
        
        return pd.Series(buy > 0, index=df.index)
    
    def _generate_sell_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate SELL signals"""
        sell = np.zeros(len(df))
        
        for i in range(len(df)):
            # Conditions for SELL
            if df.iloc[i]['trend'] != -1:  # Must be downtrend
                continue
            
            if df.iloc[i]['displacement'] != 1:  # Must have displacement
                continue
            
            if df.iloc[i]['bos'] != 1:  # Must have BOS
                continue
            
            # Entry at order block or FVG
            current_price = df.iloc[i]['close']
            
            # Option 1: OB Retest
            if pd.notna(df.iloc[i]['order_block_high']):
                ob_low = df.iloc[i]['order_block_low']
                ob_high = df.iloc[i]['order_block_high']
                
                if current_price >= ob_low and current_price <= ob_high:
                    # Validate RR
                    atr = df.iloc[i]['atr']
                    if pd.notna(atr):
                        stop_loss = ob_high + atr * self.atr_multiplier_stop
                        take_profit = current_price - atr * self.atr_multiplier_target
                        
                        risk = stop_loss - current_price
                        reward = current_price - take_profit
                        
                        if risk > 0 and reward / risk >= self.min_rr_ratio and reward / risk <= self.max_rr_ratio:
                            sell[i] = 1
            
            # Option 2: FVG Fill
            if pd.notna(df.iloc[i]['fvg_top']):
                if not df.iloc[i]['is_bullish_fvg']:
                    fvg_bottom = df.iloc[i]['fvg_bottom']
                    fvg_top = df.iloc[i]['fvg_top']
                    
                    if current_price >= fvg_bottom and current_price <= fvg_top:
                        sell[i] = 1
        
        return pd.Series(sell > 0, index=df.index)
    
    def get_parameters(self) -> dict:
        """Return strategy parameters"""
        return {
            'strategy': self.name,
            'structure_lookback': self.structure_lookback,
            'min_structure_ratio': self.min_structure_ratio,
            'order_block_lookback': self.order_block_lookback,
            'fvg_min_gap_percent': self.fvg_min_gap_percent,
            'displacement_threshold': self.displacement_threshold,
            'displacement_bars': self.displacement_bars,
            'atr_period': self.atr_period,
            'min_rr_ratio': self.min_rr_ratio,
            'max_rr_ratio': self.max_rr_ratio,
            'atr_multiplier_stop': self.atr_multiplier_stop,
            'atr_multiplier_target': self.atr_multiplier_target,
        }
